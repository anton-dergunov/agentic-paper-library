#!/usr/bin/env python3
"""`paperlib highlights`: the reader's highlights in a PDF, with the words under them.

    paperlib test   (or: uv run python tests/test_highlights.py)

Builds its PDF with PyMuPDF: highlights in two colours on two pages, one with a note, so no
paper is needed.
"""

import os
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ENGINE / "scripts"))
os.environ.setdefault("PAPER_LIBRARY", tempfile.mkdtemp())  # paperlib reads a library when it loads

import pymupdf  # noqa: E402

import highlights  # noqa: E402

failures = 0


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f": {detail}" if detail and not ok else ""))


def highlight(page, words, color, note=""):
    quads = [pymupdf.Rect(word[:4]).quad for word in words]
    annot = page.add_highlight_annot(quads)
    annot.set_colors(stroke=color)
    if note:
        annot.set_info(content=note)
    annot.update()


def build(path):
    doc = pymupdf.open()
    first = doc.new_page(width=612, height=792)
    first.insert_text((72, 100), "Memory keeps the prompt short and the answers grounded.", fontsize=11)
    first.insert_text((72, 400), "A second passage further down the page.", fontsize=11)
    words = first.get_text("words", sort=True)
    # Lower on the page first, to see them come back in the page's order.
    highlight(first, [w for w in words if w[1] > 300][1:3], (0.65, 0.84, 0.65))
    highlight(first, words[1:4], (1, 0.92, 0.23), note="Worth   quoting")
    second = doc.new_page(width=612, height=792)
    second.insert_text((72, 200), "Nothing else is marked here but this.", fontsize=11)
    highlight(second, second.get_text("words", sort=True)[-1:], (0.81, 0.58, 0.85))
    doc.new_page(width=612, height=792)  # a page with none
    doc.save(path)


with tempfile.TemporaryDirectory() as folder:
    pdf = Path(folder) / "paper.pdf"
    build(pdf)
    found = highlights.read_highlights(pdf)
    check("three highlights", len(found) == 3, found)
    first, second, third = found + [{}] * (3 - len(found))
    check("in the page's order", [h.get("page") for h in found] == [1, 1, 2]
          and first.get("rect", [0, 0])[1] < second.get("rect", [0, 0])[1], found)
    check("the words under it", first.get("text") == "keeps the prompt", first.get("text"))
    check("words lower down", second.get("text") == "second passage", second.get("text"))
    check("a colour, named", (first.get("name"), second.get("name"), third.get("name")) == ("yellow", "green", "purple"),
          [h.get("name") for h in found])
    check("its note, on one line", first.get("note") == "Worth quoting" and second.get("note") == "", first.get("note"))
    x0, y0, x1, y1 = first.get("rect", [0, 0, 0, 0])
    check("a rect in points from the top", 60 < x0 < x1 < 400 and 80 < y0 < y1 < 110, first.get("rect"))
    check("hex colour", first.get("color", "").startswith("#") and len(first["color"]) == 7, first.get("color"))
    empty = Path(folder) / "none.pdf"
    doc = pymupdf.open()
    doc.new_page()
    doc.save(empty)
    check("a PDF without any", highlights.read_highlights(empty) == [])

sys.exit(1 if failures else 0)
