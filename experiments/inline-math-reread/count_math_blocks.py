"""Count the text blocks with a mathematics font in every PDF-only paper: the work --inline-math adds.

    python3 count_math_blocks.py      # run from the library's root

As run inline in the session on 2 Oct 2026. A block counts if it has 40 or more
characters and any span in a font whose name matches MATH (the converter's own
rule, MATH_FONT in scripts/pdf-to-markdown.py).
"""
import sys, re, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import pymupdf
from paperlib import paper_files, read_paper, pdf_path_for
MATH = re.compile(r"cmmi|cmsy|cmex|msam|msbm|stix|mathjax|math|symbol", re.I)
counts = []
for md in paper_files():
    if read_paper(md)[0].get('source') != 'pdf-text': continue
    try:
        doc = pymupdf.open(pdf_path_for(md))
    except Exception:
        continue
    n = total = 0
    for page in doc:
        for b in page.get_text('dict')['blocks']:
            spans = [s for l in b.get('lines', []) for s in l['spans'] if s['text'].strip()]
            if sum(len(s['text']) for s in spans) < 40: continue
            total += 1
            n += any(MATH.search(s['font']) for s in spans)
    counts.append((n, total, len(doc), md.stem[:50]))
ns = [c[0] for c in counts]
print(len(counts), 'PDF papers; blocks with a maths font: total', sum(ns), 'median', statistics.median(ns), 'mean', round(statistics.mean(ns)), 'max', max(ns))
print('papers with 0:', sum(n == 0 for n in ns), ' 1-20:', sum(1 <= n <= 20 for n in ns), ' 21-100:', sum(21 <= n <= 100 for n in ns), ' >100:', sum(n > 100 for n in ns))
for c in sorted(counts, reverse=True)[:5]: print('  ', c)
