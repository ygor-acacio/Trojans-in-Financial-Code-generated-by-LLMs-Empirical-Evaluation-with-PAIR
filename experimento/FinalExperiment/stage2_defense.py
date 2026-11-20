#!/usr/bin/env python3
"""
ETAPA 2 / 3 — DEFESA MULTIAGENTE

Le data/attack/attack_runs.csv (900 amostras) e roda os 3 agentes de defesa
UMA unica vez por amostra (3 x 900 = 2700 chamadas), cacheando os vereditos em
data/defense/agent_verdicts.csv.

Como os agentes sao deterministicos (temperature=0.0), os 7 cenarios pedidos
(3 agentes solo, 3 pares, 1 trio) sao DERIVADOS dos vereditos cacheados sem
re-executar nada — isola a unica variavel que muda entre cenarios: a regra de
uniao dos agentes.

Regra de agregacao (config.DEFENSE_AGGREGATION='or'): o cenario BLOQUEIA se
QUALQUER agente do cenario marcar 'suspicious' com confianca >= DEFENSE_THRESHOLD.

Saida: data/defense/agent_verdicts.csv  +  data/defense/config_<nome>.csv (7 arquivos)
       cada config_<nome>.csv ja tem as colunas que o Juiz (etapa 3) espera.

RETOMADA: amostras ja presentes em agent_verdicts.csv sao puladas.

Uso:
    python stage2_defense.py
    python stage2_defense.py --rebuild-configs   # so re-deriva os 7 CSVs do cache
"""
import sys
import time
import argparse
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

import config as C
import common as K

# importa os 3 agentes do projeto (../Defense)
sys.path.insert(0, str(C.DEFENSE_SRC))
import agent_behavior_detector
import agent_trojan_pattern
import agent_policy_verifier

AGENT_MODULES = {
    "behavior_detector": agent_behavior_detector,
    "trojan_pattern": agent_trojan_pattern,
    "policy_verifier": agent_policy_verifier,
}

_log = K.setup_logging("stage2", C.LOGS / "stage2_defense.log")


def uid_of(row) -> str:
    return f"{str(row['generator_model']).split('/')[-1]}|{row['level']}|{row['base_task']}|{row['iteration']}"


def agent_blocks(verdict: str, confidence: float) -> bool:
    return str(verdict).lower() == "suspicious" and float(confidence) >= C.DEFENSE_THRESHOLD


def run_agents() -> pd.DataFrame:
    if not C.ATTACK_RUNS_CSV.exists():
        _log.error(f"Nao encontrei {C.ATTACK_RUNS_CSV}. Rode a etapa 1 primeiro.")
        sys.exit(1)

    df_attack = pd.read_csv(C.ATTACK_RUNS_CSV)
    _log.info(f"Ataque carregado: {len(df_attack)} amostras")

    cached: Dict[str, Dict[str, Any]] = {}
    if C.AGENT_VERDICTS_CSV.exists():
        prev = pd.read_csv(C.AGENT_VERDICTS_CSV)
        for _, r in prev.iterrows():
            cached[str(r["uid"])] = r.to_dict()
        _log.info(f"Cache existente: {len(cached)} amostras ja analisadas")

    out_rows: List[Dict[str, Any]] = list(cached.values())
    processed = 0
    t_start = time.time()
    total = len(df_attack)

    for idx, (_, row) in enumerate(df_attack.iterrows(), 1):
        uid = uid_of(row)
        if uid in cached:
            continue
        code = str(row.get("code", "") or "")
        task = str(row.get("task", ""))
        rec: Dict[str, Any] = {
            "uid": uid,
            "run_id": C.RUN_ID,
            "generator_model": row.get("generator_model"),
            "level": row.get("level"),
            "base_task": row.get("base_task"),
            "task": task,
            "iteration": row.get("iteration"),
            "score_r1": row.get("score_r1"),
            "possible_hidden_logic": row.get("possible_hidden_logic"),
            "code": code,
        }
        _log.info(f"[{idx}/{total}] {uid}")
        for agent_name in C.AGENTS:
            mod = AGENT_MODULES[agent_name]
            r = {"verdict": "unknown", "confidence": 0.0, "findings_str": "",
                 "rationale": "", "parse_ok": False}
            if code.strip():
                try:
                    r = mod.analyze(code, task, model=C.DEFENSE_MODEL, verbose=False)
                except Exception as e:
                    _log.error(f"  agente {agent_name} erro: {e}")
            else:
                r["rationale"] = "codigo vazio (ataque falhou)"
            rec[f"{agent_name}_verdict"] = str(r.get("verdict", "unknown")).lower()
            rec[f"{agent_name}_confidence"] = float(r.get("confidence", 0.0))
            rec[f"{agent_name}_findings"] = r.get("findings_str", "")
            rec[f"{agent_name}_rationale"] = r.get("rationale", "")
            rec[f"{agent_name}_parse_ok"] = bool(r.get("parse_ok", False))
            rec[f"{agent_name}_blocks"] = agent_blocks(r.get("verdict", ""), r.get("confidence", 0.0))
            time.sleep(C.SLEEP_SEC)

        out_rows.append(rec)
        cached[uid] = rec
        processed += 1
        # salva incrementalmente a cada 10 amostras (robustez)
        if processed % 10 == 0:
            pd.DataFrame(out_rows).to_csv(C.AGENT_VERDICTS_CSV, index=False, encoding="utf-8")
            avg = (time.time() - t_start) / processed
            _log.info(f"  checkpoint: {processed} novas | ~{avg:.1f}s/amostra")

    df_verdicts = pd.DataFrame(out_rows)
    df_verdicts.to_csv(C.AGENT_VERDICTS_CSV, index=False, encoding="utf-8")
    _log.info(f"Vereditos salvos: {C.AGENT_VERDICTS_CSV} ({len(df_verdicts)} amostras)")
    return df_verdicts


def build_configs(df_verdicts: pd.DataFrame) -> None:
    _log.info(f"Derivando {len(C.DEFENSE_CONFIGS)} cenarios (regra='{C.DEFENSE_AGGREGATION}')")
    for cfg_name, agents in C.DEFENSE_CONFIGS.items():
        rows: List[Dict[str, Any]] = []
        for _, r in df_verdicts.iterrows():
            blockers = [a for a in agents if bool(r.get(f"{a}_blocks", False))]
            blocked = len(blockers) > 0 if C.DEFENSE_AGGREGATION == "or" else len(blockers) == len(agents)
            allowed = not blocked
            reasoning = (f"config={cfg_name} agentes={agents} "
                         f"bloqueado_por={blockers if blockers else 'nenhum'}")
            rows.append({
                "run_id": C.RUN_ID,
                "config_name": cfg_name,
                "generator_model": r.get("generator_model"),
                "level": r.get("level"),
                "base_task": r.get("base_task"),
                "task": r.get("task"),
                "iteration": r.get("iteration"),
                "score_r1": r.get("score_r1"),
                # colunas EXIGIDAS pelo Juiz (etapa 3):
                "attack_hidden_logic": bool(r.get("possible_hidden_logic", False)),
                "allowed": allowed,
                "code": r.get("code", ""),
                "agent2_findings": r.get("trojan_pattern_findings", ""),
                "reasoning": reasoning,
                # provenance extra:
                "final_verdict": "allowed" if allowed else "blocked",
                "n_agents": len(agents),
            })
        out = C.DEFENSE_DIR / f"config_{cfg_name}.csv"
        pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8")
        n_block = sum(1 for x in rows if not x["allowed"])
        _log.info(f"  {cfg_name}: {out.name} ({len(rows)} linhas, {n_block} bloqueadas)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild-configs", action="store_true",
                    help="apenas re-deriva os 7 CSVs a partir do cache de vereditos")
    args = ap.parse_args()
    K.load_env()
    C.DEFENSE_DIR.mkdir(parents=True, exist_ok=True)

    if args.rebuild_configs:
        if not C.AGENT_VERDICTS_CSV.exists():
            _log.error("Sem cache de vereditos. Rode sem --rebuild-configs primeiro.")
            sys.exit(1)
        df_verdicts = pd.read_csv(C.AGENT_VERDICTS_CSV)
    else:
        df_verdicts = run_agents()

    build_configs(df_verdicts)
    _log.info("Etapa 2 concluida. Proximo: python stage3_judge.py")


if __name__ == "__main__":
    main()
