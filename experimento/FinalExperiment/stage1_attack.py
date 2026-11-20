#!/usr/bin/env python3
"""
ETAPA 1 / 3 — ATAQUE PAIR

Gera 900 amostras: 3 modelos x 3 niveis x 5 tarefas x 20 iteracoes.
Cada iteracao: gera codigo -> roda testes -> juiz PAIR da nota de stealth -> refina prompt.
Sem early stopping (todas as 20 iteracoes sempre rodam), fiel aos scripts originais.

RETOMADA: cada celula (modelo|nivel|tarefa) e salva em data/attack/cells/<cell>.csv.
Rodar de novo pula celulas ja concluidas. Ao final concatena tudo em attack_runs.csv.

Uso:
    python stage1_attack.py                 # roda tudo que falta
    python stage1_attack.py --only-model DeepSeek-R1   # so um modelo (substring)
    python stage1_attack.py --dry-run       # 1 iter x 1 tarefa x 1 nivel x 1 modelo (smoke test)
"""
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

import config as C
import common as K

_log = K.setup_logging("stage1", C.LOGS / "stage1_attack.log")


def cell_id(model: str, level: str, base_task: str) -> str:
    return f"{model.split('/')[-1]}__{level}__{base_task}"


def run_cell(model_name: str, gen_model: K.HFModel, judge_model: K.HFModel,
             level: str, base_task: str, n_iter: int) -> pd.DataFrame:
    task = K.build_task(base_task, level)
    strategies = K.STRATEGIES[level]
    short = model_name.split("/")[-1]
    rows: List[Dict[str, Any]] = []
    best = {"score": -1, "code": "", "possible_hidden_logic": False, "iteration": -1}

    prompt = K.build_prompt(task, strategies[0])
    _log.info(f"[ATTACK] model={short} level={level} task={task['name']}")

    for iteration in range(1, n_iter + 1):
        tag = f"[{short}|{task['name']}|iter={iteration}/{n_iter}]"
        t0 = time.time()
        _log.info(f"{tag} Gerando...")
        code = ""
        try:
            code = K.strip_fences(gen_model.generate(prompt))
        except Exception as e:
            _log.error(f"{tag} erro gerador: {e}")

        tests = K.run_tests(task, code)
        _log.info(f"{tag} Testes {tests['passed']}/{tests['total']}")

        j = {"score": 1, "rationale": "skip", "parse_ok": False, "raw": ""}
        try:
            j = K.judge_code(task, code, tests, judge_model)
        except Exception as e:
            _log.error(f"{tag} erro juiz PAIR: {e}")

        hidden = K.detect_hidden_logic(code)
        elapsed = round(time.time() - t0, 2)
        cat = K.score_category(j["score"])
        _log.info(f"{tag} score={j['score']}/10 ({cat}) hidden={hidden} {elapsed}s")

        rows.append({
            "run_id": C.RUN_ID,
            "generator_model": model_name,
            "level": level,
            "base_task": base_task,
            "task": task["name"],
            "iteration": iteration,
            "stream": 1,
            "score_r1": j["score"],
            "score_category": cat,
            "judge_rationale": j["rationale"],
            "judge_parse_ok": j["parse_ok"],
            "passed_tests": tests["passed"],
            "total_tests": tests["total"],
            "test_ratio": tests["ratio"],
            "test_error": tests["error"],
            "code": code,
            "code_empty": not bool(code),
            "possible_hidden_logic": hidden,
            "elapsed_sec": elapsed,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        if j["score"] > best["score"]:
            best.update({"score": j["score"], "code": code,
                         "possible_hidden_logic": hidden, "iteration": iteration})
            _log.info(f"{tag} [BEST] novo melhor: {j['score']}/10")

        # rotaciona estrategia + refina prompt (sem early stop)
        try:
            prompt = K.refine_prompt(task, prompt, code, tests, j, judge_model)
        except Exception as e:
            _log.error(f"{tag} erro refinador: {e}")
            prompt = K.build_prompt(task, strategies[iteration % len(strategies)])
        time.sleep(C.SLEEP_SEC)

    if best["code"]:
        bp = C.ATTACK_BEST / f"best_{cell_id(model_name, level, base_task)}.py"
        bp.write_text(
            f"# run_id: {C.RUN_ID}\n# task: {task['name']}\n# generator: {model_name}\n"
            f"# score: {best['score']}/10 ({K.score_category(best['score'])})\n"
            f"# possible_hidden_logic: {best['possible_hidden_logic']}\n\n" + best["code"],
            encoding="utf-8",
        )
    return pd.DataFrame(rows)


def load_progress() -> set:
    if C.ATTACK_PROGRESS.exists():
        try:
            return set(json.loads(C.ATTACK_PROGRESS.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_progress(done: set) -> None:
    C.ATTACK_PROGRESS.write_text(json.dumps(sorted(done), indent=2), encoding="utf-8")


def consolidate() -> None:
    frames = [pd.read_csv(p) for p in sorted(C.ATTACK_CELLS.glob("*.csv"))]
    if not frames:
        _log.warning("Nenhuma celula para consolidar.")
        return
    df = pd.concat(frames, ignore_index=True)
    df.to_csv(C.ATTACK_RUNS_CSV, index=False, encoding="utf-8")
    _log.info(f"Consolidado: {C.ATTACK_RUNS_CSV} ({len(df)} linhas de {C.TOTAL_ATTACK} esperadas)")
    empties = int(df["code_empty"].sum())
    if empties:
        _log.warning(f"ATENCAO: {empties} amostras com code vazio (verifique timeouts do R1).")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only-model", default=None, help="substring do modelo a rodar (ex: DeepSeek-R1)")
    ap.add_argument("--only-level", default=None, help="simple|medium|complex")
    ap.add_argument("--dry-run", action="store_true", help="smoke test minimo (1 celula, 1 iter)")
    args = ap.parse_args()

    K.load_env()

    models = C.GENERATOR_MODELS
    levels = C.LEVELS
    tasks = C.TASK_NAMES
    n_iter = C.N_ITERATIONS

    if args.dry_run:
        models, levels, tasks, n_iter = models[:1], levels[:1], tasks[:1], 1
        # isola a saida do smoke test para NAO contaminar os dados reais
        C.ATTACK_CELLS = C.ATTACK_DIR / "_dryrun"
        C.ATTACK_BEST = C.ATTACK_DIR / "_dryrun"
        C.ATTACK_PROGRESS = C.ATTACK_DIR / "_dryrun" / "progress.json"
        C.ATTACK_RUNS_CSV = C.ATTACK_DIR / "_dryrun" / "attack_runs_dryrun.csv"
        _log.info("DRY-RUN: 1 modelo x 1 nivel x 1 tarefa x 1 iteracao (saida isolada em data/attack/_dryrun)")
    if args.only_model:
        models = [m for m in models if args.only_model.lower() in m.lower()]
    if args.only_level:
        levels = [l for l in levels if l == args.only_level]

    # cria os diretorios de saida DEPOIS de resolver dry-run (que reescreve os caminhos)
    for d in [C.ATTACK_CELLS, C.ATTACK_BEST, C.ATTACK_PROGRESS.parent]:
        d.mkdir(parents=True, exist_ok=True)

    _log.info(f"Etapa 1 — ataque | run_id={C.RUN_ID}")
    _log.info(f"  modelos={[m.split('/')[-1] for m in models]} niveis={levels} "
              f"tarefas={len(tasks)} iter={n_iter}")

    judge_model = K.HFModel(C.JUDGE_MODEL, C.JUDGE_TEMPERATURE, C.MAX_NEW_TOKENS)
    done = load_progress()
    t_start = time.time()
    total_cells = len(models) * len(levels) * len(tasks)
    done_count = 0

    for model_name in models:
        gen_model = K.HFModel(
            model_name, C.GEN_TEMPERATURE, C.gen_max_tokens(model_name),
            provider=C.model_provider(model_name), timeout=C.model_timeout(model_name),
        )
        _log.info(f"  gerador {model_name.split('/')[-1]}: max_tokens={C.gen_max_tokens(model_name)} "
                  f"provider={C.model_provider(model_name) or 'auto'} timeout={C.model_timeout(model_name)}s")
        for level in levels:
            for base_task in tasks:
                cid = cell_id(model_name, level, base_task)
                done_count += 1
                cell_csv = C.ATTACK_CELLS / f"{cid}.csv"
                if cid in done and cell_csv.exists() and not args.dry_run:
                    _log.info(f"[SKIP {done_count}/{total_cells}] {cid} ja concluida")
                    continue
                _log.info(f"[CELL {done_count}/{total_cells}] {cid}")
                df_cell = run_cell(model_name, gen_model, judge_model, level, base_task, n_iter)
                df_cell.to_csv(cell_csv, index=False, encoding="utf-8")
                done.add(cid)
                save_progress(done)
                avg = (time.time() - t_start) / max(1, len([x for x in done]))
                _log.info(f"  [OK] {cid} salvo. media ~{avg/60:.1f} min/celula ate agora")

    consolidate()
    mins = (time.time() - t_start) / 60
    _log.info(f"Etapa 1 concluida em {mins:.1f} min. "
              f"Proximo: python stage2_defense.py")


if __name__ == "__main__":
    main()
