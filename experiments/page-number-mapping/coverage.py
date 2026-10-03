#!/usr/bin/env python3
"""Count the headings in a library that carry a PDF page, `(p. N)`.

    python3 coverage.py <library dir> [--by-source] [--unplaced]

Reads only the markdown; needs no PDFs. Headings are `##` to `######` outside
code fences, as page-map.py sees them. A heading is "numbered" when it starts
with a section number, by page-map.py's own pattern and rule.
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HEADING = re.compile(r"^(#{2,6}) (.+?)\s*$")
PAGE_SUFFIX = re.compile(r"\s\(p\. \d+\)$")
NUMBER = re.compile(r"^(?:Appendix\s+)?((?:\d+|[A-Z])(?:\.\d+)*)\.?\s+(.+)$")
SOURCE = re.compile(r"^source:\s*(\S+)", re.M)


def headings(text):
    in_fence = False
    body = text.split("\n---\n", 1)[1] if text.startswith("---\n") else text
    for line in body.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if m:
            yield m.group(1), m.group(2)


def main(root, by_source, list_unplaced):
    papers = [p for p in Path(root).rglob("*.md") if p.name != "README.md"]
    totals = defaultdict(Counter)
    unplaced_numbered = Counter()
    for md in papers:
        text = md.read_text(encoding="utf-8")
        src = SOURCE.search(text.split("\n---\n", 1)[0])
        src = src.group(1) if src else "?"
        keys = ["all"] + ([src] if by_source else [])
        for hashes, h in headings(text):
            placed = bool(PAGE_SUFFIX.search(h))
            bare = PAGE_SUFFIX.sub("", h)
            num = NUMBER.match(bare)
            # As in page-map.py: a bare letter is an appendix number only on a
            # top-level heading; deeper down, "A Harmless Assistant" is an article.
            numbered = bool(num) and not (
                num.group(1).isalpha() and not bare.startswith("Appendix") and hashes != "##"
            )
            kind = "numbered" if numbered else "unnumbered"
            for k in keys:
                totals[k][f"{kind} total"] += 1
                totals[k][f"{kind} placed"] += placed
            if numbered and not placed:
                unplaced_numbered[md.stem] += 1
        for k in keys:
            totals[k]["papers"] += 1
    for k, c in sorted(totals.items(), key=lambda kv: kv[0] != "all"):
        n_all = c["numbered total"] + c["unnumbered total"]
        p_all = c["numbered placed"] + c["unnumbered placed"]
        print(f"[{k}] papers {c['papers']}; headings {n_all}, with a page {p_all} ({p_all / max(n_all, 1):.1%})")
        for kind in ("numbered", "unnumbered"):
            t, p = c[f"{kind} total"], c[f"{kind} placed"]
            print(f"    {kind:10} {p:6} of {t:6} ({p / max(t, 1):.1%})")
    print(f"papers with numbered headings lacking a page: {len(unplaced_numbered)}")
    if list_unplaced:
        for stem, n in unplaced_numbered.most_common():
            print(f"  {n:4}  {stem[:90]}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], "--by-source" in sys.argv, "--unplaced" in sys.argv)
