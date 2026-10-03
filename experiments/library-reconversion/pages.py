import re,sys,os
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0,'scripts')
from paperlib import LIBRARY_DIR,paper_files,read_paper,pdf_path_for
import pymupdf
W=re.compile(r"[a-z]{3,}")
def norm(s):
    s=s.replace("ﬁ","fi").replace("ﬂ","fl").replace("ﬀ","ff").replace("ﬃ","ffi").replace("ﬄ","ffl")
    s=re.sub(r"-\n","",s)
    return W.findall(s.lower())
def one(md):
    meta,body=read_paper(md)
    if meta.get('source')!='html': return None
    pymupdf.TOOLS.mupdf_display_errors(False)
    mw=norm(body)
    grams=set(zip(mw,mw[1:],mw[2:]))
    try: doc=pymupdf.open(pdf_path_for(md))
    except Exception as e: return None
    miss=[]; texty=0
    for i,p in enumerate(doc):
        w=norm(p.get_text())
        if len(w)<120: continue
        texty+=1
        g=list(zip(w,w[1:],w[2:]))
        cov=sum(x in grams for x in g)/len(g)
        if cov<0.25: miss.append(i+1)
    return (len(miss),texty,len(doc),miss,str(md.relative_to(LIBRARY_DIR)))
if __name__=='__main__':
    with ProcessPoolExecutor(6) as ex: res=[r for r in ex.map(one,paper_files(),chunksize=20) if r]
    res.sort(key=lambda r:(-r[0]/max(1,r[1]),r[4]))
    def ranges(ps):
        out=[];s=e=None
        for p in ps:
            if s is None: s=e=p
            elif p==e+1: e=p
            else: out.append((s,e)); s=e=p
        if s is not None: out.append((s,e))
        return ",".join(f"{a}" if a==b else f"{a}-{b}" for a,b in out)
    import json
    json.dump(res,open(sys.argv[1],'w'))
    print(len(res),'papers;',sum(1 for r in res if r[0]>=3),'with 3+ uncovered pages;',sum(1 for r in res if r[0]>=1),'with 1+')
    for n,texty,pages,miss,p in res:
        if n>=3: print(f"{n:3d} of {texty:3d} text pages missing (pp. {ranges(miss)[:60]}) | {p[:120]}")
