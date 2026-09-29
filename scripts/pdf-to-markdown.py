#!/usr/bin/env python3
"""Extract a PDF's text layer into rough markdown.

    ./scripts/pdf-to-markdown.py <input.pdf> <output.md>

This is the fallback conversion used by `add-arxiv-paper.sh` when arXiv has no
HTML rendering for a paper, and the only conversion available to
`add-pdf-paper.sh` for papers that were never on arXiv at all. It is markedly
worse than converting arXiv's own HTML: section structure, tables and figures
do not survive. Both callers therefore stamp a warning at the top of the
markdown they write.

PyMuPDF's block-sorted extraction gets two-column reading order roughly right.
The post-processing undoes the PDF's hard line wrapping, which would otherwise
leave every printed line as its own markdown line.
"""

import re
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("error: PDF conversion needs PyMuPDF — pip install pymupdf")


def convert(pdf_path):
    doc = pymupdf.open(pdf_path)
    text = "\n\n".join(page.get_text("text", sort=True) for page in doc)

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
