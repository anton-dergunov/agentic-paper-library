#!/usr/bin/env python3
"""The reader's highlights in a paper's PDF: each one's page, colour and the words under it.

    paperlib highlights <paper> [--json]

<paper> is the paper's text file under the library, its PDF, or its title as its file is
named. Prints one line per highlight, by page and down the page: the page, the colour and
the words. With --json, a list of {page, color, name, rect, text, note}.

The highlights are the PDF's Highlight annotations, whichever app made them (carrel, the
VS Code viewer, a tablet's reader). Reading them takes a few milliseconds a paper.
"""

import json
import math
import sys

import pymupdf

from locate import link, pdf_for
from paperlib import LIBRARY_DIR, paper_stem

# vscode-pdf-viewer's colours, which carrel uses too: a highlight is named by the nearest.
COLORS = {
    "yellow": "#ffeb3b",
    "green": "#a5d6a7",
    "blue": "#81d4fa",
    "pink": "#f48fb1",
    "orange": "#ffb74d",
    "purple": "#ce93d8",
}


def _hex(rgb):
    return "#" + "".join(f"{round(max(0.0, min(1.0, v)) * 255):02x}" for v in rgb[:3])


def color_name(value):
    """The nearest of COLORS to a `#rrggbb` colour."""
    rgb = [int(value[i:i + 2], 16) for i in (1, 3, 5)]

    def distance(name):
        other = [int(COLORS[name][i:i + 2], 16) for i in (1, 3, 5)]
        return sum((a - b) ** 2 for a, b in zip(rgb, other))

    return min(COLORS, key=distance)


def _quads(annot):
    """A highlight's quadrilaterals as boxes; its rectangle when it has none."""
    points = annot.vertices or []
    boxes = []
    for i in range(0, len(points) - 3, 4):
        xs = [p[0] for p in points[i:i + 4]]
        ys = [p[1] for p in points[i:i + 4]]
        boxes.append(pymupdf.Rect(min(xs), min(ys), max(xs), max(ys)))
    return boxes or [annot.rect]


def _words_in(words, boxes):
    """The words whose middle lies in one of `boxes`, in reading order."""
    picked = []
    for word in words:
        x, y = (word[0] + word[2]) / 2, (word[1] + word[3]) / 2
        if any(box.x0 <= x <= box.x1 and box.y0 <= y <= box.y1 for box in boxes):
            picked.append(word[4])
    return " ".join(picked)


def read_highlights(pdf):
    """Every Highlight annotation in a PDF, by page and down the page: {page (from 1), color
    (#rrggbb), name (the nearest of COLORS), rect ([x0, y0, x1, y1] in whole points from the
    page's top-left, as a `pdf.invalid` link's `rect`), text (the words under it), note (the
    annotation's own text, often empty)}."""
    found = []
    with pymupdf.open(pdf) as doc:
        for page in doc:
            annots = list(page.annots(types=[pymupdf.PDF_ANNOT_HIGHLIGHT]))
            if not annots:
                continue
            words = page.get_text("words", sort=True)
            for annot in annots:
                boxes = _quads(annot)
                stroke = (annot.colors or {}).get("stroke") or [1.0, 0.92, 0.23]
                color = _hex(stroke)
                x0 = min(box.x0 for box in boxes)
                y0 = min(box.y0 for box in boxes)
                x1 = max(box.x1 for box in boxes)
                y1 = max(box.y1 for box in boxes)
                found.append({
                    "page": page.number + 1,
                    "color": color,
                    "name": color_name(color),
                    "rect": [math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1)],
                    "text": _words_in(words, boxes),
                    "note": " ".join(str((annot.info or {}).get("content") or "").split()),
                })
    found.sort(key=lambda each: (each["page"], each["rect"][1], each["rect"][0]))
    return found


def main(argv):
    as_json = "--json" in argv
    argv = [arg for arg in argv if arg != "--json"]
    if len(argv) != 1 or argv[0] in {"-h", "--help"}:
        print(__doc__.strip())
        return 0 if argv[:1] in (["-h"], ["--help"]) else 2
    try:
        pdf = pdf_for(argv[0])
    except ValueError:
        print(f"paperlib highlights: {argv[0]} is not a paper under {LIBRARY_DIR}", file=sys.stderr)
        return 2
    if not pdf.is_file():
        print(f"paperlib highlights: no PDF for {paper_stem(argv[0])} (looked at {pdf})", file=sys.stderr)
        return 2
    found = read_highlights(pdf)
    if as_json:
        print(json.dumps(found, ensure_ascii=False, indent=1))
        return 0
    if not found:
        print("no highlights")
    for each in found:
        note = f"  (note: {each['note']})" if each["note"] else ""
        print(f"p. {each['page']}  {each['name']}  {each['text'] or '(no text under it)'}{note}  "
              f"{link(pdf, each['page'], [each['rect']])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
