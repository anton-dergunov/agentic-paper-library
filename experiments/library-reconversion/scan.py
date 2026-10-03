import json,os,gzip,re,sys
from pathlib import Path
import lxml.html
sys.path.insert(0,'scripts')
from paperlib import CACHE_DIR
d={}
for l in open(sys.argv[1]):
    if l.strip():
        r=json.loads(l); d[r['paper']]=r
cache=CACHE_DIR/'arxiv'/'html'
hits=[]; missing=0; n=0
for paper,r in sorted(d.items()):
    if r['status'] not in('ok','partial'): continue
    m=re.match(r'(\d{4}\.\d{4,5})(v\d+)?',r['message'])
    if not m: continue
    f=cache/(m.group(1)+(m.group(2) or ''))/'index.html.gz'
    if not f.exists(): missing+=1; continue
    n+=1
    page=gzip.open(f,'rt',encoding='utf-8',errors='replace').read()
    if 'ltx_lstlisting' not in page: continue
    try: tree=lxml.html.fromstring(page)
    except Exception as e: print('parse error',paper,e); continue
    count=0; words=0
    for t in tree.xpath('//*[contains(concat(" ",@class," ")," ltx_tabular ")]'):
        ls=t.xpath('.//*[contains(concat(" ",@class," ")," ltx_lstlisting ")]')
        if not ls: continue
        if t.xpath('.//img|.//svg|.//object'): continue
        total=t.text_content()
        inside="".join(x.text_content() for x in ls if not any(a in ls for a in x.iterancestors()))
        # text outside the listings
        rest=total
        for x in ls:
            if any(a in ls for a in x.iterancestors()): continue
            rest=rest.replace(x.text_content(),'',1)
        if not rest.strip():
            # skip tables nested in another counted table
            count+=1; words+=len(re.sub(r'[A-Za-z0-9+/=]{200,}','',inside).split())
    if count: hits.append((words,count,paper))
print(f'scanned {n} cached pages, {missing} not in cache')
for w,c,p in sorted(hits,reverse=True): print(f'{c:3d} tables ~{w:6d} words | {p}')
print(len(hits),'papers')
