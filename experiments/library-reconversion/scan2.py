import json,os,gzip,re,sys,importlib.util
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0,'scripts')
from paperlib import CACHE_DIR
spec=importlib.util.spec_from_file_location("h","scripts/html-to-markdown.py"); conv=importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
start=re.compile(r'<span\b[^>]*\bclass="[^"]*\bltx_tabular\b[^"]*"[^>]*>')
def old_layout(opening,segment):
    rows=len(re.findall(r'class="ltx_tr\b',segment)); cells=len(re.findall(r'class="ltx_td\b',segment))
    return "ltx_markedasmath" in opening or rows<2 or cells<2*rows
def one(args):
    paper,f=args
    page=gzip.open(f,'rt',encoding='utf-8',errors='replace').read()
    if 'ltx_colspan_' not in page: return None
    article=conv.convert_listings(conv.extract_article(page))
    pos=0; n=0; ex=""
    while True:
        m=start.search(article,pos)
        end=conv.balanced_end(article,m.start(),"span") if m else None
        if end is None: break
        seg=article[m.start():end]
        if old_layout(m.group(0),seg) and not conv.is_layout_tabular(m.group(0),seg):
            n+=1; ex=ex or " ".join(re.sub(r"<math.*?</math>","M",seg,flags=re.S).replace("<"," <").split())
            ex=" ".join(re.sub(r"<[^>]+>"," ",ex).split())[:110]
        pos=end
    return (n,paper,ex) if n else None
if __name__=='__main__':
    d={}
    for l in open(sys.argv[2]):
        if l.strip():
            r=json.loads(l); d[r['paper']]=r
    jobs=[]
    for paper,r in sorted(d.items()):
        if r['status'] not in('ok','partial'): continue
        m=re.match(r'(\d{4}\.\d{4,5})(v\d+)?',r['message'])
        jobs.append((paper,CACHE_DIR/'arxiv'/'html'/(m.group(1)+(m.group(2) or ''))/'index.html.gz'))
    with ProcessPoolExecutor(6) as ex: res=[r for r in ex.map(one,jobs,chunksize=20) if r]
    for n,p,e in res: print(f"{n:2d} | {p}\n       {e}")
    print(len(res),"papers")
    open(sys.argv[1],'w').write("\n".join(p for _,p,_ in res)+"\n")
