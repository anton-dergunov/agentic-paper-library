import re, sys
from pathlib import Path
def stats(t):
    lines = t.split('\n')
    flat = sum(1 for l in lines if not l.startswith(('|','<','$$','!')) and len(re.findall(r'(?<![\w.])\d+\.\d+(?![\w.])', l)) >= 25)
    return dict(
        words=len(t.split()),
        imgs=len(re.findall(r'images/[^)"\s]+', t)),
        forest=t.count('{forest}'),
        pt=len(re.findall(r'(?:^|[ ,;=])\d+\.?\d*pt[A-Za-z\\]', t)),
        flat=flat,
        emptyhdr=len(re.findall(r'^\|(?:\s*\|)+\s*$', t, re.M)),
        thead=t.count('<thead>'),
        quotes=len(re.findall(r'^> ', t, re.M)),
        remote=len(re.findall(r'\]\((?:https://arxiv\.org/html/)?\d{4}\.\d{4,5}v\d+/', t)),
    )
a, b = Path(sys.argv[1]), Path(sys.argv[2])
keys = None
for d in sorted(b.iterdir()):
    sa, sb = stats((a/d.name/'body.md').read_text()), stats((d/'body.md').read_text())
    if keys is None:
        keys = list(sa); print(f"{'paper':32s}" + ''.join(f'{k:>16s}' for k in keys))
    print(f'{d.name[:32]:32s}' + ''.join(f'{str(sa[k])+"→"+str(sb[k]):>16s}' for k in keys))
