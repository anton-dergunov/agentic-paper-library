import subprocess,sys,re,difflib,collections
from pathlib import Path
def tok(s): return re.findall(r"[A-Za-z]{3,}|\d+\.\d+", s)
for rel in sys.argv[1:]:
    old=subprocess.run(["git","show",f"main:library/{rel}"],capture_output=True,text=True).stdout
    new=Path("library",rel).read_text()
    print("=====",rel)
    co,cn=collections.Counter(tok(old)),collections.Counter(tok(new))
    lost=co-cn; gained=cn-co
    print("  lost tokens:",sum(lost.values()),"gained:",sum(gained.values()))
    print("  top lost:",lost.most_common(18))
    # removed lines (by difflib), largest first
    ol,nl=old.split("\n"),new.split("\n")
    sm=difflib.SequenceMatcher(None,ol,nl,autojunk=False)
    rem=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag in("delete","replace"):
            a=" ".join(ol[i1:i2]); b=" ".join(nl[j1:j2])
            d=len(a.split())-len(b.split())
            if d>40: rem.append((d,i1,a,b))
    for d,i1,a,b in sorted(rem,reverse=True)[:4]:
        print(f"  -- main line {i1+1}: {d} fewer words")
        print("     OLD:", a[:260].replace("\n"," "))
        print("     NEW:", b[:260].replace("\n"," "))
