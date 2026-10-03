"""Run a candidate page-map.py over copies of every paper and diff the page numbers.

    python3 pagemap_regress.py <scripts dir>

<scripts dir> holds the candidate page-map.py and paperlib.py (for the paper list
and each paper's PDF path). The library's own markdown is the baseline; nothing in
it is written. Prints gained / lost / moved page numbers and how many papers used
the PDF outline.
"""
import re, shutil, subprocess, sys, tempfile
from pathlib import Path
SCRIPTS = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(SCRIPTS))
from paperlib import paper_files, pdf_path_for, read_paper
H = re.compile(r"^(#{2,6} .+?)(?: \(p\. (\d+)\))?$")
def heads(t):
    out=[]; fence=False
    for l in t.split("\n"):
        if l.startswith("```"): fence = not fence
        if fence: continue
        m=H.match(l)
        if m: out.append((m.group(1), m.group(2)))
    return out
tot = dict(gained=0, lost=0, changed=0, papers_changed=0, outline_papers=0)
details=[]
for md in paper_files():
    pdf = pdf_path_for(md)
    if not pdf.exists(): continue
    with tempfile.TemporaryDirectory() as d:
        c = Path(d)/"p.md"; shutil.copy(md, c)
        r = subprocess.run([sys.executable, str(SCRIPTS / "page-map.py"), str(pdf), str(c)], capture_output=True, text=True)
        if r.returncode: print("ERR", md.name, r.stderr[-300:]); continue
        if "PDF outline" in r.stdout: tot["outline_papers"]+=1
        old, new = heads(md.read_text()), heads(c.read_text())
    if [h for h,_ in old] != [h for h,_ in new]: print("HEADING TEXT MISMATCH", md.name); continue
    g=l=ch=0
    for (h,a),(_,b) in zip(old,new):
        if a is None and b: g+=1
        elif a and b is None: l+=1; details.append(f"LOST  {md.stem[:50]} | {h[:60]} (was p.{a})")
        elif a and b and a!=b: ch+=1; details.append(f"MOVED {md.stem[:50]} | {h[:60]} p.{a} -> p.{b}")
    if g or l or ch: tot["papers_changed"]+=1
    tot["gained"]+=g; tot["lost"]+=l; tot["changed"]+=ch
print(tot)
print("\n".join(details[:80])); print(len(details), "lost/moved in total")
