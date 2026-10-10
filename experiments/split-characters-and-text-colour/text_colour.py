#!/usr/bin/env python3
"""Which tables get a <mark> for coloured text, over every cached arXiv rendering.

    uv run python text_colour.py [<cache>/arxiv/html] > text-colour.tsv

One row per table float that has no cell shading and gets a mark from the
converter's mark_shading (scripts/html-to-markdown.py): the paper, the float's
id, the marks, the float's cells with text, and the start of its caption.
Before the change these floats got none. The summary goes to stderr.
"""

import gzip
import importlib.util
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("html_to_markdown", SCRIPTS / "html-to-markdown.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


def main(cache):
    print("paper\tfloat\tmarks\tcells\tcaption")
    papers, floats, coloured, marks = 0, 0, 0, 0
    marked_papers = set()
    for path in sorted(Path(cache).glob("*/index.html.gz")):
        papers += 1
        html = gzip.open(path, "rt", encoding="utf-8", errors="replace").read()
        for m in converter.TABLE_FLOAT.finditer(html):
            end = converter.balanced_end(html, m.start(), "figure")
            if end is None:
                continue
            body = html[m.start():end]
            floats += 1
            if "--ltx-bg-color" in body or "--ltx-fg-color" not in body:
                continue
            coloured += 1
            n = converter.mark_shading(body, "caption").count("<mark>")
            if not n:
                continue
            marks += n
            marked_papers.add(path.parent.name)
            cells = sum(bool(converter.cell_text(c.group(3))) for c in converter.TABLE_CELL.finditer(body))
            caption = converter.cell_text(" ".join(re.findall(r"<figcaption\b.*?</figcaption>", body, re.S)))
            float_id = re.search(r'id="([^"]+)"', m.group(0))
            print(f"{path.parent.name}\t{float_id.group(1) if float_id else ''}\t{n}\t{cells}\t"
                  f"{' '.join(caption.split())[:160]}")
    print(f"{papers} renderings, {floats} table floats, {coloured} with coloured text and no shading; "
          f"{marks} marks in {len(marked_papers)} papers", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else Path.home() / ".cache/papers/arxiv/html")
