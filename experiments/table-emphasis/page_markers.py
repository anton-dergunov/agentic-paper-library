#!/usr/bin/env python3
"""Which heading pages change between two versions of page-map.py, over a whole library.

    PAPER_LIBRARY=<library> uv run python page_markers.py <old page-map.py> <new page-map.py> > page-markers.tsv

Each arXiv-HTML paper is copied to a temporary file and mapped by both scripts
(page-map.py replaces the markers it finds, so it can be re-run). One row per
heading whose marker differs; the summary goes to stderr. Nothing in the
library is written.
"""

import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from paperlib import paper_files, pdf_path_for, read_paper  # noqa: E402

HEADING = re.compile(r"^#{2,6} ")
PAGE = re.compile(r"\(p\. (\d+)\)$")


def headings(script, pdf, md):
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "paper.md"
        copy.write_text(md.read_text(encoding="utf-8"), encoding="utf-8")
        run = subprocess.run([sys.executable, script, pdf, copy], capture_output=True, text=True)
        if run.returncode:
            return None
        return [line for line in copy.read_text(encoding="utf-8").split("\n") if HEADING.match(line)]


def backwards(lines):
    """Headings whose page is lower than the page of a heading before them."""
    n, top = 0, 0
    for line in lines:
        m = PAGE.search(line)
        if m:
            n += int(m.group(1)) < top
            top = max(top, int(m.group(1)))
    return n


def compare(md, old, new):
    pdf = pdf_path_for(md)
    if not pdf.exists():
        return md, None
    before, after = headings(old, pdf, md), headings(new, pdf, md)
    if before is None or after is None or len(before) != len(after):
        return md, None
    return md, (before, after)


def main(old, new):
    papers = [md for md in paper_files() if read_paper(md)[0].get("source") == "html"]
    print("paper\tbefore\tafter")
    done = changed_papers = changed = lost = back_before = back_after = total = 0
    with ThreadPoolExecutor(6) as pool:
        for md, result in pool.map(lambda md: compare(md, old, new), papers):
            if result is None:
                continue
            done += 1
            before, after = result
            total += len(before)
            back_before += backwards(before)
            back_after += backwards(after)
            rows = [(b, a) for b, a in zip(before, after) if b != a]
            changed += len(rows)
            changed_papers += bool(rows)
            lost += sum(1 for b, a in rows if PAGE.search(b) and not PAGE.search(a))
            for b, a in rows:
                print(f"{md.stem}\t{b}\t{a}")
    print(f"{done} papers, {total} headings: {changed} markers changed in {changed_papers} papers, "
          f"{lost} of them now without a page; headings paged before an earlier heading: "
          f"{back_before} before, {back_after} after", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
