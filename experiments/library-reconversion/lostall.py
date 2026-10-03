import subprocess,re,collections,sys
from pathlib import Path
sys.path.insert(0,'scripts')
from paperlib import LIBRARY_DIR,paper_files,read_paper
IGN={'Refer','caption','Uncaptioned','image','images','png','jpg','jpeg','svg','webp','fig','figures','pdf','extracted','html','arxiv','org','https','LABEL'}
def tok(s):
    s=re.sub(r"!\[[^\]]*\]\([^)]*\)"," ",s)          # image links
    s=re.sub(r'<img[^>]*>'," ",s)
    s=re.sub(r'\]\([^)]*\)',"]",s)                    # link targets and titles
    return [t for t in re.findall(r"[A-Za-z]{4,}",s) if t not in IGN]
rows=[]
for md in paper_files():
    meta,body=read_paper(md)
    if meta.get('source')!='html' or not meta.get('arxiv'): continue
    rel=md.resolve().relative_to(LIBRARY_DIR.parent)
    old=subprocess.run(['git','show',f'main:{rel}'],capture_output=True,text=True)
    if old.returncode: continue
    co,cn=collections.Counter(tok(old.stdout)),collections.Counter(tok(md.read_text()))
    lost=co-cn
    n=sum(lost.values()); tot=sum(co.values())
    if n>=60: rows.append((n,tot,str(md.relative_to(LIBRARY_DIR)),lost.most_common(10)))
rows.sort(reverse=True)
print(len(rows),'papers lost 60+ words')
for n,tot,p,top in rows[:45]:
    print(f'{n:6d} of {tot:6d} ({n/tot:5.1%}) | {p[:110]}')
    print('         ',' '.join(f'{w}:{c}' for w,c in top))
