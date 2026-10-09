#!/usr/bin/env python3
"""Mark the shaded tokens of Table 1 of "Continual Learning via Sparse Memory Finetuning" from arXiv's HTML.

    heatmap.py <index.html.gz> <paper.md> [--write]

Each row's tokens carry a background from white to #298C8C. A token at a
quarter or more of the darkest shade is wrapped in <mark>, runs joined.
"""
import gzip, html, re, sys
page = gzip.open(sys.argv[1], "rt").read()
start = page.index('id="S6.T1"'); table = page[start:page.index("</figure>", start)]
rows = []
for cell in re.findall(r'<td\b[^>]*ltx_align_top[^>]*>(.*?)</td>', table, re.S):
    toks = re.findall(r'--ltx-bg-color:#([0-9A-Fa-f]{6});">(.*?)</span></span>', cell, re.S)
    if not toks:
        continue
    out, open_ = [], False
    for colour, text in toks:
        text = re.sub(r"<[^>]+>", "", text)
        dark = (255 - int(colour[:2], 16)) / (255 - 0x29)
        if dark >= 0.25 and not open_:
            out.append("<mark>"); open_ = True
        elif dark < 0.25 and open_:
            out[-1] += "</mark>"; open_ = False
        out.append(text)
    if open_:
        out[-1] += "</mark>"
    rows.append(" ".join(out).replace("<mark> ", "<mark>"))
md = open(sys.argv[2]).read()
cells = [m for m in re.finditer(r"<td>( [^<\n]*&lt;eot&gt; )</td>", md)]
print(len(rows), "rows in the HTML,", len(cells), "in the markdown", file=sys.stderr)
assert len(rows) == len(cells)
plain = lambda s: re.sub(r"\s+", "", html.unescape(re.sub(r"<[^>]+>", "", s)))
out, pos = [], 0
for m, row in zip(cells, rows):
    assert plain(m.group(1)) == plain(row), (m.group(1), row)
    out += [md[pos:m.start(1)], " " + row + " "]; pos = m.end(1)
new = "".join(out) + md[pos:]
print(new[new.index("Fact index: 174") - 200:new.index("Fact index: 174") + 900])
if "--write" in sys.argv:
    open(sys.argv[2], "w").write(new)
