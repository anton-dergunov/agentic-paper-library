#!/usr/bin/env python3
"""Runs `paperlib locate` on the cases in cases.yaml against the reader's library, and draws
each result on its page, for judging by eye.

    PAPER_LIBRARY=~/papers uv run --with pdfplumber --with pillow python experiments/pdf-locations/run.py [--results NAME] [ids...]

Writes results.tsv here (or NAME, for another PyMuPDF), and the crops (PNG, not committed: most papers are not CC BY) and
contact sheets to $PAPERS_CACHE/experiments/pdf-locations/. Also counts, for comparison,
whether poppler's word boxes match each quote as PyMuPDF's do, and whether pdfplumber finds
a table next to each table caption.
"""

import html
import re
import subprocess
import sys
import time
from pathlib import Path

import pymupdf
import yaml
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "scripts"))
import locate  # noqa: E402
from paperlib import CACHE_DIR, LIBRARY_DIR  # noqa: E402

OUT = CACHE_DIR / "experiments" / "pdf-locations"
INK = (42, 111, 151)
SCALE = 2.0  # pixels per point in the crops


def poppler_count(pdf, page, quote):
    """How many times a quote matches poppler's words on a page, folded as locate folds."""
    out = subprocess.run(["pdftotext", "-bbox", "-f", str(page), "-l", str(page), str(pdf), "-"],
                         capture_output=True, text=True).stdout
    words = [html.unescape(w) for w in re.findall(r"<word [^>]*>([^<]*)</word>", out)]
    stream, starts = "", set()
    for w in words:
        f = locate.fold(w)
        if f:
            starts.add(len(stream))
            stream += f
    wanted, n, at = locate.fold(quote), 0, -1
    while (at := stream.find(wanted, at + 1)) >= 0:
        end = at + len(wanted)
        n += at in starts and (end == len(stream) or end in starts)
    return n


def plumber_table(pdf, page, caption):
    """Whether pdfplumber finds a table within locate.TABLE_GAP of a caption."""
    import pdfplumber
    with pdfplumber.open(pdf) as doc:
        for t in doc.pages[page - 1].find_tables():
            x0, y0, x1, y1 = t.bbox
            if min(abs(y0 - caption[3]), abs(caption[1] - y1)) <= locate.TABLE_GAP:
                return True
    return False


def draw(pdf, page_no, rects, path):
    """The page around the marks, with the marks drawn as the viewers draw them."""
    with pymupdf.open(pdf) as doc:
        page = doc[page_no - 1]
        box = locate._box(rects)
        clip = pymupdf.Rect(box[0] - 40, box[1] - 50, box[2] + 40, box[3] + 50) & page.rect
        # The mark is drawn in the unrotated page; these PDFs are not rotated.
        pix = page.get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), clip=clip)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("RGBA")
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for r in rects:
        block = r[3] - r[1] > 24
        pad = 4 if block else 1.5
        xy = [(r[0] - pad - clip.x0) * SCALE, (r[1] - pad - clip.y0) * SCALE,
              (r[2] + pad - clip.x0) * SCALE, (r[3] + pad - clip.y0) * SCALE]
        if block:
            d.rounded_rectangle(xy, radius=8, fill=INK + (13,), outline=INK + (190,), width=3)
        else:
            d.rounded_rectangle(xy, radius=4, fill=INK + (36,))
    Image.alpha_composite(img, layer).convert("RGB").save(path)


def sheets(ids):
    """Contact sheets of four crops each, labelled, for looking at many at once."""
    crops = [(i, OUT / "crops" / f"{i}.png") for i in ids if (OUT / "crops" / f"{i}.png").exists()]
    for n in range(0, len(crops), 4):
        group = crops[n:n + 4]
        images = [Image.open(p) for _, p in group]
        width = 1100
        scaled = [im.resize((width, int(im.height * width / im.width))) if im.width > width else im for im in images]
        sheet = Image.new("RGB", (width, sum(im.height + 30 for im in scaled)), "white")
        y, d = 0, ImageDraw.Draw(sheet)
        for (i, _), im in zip(group, scaled):
            d.text((6, y + 8), i, fill="black")
            sheet.paste(im, (0, y + 28))
            y += im.height + 30
        sheet.save(OUT / f"sheet-{n // 4 + 1:02d}.png")


def main(args):
    results = "results.tsv"
    if args[:1] == ["--results"]:
        results, args = args[1], args[2:]
    only = set(args)
    spec = yaml.safe_load((HERE / "cases.yaml").read_text())
    (OUT / "crops").mkdir(parents=True, exist_ok=True)
    rows = ["id\tkind\ttarget\tpage\tresult\trects\tseconds\tlink_chars\tpoppler_matches\tplumber_table"]
    done = []
    for case in spec["cases"]:
        if only and case["id"] not in only:
            continue
        pdf = locate.pdf_for(LIBRARY_DIR / spec[case["paper"]])
        _, kind, label, quote = locate.parse_target(case["target"])
        start = time.time()
        with pymupdf.open(pdf) as doc:
            page, rects, why = locate.locate(doc, case["target"])
            seconds = time.time() - start
            poppler = plumber = ""
            if kind == "quote" and page:
                poppler = poppler_count(pdf, page, quote)
            if kind == "table" and page and quote is None:
                caption = locate.Page(doc[page - 1]).caption("table", label)
                plumber = plumber_table(pdf, page, caption) if caption else ""
        url = locate.link(pdf, page, rects) if rects else ""
        query = url.split("?", 1)[1] if url else ""
        rows.append("\t".join(map(str, [case["id"], kind, case["target"], page or "", "found" if rects else why,
                                        ";".join(",".join(map(str, r)) for r in rects or []), f"{seconds:.2f}",
                                        len(query), poppler, plumber])))
        if rects:
            draw(pdf, page, rects, OUT / "crops" / f"{case['id']}.png")
            done.append(case["id"])
        print(rows[-1])
    if not only:
        (HERE / results).write_text("\n".join(rows) + "\n")
    sheets(done)


if __name__ == "__main__":
    main(sys.argv[1:])
