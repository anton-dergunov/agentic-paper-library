"""Count the contexts of a TeX pattern in the formulas of every cached arXiv rendering.

    python3 scan.py '<regex>' [<characters after>]
"""
import gzip, re, html, sys, collections, glob, os
pat = re.compile(sys.argv[1])
ctx = int(sys.argv[2]) if len(sys.argv) > 2 else 60
seen = collections.Counter(); where = collections.defaultdict(set)
for f in glob.glob(os.path.expanduser("~/.cache/papers/arxiv/html/*/index.html.gz")):
    page = gzip.open(f).read().decode("utf-8", "replace")
    for m in re.finditer(r'alttext="([^"]*)"', page):
        tex = html.unescape(m.group(1))
        for p in pat.finditer(tex):
            s = tex[max(0, p.start()-10):p.end()+ctx]
            seen[s] += 1; where[s].add(f.split("/")[-2])
for s, n in seen.most_common(40):
    print(n, len(where[s]), repr(s))
print("distinct", len(seen), "papers", len(set().union(*where.values())) if where else 0)
