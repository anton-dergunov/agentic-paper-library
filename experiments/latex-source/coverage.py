#!/usr/bin/env python3
"""How many papers of a library have a LaTeX source on arXiv, and how many of those lack an HTML rendering?

    PAPER_LIBRARY=<library> uv run python coverage.py > results/coverage.txt
    PAPER_LIBRARY=<library> uv run python coverage.py --list > papers-no-html.tsv

A paper converted from arXiv's HTML has a source: the HTML is made from it. A
paper on arXiv converted from its PDF is asked for by a header-only request to
arxiv.org/e-print/<id>, which answers application/gzip for a source and
application/pdf for a submission that was a PDF. --list prints the papers
with a source and no HTML.
"""

import collections
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from paperlib import paper_files, read_paper  # noqa: E402


def source_type(arxiv_id):
    head = subprocess.run(["curl", "-sIL", "--max-time", "30", f"https://arxiv.org/e-print/{arxiv_id}"],
                          capture_output=True, text=True).stdout
    types = [line.split(":", 1)[1].strip() for line in head.splitlines() if line.lower().startswith("content-type:")]
    return types[-1] if types else "none"


def main():
    groups, asked = collections.Counter(), []
    for md in paper_files():
        meta, _ = read_paper(md)
        if not meta.get("source"):
            continue
        arxiv_id = str(meta.get("arxiv") or "")
        if meta["source"] == "pdf-text" and arxiv_id:
            kind = source_type(arxiv_id)
            time.sleep(2)
            groups["arXiv, from the PDF, " + ("with a source" if "gzip" in kind else "submitted as a PDF")] += 1
            if "gzip" in kind:
                asked.append((arxiv_id, meta.get("title", md.stem)))
        else:
            groups[{"html": "arXiv, from the HTML (has a source)", "pdf-text": "not on arXiv, from the PDF",
                    "web": "web article"}.get(meta["source"], meta["source"])] += 1
    if "--list" in sys.argv:
        print("arxiv\ttitle")
        for arxiv_id, title in asked:
            print(f"{arxiv_id}\t{title}")
        return
    total = sum(groups.values())
    for name, n in groups.most_common():
        print(f"{n:5d}  {100 * n / total:5.1f}%  {name}")
    print(f"{total:5d}          papers")


if __name__ == "__main__":
    main()
