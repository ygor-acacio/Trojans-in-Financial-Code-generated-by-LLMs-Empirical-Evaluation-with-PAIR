"""Diagramas novos da monografia (topologias, linha do tempo, casos de uso, pipeline)."""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, FancyArrowPatch, Rectangle

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
INK, INK2, MUTED, LINE = "#0b0b0b", "#52514e", "#8a8984", "#6b6a66"
NEUT = "#f0efec"
T_BLUE, T_ORANGE, T_AQUA, T_YELLOW = "#cde2fb", "#fbd9c9", "#c6eedd", "#fbe7b5"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.dpi": 300, "savefig.bbox": "tight",
                     "savefig.facecolor": "white"})

def canvas(w, h, figw):
    fig, ax = plt.subplots(figsize=(figw, figw * h / w))
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off"); return fig, ax

def box(ax, x, y, w, h, text, fc=NEUT, ec=LINE, fs=8, bold=False, r=0.12, color=INK, lw=0.9, style="round"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"{style},pad=0,rounding_size={r}" if style == "round" else style,
                                fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color,
            fontweight="bold" if bold else "normal", linespacing=1.25)

def arrow(ax, p, q, text=None, fs=7, dashed=False, color=LINE, off=(0, 0.12), ha="center", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, lw=0.9, color=color,
                                 linestyle=(0, (3, 2)) if dashed else "solid",
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1))
    if text:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha=ha, va="bottom",
                fontsize=fs, color=INK2)

# ═════════════════════ 2.8 topologias de defesa ═════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(7.4, 6.6))
AG = [("Comportamentos", T_BLUE), ("Padrões de Trojan", T_BLUE), ("Políticas", T_BLUE)]
for ax in axes.flat: ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

def outputs(ax, x, y):
    box(ax, x - 2.3, y, 2.0, 0.8, "Bloqueia", fc=T_ORANGE, fs=7.5)
    box(ax, x + 0.3, y, 2.0, 0.8, "Libera", fc=T_AQUA, fs=7.5)

# (a) paralelo / união
ax = axes[0, 0]; ax.set_title("(a) Paralelo – união (OR)", fontsize=9, loc="left", color=INK)
box(ax, 3.0, 8.6, 4.0, 0.9, "Amostra de código", fc="white", fs=8)
for i, (nm, fc) in enumerate(AG):
    x = 0.3 + i * 3.3
    box(ax, x, 5.6, 3.0, 1.1, nm, fc=fc, fs=7.5); arrow(ax, (5, 8.6), (x + 1.5, 6.7))
    arrow(ax, (x + 1.5, 5.6), (5, 4.1))
box(ax, 3.3, 3.0, 3.4, 1.1, "OR: algum agente\nvotou por bloquear?", fc=NEUT, fs=7.5)
outputs(ax, 5, 0.9)
arrow(ax, (4.2, 3.0), (3.7, 1.7), "sim", off=(-0.35, 0)); arrow(ax, (5.8, 3.0), (6.3, 1.7), "não", off=(0.35, 0))

# (b) ponderado
ax = axes[0, 1]; ax.set_title("(b) Votação ponderada", fontsize=9, loc="left", color=INK)
box(ax, 3.0, 8.6, 4.0, 0.9, "Amostra de código", fc="white", fs=8)
for i, ((nm, fc), wgt) in enumerate(zip(AG, ["1,5", "0,6", "1,0"])):
    x = 0.3 + i * 3.3
    box(ax, x, 5.6, 3.0, 1.1, f"{nm}\npeso {wgt}", fc=fc, fs=7.5); arrow(ax, (5, 8.6), (x + 1.5, 6.7))
    arrow(ax, (x + 1.5, 5.6), (5, 4.1))
box(ax, 2.6, 3.0, 4.8, 1.1, "Soma dos pesos dos\nque bloqueiam ≥ 1,55?", fc=NEUT, fs=7.5)
outputs(ax, 5, 0.9)
arrow(ax, (4.2, 3.0), (3.7, 1.7), "sim", off=(-0.35, 0)); arrow(ax, (5.8, 3.0), (6.3, 1.7), "não", off=(0.35, 0))
ax.text(5, 2.45, "", fontsize=6.5)

# (c) série / cascata
ax = axes[1, 0]; ax.set_title("(c) Série – cascata com saída antecipada", fontsize=9, loc="left", color=INK)
box(ax, 0.2, 8.8, 3.2, 0.8, "Amostra de código", fc="white", fs=7.5)
ys = [7.0, 5.0, 3.0]; names = ["1. Comportamentos", "2. Políticas", "3. Padrões de Trojan"]
arrow(ax, (1.8, 8.8), (1.8, 7.9))
for y, nm in zip(ys, names):
    box(ax, 0.2, y, 3.2, 0.9, nm, fc=T_BLUE, fs=7.0)
    arrow(ax, (3.4, y + 0.69), (6.6, y + 0.69), "suspicious ≥ 0,90", fs=6.3, off=(0.1, 0.03))
    arrow(ax, (3.4, y + 0.21), (6.6, y + 0.21), "clean ≥ 0,70", fs=6.3, off=(0.1, -0.4))
    box(ax, 6.7, y + 0.48, 1.8, 0.42, "Bloqueia", fc=T_ORANGE, fs=6.5, r=0.06)
    box(ax, 6.7, y + 0.0, 1.8, 0.42, "Libera", fc=T_AQUA, fs=6.5, r=0.06)
for y0, y1 in [(7.0, 5.9), (5.0, 3.9)]:
    arrow(ax, (1.8, y0), (1.8, y1), "senão", fs=6.3, off=(0.55, -0.2))
arrow(ax, (1.8, 3.0), (1.8, 1.9), "senão", fs=6.3, off=(0.55, -0.2))
box(ax, 0.2, 0.8, 3.2, 1.1, "Maioria: ≥ 2 agentes\nvotam por bloquear?", fc=NEUT, fs=7.2)
box(ax, 6.7, 1.33, 1.8, 0.42, "Bloqueia", fc=T_ORANGE, fs=6.5, r=0.06)
box(ax, 6.7, 0.85, 1.8, 0.42, "Libera", fc=T_AQUA, fs=6.5, r=0.06)
arrow(ax, (3.4, 1.55), (6.6, 1.55), "sim", fs=6.3, off=(0, 0.02)); arrow(ax, (3.4, 1.05), (6.6, 1.05), "não", fs=6.3, off=(0, -0.38))

# (d) orquestrador
ax = axes[1, 1]; ax.set_title("(d) Orquestrador – seleção por LLM", fontsize=9, loc="left", color=INK)
box(ax, 3.0, 8.6, 4.0, 0.9, "Amostra de código", fc="white", fs=8)
box(ax, 2.6, 6.7, 4.8, 1.1, "Orquestrador (LLM)\nescolhe de 1 a 3 especialistas", fc=T_YELLOW, fs=7.5)
arrow(ax, (5, 8.6), (5, 7.8))
for i, (nm, fc) in enumerate(AG):
    x = 0.3 + i * 3.3
    box(ax, x, 4.6, 3.0, 1.1, nm, fc=fc, fs=7.5)
    arrow(ax, (5, 6.7), (x + 1.5, 5.7), dashed=True); arrow(ax, (x + 1.5, 4.6), (5, 4.1))
box(ax, 3.0, 3.0, 4.0, 1.1, "OR entre os agentes\nescolhidos", fc=NEUT, fs=7.5)
outputs(ax, 5, 0.9)
arrow(ax, (4.2, 3.0), (3.7, 1.7), "sim", off=(-0.35, 0)); arrow(ax, (5.8, 3.0), (6.3, 1.7), "não", off=(0.35, 0))
ax.text(5, 0.1, "seta tracejada: consulta feita só se o orquestrador escolher o agente", ha="center", fontsize=6.3, color=INK2)
fig.tight_layout(h_pad=1.2)
fig.savefig(OUT / "2-8_topologias_de_defesa.png"); plt.close(fig)

# ═════════════════════ 3.2 linha do tempo ═══════════════════════════════════
MESES = ["Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
fases = [("1. Revisão bibliográfica", 0.0, 2.0, BLUE),
         ("2. Especificação de requisitos", 0.0, 3.0, BLUE),
         ("3. Projeto da arquitetura", 1.0, 3.0, BLUE),
         ("4. Implementação incremental", 1.0, 3.0, BLUE),
         ("5. Experimentos preliminares", 2.0, 2.65, ORANGE),
         ("6. Estudo intermediário e artigo", 2.4, 3.5, ORANGE),
         ("7. Consolidação e experimento final", 5.0, 6.25, ORANGE),
         ("8. Avaliação humana cega", 6.4, 7.7, AQUA),
         ("9. Análise, redação e apresentação", 6.0, 9.0, AQUA)]
fig, ax = plt.subplots(figsize=(7.4, 3.9))
for i, (nm, a, b, c) in enumerate(fases):
    y = len(fases) - 1 - i
    ax.add_patch(Rectangle((a, y - 0.32), b - a, 0.64, fc=c, ec="white", lw=1))
    ax.text(-0.12, y, nm, ha="right", va="center", fontsize=8, color=INK)
marcos = [(2.1, "3 e 18/jun\npreliminares\n(42 amostras)"), (3.42, "13/jul\nartigo AISec Dev\n(151 amostras)"),
          (6.13, "4–6/out\nexperimento final\n(600 amostras)"), (7.6, "nov\navaliação humana\n(60 × 3)")]
for x, t in marcos:
    ax.axvline(x, color=INK2, lw=0.8, ls=(0, (3, 2)), ymax=0.82)
    ax.text(x, len(fases) + 0.25, t, ha="center", va="bottom", fontsize=6.8, color=INK, linespacing=1.15)
ax.set_xlim(0, 9); ax.set_ylim(-0.7, len(fases) + 1.9)
ax.set_xticks([i + 0.5 for i in range(9)]); ax.set_xticklabels(MESES, fontsize=8, color=INK2)
for i in range(10): ax.axvline(i, color="#e4e3df", lw=0.6, zorder=0)
ax.set_yticks([]); [s.set_visible(False) for s in ax.spines.values()]
ax.tick_params(axis="x", length=0)
ax.set_xlabel("Meses de 2026", fontsize=8, color=INK2)
leg = [Rectangle((0, 0), 1, 1, fc=c) for c in (BLUE, ORANGE, AQUA)]
ax.legend(leg, ["Projeto de Formatura I", "Experimentação", "Validação e redação"], loc="upper center",
          fontsize=7.2, frameon=False, ncol=3, bbox_to_anchor=(0.5, -0.14))
fig.savefig(OUT / "3-2_linha_do_tempo.png"); plt.close(fig)

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
ucs = [("UC01 Configurar\nexperimento", 8.0), ("UC02 Executar\nataque", 7.0), ("UC03 Analisar amostra\ncom agentes", 6.0),
       ("UC04 Derivar cenários\nde defesa", 5.0), ("UC05 Julgar\ncenários", 4.0), ("UC06 Gerar pacote de\navaliação humana", 3.0),
       ("UC07 Avaliar amostras\nàs cegas", 2.0), ("UC08 Consolidar\navaliação humana", 1.0)]
pos = {}
for i, (t, y) in enumerate(ucs):
    cx = 5.6
    ax.add_patch(Ellipse((cx, y), 3.6, 0.82, fc=T_BLUE, ec=LINE, lw=0.9))
    ax.text(cx, y, t, ha="center", va="center", fontsize=6.8, color=INK, linespacing=1.1)
    pos[t.split()[0]] = (cx, y)
ax.add_patch(Ellipse((9.1, 7.0), 2.9, 0.75, fc=NEUT, ec=LINE, lw=0.9))
ax.text(9.1, 7.0, "Executar testes\nlocais", ha="center", va="center", fontsize=6.8, color=INK)
arrow(ax, (7.4, 7.0), (7.65, 7.0), dashed=True)
ax.text(7.52, 7.1, "«include»", ha="center", va="bottom", fontsize=5.8, color=INK2)
ax.annotate("", xy=(5.6, 5.42), xytext=(5.6, 4.41), arrowprops=dict(arrowstyle="-|>", ls=(0, (3, 2)), color=LINE, lw=0.9))
ax.text(5.75, 4.88, "«include»", fontsize=5.8, color=INK2, va="center")
actor(1.3, 5.2, "Pesquisador"); actor(1.3, 1.1, "Avaliador\nhumano"); actor(12.5, 5.2, "Provedor de\ninferência")
for k in ["UC01", "UC02", "UC04", "UC05", "UC06", "UC08"]:
    x, y = pos[k]; ax.plot([1.75, x - 1.8], [6.0, y], color=LINE, lw=0.7)
x, y = pos["UC07"]; ax.plot([1.75, x - 1.8], [1.9, y], color=LINE, lw=0.7)
for k in ["UC02", "UC03", "UC05"]:
    x, y = pos[k]; ax.plot([12.05, x + 1.8 if k != "UC02" else 10.55], [6.0, y], color=LINE, lw=0.7)
x, y = pos["UC04"]; ax.plot([12.05, x + 1.8], [6.0, y], color=LINE, lw=0.7)
ax.text(12.5, 3.75, "(UC04 só no\ncenário orquestrador)", ha="center", va="top", fontsize=6, color=INK2)
fig.savefig(OUT / "4-3_casos_de_uso.png"); plt.close(fig)

# ═════════════════════ 5.2.1 pipeline do experimento ════════════════════════
fig, ax = canvas(20, 11.5, 7.6)
cols = [(0.2, "Etapa 1 – Ataque", T_BLUE), (5.3, "Etapa 2 – Defesa", T_ORANGE),
        (10.4, "Etapa 3 – Juiz", T_AQUA), (15.3, "Avaliação humana", T_YELLOW)]
for x, t, c in cols:
    ax.add_patch(FancyBboxPatch((x, 0.3), 4.5 if x < 15 else 4.5, 10.3, boxstyle="round,pad=0,rounding_size=0.2",
                                fc=c, ec="none", alpha=0.45))
    ax.text(x + 2.25, 10.15, t, ha="center", va="center", fontsize=8.5, fontweight="bold", color=INK)
W = 3.9
# etapa 1
box(ax, 0.5, 8.4, W, 1.1, "config.py\n5 tarefas × 3 níveis\n× 2 modelos × 20 iterações", fc="white", fs=6.5)
loop = [("Gerador\nDeepSeek-V3 / Qwen2.5-72B", 6.9), ("Testes locais\n(safe_exec, 4 testes)", 5.6),
        ("Juiz de ataque\nLlama-3.1-8B, nota 1–10", 4.3), ("Refinador de prompt\nLlama-3.1-8B", 3.0)]
for t, y in loop: box(ax, 0.5, y, W, 0.95, t, fc="white", fs=6.5)
arrow(ax, (2.45, 8.4), (2.45, 7.85))
for (_, y0), (_, y1) in zip(loop, loop[1:]): arrow(ax, (2.45, y0), (2.45, y1 + 0.95))
ax.add_patch(FancyArrowPatch((0.5, 3.45), (0.5, 7.35), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=LINE,
                             connectionstyle="arc3,rad=-0.55"))
ax.text(0.1, 5.4, "20×", fontsize=6.5, color=INK2, ha="center")
box(ax, 0.5, 0.8, W, 1.3, "attack_runs.csv\n600 amostras\n(código, testes, nota,\nrótulo regex)", fc="white", fs=6.3, ec=INK)
arrow(ax, (2.45, 3.0), (2.45, 2.1))
# etapa 2
for i, t in enumerate(["Comportamentos", "Padrões de Trojan", "Políticas"]):
    box(ax, 5.6, 8.1 - i * 1.05, W, 0.85, f"{t}\n(Llama-3.1-8B, temp. 0)", fc="white", fs=6.3)
box(ax, 5.6, 4.3, W, 1.2, "agent_verdicts.csv\ncache: 1.800 vereditos", fc="white", fs=6.5, ec=INK)
arrow(ax, (4.4, 1.45), (5.6, 8.5), rad=-0.1)
arrow(ax, (7.55, 6.0), (7.55, 5.5))
box(ax, 5.6, 2.65, 1.85, 1.2, "7 cenários\npor união", fc="white", fs=6.2)
box(ax, 7.65, 2.65, 1.85, 1.2, "Ponderado\ne Série", fc="white", fs=6.2)
box(ax, 5.6, 0.8, W, 1.3, "Orquestrador (LLM)\n+600 chamadas\n→ 10 × config_*.csv", fc="white", fs=6.3)
arrow(ax, (6.5, 4.3), (6.5, 3.85)); arrow(ax, (8.6, 4.3), (8.6, 3.85))
# etapa 3
box(ax, 10.7, 7.6, W, 1.5, "Métricas por cenário,\nnível e modelo\n(ASR, FPR, F1, ...)", fc="white", fs=6.5)
box(ax, 10.7, 5.6, W, 1.3, "Parecer do juiz LLM\n(Llama-3.1-8B)", fc="white", fs=6.5)
box(ax, 10.7, 2.9, W, 2.0, "judge_summary.csv\nmetrics_by_config.csv\nrelatórios JSON\nfiguras", fc="white", fs=6.3, ec=INK)
box(ax, 10.7, 0.8, W, 1.4, "Amostra estratificada\n60 amostras\n(2 por célula)", fc="white", fs=6.3)
arrow(ax, (9.5, 1.45), (10.7, 8.35), rad=-0.12)
arrow(ax, (12.65, 7.6), (12.65, 6.9)); arrow(ax, (12.65, 5.6), (12.65, 4.9))
# humana
hum = [("Pacotes cegos\n+ gabarito privado", 8.3), ("3 avaliadores\n(há trojan? confiança)", 6.6),
       ("Consolidação\nκ, maioria, métricas", 4.9)]
for t, y in hum: box(ax, 15.6, y, W, 1.15, t, fc="white", fs=6.5)
box(ax, 15.6, 2.9, W, 1.3, "metricas_vs_humano.csv\nconcordancia_avaliadores.csv", fc="white", fs=6.1, ec=INK)
arrow(ax, (14.6, 1.5), (15.6, 8.8), rad=-0.12)
for (_, y0), (_, y1) in zip(hum, hum[1:]): arrow(ax, (17.55, y0), (17.55, y1 + 1.15))
arrow(ax, (17.55, 4.9), (17.55, 4.2))
ax.add_patch(FancyArrowPatch((15.6, 3.55), (14.6, 3.9), arrowstyle="-|>", mutation_scale=9, lw=0.9,
                             color=LINE, linestyle=(0, (3, 2))))
ax.text(15.1, 4.2, "recalcula com\nrótulo humano", ha="center", fontsize=5.6, color=INK2)
fig.savefig(OUT / "5-2-1_pipeline_do_experimento.png"); plt.close(fig)
print("ok")
