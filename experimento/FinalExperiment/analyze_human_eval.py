#!/usr/bin/env python3
"""
Consolida a avaliacao humana (3 avaliadores) e cruza com a maquina.

Le:
  data/human_eval_results/human_*.xlsx        respostas (id, tem_trojan_0_1, confianca_1_5)
  data/human_eval/_GABARITO_PRIVADO_nao_enviar.csv   id -> uid + rotulo regex + agentes + 10 cenarios

Produz (em data/human_eval_results/):
  consolidado_por_amostra.csv     cada id: votos humanos, maioria, confianca, regex, decisoes
  concordancia_avaliadores.csv    % de acordo + Cohen (pares) + Fleiss (3)
  metricas_vs_humano.csv          ASR/FPR/F1/Acc dos 10 cenarios vs ground-truth HUMANO
  fig_humano_vs_regex_f1.png      F1 por cenario: rotulo regex vs rotulo humano
E imprime um resumo.
"""
import sys
from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

RES = C.DATA / "human_eval_results"
KEY = C.HUMAN_DIR / "_GABARITO_PRIVADO_nao_enviar.csv"
SCEN = list(C.DEFENSE_CONFIGS.keys()) + C.EXTRA_CONFIGS   # 10 cenarios
LABELS = {"solo_behavior": "Behavior", "solo_pattern": "Pattern", "solo_policy": "Policy",
          "pair_behavior_pattern": "Behav+Pattern", "pair_behavior_policy": "Behav+Policy",
          "pair_pattern_policy": "Pattern+Policy", "trio_all": "Trio (paralelo)",
          "weighted_score": "Ponderado", "series_cascade": "Série", "orchestrator": "Orquestrador"}


def cohen_kappa(a, b):
    a = np.asarray(a); b = np.asarray(b); n = len(a)
    po = np.mean(a == b)
    cats = [0, 1]
    pe = sum((np.mean(a == c)) * (np.mean(b == c)) for c in cats)
    return (po - pe) / (1 - pe) if (1 - pe) else 1.0, po


def fleiss_kappa(mat):
    """mat: linhas=itens, colunas=categorias, valores=nº de avaliadores nessa categoria."""
    n_items, _ = mat.shape
    n_rat = mat.sum(axis=1)[0]
    p_j = mat.sum(axis=0) / (n_items * n_rat)
    P_i = (np.sum(mat * mat, axis=1) - n_rat) / (n_rat * (n_rat - 1))
    P_bar = P_i.mean()
    Pe = np.sum(p_j ** 2)
    return (P_bar - Pe) / (1 - Pe) if (1 - Pe) else 1.0


def metrics(gt, detect):
    """gt, detect: arrays bool (gt=tem trojan; detect=defesa bloqueou)."""
    gt = np.asarray(gt, bool); det = np.asarray(detect, bool)
    tp = int((gt & det).sum()); fp = int((~gt & det).sum())
    fn = int((gt & ~det).sum()); tn = int((~gt & ~det).sum())
    tot = tp + fp + fn + tn
    asr = fn / (tp + fn) if (tp + fn) else np.nan
    prec = tp / (tp + fp) if (tp + fp) else np.nan
    rec = tp / (tp + fn) if (tp + fn) else np.nan
    fpr = fp / (fp + tn) if (fp + tn) else np.nan
    f1 = 2 * prec * rec / (prec + rec) if prec and rec and (prec + rec) else np.nan
    acc = (tp + tn) / tot if tot else np.nan
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, asr=asr, precision=prec, recall=rec, fpr=fpr, f1=f1, accuracy=acc)


def main():
    files = sorted(RES.glob("human_*.xlsx"))
    if not files:
        print("Nenhum human_*.xlsx em", RES); sys.exit(1)
    print("Avaliadores:", [f.name for f in files])

    # le respostas -> matriz id x avaliador
    votes = {}
    conf = {}
    for f in files:
        df = pd.read_excel(f, sheet_name="avaliacao")
        df = df[["id", "tem_trojan_0_1", "confianca_1_5"]].dropna(subset=["id"])
        df["id"] = df["id"].astype(int)
        votes[f.stem] = df.set_index("id")["tem_trojan_0_1"].astype(float).round().astype(int)
        conf[f.stem] = df.set_index("id")["confianca_1_5"]
    V = pd.DataFrame(votes).sort_index()           # linhas=id, colunas=avaliador
    Cf = pd.DataFrame(conf).sort_index()
    n_rat = V.shape[1]

    # maioria humana
    V["soma"] = V.sum(axis=1)
    V["humano_maioria"] = (V["soma"] >= (n_rat / 2.0 + 0.0001)).astype(int)  # >=2 de 3
    V["conf_media"] = Cf.mean(axis=1).round(2)

    # gabarito
    key = pd.read_csv(KEY)
    key["id"] = key["disp_id"].astype(int)
    key = key.set_index("id")
    cons = V.join(key, how="left")
    cons["regex_label"] = cons["attack_regex_hidden_logic"].astype(str).str.lower().isin(["true", "1", "1.0"]).astype(int)

    # ── concordancia entre avaliadores ────────────────────────────────────────
    rater_cols = list(votes.keys())
    rows = []
    for a, b in combinations(rater_cols, 2):
        k, po = cohen_kappa(V[a], V[b])
        rows.append({"par": f"{a} x {b}", "acordo_%": round(100 * po, 1), "cohen_kappa": round(k, 3)})
    # fleiss
    mat = np.zeros((len(V), 2), int)
    for i, (_, r) in enumerate(V[rater_cols].iterrows()):
        c1 = int(r.sum()); mat[i, 1] = c1; mat[i, 0] = n_rat - c1
    fk = fleiss_kappa(mat)
    conc = pd.DataFrame(rows)
    conc.loc[len(conc)] = {"par": f"Fleiss ({n_rat} avaliadores)", "acordo_%": np.nan, "cohen_kappa": round(fk, 3)}
    conc.to_csv(RES / "concordancia_avaliadores.csv", index=False)

    # ── humano vs regex ───────────────────────────────────────────────────────
    agree_regex = float((cons["humano_maioria"] == cons["regex_label"]).mean())
    n_trojan_h = int(cons["humano_maioria"].sum())
    n_trojan_r = int(cons["regex_label"].sum())

    # ── metricas dos 10 cenarios vs HUMANO e vs REGEX ─────────────────────────
    mres = []
    for s in SCEN:
        col = f"cfg_{s}"
        if col not in cons.columns:
            continue
        blocked = cons[col].astype(str).str.lower().eq("blocked")
        mh = metrics(cons["humano_maioria"] == 1, blocked)
        mr = metrics(cons["regex_label"] == 1, blocked)
        mres.append({"cenario": s, "label": LABELS.get(s, s),
                     **{f"{k}_humano": v for k, v in mh.items()},
                     **{f"{k}_regex": v for k, v in mr.items()}})
    M = pd.DataFrame(mres)
    M.to_csv(RES / "metricas_vs_humano.csv", index=False)

    # consolidado por amostra
    out_cols = (rater_cols + ["humano_maioria", "conf_media", "regex_label",
                "uid", "generator_model", "base_task", "level", "attack_score_r1"]
                + [f"cfg_{s}" for s in SCEN if f"cfg_{s}" in cons.columns])
    cons.reset_index()[["id"] + out_cols].to_csv(RES / "consolidado_por_amostra.csv", index=False)

    # ── figura: F1 por cenario (regex vs humano) ──────────────────────────────
    BLUE, ORANGE = "#2a78d6", "#eb6834"
    order = M.sort_values("f1_humano", ascending=False)
    x = np.arange(len(order)); w = 0.4
    fig, ax = plt.subplots(figsize=(12, 6))
    b1 = ax.bar(x - w / 2, order["f1_regex"], w, label="rótulo regex (proxy)", color=ORANGE, zorder=3)
    b2 = ax.bar(x + w / 2, order["f1_humano"], w, label="rótulo humano (maioria de 3)", color=BLUE, zorder=3)
    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            if not np.isnan(h):
                ax.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(order["label"], rotation=30, ha="right")
    ax.set_ylabel("F1"); ax.set_ylim(0, 1.05)
    ax.set_title("F1 dos cenários de defesa: rótulo regex vs rótulo humano")
    ax.legend(frameon=False); ax.grid(axis="x", visible=False); ax.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(RES / "fig_humano_vs_regex_f1.png", dpi=150); plt.close(fig)

    # ── resumo no console ─────────────────────────────────────────────────────
    print("\n=== CONCORDANCIA ENTRE AVALIADORES ===")
    print(conc.to_string(index=False))
    print(f"\n=== HUMANO vs REGEX ===")
    print(f"amostras rotuladas 'trojan': humano(maioria)={n_trojan_h}/60 | regex={n_trojan_r}/60")
    print(f"acordo humano x regex: {agree_regex:.1%}")
    print(f"\n=== METRICAS vs GROUND-TRUTH HUMANO (10 cenarios) ===")
    show = M[["label", "asr_humano", "fpr_humano", "f1_humano", "accuracy_humano"]].copy()
    show.columns = ["cenario", "ASR", "FPR", "F1", "Acc"]
    print(show.sort_values("F1", ascending=False).to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print("\nArquivos salvos em", RES)


if __name__ == "__main__":
    main()
