"""English figures for the extended ACM sigconf paper, drawn at print size.
Column width ~3.33 in, text width ~7.0 in; fonts 6-7.5 pt."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

D = Path(sys.argv[1]); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, MUTED, GRID, LINE, NEUT = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#6b6a66", "#f0efec"
T_BLUE, T_ORANGE, T_AQUA, T_YELLOW = "#cde2fb", "#fbd9c9", "#c6eedd", "#fbe7b5"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 6.5, "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 6, "ytick.labelsize": 6,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "savefig.dpi": 600, "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "savefig.facecolor": "white"})
COL, TXT = 3.33, 7.0
pc = lambda x, n=1: f"{100*x:.{n}f}%"
LBL = {"solo_behavior": "Behavior", "solo_pattern": "Pattern", "solo_policy": "Policy",
       "pair_behavior_pattern": "Behavior+Pattern", "pair_behavior_policy": "Behavior+Policy",
       "pair_pattern_policy": "Pattern+Policy", "trio_all": "Parallel trio", "weighted_score": "Weighted vote",
       "series_cascade": "Serial cascade", "orchestrator": "Orchestrator"}
GROUP = {k: ("iso" if k.startswith("solo") else "pair" if k.startswith("pair") else "sys") for k in LBL}
GCOL = {"iso": BLUE, "pair": ORANGE, "sys": AQUA}; GMARK = {"iso": "s", "pair": "^", "sys": "o"}
GNAME = {"iso": "Single agent", "pair": "Agent pair (union)", "sys": "System topology"}
SYS4 = ["trio_all", "weighted_score", "series_cascade", "orchestrator"]
SYSCOL = dict(zip(SYS4, [BLUE, ORANGE, AQUA, YELLOW])); SYSMARK = dict(zip(SYS4, ["o", "s", "^", "D"]))
js = pd.read_csv(D / "judge/judge_summary.csv").set_index("config_name")

# ── Fig 3: operating points (column) ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(COL, 2.55))
ax.plot([0, 1], [0, 1], ls="--", lw=0.6, color=MUTED, zorder=1)
ax.text(0.64, 0.585, "random classifier", color=MUTED, fontsize=5.5, rotation=36)
for c in [k for k in LBL if k != "trio_all"] + ["trio_all"]:
    r = js.loc[c]; g = GROUP[c]
    ax.scatter(r.fpr, r.recall_tpr, s=18, marker=GMARK[g], color=GCOL[g], edgecolor="white", linewidth=0.6, zorder=3)
cluster = [("trio_all", "Trio = Pattern+Policy", 1.005), ("pair_behavior_pattern", "Behavior+Pattern", 0.965),
           ("solo_pattern", "Pattern", 0.925), ("orchestrator", "Orchestrator", 0.885)]
for c, t, yt in cluster:
    r = js.loc[c]
    ax.annotate(f"{t} ({pc(r.asr)})", (r.fpr, r.recall_tpr), xytext=(0.69, yt), ha="right", va="center", fontsize=5.6,
                color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.4, shrinkA=1, shrinkB=2.5))
free = {"weighted_score": (5, 4), "pair_behavior_policy": (5, -8), "solo_policy": (5, -3), "solo_behavior": (5, 1),
        "series_cascade": (5, -7)}
for c, o in free.items():
    r = js.loc[c]
    ax.annotate(f"{LBL[c]} ({pc(r.asr)})", (r.fpr, r.recall_tpr), xytext=o, textcoords="offset points", fontsize=5.6, color=INK)
ax.set_xlim(0, 1); ax.set_ylim(0.5, 1.03)
ax.set_xlabel("FPR (share of clean samples blocked)"); ax.set_ylabel("Recall (share of trojans blocked)")
for g in GNAME: ax.scatter([], [], marker=GMARK[g], color=GCOL[g], s=14, label=GNAME[g])
ax.legend(loc="lower right", fontsize=5.6, handletextpad=0.2, borderaxespad=0.2)
ax.text(0.01, 0.515, "ASR = 1 − recall in parentheses", fontsize=5.3, color=INK2)
fig.savefig(OUT / "fig3_operating_points.png"); plt.close(fig)

# ── Fig 4: orchestrator (column) ─────────────────────────────────────────────
o = pd.read_csv(D / "defense/orchestrator_decisions.csv")
n = o.agents.str.split("|").str.len().value_counts().sort_index()
freq = {"Behavior": o.agents.str.contains("behavior_detector").sum(), "Pattern": o.agents.str.contains("trojan_pattern").sum(),
        "Policy": o.agents.str.contains("policy_verifier").sum()}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL, 1.45))
a1.bar([str(i) for i in n.index], n.values, color=BLUE, width=0.6, edgecolor="white", linewidth=0.5)
for x, v in zip(range(len(n)), n.values): a1.text(x, v + 10, f"{v}", ha="center", fontsize=5.6, color=INK)
a1.set_xlabel("Specialists consulted", fontsize=6); a1.set_ylabel("Samples", fontsize=6); a1.set_ylim(0, 520)
a1.set_title("(a) Per sample", fontsize=6.3, loc="left", color=INK); a1.grid(axis="x", visible=False)
a2.bar(list(freq), list(freq.values()), color=BLUE, width=0.6, edgecolor="white", linewidth=0.5)
for x, v in enumerate(freq.values()): a2.text(x, v + 10, f"{v}", ha="center", fontsize=5.6, color=INK)
a2.set_ylim(0, 650); a2.set_title("(b) Times each agent was consulted", fontsize=6.3, loc="left", color=INK)
a2.grid(axis="x", visible=False)
fig.tight_layout(w_pad=0.8); fig.savefig(OUT / "fig4_orchestrator.png"); plt.close(fig)

# ── Fig 5: complexity (column) ───────────────────────────────────────────────
m = pd.read_csv(D / "judge/metrics_by_config.csv"); lv = ["simple", "medium", "complex"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL, 1.75))
for c in SYS4:
    g = m[(m.config_name == c) & (m.model == "ALL")].set_index("level").loc[lv]
    for ax, col in [(a1, "asr"), (a2, "f1")]:
        ax.plot(range(3), g[col].values, color=SYSCOL[c], marker=SYSMARK[c], ms=3.2, lw=1.2,
                markeredgecolor="white", markeredgewidth=0.5, label=LBL[c])
for ax, t in [(a1, "(a) ASR (lower is better)"), (a2, "(b) F1 (higher is better)")]:
    ax.set_xticks(range(3)); ax.set_xticklabels(lv); ax.set_title(t, fontsize=6.3, loc="left", color=INK)
    ax.set_xlim(-0.25, 2.25)
a1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{100*v:.0f}%")); a1.set_ylim(0, 0.55)
a2.set_ylim(0.55, 1.0)
h, l = a1.get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, fontsize=5.6, bbox_to_anchor=(0.5, -0.07), handlelength=1.6, columnspacing=0.9)
fig.tight_layout(rect=(0, 0.07, 1, 1), w_pad=0.8); fig.savefig(OUT / "fig5_complexity.png"); plt.close(fig)

# ── Fig 6: F1 regex vs human (column) ────────────────────────────────────────
hm = pd.read_csv(D / "human_eval_results/metricas_vs_humano.csv").set_index("cenario")
groups = [("Pattern-\nbased (a)", "solo_pattern"), ("Orches-\ntrator", "orchestrator"), ("Weighted,\nB+Pol (b)", "weighted_score"),
          ("Behavior,\nPolicy (c)", "solo_behavior"), ("Serial\ncascade", "series_cascade")]
fig, ax = plt.subplots(figsize=(COL, 1.85))
x = np.arange(len(groups)); w = 0.38
for k, (col, nm, cc) in enumerate([("f1_regex", "Regex label", BLUE), ("f1_humano", "Human label (majority of 3)", ORANGE)]):
    vals = [hm.loc[c, col] for _, c in groups]
    xs = x + (k - 0.5) * (w + 0.02)
    ax.bar(xs, vals, width=w, color=cc, label=nm, edgecolor="white", linewidth=0.5)
    for xx, v in zip(xs, vals): ax.text(xx, v + 0.015, f"{v:.2f}", ha="center", fontsize=5.3, color=INK)
ax.set_xticks(x); ax.set_xticklabels([g for g, _ in groups], fontsize=5.8)
ax.set_ylabel("F1 on the 60 rated samples"); ax.set_ylim(0, 1.18); ax.grid(axis="x", visible=False)
ax.legend(fontsize=5.6, loc="upper right", ncol=2, handlelength=1.2)
ax.text(0, -0.27, "(a) Pattern alone, Behavior+Pattern, Pattern+Policy and parallel trio (identical results).\n"
        "(b) Weighted vote and Behavior+Policy (identical results).\n"
        "(c) Same human-label F1; the regex bar shows Behavior alone (Policy alone: 0.61).",
        transform=ax.transAxes, fontsize=4.9, color=INK2, va="top", linespacing=1.3)
fig.savefig(OUT / "fig6_f1_regex_vs_human.png"); plt.close(fig)

# ── diagram helpers ──────────────────────────────────────────────────────────
def box(ax, x, y, w, h, t, fc=NEUT, ec=LINE, fs=6, r=0.1, lw=0.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=INK, linespacing=1.2)
def arr(ax, p, q, dashed=False, ms=5, lw=0.6):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=LINE,
                                 linestyle=(0, (3, 2)) if dashed else "solid", shrinkA=0.5, shrinkB=0.5))
def lab(ax, x, y, t, fs=5, ha="center"): ax.text(x, y, t, ha=ha, va="center", fontsize=fs, color=INK2)

# ── Fig 2: topologies (column, 2x2) ──────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(COL, 3.25))
for ax in axes.flat: ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
AG = ["Behavior", "Pattern", "Policy"]
def outs(ax, y=0.5):
    box(ax, 1.4, y, 3.2, 1.1, "Block", fc=T_ORANGE, fs=5.6); box(ax, 5.4, y, 3.2, 1.1, "Allow", fc=T_AQUA, fs=5.6)
def fan(ax, ytop, yag, ydec, labels, h=1.3):
    box(ax, 2.0, ytop, 6.0, 1.1, "Code sample", fc="white", fs=5.6)
    for i, t in enumerate(labels):
        x = 0.1 + i * 3.35
        box(ax, x, yag, 3.1, h, t, fc=T_BLUE, fs=5.3); arr(ax, (5, ytop), (x + 1.55, yag + h))
        arr(ax, (x + 1.55, yag), (5, ydec))
ax = axes[0, 0]; ax.set_title("(a) Parallel union", fontsize=6.3, loc="left", color=INK, pad=2)
fan(ax, 8.6, 5.6, 4.1, AG); box(ax, 1.6, 2.9, 6.8, 1.2, "any agent blocks?", fs=5.4)
outs(ax); arr(ax, (3.6, 2.9), (3.0, 1.6)); arr(ax, (6.4, 2.9), (7.0, 1.6)); lab(ax, 2.7, 2.3, "yes"); lab(ax, 7.4, 2.3, "no")
ax = axes[0, 1]; ax.set_title("(b) Weighted vote", fontsize=6.3, loc="left", color=INK, pad=2)
fan(ax, 8.6, 5.6, 4.1, ["Behavior\nw = 1.5", "Pattern\nw = 0.6", "Policy\nw = 1.0"], h=1.5)
box(ax, 1.0, 2.9, 8.0, 1.2, "Σ w(blocking) ≥ 1.55?", fs=5.4)
outs(ax); arr(ax, (3.6, 2.9), (3.0, 1.6)); arr(ax, (6.4, 2.9), (7.0, 1.6)); lab(ax, 2.7, 2.3, "yes"); lab(ax, 7.4, 2.3, "no")
ax = axes[1, 0]; ax.set_title("(c) Serial cascade", fontsize=6.3, loc="left", color=INK, pad=2)
box(ax, 0.1, 8.8, 3.6, 1.0, "Code sample", fc="white", fs=5.3); arr(ax, (1.9, 8.8), (1.9, 8.1))
ys = [6.9, 4.9, 2.9]
for y, t in zip(ys, ["1. Behavior", "2. Policy", "3. Pattern"]):
    box(ax, 0.1, y, 3.6, 1.2, t, fc=T_BLUE, fs=5.3)
    arr(ax, (3.7, y + 0.9), (6.3, y + 0.9)); arr(ax, (3.7, y + 0.3), (6.3, y + 0.3))
    lab(ax, 5.0, y + 1.25, "susp. ≥ 0.90", fs=4.6); lab(ax, 5.0, y - 0.05, "clean ≥ 0.70", fs=4.6)
    box(ax, 6.4, y + 0.62, 3.0, 0.56, "Block", fc=T_ORANGE, fs=4.9, r=0.05); box(ax, 6.4, y + 0.02, 3.0, 0.56, "Allow", fc=T_AQUA, fs=4.9, r=0.05)
for y0, y1 in [(6.9, 6.1), (4.9, 4.1), (2.9, 2.1)]: arr(ax, (1.9, y0), (1.9, y1))
box(ax, 0.1, 0.6, 3.6, 1.5, "majority\n≥ 2 blocks?", fs=5.1)
arr(ax, (3.7, 1.65), (6.3, 1.65)); arr(ax, (3.7, 1.05), (6.3, 1.05)); lab(ax, 5.0, 1.95, "yes", fs=4.6); lab(ax, 5.0, 0.75, "no", fs=4.6)
box(ax, 6.4, 1.37, 3.0, 0.56, "Block", fc=T_ORANGE, fs=4.9, r=0.05); box(ax, 6.4, 0.77, 3.0, 0.56, "Allow", fc=T_AQUA, fs=4.9, r=0.05)
ax = axes[1, 1]; ax.set_title("(d) LLM orchestrator", fontsize=6.3, loc="left", color=INK, pad=2)
box(ax, 2.0, 8.8, 6.0, 1.0, "Code sample", fc="white", fs=5.6); arr(ax, (5, 8.8), (5, 8.1))
box(ax, 1.0, 6.9, 8.0, 1.2, "Orchestrator picks 1–3", fc=T_YELLOW, fs=5.3)
for i, t in enumerate(AG):
    x = 0.1 + i * 3.35
    box(ax, x, 4.7, 3.1, 1.2, t, fc=T_BLUE, fs=5.3); arr(ax, (5, 6.9), (x + 1.55, 5.9), dashed=True); arr(ax, (x + 1.55, 4.7), (5, 4.1))
box(ax, 1.6, 2.9, 6.8, 1.2, "any chosen agent blocks?", fs=5.2)
outs(ax); arr(ax, (3.6, 2.9), (3.0, 1.6)); arr(ax, (6.4, 2.9), (7.0, 1.6)); lab(ax, 2.7, 2.3, "yes"); lab(ax, 7.4, 2.3, "no")
fig.tight_layout(h_pad=0.6, w_pad=0.4); fig.savefig(OUT / "fig2_topologies.png"); plt.close(fig)

# ── Fig 1: pipeline (text width) ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(TXT, 3.0)); ax.set_xlim(0, 20); ax.set_ylim(0, 8.6); ax.axis("off")
for x, t, c in [(0.2, "Stage 1 – Attack", T_BLUE), (5.3, "Stage 2 – Defense", T_ORANGE),
                (10.4, "Stage 3 – Judge", T_AQUA), (15.3, "Human evaluation", T_YELLOW)]:
    ax.add_patch(FancyBboxPatch((x, 0.15), 4.5, 8.3, boxstyle="round,pad=0,rounding_size=0.2", fc=c, ec="none", alpha=0.45))
    ax.text(x + 2.25, 8.05, t, ha="center", va="center", fontsize=7.2, fontweight="bold", color=INK)
W = 3.9
def elbow(x0, y0, xg, y1, x1):
    ax.plot([x0, xg, xg], [y0, y0, y1], color=LINE, lw=0.6)
    ax.add_patch(FancyArrowPatch((xg, y1), (x1, y1), arrowstyle="-|>", mutation_scale=6, lw=0.6, color=LINE, shrinkA=0, shrinkB=0.5))
X1, W1 = 0.75, 3.75; xm = X1 + W1 / 2
box(ax, X1, 6.75, W1, 0.85, "config: 5 tasks, 3 levels,\n2 models, 20 iterations", fc="white", fs=5.2)
loop = [("Generator: DeepSeek-V3\nor Qwen2.5-72B", 5.6), ("Local unit tests (4)", 4.55),
        ("Attack judge\nLlama-3.1-8B, score 1–10", 3.5), ("Prompt refiner\n(Llama-3.1-8B)", 2.45)]
for t, y in loop: box(ax, X1, y, W1, 0.78, t, fc="white", fs=5.2)
arr(ax, (xm, 6.75), (xm, 6.38))
for (_, y0), (_, y1) in zip(loop, loop[1:]): arr(ax, (xm, y0), (xm, y1 + 0.78))
ax.plot([X1, 0.45, 0.45], [2.84, 2.84, 5.99], color=LINE, lw=0.6)
ax.add_patch(FancyArrowPatch((0.45, 5.99), (X1, 5.99), arrowstyle="-|>", mutation_scale=5, lw=0.6, color=LINE, shrinkA=0, shrinkB=0))
ax.text(0.31, 4.4, "20×", rotation=90, fontsize=5.4, color=INK2, ha="center", va="center")
box(ax, X1, 0.5, W1, 1.2, "600 samples (code, tests,\nscore, regex label)", fc="white", fs=5.2, ec=INK)
arr(ax, (xm, 2.45), (xm, 1.7))
X2 = 5.6
for i, t in enumerate(["Behavior detector", "Trojan-pattern detector", "Policy verifier"]):
    box(ax, X2, 6.75 - i * 0.82, W, 0.66, t, fc="white", fs=5.4)
elbow(X1 + W1, 1.1, 5.0, 7.08, X2)
box(ax, X2, 3.6, W, 1.0, "Verdict cache: 1,800 verdicts\n(Llama-3.1-8B, temperature 0)", fc="white", fs=5.0, ec=INK)
arr(ax, (X2 + W / 2, 5.11), (X2 + W / 2, 4.6))
bw = 1.2; gx = (W - 3 * bw) / 2
for i, t in enumerate(["Union\n(7)", "Vote,\ncascade", "Orches-\ntrator"]):
    bx = X2 + i * (bw + gx); box(ax, bx, 2.15, bw, 0.95, t, fc="white", fs=4.7)
    arr(ax, (bx + bw / 2, 3.6), (bx + bw / 2, 3.1)); arr(ax, (bx + bw / 2, 2.15), (bx + bw / 2, 1.7))
box(ax, X2, 0.5, W, 1.2, "10 scenario decisions\nper sample", fc="white", fs=5.6, ec=INK)
X3 = 10.7
box(ax, X3, 6.45, W, 1.1, "Metrics per scenario,\nlevel and model", fc="white", fs=5.6)
elbow(X2 + W, 1.1, 10.1, 7.0, X3)
box(ax, X3, 5.0, W, 0.9, "LLM judge assessment\n(Llama-3.1-8B)", fc="white", fs=5.6)
box(ax, X3, 2.85, W, 1.55, "Summary tables,\nper-level and per-model\nmetrics, figures", fc="white", fs=5.6, ec=INK)
box(ax, X3, 0.5, W, 1.2, "Stratified subsample\n60 samples (2 per cell)", fc="white", fs=5.6)
arr(ax, (X3 + W / 2, 6.45), (X3 + W / 2, 5.9)); arr(ax, (X3 + W / 2, 5.0), (X3 + W / 2, 4.4))
X4 = 15.6
hum = [("Blind packages +\nprivate answer key", 6.55), ("3 raters: trojan? (0/1)\nconfidence (1–5)", 5.2),
       ("Majority label,\nagreement, kappa", 3.85)]
for t, y in hum: box(ax, X4, y, W, 0.95, t, fc="white", fs=5.6)
elbow(X3 + W, 1.1, 15.1, 7.02, X4)
for (_, y0), (_, y1) in zip(hum, hum[1:]): arr(ax, (X4 + W / 2, y0), (X4 + W / 2, y1 + 0.95))
box(ax, X4, 2.15, W, 1.1, "Scenario metrics\nunder human labels", fc="white", fs=5.6, ec=INK)
arr(ax, (X4 + W / 2, 3.85), (X4 + W / 2, 3.25))
arr(ax, (X4, 2.7), (X3 + W, 3.3), dashed=True)
ax.text(X4 + W / 2, 1.55, "dashed arrow: metrics recomputed\nwith the human label", ha="center", va="top", fontsize=5, color=INK2)
fig.savefig(OUT / "fig1_pipeline.png"); plt.close(fig)
print("ok")
