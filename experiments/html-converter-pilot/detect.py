"""List library papers that the converter fixes would change, with the reasons.

    python3 detect.py [--counts]      # prints "<reasons>\t<path>" per affected paper
"""
import sys, re, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent))
from urllib.parse import unquote
from paperlib import paper_files, read_paper
from classify import classify
CHECKS = {
    'flat-table': lambda t: any(not l.startswith(('|', '<', '$$', '!')) and len(re.findall(r'(?<![\w.])\d+\.\d+(?![\w.])', l)) >= 25
                                for l in t.split('\n')),
    'forest': lambda t: '{forest}' in t,
    'pt-residue': lambda t: re.search(r'(?:^|[ ,;={(])\d+\.?\d*pt[A-Za-z\\]', t, re.M),
    'macro': lambda t: re.search(r'operatorname\{math(?:section|paragraph)\}|montrait|\\Cref[a-z]', t),
    'figure-link': lambda t: re.search(r'\]\((?:https://arxiv\.org/html/)?\d{4}\.\d{4,5}v\d+/|src="\d{4}\.\d{4,5}v\d+/', t),
    'empty-header': lambda t: re.search(r'^\|(?:\s*\|)+\s*\n\|[-:| ]+\|\s*$', t, re.M),
    'no-thead': lambda t: re.search(r'<table>\s*<tbody>', t),
}
def svg_kinds(md, t):
    kinds = set()
    for link in re.findall(r'images/([^)"\s]+\.svg)', t):
        f = md.parent / 'images' / unquote(link)
        if f.exists():
            s = f.read_text(errors='replace')
            if 'foreignobject' in s.lower():
                k = classify(s[s.find('<svg'):])
                if k != 'image': kinds.add('box' if k != 'badge' else 'badge')
    return kinds
out = []
counts = collections.Counter()
for md in paper_files():
    meta, body = read_paper(md)
    if meta.get('source') != 'html' or not meta.get('arxiv'):
        continue
    reasons = [k for k, f in CHECKS.items() if f(body)] + sorted(svg_kinds(md, body))
    if reasons:
        counts.update(reasons)
        out.append(f"{','.join(reasons)}\t{md}")
if '--counts' in sys.argv:
    print(len(out), 'papers'); print(counts.most_common())
else:
    print('\n'.join(out))
