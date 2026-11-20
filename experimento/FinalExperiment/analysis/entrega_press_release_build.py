"""Fill the PCS3860 press-release template (single page) with English content."""
import re, shutil, sys, zipfile
from pathlib import Path
from xml.sax.saxutils import escape

TPL, OUT, WORK = map(Path, sys.argv[1:4])
if WORK.exists(): shutil.rmtree(WORK)
zipfile.ZipFile(TPL).extractall(WORK)
dp = WORK / "word/document.xml"; d = dp.read_text(encoding="utf-8")
PURPLE, INK, INK2 = "6600FF", "1E1E1E", "4A4A4A"

def run(t, sz=10, b=False, i=False, color=INK):
    return ('<w:r><w:rPr><w:rFonts w:ascii="Tahoma" w:hAnsi="Tahoma" w:cs="Tahoma"/>'
            f'{"<w:b/>" if b else ""}{"<w:i/>" if i else ""}<w:color w:val="{color}"/>'
            f'<w:sz w:val="{int(sz*2)}"/><w:szCs w:val="{int(sz*2)}"/><w:lang w:val="en-US"/></w:rPr>'
            f'<w:t xml:space="preserve">{escape(t)}</w:t></w:r>')

def P(runs, after=6, jc="both", before=0, line=240):
    return (f'<w:p><w:pPr><w:spacing w:before="{before*20}" w:after="{after*20}" w:line="{line}" w:lineRule="auto"/>'
            f'<w:jc w:val="{jc}"/></w:pPr>{"".join(runs)}</w:p>')

TITLE = "Multi-Agent Defense Against Trojan Insertion in LLM-Generated Code for Financial Applications"
tema = [P([run(TITLE, 10, color=PURPLE)], after=0, jc="left")]

BS = 10
body = [
    P([run("AI reviewer catches 57 of 58 hidden trojans in AI-written financial code", 12, b=True, color=PURPLE)], after=3, jc="left"),
    P([run("Final-year Computer Engineering project at Escola Politécnica (USP) also shows that an automatic label "
           "can hide which defense actually works best", 10, i=True, color=INK2)], after=8, jc="left"),
    P([run("São Paulo, November 2026 – ", BS, b=True),
       run("Programming assistants based on large language models (LLMs) now write a growing share of software, including "
           "code that computes interest, loan payments and taxes. A final-year project at the Department of Computer "
           "Engineering and Digital Systems (PCS) of Escola Politécnica da USP studied a subtle risk in that code: "
           "logic trojans, small numerical deviations that activate only for a rare input and pass ordinary tests.", BS)]),
    P([run("Ygor Acacio Maria, advised by Prof. Victor Takashi Hayashi and Prof. Marcos Antonio Simplicio Junior, built an "
           "environment in which an automated attacker, inspired by the PAIR method, repeatedly asked two LLMs (DeepSeek-V3 "
           "and Qwen2.5-72B) to write financial functions with hidden deviations. Three specialized AI agents inspected the "
           "600 resulting code samples for dangerous behaviors, trojan patterns and policy violations, and their verdicts "
           "were combined in ten different ways, from simple voting to an AI “orchestrator” that decides which agents to consult.", BS)]),
    P([run("Measured against an automatic rule-based label, the defenses seemed to face a hard trade-off: catching almost "
           "every trojan meant blocking most legitimate code. A blind review by three human evaluators changed that picture. "
           "They found a trojan in 96.7% of the samples, while the automatic label flagged only 70%. Against the human "
           "judgment, the agent specialized in trojan patterns, alone or combined with others, missed only one trojan in 58.", BS)]),
    P([run("More elaborate arrangements did not help. A weighted vote turned out to be equivalent to a simple majority, a "
           "step-by-step cascade never used its early-blocking rule, and the orchestrator lost detections whenever it skipped "
           "the specialist. In all three cases the cause is the same: the agents report confidence values that do not reflect "
           "how sure they really are.", BS)]),
    P([run("“The most surprising result was not about the defense, but about how we measure it,” says Ygor Acacio Maria. "
           "“A label that looked reasonable was enough to make the best detector look like the worst.”", BS, i=True)]),
    P([run("For organizations that use AI coding assistants in finance, the results point to three practices: prioritize "
           "reviewers specialized in the specific threat, send flagged code to human review instead of discarding it, and "
           "validate automatic labels with people before trusting a security metric. Partial results were presented at the "
           "AISec Dev workshop of the Brazilian Software Congress (CBSoft 2026), and the code and data are publicly available.", BS)], after=10),
    P([run("Key figures: ", 8.5, b=True, color=PURPLE),
       run("600 code samples · 5 financial tasks · 3 levels of code complexity · 2 generator LLMs · "
           "10 ways of combining the defense agents · 3 blind human evaluators.", 8.5, color=INK2)], after=2, jc="left"),
    P([run("About the project: ", 8.5, b=True, color=PURPLE),
       run("Final-year project (PCS3860), Computer Engineering, Escola Politécnica da Universidade de São Paulo, 2026, "
           "with support from LARC – Laboratory of Computer Networks and Architecture.", 8.5, color=INK2)], after=2, jc="left"),
    P([run("Contact: ", 8.5, b=True, color=PURPLE),
       run("ygor.acacio@usp.br · github.com/ygor-acacio/Trojans-in-Financial-Code-generated-by-LLMs-Empirical-Evaluation-with-PAIR",
           8.5, color=INK2)], after=0, jc="left"),
]
members = [P([run("Team member: ", 10, color=PURPLE), run("Ygor Acacio Maria", 10)], after=0, jc="left")]
advisors = [P([run("Advisor: ", 10, color=PURPLE), run("Prof. Dr. Victor Takashi Hayashi", 10)], after=0, jc="left"),
            P([run("Co-advisor: ", 10, color=PURPLE), run("Prof. Dr. Marcos Antonio Simplicio Junior", 10)], after=0, jc="left")]

# text boxes in document order: 0-1 header, 2-3 theme, 4-5 content, 6-7 members, 8-9 advisors (Choice + VML Fallback)
plan = {2: tema, 3: tema, 4: body, 5: body, 6: members, 7: members, 8: advisors, 9: advisors}
k = [-1]
def repl(m):
    k[0] += 1
    return f"<w:txbxContent>{''.join(plan[k[0]])}</w:txbxContent>" if k[0] in plan else m.group(0)
d = re.sub(r"<w:txbxContent>.*?</w:txbxContent>", repl, d, flags=re.S)
assert k[0] == 9, k

# widen the footer boxes (DrawingML extents and VML widths)
for old, new in [("765810", "6400000"), ("1581150", "6400000")]:
    n = d.count(f'cx="{old}"'); assert n == 2, (old, n)
    d = d.replace(f'cx="{old}"', f'cx="{new}"')
for old in ("width:60.3pt", "width:124.5pt"):
    assert d.count(old) == 1, old
    d = d.replace(old, "width:504pt")
d = d.replace("height:13.85pt", "height:14pt")
dp.write_text(d, encoding="utf-8")

for f in ["docProps/core.xml"]:
    p = WORK / f; c = p.read_text(encoding="utf-8")
    c = re.sub(r"<dc:title>.*?</dc:title>|<dc:title/>", f"<dc:title>{escape(TITLE)} – Press Release</dc:title>", c)
    p.write_text(c, encoding="utf-8")
if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(WORK.rglob("*")):
        if f.is_file(): z.write(f, f.relative_to(WORK).as_posix())
words = len(re.findall(r"\w+", " ".join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', "".join(body)))))
print("ok", OUT, "body words:", words)
