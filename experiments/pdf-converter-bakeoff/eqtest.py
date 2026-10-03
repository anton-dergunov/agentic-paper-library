"""Compare render resolution and padding for the equation crops handed to surya.

    LIBRARY=<library root> python3 eqtest.py <pdf-equations.py> <pdf-dir>

Writes eq-<dpi>-<pad>.py variants of pdf-equations.py next to this script, runs
each on Larimar's and Meta-Learning's equation boxes (<name>-boxes.json, from
boxes.py), and scores Larimar's against its arXiv-HTML equations.
"""
import json, subprocess, time, sys, os
from pathlib import Path
B = Path(__file__).parent
src = Path(sys.argv[1]).read_text()
PDFS = Path(sys.argv[2])
py = os.environ.get('PAPERS_MARKER_PYTHON', os.path.expanduser('~/.cache/papers/venvs/marker/bin/python'))
ns = {'__file__': str(B / 'score.py')}
exec((B / 'score.py').read_text().split("tools = sys.argv")[0], ns)
gt = ns['body'](open(ns['GT']['larimar']).read())
geqs = [ns['tokens'](e) for e in ns['equations'](gt)]
for dpi, pad in ((192, 0), (300, 3), (300, 8)):
    variant = src.replace('SCALE = 192 / 72', f'SCALE = {dpi} / 72').replace(
        '            x0, y0, x1, y1 = (v * SCALE for v in (x0, y0, x1, y1))',
        f'            x0, y0, x1, y1 = x0 - {pad}, y0 - {pad}, x1 + {pad}, y1 + {pad}\n            x0, y0, x1, y1 = (v * SCALE for v in (x0, y0, x1, y1))')
    assert variant != src or (dpi, pad) == (192, 0)
    f = B / f'eq-{dpi}-{pad}.py'; f.write_text(variant)
    for s in ('larimar', 'metalearn'):
        t = time.time()
        r = subprocess.run([py, str(f), str(PDFS / f'{s}.pdf')], stdin=open(B / f'{s}-boxes.json'), capture_output=True, text=True)
        out = json.loads(r.stdout) if r.returncode == 0 else []
        if s == 'larimar':
            teqs = [ns['tokens'](e) for e in out if e]
            sc = [max((ns['f1'](g, e) for e in teqs), default=0) for g in geqs]
            print(f'dpi {dpi} pad {pad}: larimar {time.time()-t:.0f}s decoded {len(teqs)}/{len(out)}  >=.85: {sum(x >= .85 for x in sc)/len(sc):.2f}  mean {sum(sc)/len(sc):.2f}', flush=True)
        else:
            print(f'   metalearn {time.time()-t:.0f}s', out, flush=True)
        if r.returncode: print(r.stderr[-300:])
