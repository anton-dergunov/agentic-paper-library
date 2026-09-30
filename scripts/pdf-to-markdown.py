#!/usr/bin/env python3
"""Extract a PDF's text layer into rough markdown.

    ./scripts/pdf-to-markdown.py <input.pdf> <output.md>

This is the fallback conversion used by `add-arxiv-paper.sh` when arXiv has no
HTML rendering for a paper, and the only conversion available to
`add-pdf-paper.sh` for papers that were never on arXiv at all. It is markedly
worse than converting arXiv's own HTML: section structure, tables and figures
do not survive. Both callers therefore stamp a warning at the top of the
markdown they write.

Reading order comes from pymupdf4llm's column detection (column_boxes): each
page is split into text regions in reading order, so a two-column paper reads
down the left column and then the right, instead of interleaving the two line
by line as a plain position sort does. The text itself is still PyMuPDF's raw
extraction, which keeps equations (flattened) where pymupdf4llm's own markdown
drops display maths (docs/experiments/pdf-vs-html-conversion.md). A page whose
regions miss much of its text falls back to the plain sort. The
post-processing undoes the PDF's hard line wrapping, which would otherwise
leave every printed line as its own markdown line.
"""

import re
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("error: PDF conversion needs PyMuPDF — pip install pymupdf")


try:
    from pymupdf4llm.helpers.multi_column import column_boxes
except ImportError:
    column_boxes = None

# Running headers and page numbers sit in these margins (points) and are left out.
MARGIN = 40


def region_paragraphs(page, box):
    """One region's lines joined into paragraphs, from their geometry.

    A paragraph ends where the line spacing jumps well above the region's usual
    pitch, or after a line that stops well short of the region's right edge.
    """
    lines = []
    for block in page.get_text("dict", clip=box, sort=True)["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if text:
                lines.append((line["bbox"], text))
    if not lines:
        return ""
    # Line pitch (baseline to baseline) is the reliable spacing measure: glyph
    # boxes can be much shorter than the line spacing.
    pitches = sorted(b[3] - a[3] for (a, _), (b, _) in zip(lines, lines[1:]) if b[3] > a[3])
    pitch = pitches[len(pitches) // 2] if pitches else 12
    width = box[2] - box[0]
    paragraphs, current, prev = [], "", None
    for bbox, text in lines:
        if prev is not None:
            step = bbox[3] - prev[3]
            short = prev[2] < box[2] - 0.12 * width
            if step > 1.4 * pitch or step < 0 or short:  # a gap, a jump back up, or a short last line
                paragraphs.append(current)
                current = ""
        if current.endswith("-") and text[:1].islower():
            # "personal-" + "isation" joins; a compound ("cost-per-" + "click") keeps its hyphen.
            last = current.rsplit(" ", 1)[-1]
            current = current + text if "-" in last[:-1] else current[:-1] + text
        else:
            current = f"{current} {text}" if current else text
        prev = bbox
    paragraphs.append(current)
    return "\n\n".join(paragraphs)


def page_text(page):
    """A page's text in reading order, region by region."""
    plain = page.get_text("text", sort=True)
    if column_boxes is None:
        return plain
    try:
        boxes = column_boxes(page, footer_margin=MARGIN, header_margin=MARGIN)
    except Exception:
        return plain
    parts = [region_paragraphs(page, box) for box in boxes]
    ordered = "\n\n".join(p for p in parts if p.strip())
    # Only trust the regions if they hold nearly all of the page's text (the
    # margins legitimately drop a header line and a page number).
    if len("".join(ordered.split())) < 0.9 * len("".join(plain.split())) - 200:
        return plain
    return ordered


def convert(pdf_path):
    doc = pymupdf.open(pdf_path)
    text = "\n\n".join(page_text(page) for page in doc)

    # Join words split across a line break ("personal-\nisation"), then join the
    # lines inside each paragraph, treating a blank line as the boundary.
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    paragraphs = []
    for block in re.split(r"\n\s*\n", text):
        joined = " ".join(line.strip() for line in block.splitlines() if line.strip())
        if joined:
            paragraphs.append(joined)
    return "\n\n".join(paragraphs) + "\n"


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: pdf-to-markdown.py <input.pdf> <output.md>")
    pdf_path, out_path = sys.argv[1], sys.argv[2]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(convert(pdf_path))


if __name__ == "__main__":
    main()
