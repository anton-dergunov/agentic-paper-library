"""Compare PDF conversions with and without --inline-math against the arXiv-HTML copy.

    LIBRARY=<library root> OUTPUTS=<folder with final/ and inline/> python3 score_inline.py memlayers larimar dpo

Uses the bake-off's scorer (../pdf-converter-bakeoff/score.py) for tokens, F1,
prose n-grams and the ground-truth paths.
"""
import collections
import os
import re
import sys
from pathlib import Path

SCORE = Path(__file__).resolve().parent.parent / 'pdf-converter-bakeoff' / 'score.py'
B = Path(os.environ.get('OUTPUTS', Path(__file__).parent))
ns = {'__file__': str(SCORE)}
exec(SCORE.read_text().split("tools = sys.argv")[0], ns)
tokens, f1, body, GT, prose_ngrams = ns['tokens'], ns['f1'], ns['body'], ns['GT'], ns['prose_ngrams']
NUM = re.compile(r'(?<![\w.])\d+\.\d+(?![\w.])')


def prose(t):
    t = re.sub(r'\$\$.+?\$\$', ' ', t, flags=re.S)
    return '\n'.join(l for l in t.split('\n') if not l.lstrip().startswith(('|', '#', '>', '<', '!')))


def inline(t, least=3):
    out = [tokens(e) for e in re.findall(r'(?<!\$)\$([^$\n]+)\$(?!\$)', prose(t))]
    return [e for e in out if len(e) >= least]


def numbers(t):
    return collections.Counter(NUM.findall(re.sub(r'\$[^$\n]*\$', ' ', prose(t))))


print(f"{'paper':10s} {'version':7s} inline-gt  found  matched>=.85  mean   prose  prose-numbers")
for s in sys.argv[1:]:
    gt = body(Path(GT[s]).read_text()).split('\n## References')[0]
    g_inline, g_grams, g_nums = inline(gt), prose_ngrams(gt), numbers(gt)
    for version in ('final', 'inline'):
        f = B / version / f'{s}.md'
        if not f.exists():
            continue
        t = re.sub(r'(?<=\d) \. (?=\d)', '.', f.read_text())
        t_inline = inline(t, least=1)
        scores = [max((f1(g, e) for e in t_inline), default=0.0) for g in g_inline]
        matched = sum(x >= 0.85 for x in scores) / max(1, len(scores))
        mean = sum(scores) / max(1, len(scores))
        t_nums = numbers(t)
        print(f"{s:10s} {version:7s} {len(g_inline):6d}  {len(t_inline):6d}     {matched:5.2f}      {mean:5.2f}   "
              f"{len(g_grams & prose_ngrams(t)) / max(1, len(g_grams)):5.2f}   "
              f"{sum((g_nums & t_nums).values()) / max(1, sum(g_nums.values())):5.2f}")
