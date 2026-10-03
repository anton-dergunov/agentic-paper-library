"""Write catalog/conversion-issues.yaml entries for the papers incomplete.py kept.

    python3 catalog_entries.py incomplete.json catalog-entries.yaml

Inline in the session; saved here unchanged."""
import json,sys,re,textwrap,statistics
sys.path.insert(0,'scripts')
from paperlib import LIBRARY_DIR,read_paper
from pathlib import Path
rows=json.load(open(sys.argv[1]))
def ranges(ps):
    out=[];s=e=None
    for p in ps:
        if s is None: s=e=p
        elif p==e+1: e=p
        else: out.append((s,e)); s=e=p
    if s is not None: out.append((s,e))
    return out
out=[]
existing=open('catalog/conversion-issues.yaml').read()
for k,texty,keep,main,refp,last,rel in sorted(rows,key=lambda r:Path(r[6]).stem.lower()):
    stem=Path(rel).stem
    meta,body=read_paper(LIBRARY_DIR/rel)
    pages=[int(x) for x in re.findall(r"^#+ .*\(p\. (\d+)\)$",body,flags=re.M)]
    lastpage=max(pages) if pages else 0
    lasth=[h for h in re.findall(r"^#+ (.*?)(?: \(p\. \d+\))?$",body,flags=re.M) if not re.match(r"References|Bibliography",h)][-1]
    rs=ranges(keep)
    span=", ".join(f"{a}" if a==b else f"{a}–{b}" for a,b in rs) if len(rs)<=4 else f"{keep[0]}–{keep[-1]}, with gaps"
    if lastpage<statistics.median(keep):
        problem=(f"Truncated: arXiv's HTML lacks the text of {k} of the PDF's {texty} text pages (pp. {span}); "
                 f"the markdown's last section is '{lasth[:60]}' (p. {lastpage}).")
    else:
        problem=(f"Incomplete: arXiv's HTML lacks the text of {k} of the PDF's {texty} text pages "
                 f"(pp. {span}), appendix material such as prompts, examples or per-dataset tables.")
    assert stem not in existing, stem
    wrapped=textwrap.wrap(problem,width=100,initial_indent="  problem: ",subsequent_indent="    ")
    out.append(f"- paper: {stem}\n"+"\n".join(wrapped)+"\n  found: '2026-10-02'\n")
open(sys.argv[2],'w').write("".join(out))
print("".join(out))
