import sys,re,os
sys.path.insert(0,'scripts')
from urllib.parse import unquote
from paperlib import LIBRARY_DIR,read_paper,pdf_path_for
import pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
def norm(s):
    for a,b in (("ﬁ","fi"),("ﬂ","fl"),("ﬀ","ff"),("ﬃ","ffi"),("ﬄ","ffl")): s=s.replace(a,b)
    return re.sub(r"[^a-z0-9]+","",s.lower())
for rel in [l.strip() for l in open(sys.argv[1]) if l.strip()]:
    md=LIBRARY_DIR/rel; meta,body=read_paper(md); doc=pymupdf.open(pdf_path_for(md))
    pages=[norm(p.get_text()) for p in doc]
    heads=re.findall(r"^(#{1,6}) (.*?)(?: \(p\. (\d+)\))?$",body,flags=re.M)
    incode=False
    paged=[(h,int(p)) for _,h,p in heads if p]
    right=wrong=0; bad=[]
    for h,p in paged:
        t=norm(re.sub(r"\[[^\]]*\]\([^)]*\)|\$[^$]*\$|<[^>]+>|\\","",h))
        t=re.sub(r"^(appendix)?[0-9ivx]*","",t)[:40] if len(t)>12 else t
        if not t or p>len(pages): continue
        if t in pages[p-1]: right+=1
        elif any(t in pg for pg in pages): wrong+=1; bad.append((h[:40],p,[i+1 for i,pg in enumerate(pages) if t in pg][:3]))
    imgs=re.findall(r'!\[[^\]]*\]\(([^)\s]+)|<img[^>]*src="([^"]+)"',body)
    imgs=[a or b for a,b in imgs]
    local=[i for i in imgs if i.startswith("images/")]
    missing=[i for i in local if not (md.parent/unquote(i)).exists()]
    remote=[i for i in imgs if not i.startswith("images/")]
    pipe=len(re.findall(r"^\|[-:| ]+\|\s*$",body,flags=re.M)); htmlt=body.count("<table"); thead=body.count("<thead")
    empty=len(re.findall(r"^\|(?:\s*\|)+\s*\n\|[-:| ]+\|\s*$",body,flags=re.M))
    quotes=len(re.findall(r"(?:^|\n\n)> ",body)); eqs=len(re.findall(r"^\$\$",body,flags=re.M)); raw=body.count("raw text, not LaTeX")
    print(f"== {md.stem[:62]} [{meta.get('source')}, {len(doc)} pp]")
    print(f"   headings {len(heads)}, with page {len(paged)}; title found on stated page {right}, on another page {wrong} {bad[:3] if bad else ''}")
    print(f"   figures {len(local)} local ({len(missing)} missing files), {len(remote)} remote | tables: {pipe} pipe ({empty} empty header), {htmlt} html ({thead} with thead) | quotes {quotes} | display equations {eqs}, raw {raw}")
