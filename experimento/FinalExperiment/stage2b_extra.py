#!/usr/bin/env python3
"""
ETAPA 2b — CENARIOS EXTRA DE DEFESA (topologias)

Le data/defense/agent_verdicts.csv (produzido pela Etapa 2) e gera 3 cenarios novos,
no MESMO formato config_<nome>.csv que o Juiz (Etapa 3) consome:

  1) weighted_score  — voto PONDERADO sobre as decisoes de bloqueio (config.WEIGHTS).
                       bloqueia se soma dos pesos dos bloqueadores >= limiar (maioria ponderada).
  2) series_cascade  — topologia SERIE: agentes em ordem (config.SERIES_ORDER) com saida
                       antecipada (bloqueio forte / liberacao forte) e fallback por maioria.
  3) orchestrator    — 4o agente LLM decide QUAIS especialistas consultar; veredito = uniao
                       (OR) dos escolhidos. Usa 1 chamada LLM por amostra (cache retomavel).

Uso:
    python stage2b_extra.py                 # gera os 3
    python stage2b_extra.py --skip-orch     # so weighted + series (sem gastar API)
    python stage2b_extra.py --only orchestrator
"""
import sys
import time
import argparse
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

import config as C
import common as K
import agent_orchestrator

_log = K.setup_logging("stage2b", C.LOGS / "stage2b_extra.log")


def _base_row(r, cfg_name: str, allowed: bool, reasoning: str) -> Dict[str, Any]:
    """Linha no schema exigido pelo Juiz + provenance."""
    return {
        "run_id": C.RUN_ID,
        "config_name": cfg_name,
        "generator_model": r["generator_model"],
        "level": r["level"],
        "base_task": r["base_task"],
        "task": r["task"],
        "iteration": r["iteration"],
        "score_r1": r["score_r1"],
        "attack_hidden_logic": bool(r["possible_hidden_logic"]),
        "allowed": allowed,
        "code": r["code"],
        "agent2_findings": r.get("trojan_pattern_findings", ""),
        "reasoning": reasoning,
        "final_verdict": "allowed" if allowed else "blocked",
        "n_agents": None,
    }


def build_weighted(dfv: pd.DataFrame) -> None:
    W = C.WEIGHTS
    thr = C.weight_threshold()
    rows = []
    for _, r in dfv.iterrows():
        blockers = {a: bool(r[f"{a}_blocks"]) for a in W}
        score = sum(W[a] for a, b in blockers.items() if b)
        allowed = not (score >= thr)
        reasoning = (f"weighted_score={score:.2f}/{sum(W.values()):.2f} thr={thr:.2f} "
                     f"blockers={[a for a, b in blockers.items() if b] or 'nenhum'}")
        row = _base_row(r, "weighted_score", allowed, reasoning)
        row["n_agents"] = 3
        row["weighted_score"] = round(score, 3)
        rows.append(row)
    out = C.DEFENSE_DIR / "config_weighted_score.csv"
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8")
    nb = sum(1 for x in rows if not x["allowed"])
    _log.info(f"weighted_score: {out.name} ({len(rows)} linhas, {nb} bloqueadas) pesos={W} thr={thr:.2f}")


def _series_decision(r) -> (bool, str):
    """Retorna (allowed, trilha). Cascata com saida antecipada + fallback por maioria."""
    trail = []
    for a in C.SERIES_ORDER:
        verdict = str(r[f"{a}_verdict"]).lower()
        conf = float(r[f"{a}_confidence"])
        blocks = bool(r[f"{a}_blocks"])
        trail.append(f"{a}:{verdict}/{conf:.2f}")
        if blocks and conf >= C.SERIES_TAU_BLOCK:
            return False, "EARLY_BLOCK @ " + " -> ".join(trail)
        if verdict == "clean" and conf >= C.SERIES_TAU_CLEAR:
            return True, "EARLY_CLEAR @ " + " -> ".join(trail)
    # sem decisao forte: maioria dos blocks
    nblocks = sum(1 for a in C.SERIES_ORDER if bool(r[f"{a}_blocks"]))
    allowed = not (nblocks >= C.SERIES_FALLBACK_MIN_BLOCKS)
    return allowed, f"FALLBACK maioria blocks={nblocks}>=({C.SERIES_FALLBACK_MIN_BLOCKS}) @ " + " -> ".join(trail)


def build_series(dfv: pd.DataFrame) -> None:
    rows = []
    for _, r in dfv.iterrows():
        allowed, reasoning = _series_decision(r)
        row = _base_row(r, "series_cascade", allowed, reasoning)
        row["n_agents"] = len(C.SERIES_ORDER)
        rows.append(row)
    out = C.DEFENSE_DIR / "config_series_cascade.csv"
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8")
    nb = sum(1 for x in rows if not x["allowed"])
    _log.info(f"series_cascade: {out.name} ({len(rows)} linhas, {nb} bloqueadas) ordem={C.SERIES_ORDER}")


def build_orchestrator(dfv: pd.DataFrame) -> None:
    K.load_env()
    # cache de decisoes do orquestrador (retomavel)
    decided: Dict[str, Dict[str, Any]] = {}
    if C.ORCH_DECISIONS_CSV.exists():
        prev = pd.read_csv(C.ORCH_DECISIONS_CSV)
        for _, d in prev.iterrows():
            decided[str(d["uid"])] = d.to_dict()
        _log.info(f"orquestrador: cache existente {len(decided)} decisoes")

    dec_rows: List[Dict[str, Any]] = list(decided.values())
    total = len(dfv)
    t0 = time.time()
    processed = 0
    for idx, (_, r) in enumerate(dfv.iterrows(), 1):
        uid = str(r["uid"])
        if uid in decided:
            continue
        code = str(r.get("code", "") or "")
        if code.strip():
            d = agent_orchestrator.decide(code, str(r["task"]), str(r["level"]),
                                          model=C.ORCH_MODEL, verbose=False)
        else:
            d = {"agents": list(agent_orchestrator.VALID_AGENTS), "reason": "codigo vazio", "parse_ok": False}
        rec = {"uid": uid, "agents": "|".join(d["agents"]), "reason": d.get("reason", ""),
               "parse_ok": d.get("parse_ok", False)}
        dec_rows.append(rec)
        decided[uid] = rec
        processed += 1
        if idx % 25 == 0:
            pd.DataFrame(dec_rows).to_csv(C.ORCH_DECISIONS_CSV, index=False, encoding="utf-8")
            _log.info(f"  orquestrador {idx}/{total} | ~{(time.time()-t0)/max(1,processed):.1f}s/amostra")
        time.sleep(C.SLEEP_SEC)
    pd.DataFrame(dec_rows).to_csv(C.ORCH_DECISIONS_CSV, index=False, encoding="utf-8")
    _log.info(f"orquestrador: {len(dec_rows)} decisoes salvas em {C.ORCH_DECISIONS_CSV.name}")

    # monta o config a partir das decisoes + vereditos cacheados (uniao dos escolhidos)
    dec_by_uid = {str(x["uid"]): str(x["agents"]).split("|") for x in dec_rows}
    rows = []
    dist: Dict[int, int] = {}
    for _, r in dfv.iterrows():
        chosen = [a for a in dec_by_uid.get(str(r["uid"]), list(agent_orchestrator.VALID_AGENTS)) if a]
        if not chosen:
            chosen = list(agent_orchestrator.VALID_AGENTS)
        blockers = [a for a in chosen if bool(r[f"{a}_blocks"])]
        allowed = len(blockers) == 0
        reasoning = f"orchestrator escolheu={chosen} bloqueado_por={blockers or 'nenhum'}"
        row = _base_row(r, "orchestrator", allowed, reasoning)
        row["n_agents"] = len(chosen)
        rows.append(row)
        dist[len(chosen)] = dist.get(len(chosen), 0) + 1
    out = C.DEFENSE_DIR / "config_orchestrator.csv"
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8")
    nb = sum(1 for x in rows if not x["allowed"])
    _log.info(f"orchestrator: {out.name} ({len(rows)} linhas, {nb} bloqueadas) "
              f"distrib_n_agentes={dict(sorted(dist.items()))}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-orch", action="store_true", help="nao roda o orquestrador (sem API)")
    ap.add_argument("--only", choices=["weighted_score", "series_cascade", "orchestrator"], default=None)
    args = ap.parse_args()

    if not C.AGENT_VERDICTS_CSV.exists():
        _log.error(f"Faltando {C.AGENT_VERDICTS_CSV}. Rode a Etapa 2 primeiro.")
        sys.exit(1)
    dfv = pd.read_csv(C.AGENT_VERDICTS_CSV)
    _log.info(f"Vereditos carregados: {len(dfv)} amostras")

    todo = [args.only] if args.only else ["weighted_score", "series_cascade", "orchestrator"]
    if args.skip_orch and "orchestrator" in todo:
        todo.remove("orchestrator")

    if "weighted_score" in todo:
        build_weighted(dfv)
    if "series_cascade" in todo:
        build_series(dfv)
    if "orchestrator" in todo:
        build_orchestrator(dfv)

    _log.info("Etapa 2b concluida. Rode a Etapa 3 (stage3_judge.py) p/ juiz+metricas+amostras.")


if __name__ == "__main__":
    main()
