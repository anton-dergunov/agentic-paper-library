import re,sys,os
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0,'scripts')
from paperlib import LIBRARY_DIR,paper_files,read_paper,pdf_path_for
import pymupdf
W=re.compile(r"[A-Za-z]{4,}")
def one(md):
    meta,body=read_paper(md)
    if meta.get('source')!='html': return None
    pdf=pdf_path_for(md)
    try:
        doc=pymupdf.open(pdf)
        pw=sum(len(W.findall(p.get_text())) for p in doc); pages=len(doc)
    except Exception as e:
        return ('err',str(md.relative_to(LIBRARY_DIR)),str(e)[:80])
    b=re.sub(r"!\[[^\]]*\]\([^)]*\)|\]\([^)]*\)|<[^>]+>"," ",body)
    mw=len(W.findall(b))
    return (mw/pw if pw else 9, mw, pw, pages, str(md.relative_to(LIBRARY_DIR)))
if __name__=='__main__':
    pymupdf.TOOLS.mupdf_display_errors(False)
    with ProcessPoolExecutor(6) as ex: res=[r for r in ex.map(one,paper_files(),chunksize=20) if r]
    errs=[r for r in res if r[0]=='err']; res=sorted(r for r in res if r[0]!='err')
    print(len(res),'html papers;',len(errs),'pdf errors'); [print('  ERR',e) for e in errs[:10]]
    import statistics
    print('median ratio',round(statistics.median(r[0] for r in res),2))
    for ratio,mw,pw,pages,p in res:
        if ratio<0.62: print(f'{ratio:5.2f}  md {mw:6d} / pdf {pw:6d} words, {pages:3d} pp | {p}')
