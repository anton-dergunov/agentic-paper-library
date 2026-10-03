import subprocess,sys,re,difflib
from pathlib import Path
def words(s): return re.findall(r"[A-Za-z0-9]+", s)
for rel in sys.argv[1:]:
    old=subprocess.run(["git","show",f"main:library/{rel}"],capture_output=True,text=True).stdout
    new=Path("library",rel).read_text()
    newset=set()
    nw=words(new)
    # 8-gram shingles of the new text
    sh=set(tuple(nw[i:i+6]) for i in range(len(nw)-5))
    print("=====",rel)
    lost=[]
    for para in re.split(r"\n\s*\n",old):
        w=words(para)
        if len(w)<12: continue
        hits=sum(tuple(w[i:i+6]) in sh for i in range(len(w)-5))
        frac=hits/max(1,len(w)-5)
        if frac<0.3: lost.append((len(w),para))
    tot=sum(n for n,_ in lost)
    print(f"  paragraphs of main missing in new: {len(lost)}, {tot} words")
    for n,p in sorted(lost,key=lambda x:-x[0])[:6]:
        print(f"  [{n}w] "+" ".join(p.split())[:330])
