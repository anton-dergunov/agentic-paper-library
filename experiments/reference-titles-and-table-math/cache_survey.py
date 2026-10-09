#!/usr/bin/env python3
"""Count, in every cached arXiv rendering, what the converter changes of 9 Oct 2026 act on.

    python3 cache_survey.py <cache>/arxiv/html > cache-survey.tsv

One row per rendering that has any of them:

  title chars        characters of the title="..." of links inside the paper
  formulas in HTML   <math> elements holding a <div> or an <svg> (a \\scalebox, a TikZ picture)
  picture formulas   of those, the ones whose TeX holds \\pgfpicture, and the characters of that TeX
  par numbers        formulas whose TeX is "\\par" and whose digits are only in the MathML
  par text           "\\par" set as text, in headings, captions and the author block
  undefined, classed undefined-macro spans carrying a second class, which the converter's pattern missed
  colour macros      \\cellcolor, \\rowcolor or \\columncolor left undefined, their colour's name set as text
  citeauthoryear, raw cite, diaghead   three kinds of TeX set as text
"""

import gzip
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

MATH = re.compile(r"<math\b[^>]*>.*?</math>", re.S)
COLUMNS = ["title chars", "formulas in HTML", "picture formulas", "picture chars", "par numbers", "par text",
           "undefined, classed", "colour macros", "citeauthoryear", "raw cite", "diaghead"]


def scan(folder):
    try:
        page = gzip.open(folder / "index.html.gz", "rt", errors="replace").read()
    except OSError:
        return folder.name, None
    article = page[page.find("ltx_page_content"):]
    row = dict.fromkeys(COLUMNS, 0)
    row["title chars"] = sum(len(t) for t in re.findall(r'<a\b[^>]*\bhref="#[^"]*"[^>]*\btitle="([^"]*)"', article))
    for m in MATH.finditer(article):
        if "<div" in m.group(0) or "<svg" in m.group(0):
            row["formulas in HTML"] += 1
            alt = re.search(r'alttext="([^"]*)"', m.group(0))
            if alt and "\\pgfpicture" in alt.group(1):
                row["picture formulas"] += 1
                row["picture chars"] += len(alt.group(1))
    row["par numbers"] = len(re.findall(r'<annotation encoding="application/x-tex">\\par</annotation>', article))
    prose = re.sub(r'<annotation\b.*?</annotation>|alttext="[^"]*"|title="[^"]*"', "", article, flags=re.S)
    row["par text"] = len(re.findall(r">[^<]*\\par\b(?![a-zA-Z])", prose))
    row["undefined, classed"] = len(re.findall(r'class="ltx_ERROR [^"]*undefined"', article))
    row["colour macros"] = len(re.findall(r'undefined">\\(?:cell|row|column)color</span>', article))
    row["citeauthoryear"] = prose.count("\\citeauthoryear")
    row["raw cite"] = len(re.findall(r"\\cite\[cite[pt]\]\{", prose))
    row["diaghead"] = prose.count("\\diaghead")
    return folder.name, row


def main():
    folders = sorted(p for p in Path(sys.argv[1]).iterdir() if p.is_dir())
    print("rendering\t" + "\t".join(COLUMNS))
    with ProcessPoolExecutor() as pool:
        for name, row in pool.map(scan, folders, chunksize=20):
            if row and any(row.values()):
                print(name + "\t" + "\t".join(str(row[c]) for c in COLUMNS))


if __name__ == "__main__":
    main()
