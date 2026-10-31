#!/usr/bin/env python3
"""`paperlib locate`: where a quote, table, figure or equation is printed in a PDF.

    paperlib test   (or: uv run python tests/test_locate.py)

Builds its PDF with PyMuPDF, so no paper and no network are needed: a page of prose with a
table, a figure and an equation; a two-column page; and a page with a crop box and a
rotation, for the coordinates a link carries.
"""

import os
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ENGINE / "scripts"))
os.environ.setdefault("PAPER_LIBRARY", tempfile.mkdtemp())  # paperlib reads a library when it loads

import pymupdf  # noqa: E402

import locate  # noqa: E402

failures = 0
PROSE = ("The method keeps a small memory of past sessions and retrieves from it when a question "
         "needs an older fact, which keeps the prompt short and the answers grounded in what was said.")


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f": {detail}" if detail and not ok else ""))


def paragraph(page, y, text, x0=72, x1=540, size=10):
    """Running text, wrapped to the column; returns the y below it."""
    rect = pymupdf.Rect(x0, y, x1, y + 200)
    spare = page.insert_textbox(rect, text, fontsize=size, fontname="tiro")
    return y + 200 - spare + 6


def build(path):
    """Writes the PDF; returns where its table was drawn: (caption top, note bottom)."""
    doc = pymupdf.open()

    # Page 1: prose, a ruled table with a note, a figure, an equation.
    page = doc.new_page(width=612, height=792)
    y = paragraph(page, 72, PROSE + " The memory is small. " + PROSE)
    page.insert_text((72, y + 10), "We report the results in a table, and the trade-off of mem-", fontsize=10, fontname="tiro")
    page.insert_text((72, y + 22), "ory size against accuracy in a figure.", fontsize=10, fontname="tiro")
    y += 40
    page.insert_text((200, y + 10), "Table 1: Accuracy on the benchmark.", fontsize=9, fontname="tiro")
    top = y + 16
    page.draw_line((180, top), (430, top))
    rows = [("Method", "Accuracy"), ("Baseline", "35.3%"), ("Ours", "93.4%"), ("Ours, small", "88.0%")]
    for i, (a, b) in enumerate(rows):
        page.insert_text((190, top + 12 + 13 * i), a, fontsize=9, fontname="tiro")
        page.insert_text((350, top + 12 + 13 * i), b, fontsize=9, fontname="tiro")
        page.draw_line((180, top + 16 + 13 * i), (430, top + 16 + 13 * i))
    page.insert_text((190, top + 70), "* Results reported by the authors.", fontsize=7, fontname="tiro")
    table = (y + 3, top + 72)
    y = top + 90
    y = paragraph(page, y, PROSE)
    fig_top = y + 6
    page.draw_rect(pymupdf.Rect(200, fig_top, 420, fig_top + 120), color=(0, 0, 0))
    page.draw_line((210, fig_top + 110), (410, fig_top + 20), color=(0.2, 0.4, 0.8))
    page.insert_text((215, fig_top + 15), "accuracy", fontsize=6, fontname="helv")
    page.insert_text((150, fig_top + 140), "Figure 1: Accuracy against the memory's size.", fontsize=9, fontname="tiro")
    y = fig_top + 150
    y = paragraph(page, y, PROSE)
    page.insert_text((250, y + 14), "a = b + c / d", fontsize=10, fontname="tiro")
    page.insert_text((520, y + 14), "(1)", fontsize=10, fontname="tiro")
    paragraph(page, y + 26, PROSE)

    # Page 2: two columns; Table 2 lives in the right one, and its value 93.4 repeats on the left.
    page = doc.new_page(width=612, height=792)
    for x0 in (72, 316):
        y = 72
        for _ in range(3):
            y = paragraph(page, y, PROSE, x0=x0, x1=x0 + 224)
    page.insert_text((72, y + 10), "On the left, 93.4 again.", fontsize=10, fontname="tiro")
    page.insert_text((330, y + 10), "Table 2: The right column's table.", fontsize=9, fontname="tiro")
    for i, (a, b) in enumerate([("Model", "Score"), ("Ours", "93.4")]):
        page.insert_text((330, y + 26 + 13 * i), a, fontsize=9, fontname="tiro")
        page.insert_text((470, y + 26 + 13 * i), b, fontsize=9, fontname="tiro")
    page.draw_line((320, y + 14), (536, y + 14))
    page.draw_line((320, y + 46), (536, y + 46))
    paragraph(page, y + 60, PROSE, x0=316, x1=540)

    # Page 3: a crop box that starts 20 points in, turned a quarter.
    page = doc.new_page(width=612, height=792)
    page.insert_text((100, 120), "A marked phrase near the top.", fontsize=10, fontname="tiro")
    page.set_cropbox(pymupdf.Rect(20, 30, 592, 762))
    page.set_rotation(90)
    doc.save(path)
    return table


def strings():
    check("a target: page and quote", locate.parse_target("6:easily fitting within") == (6, "quote", None, "easily fitting within"))
    check("a target: quotes around the quote are dropped", locate.parse_target('"top 10"') == (None, "quote", None, "top 10"))
    check("a target: a float", locate.parse_target("7:table.2") == (7, "table", "2", None))
    check("a target: a figure and an equation", locate.parse_target("fig.3")[1:3] == ("figure", "3")
          and locate.parse_target("2:eq.1")[1:3] == ("equation", "1"))
    check("a target: a quote inside a float", locate.parse_target("7:table.1>49.60") == (7, "table", "1", "49.60"))
    check("a target: a colon inside a quote", locate.parse_target("3:a 3:1 ratio") == (3, "quote", None, "a 3:1 ratio"))
    check("fold: ligatures, case, spacing and hyphens", locate.fold("eﬃcient  Re-\nranking") == "efficientreranking")


def pdf_cases(pdf, table):
    def find(target):
        with pymupdf.open(pdf) as doc:
            return locate.locate(doc, target)

    page, rects, why = find("1:retrieves from it")
    check("a quote that repeats is reported, not guessed", rects is None and " matches on p. 1" in why, why)
    page, rects, why = find("1:The memory is small")
    check("a unique quote: one line", page == 1 and rects and len(rects) == 1, (rects, why))
    page, rects, why = find("1:trade-off of memory size")
    check("a quote over a line break and a hyphen: a box per line", rects and len(rects) == 2, (rects, why))
    page, rects, why = find("1:not in the paper at all")
    check("a quote not found gives the page alone", rects is None and page == 1 and "not found" in why, why)

    page, rects, why = find("1:table.1")
    box = rects[0] if rects else None
    check("a table: its caption, rules and note", box and box[1] <= table[0] + 1 and box[3] >= table[1]
          and box[0] <= 180 and box[2] >= 430 and box[3] - box[1] < table[1] - table[0] + 15, (rects, table, why))
    page, rects, why = find("1:table.1>35.3")
    check("a value inside a table", rects and rects[0][0] >= 340 and rects[0][2] <= 380, (rects, why))
    page, rects, why = find("1:figure.1")
    box = rects[0] if rects else None
    check("a figure: its drawing and caption", box and box[0] <= 200 and box[2] >= 420
          and box[3] - box[1] >= 140, (rects, why))
    if box:
        check("a figure stops at the running text above it", box[3] - box[1] < 175, rects)
    page, rects, why = find("1:eq.1")
    box = rects[0] if rects else None
    check("an equation: its row with its number", box and box[0] <= 250 and box[2] >= 530
          and box[3] - box[1] < 20, (rects, why))
    page, rects, why = find("2:table.1")
    check("a float not on the page named is found on its own page", page == 1 and rects, (page, why))

    page, rects, why = find("2:table.2")
    box = rects[0] if rects else None
    check("a table in the right column stays in it", box and box[0] >= 316, (rects, why))
    page, rects, why = find("2:93.4")
    check("a value on the page twice is reported", rects is None and "2 matches" in why, why)
    page, rects, why = find("2:table.2>93.4")
    check("a value is unique inside its table", rects and rects[0][0] >= 460, (rects, why))

    page, rects, why = find("3:A marked phrase")
    with pymupdf.open(pdf) as doc:
        view = doc[2].cropbox
    box = rects[0] if rects else None
    # The phrase starts at x=100 on the page; in the crop box that is 80, unrotated.
    check("rectangles are in the unrotated crop box", box and 78 <= box[0] <= 82 and box[3] <= view.height,
          (rects, why))


def papers():
    """A paper named by its text file, its path under the library, or its title alone."""
    folder = locate.LIBRARY_DIR / "llm" / "memory"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "Zep. A Memory.txt").write_text("[page 1]\n")
    want = locate.PDF_ROOT / "llm" / "memory" / "Zep. A Memory.pdf"
    check("a paper by its text file", locate.pdf_for(str(folder / "Zep. A Memory.txt")) == want)
    check("a paper by its path under the library", locate.pdf_for("llm/memory/Zep. A Memory") == want)
    check("a paper by its title", locate.pdf_for("Zep. A Memory") == want, locate.pdf_for("Zep. A Memory"))
    check("a PDF as itself", locate.pdf_for("/x/y.pdf") == Path("/x/y.pdf"))


def links():
    pdf = locate.PDF_ROOT / "llm" / "Wide & Deep #2 100%.pdf"
    url = locate.link(pdf, 7, [(1, 2, 3, 4), (5, 6, 7, 8)])
    check("a link: path encoded as the guide says, & kept",
          url == "http://pdf.invalid/llm/Wide%20&%20Deep%20%232%20100%25.pdf?page=7&rect=1,2,3,4;5,6,7,8", url)
    check("a link without a mark", locate.link(pdf, 3).endswith(".pdf?page=3"))


def check_pages():
    """`paperlib check-pages`: citations read from notes and reviews, captions found in a
    text layer, and pages rewritten."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_pages", ENGINE / "scripts" / "check-pages.py")
    cp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cp)

    note = ("- Max context (p. 8, Table 1). Setup (p. 8). Both (p. 9, Tables 2–3; p. 4, Fig. 3b).\n"
            "- A range (p. 8–9, Figure 8) and two floats (pp. 3, 9, Table 4) and (see p. 6, Table III).\n")
    refs = cp.note_refs(note)
    got = [(r.first, r.last, r.floats) for r in refs]
    want = [(8, 8, [("table", "1")]), (8, 8, []), (9, 9, [("table", "2"), ("table", "3")]),
            (4, 4, [("figure", "3b")]), (8, 9, [("figure", "8")]), (3, 3, []), (9, 9, [("table", "4")]),
            (6, 6, [("table", "III")])]
    check("note citations: pages, ranges, ';' items, bare pages in a list, plural and lettered floats",
          got == want, got)

    body = ("[page 1]\nIntro mentions Table 1. and Figure 2 in passing.\n"
            "[page 2]\nTable 1: Results.        Figure 2. Accuracy over time.\n"
            "[page 3]\nTABLE III\nA sentence ending in Table 1. so it is not a caption.\n")
    caps = cp.caption_pages(cp.text_pages(body))
    check("captions: a column's start, after ':' or '.', a Roman number alone",
          caps[("table", "1")] == {2: 2} and caps[("figure", "2")] == {2: 1} and caps[("table", "III")] == {3: 1},
          dict(caps))

    text = "Max context (p. 8, Table 1); a range (p. 8–9, Figure 8)."
    a, b = cp.note_refs(text)
    one = cp.Check(a, "wrong", (9,))
    two = cp.Check(b, "wrong", (10,))
    fixed = cp.apply(text, [(one.ref, one.fixed), (two.ref, two.fixed)])
    check("a page becomes the caption's; a range grows to hold it",
          fixed == "Max context (p. 9, Table 1); a range (p. 8–10, Figure 8).", fixed)
    check("the shift of a single page", one.shift == 1)
    listed = "Fails (p. 2, 7, Fig. 3)."
    bare = cp.note_refs(listed)[1]
    fixed = cp.apply(listed, [(bare, cp.Check(bare, "wrong", (5,)).fixed)])
    check("a bare page in a list stays bare", fixed == "Fails (p. 2, 5, Fig. 3).", fixed)

    review = ("See [p. 4, Table 2](http://pdf.invalid/llm/A.pdf?dest=table.2&page=4) and "
              "[p. 6](http://pdf.invalid/llm/A.pdf?dest=figure.1&page=6).")
    found = cp.review_link_refs(review)
    check("review links: the float from the text, else from dest",
          [(r.first, r.floats, stem) for r, stem, _ in found] == [(4, [("table", "2")], "A"), (6, [("figure", "1")], "A")],
          [(r.first, r.floats, stem) for r, stem, _ in found])
    ref, _, m = found[0]
    new = cp.fix_review_text(review, [(ref, m, "p. 5", 5)])
    check("a review link's text and page= rewritten, dest kept",
          new.startswith("See [p. 5, Table 2](http://pdf.invalid/llm/A.pdf?dest=table.2&page=5) and"), new)


if __name__ == "__main__":
    strings()
    papers()
    links()
    check_pages()
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / "paper.pdf"
        pdf_cases(pdf, build(pdf))
    sys.exit(1 if failures else 0)
