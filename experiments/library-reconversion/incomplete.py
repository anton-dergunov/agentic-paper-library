import re,sys,os,json
sys.path.insert(0,'scripts')
from paperlib import LIBRARY_DIR,read_paper,pdf_path_for
from pathlib import Path
import pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
res=json.load(open(sys.argv[1]))
def ranges(ps):
    out=[];s=e=None
    for p in ps:
        if s is None: s=e=p
        elif p==e+1: e=p
        else: out.append((s,e)); s=e=p
    if s is not None: out.append((s,e))
    return ", ".join(f"{a}" if a==b else f"{a}–{b}" for a,b in out)
rows=[]
for n,texty,pages,miss,rel in res:
    if n<3: continue
    md=LIBRARY_DIR/rel; meta,body=read_paper(md); doc=pymupdf.open(pdf_path_for(md))
    keep=[]
    for p in miss:
        t=doc[p-1].get_text()
        years=len(re.findall(r"\b(?:19|20)\d\d[a-z]?\b",t))
        if years>=12 and re.search(r"arXiv|Proceedings|Conference|Journal|In [A-Z]",t): continue  # a reference page
        keep.append(p)
    if len(keep)>=8 or (len(keep)>=4 and len(keep)>=0.25*texty):
        ref=re.search(r"^#+ (?:References|Bibliography).*?\(p\. (\d+)\)",body,flags=re.M)
        refp=int(ref.group(1)) if ref else None
        main=[p for p in keep if refp and p<refp]
        heads=[h for h in re.findall(r"^#+ (.*)$",body,flags=re.M) if not re.match(r"References|Bibliography",h)]
        rows.append((len(keep),texty,keep,main,refp,heads[-1] if heads else "",rel))
rows.sort(key=lambda r:-r[0]/r[1])
json.dump(rows,open(sys.argv[2],'w'))
for k,texty,keep,main,refp,last,rel in rows:
    print(f"{k:3d}/{texty:3d} | main-text pages missing: {len(main):3d} | refs p.{refp} | pp. {ranges(keep)[:70]} | {Path(rel).stem[:60]}")
print(len(rows))
