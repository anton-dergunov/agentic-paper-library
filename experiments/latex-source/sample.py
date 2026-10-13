#!/usr/bin/env python3
"""Pick the control papers: ones that have arXiv HTML, so a conversion from the source can be compared with it.

    PAPER_LIBRARY=<library> uv run python sample.py > papers-control.tsv

Nine papers at random from those converted from arXiv's HTML, and four at
random from those the library's catalog says arXiv's HTML is incomplete for
(seeded). Papers of more than 150,000 characters are left out: a LaTeXML run
on a book-length source takes most of an hour.
"""

import random
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from paperlib import CONVERSION_ISSUES_FILE, paper_files, read_paper  # noqa: E402

incomplete = {e["paper"] for e in yaml.safe_load(CONVERSION_ISSUES_FILE.read_text(encoding="utf-8"))
              if "HTML is incomplete" in e.get("problem", "")}
groups = {"random": [], "incomplete": []}
for md in paper_files():
    meta, body = read_paper(md)
    if meta.get("source") == "html" and meta.get("arxiv") and len(body) <= 150_000:
        groups["incomplete" if md.stem in incomplete else "random"].append((str(meta["arxiv"]), meta["title"]))
rng = random.Random(20261013)
print("arxiv\ttitle\tgroup")
for group, n in (("random", 9), ("incomplete", 4)):
    for arxiv_id, title in rng.sample(sorted(groups[group]), n):
        print(f"{arxiv_id}\t{title}\t{group}")
