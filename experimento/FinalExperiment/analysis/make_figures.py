#!/usr/bin/env python3
"""
Analise rica + figuras para a monografia (10 cenarios de defesa, 600 amostras V3+Qwen).

Gera em data/figures/:
  metrics_complete.csv              tabela completa (overall + por nivel + por modelo)
  fig1_operating_points.png         ROC-like: FPR x Recall(TPR) por cenario (frente de trade-off)
  fig2_metrics_bars.png             barras: ASR, FPR, F1, Accuracy nos 10 cenarios
  fig3_confusion_matrices.png       matrizes de confusao (agentes isolados + 4 topologias)
  fig4_complexity.png               ASR e F1 vs complexidade (4 topologias de sistema)
  fig5_boxplot_percell_asr.png      boxplot da ASR por celula (tarefa x nivel x modelo)
  fig6_orchestrator.png             orquestrador: nº de agentes escolhidos e frequencia por agente
  fig7_model_breakdown.png          ASR por modelo gerador (V3 vs Qwen) nas 4 topologias

Uso: python analysis/make_figures.py   (a partir de FinalExperiment/, PYTHONPATH=.)
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as C

FIG = C.DATA / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# ── Paleta validada (dataviz, colorblind-safe) ────────────────────────────────────
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
MAGENTA, GREEN, VIOLET, RED = "#e87ba4", "#008300", "#4a3aa7", "#e34948"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
BLUES = LinearSegmentedColormap.from_list("blues", ["#eef5fe", "#2a78d6", "#0d366b"])

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 11,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.titleweight": "bold",
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "figure.facecolor": "white", "axes.facecolor": "white",
})

# ── Ordem e rotulos dos cenarios ───────────────────────────────────────────────────
ORDER = ["solo_behavior", "solo_policy", "solo_pattern",
         "pair_behavior_policy", "pair_behavior_pattern", "pair_pattern_policy",
         "trio_all", "weighted_score", "series_cascade", "orchestrator"]
LABEL = {"solo_behavior": "Behavior", "solo_policy": "Policy", "solo_pattern": "Pattern",
         "pair_behavior_policy": "Behav+Policy", "pair_behavior_pattern": "Behav+Pattern",
         "pair_pattern_policy": "Pattern+Policy", "trio_all": "Trio (paralelo)",
         "weighted_score": "Ponderado", "series_cascade": "Série", "orchestrator": "Orquestrador"}
SYSTEMS = ["trio_all", "weighted_score", "series_cascade", "orchestrator"]
SYS_COLOR = {"trio_all": BLUE, "weighted_score": ORANGE, "series_cascade": AQUA, "orchestrator": YELLOW}
FAMILY_COLOR = {"solo": VIOLET, "pair": MAGENTA, "trio_all": BLUE,
                "weighted_score": ORANGE, "series_cascade": AQUA, "orchestrator": YELLOW}

def family(cfg):
    if cfg in SYSTEMS and cfg != "trio_all":
        return cfg
    if cfg == "trio_all":
        return "trio_all"
    return "solo" if cfg.startswith("solo") else "pair"

def _bool(s):
    return s.astype(str).str.lower().isin(["true", "1", "1.0"])

def metrics(gt, allowed):
    gt = _bool(gt); allowed = _bool(allowed); blocked = ~allowed
    tp = int((gt & blocked).sum()); fp = int((~gt & blocked).sum())
    fn = int((gt & allowed).sum()); tn = int((~gt & allowed).sum())
    tot = tp + fp + fn + tn
    asr = fn / (tp + fn) if (tp + fn) else np.nan
    prec = tp / (tp + fp) if (tp + fp) else np.nan
    rec = tp / (tp + fn) if (tp + fn) else np.nan
    fpr = fp / (fp + tn) if (fp + tn) else np.nan
    f1 = 2 * prec * rec / (prec + rec) if prec and rec else np.nan
    acc = (tp + tn) / tot if tot else np.nan
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, total=tot, asr=asr, precision=prec,
                recall=rec, fpr=fpr, f1=f1, accuracy=acc)

# ── Carrega os config_<cenario>.csv presentes ──────────────────────────────────────
dfs = {}
for cfg in ORDER:
    p = C.DEFENSE_DIR / f"config_{cfg}.csv"
    if p.exists():
        dfs[cfg] = pd.read_csv(p)
present = [c for c in ORDER if c in dfs]
print("cenarios:", present)

# ── Tabela completa ────────────────────────────────────────────────────────────────
rows = []
for cfg in present:
    d = dfs[cfg]
    rows.append({"config": cfg, "label": LABEL[cfg], "scope": "ALL", **metrics(d["attack_hidden_logic"], d["allowed"])})
    for lvl, g in d.groupby("level"):
        rows.append({"config": cfg, "label": LABEL[cfg], "scope": f"level={lvl}", **metrics(g["attack_hidden_logic"], g["allowed"])})
    for mdl, g in d.groupby("generator_model"):
        rows.append({"config": cfg, "label": LABEL[cfg], "scope": f"model={str(mdl).split('/')[-1]}", **metrics(g["attack_hidden_logic"], g["allowed"])})
tab = pd.DataFrame(rows)
tab.to_csv(FIG / "metrics_complete.csv", index=False, encoding="utf-8")
over = tab[tab.scope == "ALL"].set_index("config")
print("tabela salva:", FIG / "metrics_complete.csv")

def barlabels(ax, bars, vals, fmt="{:.2f}", dx=0.0):
    for b, v in zip(bars, vals):
        if np.isnan(v):
            continue
        ax.text(b.get_width() + dx, b.get_y() + b.get_height() / 2, fmt.format(v),
                va="center", ha="left", fontsize=9, color=INK)

# ── FIG 1 — Pontos de operacao (FPR x Recall) ──────────────────────────────────────
from matplotlib.lines import Line2D
fig, ax = plt.subplots(figsize=(9, 6.3))
ax.plot([0, 1], [0, 1], ls="--", lw=1, color=GRID, zorder=0)
for cfg in present:
    m = over.loc[cfg]
    mk = "o" if cfg in SYSTEMS else ("s" if cfg.startswith("solo") else "^")
    ax.scatter(m.fpr, m.recall, s=170, color=FAMILY_COLOR[family(cfg)],
               edgecolor="white", linewidth=1.5, zorder=3, marker=mk)

# rotulos diretos (pontos espacados) e empilhados c/ linha-guia (cluster superior-direito)
direct = {  # cfg: (dx, dy) em pontos
    "solo_behavior": (8, 6), "series_cascade": (8, -16),
    "solo_policy": (-10, -16), "weighted_score": (8, 7), "pair_behavior_policy": (8, -15),
}
for cfg, (dx, dy) in direct.items():
    if cfg in present:
        m = over.loc[cfg]
        ax.annotate(LABEL[cfg], (m.fpr, m.recall), xytext=(dx, dy),
                    textcoords="offset points", fontsize=9, color=INK)
# cluster: trio == pattern_policy (coincidentes) -> rotulo unico; empilhar na area vazia
stacked = [("trio_all", "Trio (paralelo) = Pattern+Policy", 0.985),
           ("pair_behavior_pattern", "Behav+Pattern", 0.935),
           ("solo_pattern", "Pattern", 0.885),
           ("orchestrator", "Orquestrador", 0.835)]
for cfg, text, ytext in stacked:
    if cfg not in present:
        continue
    m = over.loc[cfg]
    ax.annotate(text, xy=(m.fpr, m.recall), xycoords="data",
                xytext=(0.04, ytext), textcoords="axes fraction", fontsize=9, color=INK,
                va="center", ha="left",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkA=2, shrinkB=4))
ax.set_xlabel("FPR  — taxa de falso-positivo (código limpo bloqueado)")
ax.set_ylabel("Recall / TPR — trojans detectados")
ax.set_title("Pontos de operação das defesas  (topo-esquerda = ideal)")
ax.text(0.015, 0.02, "ASR = 1 − Recall  ·  diagonal tracejada = acaso", transform=ax.transAxes,
        ha="left", fontsize=9, color=INK2)
ax.set_xlim(-0.02, 1.02); ax.set_ylim(0.5, 1.04)
leg = [Line2D([0], [0], marker="s", color="w", markerfacecolor=VIOLET, markersize=11, label="agente isolado"),
       Line2D([0], [0], marker="^", color="w", markerfacecolor=MAGENTA, markersize=11, label="par de agentes"),
       Line2D([0], [0], marker="o", color="w", markerfacecolor=BLUE, markersize=11, label="topologia de sistema")]
ax.legend(handles=leg, loc="lower right", frameon=True, framealpha=0.9, edgecolor=GRID)
fig.tight_layout(); fig.savefig(FIG / "fig1_operating_points.png"); plt.close(fig)

# ── FIG 2 — Barras: ASR, FPR, F1, Accuracy ─────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
panels = [("asr", "ASR (↓ melhor) — ataques que passam", "{:.1%}"),
          ("fpr", "FPR (↓ melhor) — falsos positivos", "{:.1%}"),
          ("f1", "F1 (↑ melhor)", "{:.3f}"),
          ("accuracy", "Acurácia (↑ melhor)", "{:.3f}")]
for ax, (key, title, fmt) in zip(axes.ravel(), panels):
    order_sorted = over[key].sort_values(ascending=(key in ("asr", "fpr"))).index.tolist()
    vals = [over.loc[c, key] for c in order_sorted]
    cols = [FAMILY_COLOR[family(c)] for c in order_sorted]
    y = np.arange(len(order_sorted))
    bars = ax.barh(y, vals, color=cols, height=0.68, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels([LABEL[c] for c in order_sorted])
    ax.invert_yaxis(); ax.set_title(title); ax.set_xlim(0, max(1.0, max(vals) * 1.15))
    ax.grid(axis="y", visible=False)
    barlabels(ax, bars, vals, fmt=fmt, dx=max(vals) * 0.01)
fig.suptitle("Métricas por cenário de defesa  (600 amostras, V3 + Qwen)", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.97]); fig.savefig(FIG / "fig2_metrics_bars.png"); plt.close(fig)

# ── FIG 3 — Matrizes de confusao ───────────────────────────────────────────────────
cm_cfgs = ["solo_behavior", "solo_pattern", "solo_policy", "trio_all",
           "weighted_score", "series_cascade", "orchestrator"]
cm_cfgs = [c for c in cm_cfgs if c in present]
ncol = 4; nrow = int(np.ceil(len(cm_cfgs) / ncol))
fig, axes = plt.subplots(nrow, ncol, figsize=(3.4 * ncol, 3.4 * nrow))
axes = np.array(axes).ravel()
for ax, cfg in zip(axes, cm_cfgs):
    m = over.loc[cfg]
    M = np.array([[m.tn, m.fp], [m.fn, m.tp]], dtype=float)  # [[TN,FP],[FN,TP]]
    im = ax.imshow(M, cmap=BLUES, vmin=0, vmax=M.max())
    ax.set_title(LABEL[cfg], fontsize=11)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["prev. limpo", "prev. bloq."], fontsize=8)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["real limpo", "real trojan"], fontsize=8)
    names = [["TN", "FP"], ["FN", "TP"]]
    for i in range(2):
        for j in range(2):
            v = M[i, j]
            ax.text(j, i, f"{names[i][j]}\n{int(v)}", ha="center", va="center", fontsize=10,
                    color="white" if v > M.max() * 0.55 else INK, fontweight="bold")
    ax.grid(False)
for ax in axes[len(cm_cfgs):]:
    ax.axis("off")
fig.suptitle("Matrizes de confusão por cenário  (linha=verdade, coluna=decisão)", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.96]); fig.savefig(FIG / "fig3_confusion_matrices.png"); plt.close(fig)

# ── FIG 4 — Degradacao por complexidade (4 sistemas) ────────────────────────────────
levels = ["simple", "medium", "complex"]
fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
for key, ax, title, fmt in [("asr", axes[0], "ASR por complexidade (↓ melhor)", "{:.0%}"),
                            ("f1", axes[1], "F1 por complexidade (↑ melhor)", "{:.2f}")]:
    for cfg in SYSTEMS:
        if cfg not in present:
            continue
        d = dfs[cfg]
        ys = [metrics(g["attack_hidden_logic"], g["allowed"])[key]
              for lvl in levels for g in [d[d.level == lvl]]]
        ax.plot(levels, ys, marker="o", lw=2.2, ms=9, color=SYS_COLOR[cfg], label=LABEL[cfg])
        for x, yv in zip(levels, ys):
            ax.annotate(fmt.format(yv), (x, yv), xytext=(0, 8), textcoords="offset points",
                        ha="center", fontsize=8, color=SYS_COLOR[cfg])
    ax.set_title(title); ax.set_xlabel("complexidade da tarefa")
ax.legend(frameon=False, loc="best")
axes[0].legend(frameon=False, loc="best")
fig.suptitle("Efeito da complexidade — topologias de sistema", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(FIG / "fig4_complexity.png"); plt.close(fig)

# ── FIG 5 — Boxplot da ASR por celula (tarefa x nivel x modelo) ─────────────────────
fig, ax = plt.subplots(figsize=(11, 6))
data = []
for cfg in present:
    d = dfs[cfg]
    vals = []
    for _, g in d.groupby(["base_task", "level", "generator_model"]):
        mm = metrics(g["attack_hidden_logic"], g["allowed"])
        if not np.isnan(mm["asr"]):
            vals.append(mm["asr"])
    data.append(vals)
bp = ax.boxplot(data, vert=True, patch_artist=True, widths=0.62,
                medianprops=dict(color=INK, lw=2),
                flierprops=dict(marker="o", ms=4, mfc=INK2, mec="none", alpha=0.5))
for patch, cfg in zip(bp["boxes"], present):
    patch.set_facecolor(FAMILY_COLOR[family(cfg)]); patch.set_alpha(0.8); patch.set_edgecolor("white")
ax.set_xticklabels([LABEL[c] for c in present], rotation=30, ha="right")
ax.set_ylabel("ASR por célula (30 células: tarefa × nível × modelo)")
ax.set_title("Distribuição da ASR entre células — variabilidade/robustez de cada defesa")
ax.grid(axis="x", visible=False)
fig.tight_layout(); fig.savefig(FIG / "fig5_boxplot_percell_asr.png"); plt.close(fig)

# ── FIG 6 — Orquestrador: escolhas ──────────────────────────────────────────────────
if C.ORCH_DECISIONS_CSV.exists():
    od = pd.read_csv(C.ORCH_DECISIONS_CSV)
    od["agent_list"] = od["agents"].astype(str).str.split("|")
    od["n"] = od["agent_list"].apply(lambda xs: len([a for a in xs if a]))
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    # (a) nº de agentes escolhidos
    cnt = od["n"].value_counts().sort_index()
    b = axes[0].bar([str(i) for i in cnt.index], cnt.values, color=BLUE, width=0.6, zorder=3)
    for bar, v in zip(b, cnt.values):
        axes[0].text(bar.get_x() + bar.get_width() / 2, v, str(int(v)), ha="center", va="bottom", fontsize=10)
    axes[0].set_title("Quantos agentes o orquestrador consultou")
    axes[0].set_xlabel("nº de agentes"); axes[0].set_ylabel("amostras"); axes[0].grid(axis="x", visible=False)
    # (b) frequencia por agente
    from collections import Counter
    c = Counter(a for xs in od["agent_list"] for a in xs if a)
    names = ["behavior_detector", "trojan_pattern", "policy_verifier"]
    vals = [c.get(n, 0) for n in names]
    cols = [VIOLET, ORANGE, AQUA]
    b2 = axes[1].bar(["behavior", "pattern", "policy"], vals, color=cols, width=0.6, zorder=3)
    for bar, v in zip(b2, vals):
        axes[1].text(bar.get_x() + bar.get_width() / 2, v, str(int(v)), ha="center", va="bottom", fontsize=10)
    axes[1].set_title("Frequência com que cada agente foi consultado")
    axes[1].set_ylabel("amostras (de 600)"); axes[1].grid(axis="x", visible=False)
    fig.suptitle("Comportamento do agente orquestrador", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(FIG / "fig6_orchestrator.png"); plt.close(fig)

# ── FIG 7 — ASR por modelo gerador (4 sistemas) ─────────────────────────────────────
models = sorted({str(m).split("/")[-1] for m in dfs["trio_all"]["generator_model"].unique()})
fig, ax = plt.subplots(figsize=(9, 5.5))
x = np.arange(len(SYSTEMS)); w = 0.38
for i, mdl in enumerate(models):
    ys = []
    for cfg in SYSTEMS:
        d = dfs[cfg]; g = d[d["generator_model"].astype(str).str.endswith(mdl)]
        ys.append(metrics(g["attack_hidden_logic"], g["allowed"])["asr"])
    bars = ax.bar(x + (i - 0.5) * w, ys, width=w, label=mdl,
                  color=[BLUE, ORANGE][i], zorder=3)
    for bar, v in zip(bars, ys):
        ax.text(bar.get_x() + bar.get_width() / 2, v, f"{v:.0%}", ha="center", va="bottom", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels([LABEL[c] for c in SYSTEMS])
ax.set_ylabel("ASR (↓ melhor)"); ax.set_title("ASR por modelo gerador × topologia de defesa")
ax.legend(frameon=False); ax.grid(axis="x", visible=False)
fig.tight_layout(); fig.savefig(FIG / "fig7_model_breakdown.png"); plt.close(fig)

print("Figuras salvas em:", FIG)
for p in sorted(FIG.glob("*.png")):
    print("  -", p.name)
