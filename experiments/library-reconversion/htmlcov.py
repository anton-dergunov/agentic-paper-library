import re,sys,os,gzip,json
from pathlib import Path
import lxml.html
sys.path.insert(0,'scripts')
from paperlib import LIBRARY_DIR,CACHE_DIR,read_paper
W=re.compile(r"[a-z]{3,}")
d={}
for l in open(sys.argv[2]):
    if l.strip():
        r=json.loads(l); d[r['paper']]=r
res=json.load(open(sys.argv[1]))
out=[]
for n,texty,pages,miss,rel in res:
    if n<3: continue
    md=LIBRARY_DIR/rel
    meta,body=read_paper(md)
    m=re.match(r'(\d{4}\.\d{4,5})(v\d+)?',d[rel]['message'])
    f=CACHE_DIR/'arxiv'/'html'/(m.group(1)+(m.group(2) or ''))/'index.html.gz'
    page=gzip.open(f,'rt',encoding='utf-8',errors='replace').read()
    tree=lxml.html.fromstring(page)
    art=tree.xpath('//*[contains(@class,"ltx_page_content")]')
    art=art[0] if art else tree
    for x in art.xpath('.//math|.//*[contains(@class,"ltx_listing_data")]|.//script|.//style|.//svg'):
        x.drop_tree()
    hw=W.findall(art.text_content().lower())
    mw=W.findall(body.lower()); grams=set(zip(mw,mw[1:],mw[2:]))
    g=list(zip(hw,hw[1:],hw[2:]))
    cov=sum(x in grams for x in g)/max(1,len(g))
    errs=page.count('ltx_ERROR')
    out.append((cov,len(hw),len(mw),errs,n,texty,rel))
out.sort()
print("html text covered by md | html words | md words | LaTeXML errors | missing pdf pages")
for cov,hw,mw,errs,n,texty,rel in out:
    flag=" <== converter?" if cov<0.9 else ""
    print(f"{cov:5.2f} | {hw:6d} | {mw:6d} | {errs:4d} | {n:3d}/{texty:3d} | {Path(rel).stem[:70]}{flag}")
