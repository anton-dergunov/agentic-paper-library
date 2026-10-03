"""Score each tool's markdown against the arXiv-HTML conversion of the same paper.

    LIBRARY=<library root> OUTPUTS=<outputs dir> python3 score.py [tool ...]

papers.tsv maps a short name to the paper's path under LIBRARY (the ground
truth: its arXiv-HTML markdown); a tool's output is OUTPUTS/<tool>/<short>.md
(or marker's <short>/<short>.md). times.tsv sits next to this script.
"""
import os, re, sys, glob, collections
from pathlib import Path
HERE = Path(__file__).parent
B = Path(os.environ.get('OUTPUTS', HERE))
LIBRARY = Path(os.environ.get('LIBRARY', 'library'))
GT = {s: str(LIBRARY / p) for s, p in (l.rstrip('\n').split('\t') for l in open(HERE / 'papers.tsv'))}
NUM = re.compile(r'(?<![\w.])\d+\.\d+(?![\w.])')

def body(t):
    return t.split('\n---\n', 1)[1] if t.startswith('---') else t
def table_text(t):
    lines = [l for l in t.split('\n') if l.lstrip().startswith('|')]
    html = re.findall(r'<table.*?</table>', t, flags=re.S)
    return '\n'.join(lines) + '\n' + '\n'.join(html)
def equations(t, inline=False):
    eqs = re.findall(r'\$\$(.+?)\$\$', t, flags=re.S)
    if inline:  # a tool may set a display equation as inline math, or several on one line
        rest = re.sub(r'\$\$.+?\$\$', ' ', t, flags=re.S)
        for line in rest.split('\n'):
            parts = re.findall(r'(?<!\$)\$([^$\n]+)\$(?!\$)', line)
            eqs += parts + ([' '.join(parts)] if len(parts) > 1 else [])
    return [e for e in eqs if len(tokens(e)) >= 6]
def tokens(e):
    e = re.sub(r'\\tag\{[^}]*\}|\\displaystyle|\\left|\\right|\\[,;!: ]|\\(?:big|Big|bigg|Bigg)[lr]?|\\qquad|\\quad|\\label\{[^}]*\}', ' ', e)
    e = re.sub(r'\\(?:mathrm|text|textrm|operatorname|mathbf|boldsymbol|bm|mathcal|mathbb|textbf|mathit)\b', ' ', e)
    return re.findall(r'\\[a-zA-Z]+|[a-zA-Z]|\d+(?:\.\d+)?|[=+\-*/^_<>|]', e)
def f1(a, b):
    ca, cb = collections.Counter(a), collections.Counter(b)
    inter = sum((ca & cb).values())
    return 2 * inter / (len(a) + len(b)) if inter else 0.0
def headings(t):
    out = []
    for l in t.split('\n'):
        m = re.match(r'#{1,6}\s+(.*)', l)
        if m:
            h = re.sub(r'\(p\. \d+\)$', '', m.group(1))
            h = re.sub(r'^(?:Appendix\s+)?[\dA-Z.\-]*\s+', '', h.strip()) if re.match(r'^(?:Appendix\s+)?(?:\d|[A-Z]\b|[IVX]+\b)', h) else h
            h = re.sub(r'[^a-z0-9 ]', '', h.lower()).strip()
            if h: out.append(h)
    return out
def prose_ngrams(t):
    t = re.sub(r'\$\$.*?\$\$|\$[^$\n]*\$|<[a-zA-Z/!][^>\n]*>|!\[[^\]]*\]\([^)]*\)|\[([^\]]*)\]\([^)]*\)', r' \1 ', t, flags=re.S)
    lines = [l for l in t.split('\n') if not l.lstrip().startswith(('|', '#', '>'))]
    w = re.findall(r'[a-z]{2,}', ' '.join(lines).lower())
    return {tuple(w[i:i + 5]) for i in range(len(w) - 4)}

def tool_output(tool, s):
    for pat in (f'{tool}/{s}.md', f'{tool}/{s}/{s}.md', f'{tool}/{s}/*/{s}.md'):
        hits = glob.glob(str(B / pat))
        if hits: return re.sub(r'(?<=\d) \. (?=\d)', '.', Path(hits[0]).read_text(errors='replace'))
    return None

tools = sys.argv[1:] or ['textlayer', 'docling', 'docling-formula', 'marker', 'mineru']
times = collections.defaultdict(dict)
for l in open(HERE / 'times.tsv'):
    p = l.split('\t')
    if len(p) == 3: times[p[0]][p[1]] = p[2].split('s')[0]
rows = collections.defaultdict(list)
for s, md in GT.items():
    gt = body(Path(md).read_text())
    if '\nsource: html' not in Path(md).read_text()[:2000]: continue
    gnums = collections.Counter(NUM.findall(table_text(gt)))
    geqs = [tokens(e) for e in equations(gt)]
    gheads = headings(gt)
    gheads = gheads[:next((i for i, h in enumerate(gheads) if h.startswith('references')), len(gheads))]
    ggrams = prose_ngrams(gt.split('\n## References')[0])
    for tool in tools:
        t = tool_output(tool, s)
        if t is None: continue
        tnums = collections.Counter(NUM.findall(table_text(t)))
        anynums = collections.Counter(NUM.findall(t))
        teqs = [tokens(e) for e in equations(t, inline=True)]
        eq_scores = [max((f1(g, e) for e in teqs), default=0.0) for g in geqs]
        theads = set(headings(t))
        rows[tool].append(dict(
            paper=s,
            table_nums=sum((gnums & tnums).values()) / max(1, sum(gnums.values())),
            any_nums=sum((gnums & anynums).values()) / max(1, sum(gnums.values())),
            eq_n=len(geqs), eq_found=len(teqs),
            eq_good=sum(x >= 0.85 for x in eq_scores) / max(1, len(geqs)) if geqs else None,
            eq_mean=sum(eq_scores) / len(eq_scores) if geqs else None,
            heads=sum(h in theads for h in gheads) / max(1, len(gheads)),
            prose=len(ggrams & prose_ngrams(t)) / max(1, len(ggrams)),
            secs=times[tool].get(s, ''),
        ))
def fmt(x): return '  -  ' if x is None else f'{x:5.2f}'
for tool in tools:
    if not rows[tool]: continue
    print(f'\n== {tool}')
    print(f"{'paper':10s} tbl-nums any-nums  eqs(gt/found) eq>=.85 eq-mean  heads prose  secs")
    for r in rows[tool]:
        print(f"{r['paper']:10s} {fmt(r['table_nums'])}    {fmt(r['any_nums'])}   {r['eq_n']:3d}/{r['eq_found']:<3d}      {fmt(r['eq_good'])}   {fmt(r['eq_mean'])}  {fmt(r['heads'])} {fmt(r['prose'])}  {r['secs']}")
    n = len(rows[tool]); avg = lambda k: sum(r[k] for r in rows[tool] if r[k] is not None) / max(1, sum(r[k] is not None for r in rows[tool]))
    print(f"{'MEAN':10s} {fmt(avg('table_nums'))}    {fmt(avg('any_nums'))}                  {fmt(avg('eq_good'))}   {fmt(avg('eq_mean'))}  {fmt(avg('heads'))} {fmt(avg('prose'))}")
