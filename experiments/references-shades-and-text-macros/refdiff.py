"""Print each in-paper reference whose number differs between two versions of a paper's markdown.

    python3 refdiff.py <before.md> <after.md>
"""
import sys, re, difflib
from pathlib import Path
link = re.compile(r'\[([^\]\n]*)\]\((#[^ )]+)')
a = Path(sys.argv[1]).read_text(); b = Path(sys.argv[2]).read_text()
la, lb = a.split("\n"), b.split("\n")
for x, y in zip(la, lb):
    if x == y: continue
    for ma, mb in zip(link.finditer(x), link.finditer(y)):
        if ma.group(1) != mb.group(1):
            print(f"  …{x[max(0,ma.start()-70):ma.start()]!s}[{ma.group(1)}→{mb.group(1)}]({ma.group(2)}) {x[ma.end():ma.end()+30]}")
