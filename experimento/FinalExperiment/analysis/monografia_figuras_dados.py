"""Regera as figuras de resultados da monografia em português, a partir dos CSVs do experimento."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter

D = Path(sys.argv[1]); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)

# ── estilo (paleta de referência, modo claro; impressão em fundo branco) ──────
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": MUTED, "axes.linewidth": 0.8,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.7, "axes.axisbelow": True, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "savefig.dpi": 300, "savefig.bbox": "tight",
    "savefig.facecolor": "white", "figure.facecolor": "white",
})
def br(x, n=2): return f"{x:.{n}f}".replace(".", ",")
def pc(x, n=1): return f"{100*x:.{n}f}%".replace(".", ",")
FMT2 = FuncFormatter(lambda v, _: br(v, 1))
FMTP = FuncFormatter(lambda v, _: f"{100*v:.0f}%")

LBL = {"solo_behavior": "Comportamentos", "solo_pattern": "Padrões", "solo_policy": "Políticas",
       "pair_behavior_pattern": "Comport. + Padrões", "pair_behavior_policy": "Comport. + Políticas",
       "pair_pattern_policy": "Padrões + Políticas", "trio_all": "Trio (paralelo)",
       "weighted_score": "Ponderado", "series_cascade": "Série (cascata)", "orchestrator": "Orquestrador"}
GROUP = {k: ("isolado" if k.startswith("solo") else "par" if k.startswith("pair") else "sistema") for k in LBL}
GCOL = {"isolado": BLUE, "par": ORANGE, "sistema": AQUA}
GMARK = {"isolado": "s", "par": "^", "sistema": "o"}
GNAME = {"isolado": "Agente isolado", "par": "Par de agentes (união)", "sistema": "Topologia de sistema"}
SYS4 = ["trio_all", "weighted_score", "series_cascade", "orchestrator"]
SYSCOL = {"trio_all": BLUE, "weighted_score": ORANGE, "series_cascade": AQUA, "orchestrator": YELLOW}
SYSMARK = {"trio_all": "o", "weighted_score": "s", "series_cascade": "^", "orchestrator": "D"}

js = pd.read_csv(D / "judge/judge_summary.csv").set_index("config_name")
v = pd.read_csv(D / "defense/agent_verdicts.csv")

def load_cfg(c):
    d = pd.read_csv(D / f"defense/config_{c}.csv")
    d["gt"] = d["attack_hidden_logic"].fillna(False).astype(bool)
    d["det"] = ~d["allowed"].fillna(True).astype(bool)   # mesma convenção do juiz
    d["model"] = d["generator_model"].str.split("/").str[-1]
    return d
def asr(g):
    pos = g[g["gt"]]; return (~pos["det"]).mean() if len(pos) else np.nan

# ── 5.4.7a pontos de operação ─────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6.6, 4.6))
ax.plot([0, 1], [0, 1], ls="--", lw=0.8, color=MUTED, zorder=1)
ax.text(0.62, 0.585, "classificador aleatório", color=MUTED, fontsize=8, rotation=33)
# agrupamento do canto superior direito: rótulos em coluna à esquerda, de cima para baixo na ordem do recall
cluster = [("trio_all", "Trio (paralelo) = Padrões + Políticas", 1.005),
           ("pair_behavior_pattern", "Comport. + Padrões", 0.965),
           ("solo_pattern", "Padrões", 0.925),
           ("orchestrator", "Orquestrador", 0.885)]
free = {"weighted_score": (10, 8), "pair_behavior_policy": (10, -14), "solo_policy": (10, -4),
        "solo_behavior": (10, 2), "series_cascade": (10, -12)}
draw = [c for c in LBL if c != "trio_all"] + ["trio_all"]       # trio por cima do par idêntico
for c in draw:
    r = js.loc[c]; g = GROUP[c]
    ax.scatter(r.fpr, r.recall_tpr, s=55, marker=GMARK[g], color=GCOL[g], edgecolor="white", linewidth=1.2, zorder=3)
for c, txt, ytxt in cluster:
    r = js.loc[c]
    ax.annotate(f"{txt}  ({pc(r.asr)})", (r.fpr, r.recall_tpr), xytext=(0.70, ytxt), textcoords="data",
                ha="right", va="center", fontsize=7.8, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkA=2, shrinkB=4))
for c, o in free.items():
    r = js.loc[c]
    ax.annotate(f"{LBL[c]}  ({pc(r.asr)})", (r.fpr, r.recall_tpr), xytext=o, textcoords="offset points",
                fontsize=7.8, color=INK)
ax.set_xlim(0, 1.0); ax.set_ylim(0.5, 1.03)
ax.set_xlabel("FPR – fração de amostras limpas bloqueadas"); ax.set_ylabel("Recall – fração de trojans bloqueados")
ax.xaxis.set_major_formatter(FMT2); ax.yaxis.set_major_formatter(FMT2)
for g in GNAME: ax.scatter([], [], marker=GMARK[g], color=GCOL[g], s=45, label=GNAME[g])
ax.legend(loc="lower right", fontsize=8)
ax.text(0.01, 0.515, "Entre parênteses: ASR = 1 − recall.", fontsize=7.5, color=INK2)
fig.savefig(OUT / "5-4-7a_pontos_de_operacao.png"); plt.close(fig)

# ── 5.4.7b barras de métricas ─────────────────────────────────────────────────
metrics = [("asr", "ASR (menor é melhor)", True), ("fpr", "FPR (menor é melhor)", True),
           ("f1", "F1 (maior é melhor)", False), ("accuracy", "Acurácia (maior é melhor)", False)]
order = js.sort_values("asr").index.tolist()
fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.4), sharey=True)
for ax, (m, title, pct) in zip(axes.flat, metrics):
    vals = js.loc[order, m].values; ys = np.arange(len(order))[::-1]
    ax.barh(ys, vals, height=0.62, color=[GCOL[GROUP[c]] for c in order], edgecolor="white", linewidth=1)
    for y, val in zip(ys, vals):
        ax.text(val + 0.015, y, pc(val) if pct else br(val, 3), va="center", fontsize=7.3, color=INK)
    ax.set_yticks(ys); ax.set_yticklabels([LBL[c] for c in order], fontsize=8)
    ax.set_xlim(0, 1.12); ax.set_title(title, fontsize=9, color=INK, loc="left")
    ax.xaxis.set_major_formatter(FMTP if pct else FMT2); ax.grid(axis="y", visible=False)
handles = [plt.Rectangle((0, 0), 1, 1, color=GCOL[g]) for g in GNAME]
fig.legend(handles, GNAME.values(), loc="lower center", ncol=3, fontsize=8, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT / "5-4-7b_metricas_por_cenario.png"); plt.close(fig)

# ── 5.4.7c matrizes de confusão ───────────────────────────────────────────────
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("seq", SEQ)
cm_cfgs = ["solo_behavior", "solo_pattern", "solo_policy", "trio_all", "weighted_score", "series_cascade", "orchestrator"]
fig, axes = plt.subplots(2, 4, figsize=(7.6, 4.3))
for ax, c in zip(axes.flat, cm_cfgs):
    r = js.loc[c]; M = np.array([[r.tn, r.fp], [r.fn, r.tp]])
    ax.imshow(M, cmap=cmap, vmin=0, vmax=460)
    for (i, j), lab in zip([(0, 0), (0, 1), (1, 0), (1, 1)], ["TN", "FP", "FN", "TP"]):
        val = M[i, j]; col = "white" if val > 230 else INK
        ax.text(j, i, f"{lab}\n{val}", ha="center", va="center", fontsize=8.5, color=col, fontweight="bold")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["liberada", "bloqueada"], fontsize=7)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["limpa", "trojan"], fontsize=7)
    ax.set_title(LBL[c], fontsize=8.5, color=INK); ax.grid(False)
    for s in ax.spines.values(): s.set_visible(False)
axes.flat[-1].axis("off")
axes.flat[-1].text(0.02, 0.5, "Linhas: rótulo de referência\n(heurística regex).\nColunas: decisão da defesa.\n\nTP = verdadeiro positivo\nFP = falso positivo\nFN = falso negativo\nTN = verdadeiro negativo",
                   fontsize=7.5, color=INK2, va="center")
fig.tight_layout()
fig.savefig(OUT / "5-4-7c_matrizes_de_confusao.png"); plt.close(fig)

# ── 5.4.7d boxplot ASR por célula ─────────────────────────────────────────────
box_order = ["solo_behavior", "solo_policy", "solo_pattern", "pair_behavior_policy", "pair_behavior_pattern",
             "pair_pattern_policy", "trio_all", "weighted_score", "series_cascade", "orchestrator"]
data = []
for c in box_order:
    d = load_cfg(c)
    data.append(d.groupby(["base_task", "level", "model"]).apply(asr).dropna().values)
fig, ax = plt.subplots(figsize=(7.2, 3.9))
bp = ax.boxplot(data, patch_artist=True, widths=0.55, medianprops=dict(color=INK, lw=1.6),
                whiskerprops=dict(color=INK2, lw=0.9), capprops=dict(color=INK2, lw=0.9),
                flierprops=dict(marker="o", markersize=3.5, markerfacecolor=MUTED, markeredgecolor="none"))
for patch, c in zip(bp["boxes"], box_order):
    patch.set_facecolor(GCOL[GROUP[c]]); patch.set_alpha(0.85); patch.set_edgecolor("white")
for i, arr in enumerate(data, 1):
    ax.text(i, -0.075, f"med. {pc(np.median(arr), 0)}", ha="center", fontsize=6.8, color=INK2)
ax.set_xticks(range(1, len(box_order) + 1)); ax.set_xticklabels([LBL[c] for c in box_order], rotation=30, ha="right", fontsize=8)
ax.set_ylim(-0.11, 1.0); ax.yaxis.set_major_formatter(FMTP)
ax.set_ylabel("ASR por célula (30 células:\ntarefa × nível × modelo)")
ax.grid(axis="x", visible=False)
ax.legend(handles, GNAME.values(), loc="upper left", fontsize=7.5, ncol=3)
fig.savefig(OUT / "5-4-7d_boxplot_asr_por_celula.png"); plt.close(fig)

# ── 5.4.7e orquestrador ───────────────────────────────────────────────────────
o = pd.read_csv(D / "defense/orchestrator_decisions.csv")
n = o.agents.str.split("|").str.len().value_counts().sort_index()
freq = {"Comportamentos": o.agents.str.contains("behavior_detector").sum(),
        "Padrões": o.agents.str.contains("trojan_pattern").sum(),
        "Políticas": o.agents.str.contains("policy_verifier").sum()}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 3.0))
a1.bar([str(i) for i in n.index], n.values, color=BLUE, width=0.6, edgecolor="white")
for x, val in zip(range(len(n)), n.values): a1.text(x, val + 8, f"{val} ({pc(val/600)})", ha="center", fontsize=8, color=INK)
a1.set_xlabel("Número de agentes consultados"); a1.set_ylabel("Amostras"); a1.set_ylim(0, 500)
a1.set_title("(a) Agentes consultados por amostra", fontsize=9, loc="left", color=INK); a1.grid(axis="x", visible=False)
a2.bar(list(freq), list(freq.values()), color=BLUE, width=0.6, edgecolor="white")
for x, val in enumerate(freq.values()): a2.text(x, val + 8, f"{val} ({pc(val/600)})", ha="center", fontsize=8, color=INK)
a2.set_ylabel("Amostras (de 600)"); a2.set_ylim(0, 640)
a2.set_title("(b) Frequência de consulta de cada agente", fontsize=9, loc="left", color=INK); a2.grid(axis="x", visible=False)
fig.tight_layout()
fig.savefig(OUT / "5-4-7e_orquestrador.png"); plt.close(fig)

# ── 5.4.8a complexidade ───────────────────────────────────────────────────────
m = pd.read_csv(D / "judge/metrics_by_config.csv")
lv = ["simple", "medium", "complex"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.3))
lab_off = {"trio_all": -11, "weighted_score": 6, "series_cascade": 6, "orchestrator": 6}
for c in SYS4:
    g = m[(m.config_name == c) & (m.model == "ALL")].set_index("level").loc[lv]
    for ax, col in [(a1, "asr"), (a2, "f1")]:
        ax.plot(range(3), g[col].values, color=SYSCOL[c], marker=SYSMARK[c], ms=6, lw=2,
                markeredgecolor="white", markeredgewidth=1, label=LBL[c])
    a1.annotate(LBL[c], (2, g["asr"].values[-1]), xytext=(8, lab_off[c] if c == "trio_all" else 0),
                textcoords="offset points", fontsize=7.5, color=INK, va="center")
for ax, t in [(a1, "(a) ASR por nível (menor é melhor)"), (a2, "(b) F1 por nível (maior é melhor)")]:
    ax.set_xticks(range(3)); ax.set_xticklabels(lv); ax.set_xlabel("Nível de complexidade")
    ax.set_title(t, fontsize=9, loc="left", color=INK); ax.set_xlim(-0.2, 2.2)
a1.yaxis.set_major_formatter(FMTP); a1.set_ylim(0, 0.55)
a2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: br(v, 2))); a2.set_ylim(0.55, 1.0)
a1.set_xlim(-0.2, 2.9)
a2.legend(fontsize=7.5, loc="lower left")
fig.tight_layout()
fig.savefig(OUT / "5-4-8a_efeito_da_complexidade.png"); plt.close(fig)

# ── 5.4.8b modelo gerador ─────────────────────────────────────────────────────
rows = []
for c in SYS4:
    d = load_cfg(c)
    for mo, g in d.groupby("model"): rows.append((c, mo, asr(g)))
rm = pd.DataFrame(rows, columns=["c", "m", "asr"])
fig, ax = plt.subplots(figsize=(6.4, 3.2))
x = np.arange(len(SYS4)); w = 0.36
for k, (mo, col, nm) in enumerate([("DeepSeek-V3", BLUE, "DeepSeek-V3"), ("Qwen2.5-72B-Instruct", ORANGE, "Qwen2.5-72B-Instruct")]):
    vals = [rm[(rm.c == c) & (rm.m == mo)].asr.values[0] for c in SYS4]
    xs = x + (k - 0.5) * (w + 0.02)
    ax.bar(xs, vals, width=w, color=col, label=nm, edgecolor="white")
    for xx, val in zip(xs, vals): ax.text(xx, val + 0.008, pc(val), ha="center", fontsize=7.8, color=INK)
ax.set_xticks(x); ax.set_xticklabels([LBL[c] for c in SYS4]); ax.yaxis.set_major_formatter(FMTP)
ax.set_ylabel("ASR (menor é melhor)"); ax.set_ylim(0, 0.47); ax.grid(axis="x", visible=False)
ax.legend(fontsize=8, loc="upper left")
fig.savefig(OUT / "5-4-8b_asr_por_modelo_gerador.png"); plt.close(fig)

# ── 5.4.11 F1 regex vs humano ─────────────────────────────────────────────────
h = pd.read_csv(D / "human_eval_results/metricas_vs_humano.csv").set_index("cenario")
ho = h.sort_values("f1_humano", ascending=False).index.tolist()
fig, ax = plt.subplots(figsize=(7.2, 3.6))
x = np.arange(len(ho)); w = 0.38
for k, (col, nm, cc) in enumerate([("f1_regex", "Rótulo da heurística regex", BLUE), ("f1_humano", "Rótulo humano (maioria de 3)", ORANGE)]):
    xs = x + (k - 0.5) * (w + 0.02)
    ax.bar(xs, h.loc[ho, col].values, width=w, color=cc, label=nm, edgecolor="white")
    for xx, val in zip(xs, h.loc[ho, col].values): ax.text(xx, val + 0.012, br(val), ha="center", fontsize=6.8, color=INK)
ax.set_xticks(x); ax.set_xticklabels([LBL[c] for c in ho], rotation=30, ha="right", fontsize=8)
ax.set_ylabel("F1 nas 60 amostras avaliadas"); ax.set_ylim(0, 1.12); ax.yaxis.set_major_formatter(FMT2)
ax.grid(axis="x", visible=False); ax.legend(fontsize=8, loc="upper right", ncol=2)
fig.savefig(OUT / "5-4-11_f1_regex_vs_humano.png"); plt.close(fig)

# ── 5.4.2 estudo intermediário (números do artigo AISec Dev, DeepSeek-V3) ─────
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.8))
lv2 = ["Simples\n(1 função)", "Médio\n(2 funções)", "Complexo\n(3 funções)"]
a1.bar(range(3), [0.0, 0.067, 0.214], color=BLUE, width=0.55, edgecolor="white")
for i, val in enumerate([0.0, 0.067, 0.214]): a1.text(i, val + 0.006, pc(val), ha="center", fontsize=8, color=INK)
a1.set_ylim(0, 0.26); a1.yaxis.set_major_formatter(FMTP); a1.set_title("(a) ASR", fontsize=9, loc="left", color=INK)
a2.bar(range(3), [0.895, 0.875, 0.667], color=BLUE, width=0.55, edgecolor="white")
for i, val in enumerate([0.895, 0.875, 0.667]): a2.text(i, val + 0.015, br(val, 3), ha="center", fontsize=8, color=INK)
a2.set_ylim(0, 1.05); a2.yaxis.set_major_formatter(FMT2); a2.set_title("(b) F1", fontsize=9, loc="left", color=INK)
for ax in (a1, a2):
    ax.set_xticks(range(3)); ax.set_xticklabels(lv2, fontsize=8); ax.grid(axis="x", visible=False)
fig.tight_layout()
fig.savefig(OUT / "5-4-2_estudo_intermediario.png"); plt.close(fig)
print("ok")
