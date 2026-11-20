"""Versões corrigidas do diagrama de casos de uso e do pipeline (sobrescrevem as do figs_diagramas.py)."""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, FancyArrowPatch, Rectangle

OUT = Path(sys.argv[1])
INK, INK2, LINE, NEUT = "#0b0b0b", "#52514e", "#6b6a66", "#f0efec"
T_BLUE, T_ORANGE, T_AQUA, T_YELLOW = "#cde2fb", "#fbd9c9", "#c6eedd", "#fbe7b5"
plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.dpi": 300, "savefig.bbox": "tight",
                     "savefig.facecolor": "white"})

def canvas(w, h, figw):
    fig, ax = plt.subplots(figsize=(figw, figw * h / w))
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off"); return fig, ax

def box(ax, x, y, w, h, text, fc=NEUT, ec=LINE, fs=8, r=0.12, lw=0.9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK, linespacing=1.25)

def arrow(ax, p, q, dashed=False, ms=9):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, lw=0.9, color=LINE,
                                 linestyle=(0, (3, 2)) if dashed else "solid", shrinkA=1, shrinkB=1))

# ═════════════════════ 4.3 casos de uso ═════════════════════════════════════
fig, ax = canvas(14, 9.6, 7.4)
def actor(x, y, name):
    ax.add_patch(Ellipse((x, y + 1.25), 0.45, 0.45, fc="white", ec=INK, lw=1))
    ax.plot([x, x], [y + 0.45, y + 1.02], color=INK, lw=1)
    ax.plot([x - 0.4, x + 0.4], [y + 0.82, y + 0.82], color=INK, lw=1)
    ax.plot([x, x - 0.33], [y + 0.45, y], color=INK, lw=1); ax.plot([x, x + 0.33], [y + 0.45, y], color=INK, lw=1)
    ax.text(x, y - 0.25, name, ha="center", va="top", fontsize=7.5, color=INK)
ax.add_patch(Rectangle((3.0, 0.3), 7.8, 9.0, fc="white", ec=INK, lw=1))
ax.text(6.9, 8.95, "Ambiente experimental", ha="center", fontsize=8.5, fontweight="bold", color=INK)
CX, RW = 5.4, 1.8
ucs = [("UC01", "UC01 Configurar\nexperimento", 8.0), ("UC02", "UC02 Executar\nataque", 7.0),
       ("UC03", "UC03 Analisar amostra\ncom agentes", 6.0), ("UC04", "UC04 Derivar cenários\nde defesa", 5.0),
       ("UC05", "UC05 Julgar\ncenários", 4.0), ("UC06", "UC06 Gerar pacote de\navaliação humana", 3.0),
       ("UC07", "UC07 Avaliar amostras\nàs cegas", 2.0), ("UC08", "UC08 Consolidar\navaliação humana", 1.0)]
pos = {}
for k, t, y in ucs:
    ax.add_patch(Ellipse((CX, y), 2 * RW, 0.82, fc=T_BLUE, ec=LINE, lw=0.9))
    ax.text(CX, y, t, ha="center", va="center", fontsize=6.8, color=INK, linespacing=1.1)
    pos[k] = (CX, y)
# UC02 «include» Executar testes locais (local, sem provedor)
ax.add_patch(Ellipse((9.0, 8.1), 2.7, 0.75, fc=NEUT, ec=LINE, lw=0.9))
ax.text(9.0, 8.1, "Executar testes\nlocais", ha="center", va="center", fontsize=6.8, color=INK)
arrow(ax, (7.0, 7.25), (7.85, 7.85), dashed=True, ms=8)
ax.text(7.62, 7.4, "«include»", fontsize=5.8, color=INK2, ha="left", va="center")
# UC04 «include» UC03 (seta de UC04 para UC03)
xi = CX + 1.2; dy = 0.41 * (1 - (1.2 / RW) ** 2) ** 0.5
ax.add_patch(FancyArrowPatch((xi, 5.0 + dy), (xi, 6.0 - dy), arrowstyle="-|>", mutation_scale=7, lw=0.9,
                             color=LINE, linestyle=(0, (3, 2)), shrinkA=0, shrinkB=0))
ax.text(xi + 0.12, 5.5, "«include»", fontsize=5.8, color=INK2, ha="left", va="center")
actor(1.3, 5.2, "Pesquisador"); actor(1.3, 1.1, "Avaliador\nhumano"); actor(12.5, 5.2, "Provedor de\ninferência")
for k in ["UC01", "UC02", "UC04", "UC05", "UC06", "UC08"]:
    x, y = pos[k]; ax.plot([1.75, x - RW], [6.0, y], color=LINE, lw=0.7)
x, y = pos["UC07"]; ax.plot([1.75, x - RW], [1.9, y], color=LINE, lw=0.7)
for k in ["UC02", "UC03", "UC04", "UC05"]:
    x, y = pos[k]; ax.plot([12.05, x + RW], [6.0, y], color=LINE, lw=0.7)
ax.text(12.5, 3.75, "UC02: gerador, juiz e refinador\nUC03: três agentes de defesa\nUC04: só o orquestrador\nUC05: juiz final",
        ha="center", va="top", fontsize=5.9, color=INK2, linespacing=1.3)
fig.savefig(OUT / "4-3_casos_de_uso.png"); plt.close(fig)

# ═════════════════════ 5.2.1 pipeline do experimento ════════════════════════
fig, ax = canvas(20, 11.5, 7.6)
for x, t, c in [(0.2, "Etapa 1 – Ataque", T_BLUE), (5.3, "Etapa 2 – Defesa", T_ORANGE),
                (10.4, "Etapa 3 – Juiz", T_AQUA), (15.3, "Avaliação humana", T_YELLOW)]:
    ax.add_patch(FancyBboxPatch((x, 0.3), 4.5, 10.3, boxstyle="round,pad=0,rounding_size=0.2",
                                fc=c, ec="none", alpha=0.45))
    ax.text(x + 2.25, 10.15, t, ha="center", va="center", fontsize=8.5, fontweight="bold", color=INK)
W = 3.9
def elbow(x0, y0, xg, y1, x1):
    """sai pela direita, percorre a calha entre colunas e entra na próxima caixa"""
    ax.plot([x0, xg, xg], [y0, y0, y1], color=LINE, lw=0.9)
    ax.add_patch(FancyArrowPatch((xg, y1), (x1, y1), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=LINE,
                                 shrinkA=0, shrinkB=1))
# etapa 1
X1, W1 = 0.75, 3.75; xm = X1 + W1 / 2
box(ax, X1, 8.45, W1, 1.15, "config.py: 5 tarefas,\n3 níveis, 2 modelos,\n20 iterações", fc="white", fs=6.0)
loop = [("Gerador (DeepSeek-V3\nou Qwen2.5-72B)", 7.0), ("Testes locais\nsafe_exec, 4 testes", 5.75),
        ("Juiz de ataque\nLlama-3.1-8B, nota 1–10", 4.5), ("Refinador de prompt\nLlama-3.1-8B", 3.25)]
for t, y in loop: box(ax, X1, y, W1, 0.95, t, fc="white", fs=6.0)
arrow(ax, (xm, 8.45), (xm, 7.95))
for (_, y0), (_, y1) in zip(loop, loop[1:]): arrow(ax, (xm, y0), (xm, y1 + 0.95))
ax.plot([X1, 0.45, 0.45], [3.72, 3.72, 7.47], color=LINE, lw=0.9)
ax.add_patch(FancyArrowPatch((0.45, 7.47), (X1, 7.47), arrowstyle="-|>", mutation_scale=8, lw=0.9, color=LINE,
                             shrinkA=0, shrinkB=0))
ax.text(0.31, 5.6, "repete 20×", rotation=90, fontsize=6, color=INK2, ha="center", va="center")
box(ax, X1, 0.8, W1, 1.45, "attack_runs.csv\n600 amostras (código,\ntestes, nota, regex)", fc="white", fs=6.0, ec=INK)
arrow(ax, (xm, 3.25), (xm, 2.25))
# etapa 2
X2 = 5.6
for i, t in enumerate(["Comportamentos", "Padrões de Trojan", "Políticas"]):
    box(ax, X2, 8.6 - i * 1.0, W, 0.82, f"{t}\n(Llama-3.1-8B)", fc="white", fs=6.0)
elbow(X1 + W1, 1.52, 5.0, 9.0, X2)
box(ax, X2, 4.75, W, 1.05, "agent_verdicts.csv\ncache: 1.800 vereditos\n(temperatura 0)", fc="white", fs=6.2, ec=INK)
arrow(ax, (X2 + W / 2, 6.6), (X2 + W / 2, 5.8))
bw = 1.2; gx = (W - 3 * bw) / 2
for i, t in enumerate(["União\n(7 cen.)", "Pond. +\nSérie", "Orquest.\n(+600)"]):
    bx = X2 + i * (bw + gx)
    box(ax, bx, 2.75, bw, 1.15, t, fc="white", fs=5.7)
    arrow(ax, (bx + bw / 2, 4.75), (bx + bw / 2, 3.9)); arrow(ax, (bx + bw / 2, 2.75), (bx + bw / 2, 2.25))
box(ax, X2, 0.8, W, 1.45, "10 × config_*.csv\n(decisão de cada\ncenário por amostra)", fc="white", fs=6.0, ec=INK)
# etapa 3
X3 = 10.7
box(ax, X3, 8.1, W, 1.3, "Métricas por cenário,\nnível e modelo\n(ASR, FPR, F1, ...)", fc="white", fs=6.2)
elbow(X2 + W, 1.52, 10.1, 8.75, X3)
box(ax, X3, 6.3, W, 1.1, "Parecer do juiz LLM\nLlama-3.1-8B", fc="white", fs=6.2)
box(ax, X3, 3.55, W, 2.05, "judge_summary.csv\nmetrics_by_config.csv\nrelatórios JSON\nfiguras", fc="white", fs=6.1, ec=INK)
box(ax, X3, 0.8, W, 1.45, "Amostra estratificada\n60 amostras\n(2 por célula)", fc="white", fs=6.1)
arrow(ax, (X3 + W / 2, 8.1), (X3 + W / 2, 7.4)); arrow(ax, (X3 + W / 2, 6.3), (X3 + W / 2, 5.6))
# avaliação humana
X4 = 15.6
hum = [("Pacotes cegos\n+ gabarito privado", 8.25), ("3 avaliadores:\nhá trojan? confiança?", 6.6),
       ("Consolidação: maioria,\nconcordância e kappa", 4.95)]
for t, y in hum: box(ax, X4, y, W, 1.15, t, fc="white", fs=6.1)
elbow(X3 + W, 1.52, 15.1, 8.82, X4)
for (_, y0), (_, y1) in zip(hum, hum[1:]): arrow(ax, (X4 + W / 2, y0), (X4 + W / 2, y1 + 1.15))
box(ax, X4, 2.75, W, 1.45, "metricas_vs_humano.csv\nconcordancia_*.csv", fc="white", fs=5.8, ec=INK)
arrow(ax, (X4 + W / 2, 4.95), (X4 + W / 2, 4.2))
arrow(ax, (X4, 3.47), (X3 + W, 4.2), dashed=True)
ax.text(X4 + W / 2, 2.35, "a seta tracejada recalcula as\nmétricas com o rótulo humano", ha="center", va="top",
        fontsize=5.8, color=INK2)
fig.savefig(OUT / "5-2-1_pipeline_do_experimento.png"); plt.close(fig)
print("ok")
