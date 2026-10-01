#!/usr/bin/env python3
"""Read equations, and text with mathematics in it, from the pages of a PDF.

    <marker-python> scripts/pdf-equations.py <paper.pdf> < boxes.json > read.json

Called by pdf-to-markdown.py, which finds the blocks with docling and needs
them read from the page image: a PDF's text layer holds an equation only as
scattered glyphs, and in some PDFs (made with Word, mostly) the symbols in
running text are missing too. stdin is a JSON list of {"page": 1, "bbox":
[x0, y0, x1, y1], "kind": "equation" | "text"}, pages counted from 1 and
boxes in PDF points from the page's top-left corner. stdout is a JSON list
of the same length: an equation's LaTeX, or a text block as markdown with its
mathematics as $...$; "" where the model returned nothing.

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
# Points added around a box. docling's boxes are tight, which clips an
# equation's subscripts; a wider margin pulls in the lines above and below.
PAD = {"equation": 3, "text": 1}
KINDS = {"equation": BlockTypes.Equation, "text": BlockTypes.Text}
TOKEN_BUDGET = 2000  # marker's budget for one equation


def main(pdf_path):
    boxes = json.load(sys.stdin)
    pdf = pypdfium2.PdfDocument(pdf_path)
    by_page = {}
    for index, box in enumerate(boxes):
        by_page.setdefault(box["page"], []).append((index, box["bbox"], box.get("kind", "equation")))

    images, layouts, indexes = [], [], []
    for page_no, entries in sorted(by_page.items()):
        image = pdf[page_no - 1].render(scale=SCALE).to_pil().convert("RGB")
        layout_boxes = []
        for position, (_, (x0, y0, x1, y1), kind) in enumerate(entries):
            pad = PAD[kind]
            x0, y0, x1, y1 = ((v + d) * SCALE for v, d in zip((x0, y0, x1, y1), (-pad, -pad, pad, pad)))
            layout_boxes.append(LayoutBox(
                polygon=[[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
                label=block_type_to_surya_label(KINDS[kind]), raw_label=kind.capitalize(),
                position=position, count=TOKEN_BUDGET,
            ))
        images.append(image)
        layouts.append(LayoutResult(bboxes=layout_boxes, image_bbox=[0, 0, *image.size]))
        indexes.append([(index, kind) for index, _, kind in entries])

    latex = [""] * len(boxes)
    if images:
        results = RecognitionPredictor()(images=images, layout_results=layouts, full_page=False)
        for page_indexes, result in zip(indexes, results):
            for (index, kind), block in zip(page_indexes, result.blocks):
                if block.error or not block.html:
                    continue
                if kind == "text":
                    latex[index] = text_markdown(block.html)
                    continue
                # The model answers in HTML: <math display="block">LaTeX</math>.
                maths = re.findall(r"<math\b[^>]*>(.*?)</math>", block.html, re.S)
                text = "\n".join(maths) if maths else re.sub(r"</?[a-zA-Z][^<>]*>", "", block.html)
                latex[index] = html.unescape(text).strip()
    json.dump(latex, sys.stdout)


def text_markdown(block_html):
    """A text block's HTML from the model as markdown, its mathematics as $...$."""
    text = re.sub(r'<math\b[^>]*display="block"[^>]*>(.*?)</math>',
                  lambda m: f" $${m.group(1).strip()}$$ ", block_html, flags=re.S)
    text = re.sub(r"<math\b[^>]*>(.*?)</math>", lambda m: f"${m.group(1).strip()}$", text, flags=re.S)
    text = re.sub(r"</?(?:b|strong)>", "**", text)
    text = re.sub(r"</?(?:i|em)>", "*", text)
    text = re.sub(r"</p>\s*<p>|<br\s*/?>", " ", text)
    text = re.sub(r"</?[a-zA-Z][^<>]*>", "", text)
    return " ".join(html.unescape(text).split())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
