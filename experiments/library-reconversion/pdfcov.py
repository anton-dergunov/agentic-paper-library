import re,sys,os,json
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0,'scripts')
from paperlib import LIBRARY_DIR,paper_files,read_paper,pdf_path_for
import pymupdf
W=re.compile(r"[a-zа-я]{3,}")
def norm(s):
    for a,b in (("ﬁ","fi"),("ﬂ","fl"),("ﬀ","ff"),("ﬃ","ffi"),("ﬄ","ffl")): s=s.replace(a,b)
    return W.findall(re.sub(r"-\n","",s).lower())
def one(md):
    meta,body=read_paper(md)
    if meta.get('source')!='pdf-text': return None
    pymupdf.TOOLS.mupdf_display_errors(False)
    mw=norm(body); grams=set(zip(mw,mw[1:],mw[2:]))
    doc=pymupdf.open(pdf_path_for(md))
    covs=[]
    for i,p in enumerate(doc):
        w=norm(p.get_text())
        if len(w)<120: continue
        g=list(zip(w,w[1:],w[2:])); covs.append((i+1,round(sum(x in grams for x in g)/len(g),2)))
    low=[(p,c) for p,c in covs if c<0.6]
    return (len(low),len(covs),low,str(md.relative_to(LIBRARY_DIR)))
if __name__=='__main__':
    with ProcessPoolExecutor(6) as ex: res=[r for r in ex.map(one,paper_files(),chunksize=10) if r]
    res.sort(key=lambda r:-r[0])
    print(len(res),'pdf papers;',sum(1 for r in res if r[0]),'with a page under 60% covered')
    for n,t,low,p in res:
        if n: print(f"{n:3d}/{t:3d} | {p[:95]} | {str(low[:9])[:150]}")
