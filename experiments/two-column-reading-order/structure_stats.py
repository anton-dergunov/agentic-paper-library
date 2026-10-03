#!/usr/bin/env python3
"""Shape of the `source: pdf-text` papers in one or more library snapshots.

    python3 structure_stats.py <label>=<library dir> [<label>=<library dir> ...]

For the papers present as pdf-text in every snapshot, prints per snapshot: body
words, non-empty lines, paragraphs (blank-line separated), median paragraph
length, one- or two-word paragraphs (figure and table fragments), the share of
words in paragraphs of 30 or more words (running prose), fenced code blocks and
the papers that have one, and side-by-side lines: lines outside code blocks
with a run of four or more spaces between two words, which is how a plain
position sort prints two columns next to each other ("Abstract      ACM
Reference Format: ..."). Reads markdown only.
"""
import re
import statistics
import sys
from pathlib import Path


def body(text):
    if text.startswith("---\n"):
        text = text.split("\n---\n", 1)[1]
    return re.sub(r"^(?:>.*\n)+", "", text.lstrip())  # the warning banner


SIDE_BY_SIDE = re.compile(r"\S {4,}\S")


def side_by_side(b):
    n, fence = 0, False
    for line in b.split("\n"):
        if line.startswith("```"):
            fence = not fence
        elif not fence and SIDE_BY_SIDE.search(line):
            n += 1
    return n


def stats(text):
    b = body(text)
    paras = [p for p in re.split(r"\n\s*\n", b) if p.strip()]
    return {
        "words": len(b.split()),
        "lines": sum(1 for l in b.split("\n") if l.strip()),
        "paragraphs": len(paras),
        "para_words": [len(p.split()) for p in paras],
        "code_blocks": len(re.findall(r"^```text$", b, re.M)),
        "side_by_side": side_by_side(b),
    }


def pdf_text_papers(root):
    out = {}
    for md in Path(root).rglob("*.md"):
        if md.name == "README.md":
            continue
        t = md.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^source:\s*pdf-text\s*$", t.split("\n---\n", 1)[0], re.M):
            out[md.stem] = t
    return out


def main(args):
    snaps = [(a.split("=", 1)[0], pdf_text_papers(a.split("=", 1)[1])) for a in args]
    common = set.intersection(*(set(p) for _, p in snaps))
    print(f"pdf-text papers in every snapshot: {len(common)}")
    print("| snapshot | words | lines | paragraphs | median words/paragraph | 1-2 word paragraphs | words in 30+ word paragraphs | code blocks | papers with code | side-by-side lines | papers with 10+ |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for label, papers in snaps:
        s = [stats(papers[k]) for k in sorted(common)]
        pw = [w for x in s for w in x["para_words"]]
        print(f"| {label} | {sum(x['words'] for x in s):,} | {sum(x['lines'] for x in s):,} | "
              f"{sum(x['paragraphs'] for x in s):,} | {statistics.median(pw):.0f} | "
              f"{sum(1 for w in pw if w <= 2):,} | {sum(w for w in pw if w >= 30) / sum(pw):.1%} | "
              f"{sum(x['code_blocks'] for x in s)} | {sum(1 for x in s if x['code_blocks'])} | "
              f"{sum(x['side_by_side'] for x in s):,} | {sum(1 for x in s if x['side_by_side'] >= 10)} |")


if __name__ == "__main__":
    main(sys.argv[1:])
