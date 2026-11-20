"""Fill the PCS3860 banner template (single 74x106 cm slide) with the English poster content."""
import re, shutil, sys, zipfile
from pathlib import Path
from xml.sax.saxutils import escape

TPL, FIGS, OUT, WORK = map(Path, sys.argv[1:5])
if WORK.exists(): shutil.rmtree(WORK)
zipfile.ZipFile(TPL).extractall(WORK)
slide_p = WORK / "ppt/slides/slide1.xml"; rels_p = WORK / "ppt/slides/_rels/slide1.xml.rels"
ct_p = WORK / "[Content_Types].xml"
s = slide_p.read_text(encoding="utf-8")

PURPLE, INK, INK2, CARD, WHITE = "6600FF", "1E1E1E", "4A4A4A", "E6EEE9", "FFFFFF"
FONT = "Tahoma"
M = 360000  # EMU per cm

# ── 1. template text replacements ───────────────────────────────────────────
TITLE = "Multi-Agent Defense Against Trojan Insertion in LLM-Generated Code for Financial Applications"
s = s.replace('sz="4800" b="1" dirty="0"><a:solidFill><a:srgbClr val="6600FF"/></a:solidFill><a:latin typeface="Tahoma"/><a:ea typeface="Times New Roman"/></a:rPr><a:t>Digite o tema aqui!</a:t>',
              f'sz="3600" b="1" dirty="0"><a:solidFill><a:srgbClr val="6600FF"/></a:solidFill><a:latin typeface="Tahoma"/><a:ea typeface="Times New Roman"/></a:rPr><a:t>{escape(TITLE)}</a:t>', 1)
s = s.replace('lang="pt-BR" sz="4800"', 'lang="en-US" sz="4800"')
assert TITLE in s

# member names box (TextBox 8): one member, drop the other two placeholder paragraphs
sp8 = re.search(r'<p:sp><p:nvSpPr><p:cNvPr id="\d+" name="TextBox 8"/>.*?</p:sp>', s, re.S).group(0)
paras = re.findall(r'<a:p>.*?</a:p>', sp8, re.S)
new_p = paras[0].replace("<a:t>- </a:t>", "<a:t>Ygor Acacio Maria</a:t>")
sp8n = sp8.replace("".join(paras), new_p)
s = s.replace(sp8, sp8n)

# advisors (two TextBox 9, in order)
names = iter(["Prof. Dr. Victor Takashi Hayashi", "Prof. Dr. Marcos Antonio Simplicio Junior"])
s = re.sub(r"<a:t>- \(Prof\. Dr\. /Profa\. Dra\.\)</a:t>", lambda m: f"<a:t>{next(names)}</a:t>", s)
# advisor name boxes: move right of the labels and widen so the names do not wrap
for yy in ("36475936", "37100489"):
    s = s.replace(f'<a:off x="6530901" y="{yy}"/><a:ext cx="7596187" cy="676275"/>',
                  f'<a:off x="7150000" y="{yy}"/><a:ext cx="11800000" cy="676275"/>')
assert s.count('<a:off x="7150000"') == 2

# labels
s = s.replace("<a:t>Integrantes:</a:t>", "<a:t>Team member:</a:t>")
s = s.replace('<a:off x="1524001" y="34290000"/><a:ext cx="3048000" cy="641350"/>',
              '<a:off x="588963" y="34290000"/><a:ext cx="4300000" cy="641350"/>')
s = s.replace('<a:p><a:pPr><a:lnSpc><a:spcPct val="90000"/></a:lnSpc></a:pPr><a:r><a:rPr lang="pt-BR" altLang="pt-BR" sz="4000" dirty="0"><a:solidFill><a:srgbClr val="6600FF"/></a:solidFill><a:latin typeface="Tahoma" pitchFamily="34" charset="0"/></a:rPr><a:t>Team member:</a:t>',
              '<a:p><a:pPr algn="r"><a:lnSpc><a:spcPct val="90000"/></a:lnSpc></a:pPr><a:r><a:rPr lang="en-US" altLang="pt-BR" sz="4000" dirty="0"><a:solidFill><a:srgbClr val="6600FF"/></a:solidFill><a:latin typeface="Tahoma" pitchFamily="34" charset="0"/></a:rPr><a:t>Team member:</a:t>')
s = s.replace('<a:p><a:pPr><a:lnSpc><a:spcPct val="90000"/></a:lnSpc></a:pPr><a:r><a:rPr lang="pt-BR" altLang="pt-BR" sz="4000" dirty="0"><a:solidFill><a:srgbClr val="6600FF"/></a:solidFill><a:latin typeface="Tahoma" pitchFamily="34" charset="0"/></a:rPr><a:t>Professor(a) Orientador(a):</a:t>',
              '<a:p><a:pPr algn="r"><a:lnSpc><a:spcPct val="90000"/></a:lnSpc></a:pPr><a:r><a:rPr lang="en-US" altLang="pt-BR" sz="4000" dirty="0"><a:solidFill><a:srgbClr val="6600FF"/></a:solidFill><a:latin typeface="Tahoma" pitchFamily="34" charset="0"/></a:rPr><a:t>Advisor:</a:t>')
s = re.sub(r'<a:t>Co-orientador</a:t></a:r><a:r>(<a:rPr[^>]*>.*?</a:rPr>)<a:t>\(a\):</a:t>',
           r'<a:t>Co-advisor:</a:t></a:r><a:r>\1<a:t></a:t>', s, flags=re.S)
for t in ["Team member:", "Advisor:", "Co-advisor:", "Ygor Acacio Maria", "Simplicio Junior"]: assert t in s, t

# ── 2. new shapes ───────────────────────────────────────────────────────────
nid = [100]
def _id():
    nid[0] += 1; return nid[0]

def rpr(sz, bold=False, color=INK, italic=False):
    return (f'<a:rPr lang="en-US" sz="{int(sz*100)}" b="{1 if bold else 0}" i="{1 if italic else 0}" dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="{FONT}"/><a:cs typeface="{FONT}"/></a:rPr>')

def para(runs, algn="l", bullet=False, after=6, before=0, line=100):
    """runs: list of (text, size, bold, color)"""
    sz = runs[0][1]
    ppr = f'<a:pPr algn="{algn}"'
    if bullet: ppr += f' marL="{int(sz*12700*1.15)}" indent="-{int(sz*12700*1.15)}"'
    ppr += f'><a:lnSpc><a:spcPct val="{line*1000}"/></a:lnSpc><a:spcBef><a:spcPts val="{before*100}"/></a:spcBef><a:spcAft><a:spcPts val="{after*100}"/></a:spcAft>'
    ppr += (f'<a:buClr><a:srgbClr val="{PURPLE}"/></a:buClr><a:buFont typeface="Arial"/><a:buChar char="•"/>' if bullet else '<a:buNone/>')
    ppr += "</a:pPr>"
    body = "".join(f'<a:r>{rpr(sz_, b_, c_)}<a:t xml:space="preserve">{escape(t)}</a:t></a:r>' for t, sz_, b_, c_ in runs)
    return f"<a:p>{ppr}{body}</a:p>"

def textbox(x, y, w, h, paras, anchor="t", name="Text"):
    i = _id()
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="{name} {i}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="{anchor}"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
            f'{"".join(paras)}</p:txBody></p:sp>')

def card(x, y, w, h, fill=CARD, name="Card"):
    i = _id()
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="{name} {i}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 2500"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill><a:ln><a:noFill/></a:ln>'
            f'<a:effectLst><a:outerShdw blurRad="76200" dist="38100" dir="5400000" algn="t" rotWithShape="0">'
            f'<a:srgbClr val="000000"><a:alpha val="22000"/></a:srgbClr></a:outerShdw></a:effectLst></p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-US"/></a:p></p:txBody></p:sp>')

rels = rels_p.read_text(encoding="utf-8"); media = {}
def pic(fname, x, y, w, descr):
    from PIL import Image
    src = FIGS / fname; W_, H_ = Image.open(src).size; h = w * H_ / W_
    if fname not in media:
        rid = f"rId{50 + len(media)}"; media[fname] = rid
        shutil.copy(src, WORK / "ppt/media" / f"poster_{fname}")
    i = _id()
    xml = (f'<p:pic><p:nvPicPr><p:cNvPr id="{i}" name="Picture {i}" descr="{escape(descr)}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
           f'<p:blipFill><a:blip r:embed="{media[fname]}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
           f'<p:spPr><a:xfrm><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
    return xml, h

BODY, HEAD, SMALL = 26, 40, 20
X0, XR = 1.52e6, 25.50e6; GAP = 0.6e6
CW = (XR - X0 - GAP) / 2; C1, C2 = X0, X0 + CW + GAP
P = 0.45e6  # inner padding
shapes = []
def heading(x, y, w, t):
    shapes.append(textbox(x + P, y + P * 0.8, w - 2 * P, 0.75e6, [para([(t, HEAD, True, PURPLE)], after=0)], name="Heading"))
    return y + P * 0.8 + 0.85e6
def B(t, bold_lead=None):
    runs = ([(bold_lead, BODY, True, INK)] if bold_lead else []) + [(t, BODY, False, INK)]
    return para(runs, bullet=True, after=8)

# ── Row 1 ────────────────────────────────────────────────────────────────────
R1, H1 = 7.65e6, 5.55e6
shapes.append(card(C1, R1, CW, H1)); y = heading(C1, R1, CW, "Motivation")
shapes.append(textbox(C1 + P, y, CW - 2 * P, H1 - (y - R1) - P, [
    para([("LLM assistants now write production code, including in finance. A ", BODY, False, INK),
          ("logic trojan", BODY, True, INK),
          (" is a tiny numerical deviation that fires only on a rare input: it uses no network, files or eval, passes "
           "ordinary unit tests and is invisible to rule-based static analysis.", BODY, False, INK)], after=12),
    para([("Example: a loan payment that comes out slightly higher only for one specific principal value.", BODY - 2, False, INK2)], after=12),
    para([("Can a defense built from specialized LLM agents catch it, and does the way the agents are combined matter?",
           BODY, True, PURPLE)], after=0)]))
shapes.append(card(C2, R1, CW, H1)); y = heading(C2, R1, CW, "The study at a glance")
tiles = [("600", "code samples"), ("5", "financial tasks"), ("3", "complexity levels"),
         ("2", "generator LLMs"), ("10", "defense scenarios"), ("3", "blind human raters")]
tw = (CW - 2 * P - 2 * 0.3e6) / 3; th = (H1 - (y - R1) - P - 0.3e6) / 2
for k, (num, lab) in enumerate(tiles):
    tx = C2 + P + (k % 3) * (tw + 0.3e6); ty = y + (k // 3) * (th + 0.3e6)
    shapes.append(card(tx, ty, tw, th, fill=WHITE, name="Tile"))
    shapes.append(textbox(tx, ty + 0.12e6, tw, th - 0.2e6, [para([(num, 60, True, PURPLE)], algn="ctr", after=0, line=90),
                                                             para([(lab, 22, False, INK2)], algn="ctr", after=0)], anchor="ctr"))

# ── Row 2 ────────────────────────────────────────────────────────────────────
R2, H2 = 13.6e6, 9.45e6
shapes.append(card(C1, R2, CW, H2)); y = heading(C1, R2, CW, "Approach")
xml, h = pic("fig1_pipeline.png", C1 + P, y, CW - 2 * P, "Pipeline: attack, defense, judge and human evaluation"); shapes.append(xml)
y += h + 0.3e6
shapes.append(textbox(C1 + P, y, CW - 2 * P, R2 + H2 - y - P, [
    B("PAIR-style loop (generator, unit tests, judge, refiner), 20 iterations per cell, DeepSeek-V3 and Qwen2.5-72B.", "Attack: "),
    B("behavior, trojan-pattern and policy agents (Llama-3.1-8B), run once per sample and cached, so the aggregation rule is the only variable.", "Defense: "),
    B("regex heuristic on all 600 samples; blind majority vote of 3 raters on a stratified subset of 60.", "Labels: ")]))
shapes.append(card(C2, R2, CW, H2)); y = heading(C2, R2, CW, "Ten defense scenarios")
fw = 6.55e6
xml, h = pic("fig2_topologies.png", C2 + P, y + 0.1e6, fw, "Four system topologies"); shapes.append(xml)
tx = C2 + P + fw + 0.35e6
shapes.append(textbox(tx, y + 0.1e6, C2 + CW - P - tx, R2 + H2 - y - P, [
    para([("Single agents (×3) and pairs (×3)", BODY - 2, True, INK)], after=2),
    para([("union of their votes", BODY - 2, False, INK2)], after=14),
    para([("(a) Parallel trio", BODY - 2, True, INK)], after=2),
    para([("block if any agent blocks", BODY - 2, False, INK2)], after=14),
    para([("(b) Weighted vote", BODY - 2, True, INK)], after=2),
    para([("weights 1.5 / 0.6 / 1.0, threshold 1.55", BODY - 2, False, INK2)], after=14),
    para([("(c) Serial cascade", BODY - 2, True, INK)], after=2),
    para([("early exit on a confident verdict", BODY - 2, False, INK2)], after=14),
    para([("(d) LLM orchestrator", BODY - 2, True, INK)], after=2),
    para([("picks which agents to consult", BODY - 2, False, INK2)], after=0)]))
ny = y + 0.1e6 + h + 0.35e6
shapes.append(textbox(C2 + P, ny, CW - 2 * P, R2 + H2 - ny - P * 0.6, [
    para([("All scenarios reuse the same 1,800 cached agent verdicts, so any difference between them comes from the "
           "aggregation rule alone.", BODY - 2, False, INK)], after=0)]))

# ── Row 3 ────────────────────────────────────────────────────────────────────
R3, H3 = 23.45e6, 6.95e6
shapes.append(card(C1, R3, CW, H3)); y = heading(C1, R3, CW, "Heuristic labels: a trade-off")
fw = 6.6e6
xml, h = pic("fig3_operating_points.png", C1 + P, y, fw, "Operating points of the ten scenarios"); shapes.append(xml)
tx = C1 + P + fw + 0.35e6; tw_ = C1 + CW - P - tx
shapes.append(textbox(tx, y, tw_, R3 + H3 - y - P, [
    para([("Trio: ", BODY - 2, True, INK), ("2.6% of trojans pass, but 85% of “clean” samples are blocked.", BODY - 2, False, INK)], after=12),
    para([("Cascade: ", BODY - 2, True, INK), ("26% false alarms, but 40% of trojans pass.", BODY - 2, False, INK)], after=12),
    para([("Complexity: ", BODY - 2, True, INK), ("spreading the trojan over 3 functions lowers F1 in every topology (trio 0.97 → 0.73).", BODY - 2, False, INK)], after=0)]))
shapes.append(card(C2, R3, CW, H3)); y = heading(C2, R3, CW, "Human labels: the trade-off disappears")
sw = 2.6e6
for k, (num, lab) in enumerate([("96.7%", "of samples contain a\ntrojan (3 raters)"), ("70%", "flagged by the\nregex heuristic")]):
    ty = y + k * 1.75e6
    shapes.append(textbox(C2 + P, ty, sw, 0.95e6, [para([(num, 56, True, PURPLE)], after=0, line=90)]))
    shapes.append(textbox(C2 + P, ty + 0.92e6, sw, 0.75e6, [para([(l, 18, False, INK2)], after=0) for l in lab.split("\n")]))
fw = 7.0e6; fx = C2 + CW - P - fw
xml, h = pic("fig6_f1_regex_vs_human.png", fx, y, fw, "F1 per scenario under regex and human labels"); shapes.append(xml)
shapes.append(textbox(C2 + P, y + max(h, 3.5e6) + 0.15e6, CW - 2 * P, R3 + H3 - (y + max(h, 3.5e6) + 0.15e6) - P * 0.4, [
    para([("The regex misses 28% of the trojans. Re-scored, the trojan-pattern agent and every topology using it miss ", BODY - 4, False, INK),
          ("1 of 58", BODY - 4, True, INK), (" trojans (F1 0.991); conservative topologies miss between 47% and 67%.", BODY - 4, False, INK)], after=0)]))

# ── Row 4 ────────────────────────────────────────────────────────────────────
R4, H4 = 30.7e6, 3.3e6
shapes.append(card(C1, R4, CW, H4)); y = heading(C1, R4, CW, "Why elaborate topologies did not help")
SB = BODY - 4
def Bs(t, lead): return para([(lead, SB, True, INK), (t, SB, False, INK)], bullet=True, after=4)
shapes.append(textbox(C1 + P, y, CW - 2 * P, R4 + H4 - y - P * 0.5, [
    Bs("no agent can block alone and any pair can, so it equals a simple majority (425 blocks in both).", "Weighted vote: "),
    Bs("no “suspicious” verdict reached 0.90 confidence, so it never blocked early.", "Cascade: "),
    Bs("skipping the pattern agent in 40 samples caused all 9 extra misses (p = 0.004).", "Orchestrator: ")]))
shapes.append(card(C2, R4, CW, H4)); y = heading(C2, R4, CW, "Takeaways")
shapes.append(textbox(C2 + P, y, CW - 2 * P, R4 + H4 - y - P * 0.5, [
    para([("A detector specialized in the threat model is the decisive component.", SB, False, INK)], bullet=True, after=4),
    para([("LLM confidence must be calibrated before thresholds or cascades can work.", SB, False, INK)], bullet=True, after=4),
    para([("Validate heuristic ground truth with humans: it can invert which detector looks best.", SB, False, INK)], bullet=True, after=8),
    para([("Next: ", SB, True, PURPLE), ("calibrated confidence, a verified clean-code set to measure false alarms, larger defense models.", SB, False, INK)], after=0)]))

# ── Footer info (right side, beside advisors) ────────────────────────────────
shapes.append(textbox(14.6e6, 34.25e6, XR - 14.6e6, 3.5e6, [
    para([("Related publication: ", SMALL, True, INK2), ("Y. A. Maria, V. T. Hayashi, M. A. Simplicio Jr. Trojans in Financial Code Generated by LLMs: Empirical Evaluation with PAIR. AISec Dev @ CBSoft 2026.", SMALL, False, INK2)], after=8),
    para([("Code and data: ", SMALL, True, INK2), ("github.com/ygor-acacio/Trojans-in-Financial-Code-generated-by-LLMs-Empirical-Evaluation-with-PAIR", SMALL, False, INK2)], after=8),
    para([("Support: ", SMALL, True, INK2), ("LARC – Laboratory of Computer Networks and Architecture, Escola Politécnica, USP.", SMALL, False, INK2)], after=0)]))

s = s.replace("</p:spTree>", "".join(shapes) + "</p:spTree>", 1)
slide_p.write_text(s, encoding="utf-8")
rels = rels.replace("</Relationships>", "".join(
    f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/poster_{f}"/>'
    for f, rid in media.items()) + "</Relationships>")
rels_p.write_text(rels, encoding="utf-8")
ct = ct_p.read_text(encoding="utf-8")
if 'Extension="png"' not in ct:
    ct = ct.replace('<Default Extension="jpeg"', '<Default Extension="png" ContentType="image/png"/><Default Extension="jpeg"', 1)
ct_p.write_text(ct, encoding="utf-8")
# core title
core = WORK / "docProps/core.xml"; c = core.read_text(encoding="utf-8")
c = re.sub(r"<dc:title>.*?</dc:title>", f"<dc:title>{escape(TITLE)}</dc:title>", c)
core.write_text(c, encoding="utf-8")
if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(WORK.rglob("*")):
        if f.is_file(): z.write(f, f.relative_to(WORK).as_posix())
print("ok", OUT, len(shapes), "shapes")
