#!/usr/bin/env python3
"""Annotate a paper's markdown headings with the PDF page they start on.

    ./scripts/page-map.py <paper.pdf> <paper.md>

Turns `### 4.3 LongMemEval (LME)` into `### 4.3 LongMemEval (LME) (p. 6)`, so
an agent reading the markdown can always tell the reader where something is in
the PDF they are holding.

Two ways to place a heading, in order:

1. The PDF's named destinations. LaTeX with hyperref writes one per numbered
   section (`section.4`, `subsection.4.3`, `subsubsection.2.2.3`, and
   `appendix.A` / `subsection.A.1` for appendices), which is exact.
2. Searching the page text for the heading, starting from the page of the
   previous placed heading, since headings appear in reading order. A heading
   counts as found when a line of the page is the heading, or (for numbered
   headings) when "<number> <title>" appears in the page text. Unnumbered
   headings are short and also occur in tables of contents, so they are only
   searched up to the next exactly-known heading (and at most two pages on).

Headings neither method places are left alone and reported. Existing `(p. N)`
suffixes are replaced, so the script is safe to re-run.
"""

import re
import sys
from pathlib import Path

import pymupdf

HEADING = re.compile(r"^(#{2,6}) (.+?)\s*$")
PAGE_SUFFIX = re.compile(r"\s*\(p\. \d+\)$")
NUMBER = re.compile(r"^(?:Appendix\s+)?((?:\d+|[A-Z])(?:\.\d+)*)\.?\s+(.+)$")
DEPTH_NAMES = ["section", "subsection", "subsubsection"]


def normalise(text):
    text = text.replace("­", "").replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = re.sub(r"-\n(\w)", r"\1", text)  # rejoin words hyphenated across lines
    return " ".join(text.lower().split())


def plain_title(title):
    """Heading text as it would appear in the PDF: no markdown, no math."""
    if "$`" in title:
        return None
    title = re.sub(r"[*_`]", "", title)
    title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title)
    return normalise(title.rstrip("."))


def dest_candidates(number):
    parts = number.split(".")
    depth = len(parts) - 1
    names = []
    if depth < len(DEPTH_NAMES):
        names.append(f"{DEPTH_NAMES[depth]}.{number}")
    if depth == 0 and parts[0].isalpha():
        names.append(f"appendix.{number}")
    return names


def main(pdf_path, md_path):
    doc = pymupdf.open(pdf_path)
    dests = {
        name: target["page"] + 1
        for name, target in doc.resolve_names().items()
        if target.get("page", -1) >= 0
    }
    pages = [normalise(page.get_text()) for page in doc]
    page_lines = [
        {normalise(line) for line in page.get_text().splitlines() if line.strip()}
        for page in doc
    ]

    lines = Path(md_path).read_text(encoding="utf-8").split("\n")

    # First pass: every heading, and the exact page of those a destination names.
    headings = []  # (line index, hashes, text, number match, destination page)
    in_fence = False
    for i, line in enumerate(lines):
        if line.startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        m = HEADING.match(line)
        if not m:
            continue
        text = PAGE_SUFFIX.sub("", m.group(2))
        numbered = NUMBER.match(text)
        # A bare letter is an appendix number only on a top-level heading
        # ("## B Proofs"); deeper down, "A Harmless Assistant" is just an article.
        if (
            numbered
            and numbered.group(1).isalpha()
            and not text.startswith("Appendix")
            and m.group(1) != "##"
        ):
            numbered = None
        dest_page = None
        if numbered:
            for name in dest_candidates(numbered.group(1)):
                if name in dests:
                    dest_page = dests[name]
                    break
        headings.append((i, m.group(1), text, numbered, dest_page))

    last_page = 1
    placed = unplaced = 0
    missing = []

    for k, (i, hashes, text, numbered, page) in enumerate(headings):
        if page is None:
            # Search forward from the previous heading. An unnumbered heading
            # ("Objective.", "Tasks.") is short and also appears in tables of
            # contents and running text, so it may only land before the next
            # heading whose page is known exactly; a numbered one is specific
            # enough to search to the end.
            upper = len(pages)
            if not numbered:
                later = [h[4] for h in headings[k + 1:] if h[4]]
                upper = min(later[0] if later else len(pages), last_page + 2, len(pages))
            title = plain_title(numbered.group(2) if numbered else text)
            if title:
                full = f"{numbered.group(1).lower()} {title}" if numbered else None
                for p in range(last_page - 1, upper):
                    if title in page_lines[p] or (full and full in page_lines[p]):
                        page = p + 1
                        break
                    if full and full in pages[p]:
                        page = p + 1
                        break

        if page is None:
            lines[i] = f"{hashes} {text}"
            if numbered:
                unplaced += 1
                missing.append(text)
            continue
        lines[i] = f"{hashes} {text} (p. {page})"
        last_page = page
        placed += 1

    Path(md_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"page-map: {placed} headings placed, {unplaced} numbered headings unplaced")
    for text in missing[:10]:
        print(f"  unplaced: {text}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
