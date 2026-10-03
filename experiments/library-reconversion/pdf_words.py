#!/usr/bin/env python3
"""Word counts of the PDF-only papers, before and after their reconversion.

    python3 pdf_words.py <old library/> <new library/>

The task's check for PDF papers: the new conversion (docling's layout analysis) should
not be shorter than the old one (the PDF's text layer) by more than running headers
and page numbers. Prints the median new/old ratio, every paper below 0.95, and how
many papers carry the "layout analysis" conversion note and how many display
equations were left as the PDF's raw text.

During the validation this was an inline script run in the worktree against
`git show main:<path>`; here it reads two checked-out copies instead, so it needs no
git. The counting is unchanged: whitespace words of the body after the frontmatter.
"""

import re
import statistics
import sys
from pathlib import Path


def pdf_papers(root):
    out = {}
    for md in Path(root).rglob("*.md"):
        if md.name == "README.md":
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^source: pdf-text\s*$", text.split("\n---\n", 1)[0], re.M):
            out[str(md.relative_to(root))] = text
    return out


def main(old_root, new_root):
    old, new = pdf_papers(old_root), pdf_papers(new_root)
    rows, layout, raw = [], 0, []
    for p, text in sorted(new.items()):
        body = text.split("---", 2)[-1]
        layout += "layout analysis" in body[:900]
        nraw = body.count("equation: the PDF's raw text")
        if nraw:
            raw.append((nraw, len(re.findall(r"^\$\$", body, flags=re.M)), Path(p).stem))
        if p in old:
            w0, w1 = len(old[p].split("---", 2)[-1].split()), len(body.split())
            rows.append((w1 / w0 if w0 else 9, w0, w1, p))
    rows.sort()
    print(f"{len(new)} PDF papers now, {layout} with the layout-analysis note; {len(rows)} also PDF papers before")
    print(f"median new/old words {statistics.median(r[0] for r in rows):.3f}")
    for ratio, w0, w1, p in rows:
        if ratio < 0.95:
            print(f"{ratio:5.2f} {w0:6d} -> {w1:6d} | {p}")
    print(f"papers with raw-text equations: {len(raw)}")
    for nraw, neq, stem in sorted(raw, reverse=True):
        print(f"  {nraw} raw of {neq} display equations | {stem}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
