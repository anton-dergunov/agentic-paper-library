#!/usr/bin/env python3
"""Probe, 1 Oct 2026: what surya returns for a *text* block rather than an equation.

pdf-equations.py as of commit 98ffa50 with three edits made by sed: blocks are
labelled Text instead of Equation, and the model's raw HTML is returned as is.
Run on the four garbled blocks of Meta-Learning (metalearn-text-boxes.json):

    <marker-python> eq-text.py <metalearn.pdf> < metalearn-text-boxes.json

The original docstring follows.

Read the equations of a PDF as LaTeX, given where they are on the pages.

    <marker-python> scripts/pdf-equations.py <paper.pdf> < boxes.json > latex.json

Called by pdf-to-markdown.py, which finds the equations with docling and
needs their LaTeX: a PDF's text layer holds an equation only as scattered
glyphs. stdin is a JSON list of {"page": 1, "bbox": [x0, y0, x1, y1]}, pages
counted from 1 and boxes in PDF points from the page's top-left corner. stdout
is a JSON list of the same length: each equation's LaTeX, or "" where the
model returned nothing.

Each box is cropped from the rendered page and read by surya's recognition
model, the one marker uses for equations (a vision-language model served by
llama.cpp). It runs in marker's own Python environment, because marker and
docling pin different versions of the same libraries; pdf-to-markdown.py
knows where that environment is.
"""

import html
import json
import re
import sys

import pypdfium2
from marker.schema import BlockTypes
from marker.schema.labels import block_type_to_surya_label
from surya.layout.schema import LayoutBox, LayoutResult
from surya.recognition import RecognitionPredictor

SCALE = 300 / 72  # render at 300 dpi: pixels per PDF point
PAD = 3  # points added around a box; docling's boxes are tight, a wider margin pulls in the text nearby
TOKEN_BUDGET = 2000  # marker's budget for one equation


def main(pdf_path):
    boxes = json.load(sys.stdin)
    pdf = pypdfium2.PdfDocument(pdf_path)
    label = block_type_to_surya_label(BlockTypes.Text)
    by_page = {}
    for index, box in enumerate(boxes):
        by_page.setdefault(box["page"], []).append((index, box["bbox"]))

    images, layouts, indexes = [], [], []
    for page_no, entries in sorted(by_page.items()):
        image = pdf[page_no - 1].render(scale=SCALE).to_pil().convert("RGB")
        layout_boxes = []
        for position, (_, (x0, y0, x1, y1)) in enumerate(entries):
            x0, y0, x1, y1 = ((v + d) * SCALE for v, d in zip((x0, y0, x1, y1), (-PAD, -PAD, PAD, PAD)))
            layout_boxes.append(LayoutBox(
                polygon=[[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
                label=label, raw_label="Text", position=position, count=TOKEN_BUDGET,
            ))
        images.append(image)
        layouts.append(LayoutResult(bboxes=layout_boxes, image_bbox=[0, 0, *image.size]))
        indexes.append([index for index, _ in entries])

    latex = [""] * len(boxes)
    if images:
        results = RecognitionPredictor()(images=images, layout_results=layouts, full_page=False)
        for page_indexes, result in zip(indexes, results):
            for index, block in zip(page_indexes, result.blocks):
                if block.error or not block.html:
                    continue
                # The model answers in HTML: <math display="block">LaTeX</math>.
                latex[index] = block.html; continue
                text = "\n".join(maths) if maths else re.sub(r"<[^>]+>", "", block.html)
                latex[index] = html.unescape(text).strip()
    json.dump(latex, sys.stdout)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
