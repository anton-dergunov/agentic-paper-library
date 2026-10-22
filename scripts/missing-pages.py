#!/usr/bin/env python3
"""Put into an arXiv-HTML paper the pages of its PDF that arXiv's HTML lacks.

    ./scripts/missing-pages.py <paper.pdf> <paper.md>

arXiv's HTML can stop partway through a paper, leave out its appendices, or drop a
page of results tables that LaTeXML could not set (ticket html-incomplete). Run after
page-map.py, this finds the pages whose text the markdown lacks (page-map.py's
missing_pages), converts them as pdf-to-markdown.py converts a paper with no HTML
(convert_pages: layout analysis, equations and inline mathematics read by a model), and
puts each run of pages where it belongs: before the first heading on a later page, so a
run before the references goes before them and the reading view keeps it. A page the
measure flags whose text is all in a picture (a plot's labels, examples set as a
figure) is left out, since the HTML has the picture; a page with little text between
two missing ones (a page of figures in a stretch the HTML lacks) is taken with them.

Each run is marked, so an agent knows to check the PDF before quoting an equation or a
table from it:

    <!-- pp. 10–55 from the PDF, not in arXiv's HTML. … -->
    …
    <!-- end of pp. 10–55 from the PDF -->

Its figures are numbered after the HTML's. Prints one line: the pages taken, and those
left out.
"""

import importlib.util
import re
import sys
from pathlib import Path

import pymupdf

SCRIPTS = Path(__file__).resolve().parent
HEADING = re.compile(r"^#{1,6} .*?(?:\(p\. (\d+)\))?\s*$")
REFERENCES = re.compile(r"^#{1,3} +(?:References|Bibliography|REFERENCES)\b")
REFERENCES_LINE = re.compile(r"(?:\d+\.?\s+)?(?:References|Bibliography|REFERENCES|BIBLIOGRAPHY)")
MARK = ("<!-- {pages} from the PDF, not in arXiv's HTML. Converted by layout analysis{equations};"
        " check the PDF before quoting a table whose columns look off. -->")
EQUATIONS = ", equations read from the page image by a model (check the PDF before quoting one)"


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def candidates(doc, markdown, page_map):
    """The pages to convert: those missing_pages finds, and a page with little text
    between two of them."""
    missing, _ = page_map.missing_pages(doc, markdown)
    missing = set(missing)
    sparse = {n for n, page in enumerate(doc, 1) if len(page_map.text_words(page.get_text())) < 120}
    out = set(missing)
    for p in sparse:
        before = [q for q in missing if q < p and all(r in sparse for r in range(q + 1, p))]
        after = [q for q in missing if q > p and all(r in sparse for r in range(p + 1, q))]
        if before and after:
            out.add(p)
    return out


def references_page(doc, lines, page_map):
    """The PDF page the reference list starts on: its heading's (p. N); else the first page
    with a quarter of its text in the markdown's list; else, since a truncated HTML lists
    only the works its part cites, the first page after the markdown's last placed heading
    with a line that is only "References" (a contents page aside). None without a list."""
    start = next((i for i, line in enumerate(lines) if REFERENCES.match(line)), None)
    if start is None:
        return None
    m = HEADING.match(lines[start])
    if m and m.group(1):
        return int(m.group(1))
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"#{1,3} ", lines[i])), len(lines))
    words = page_map.text_words("\n".join(lines[start:end]))
    listed = set(zip(words, words[1:], words[2:]))
    texts = [page.get_text() for page in doc]
    for n, text in enumerate(texts, 1):
        words = page_map.text_words(text)
        grams = list(zip(words, words[1:], words[2:]))
        if len(grams) >= 100 and sum(g in listed for g in grams) >= 0.25 * len(grams):
            return n
    placed = [int(m.group(1)) for line in lines[:start] if (m := HEADING.match(line)) and m.group(1)]
    return list_heading_page(texts, max(placed, default=0), page_map)


def list_heading_page(texts, after, page_map):
    """The first page after `after` with a line that is only a reference list's heading,
    a contents page (dot leaders) aside; None if there is none."""
    for n, text in enumerate(texts, 1):
        if n > after and len(page_map.DOT_LEADER.findall(text)) < 5 and any(
                REFERENCES_LINE.fullmatch(line.strip()) for line in text.splitlines()):
            return n
    return None


def place(lines, last, refs_page):
    """The line a run of pages ending at `last` goes before: the first heading on a
    later page, the reference list counting as on `refs_page`; else the end."""
    in_fence = False
    for i, line in enumerate(lines):
        if line.startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else HEADING.match(line)
        if not m:
            continue
        page = int(m.group(1)) if m.group(1) else (refs_page if REFERENCES.match(line) else None)
        if page is not None and page > last:
            return i
    return len(lines)


def next_figure(md):
    """The number after the highest of the paper's figure files."""
    images = md.parent / "images"
    numbers = [int(m.group(1)) for f in (images.iterdir() if images.exists() else [])
               if f.name.startswith(md.stem + "-fig") and (m := re.match(r"(\d+)", f.name[len(md.stem) + 4:]))]
    return max(numbers, default=0) + 1


def main(pdf_path, md_path):
    md = Path(md_path)
    page_map, pdf = load("page-map"), load("pdf-to-markdown")
    pymupdf.TOOLS.mupdf_display_errors(False)
    text = md.read_text(encoding="utf-8")
    with pymupdf.open(pdf_path) as doc:
        pages = candidates(doc, text, page_map)
        if not pages:
            print("missing pages: none")
            return
        lines = text.split("\n")
        refs_page = references_page(doc, lines, page_map)
    runs, left, equations = pdf.convert_pages(pdf_path, pages, md.parent / "images", md.stem, next_figure(md))
    inserts = {}  # line index: the runs that go before it, in page order
    for first, last, body in runs:
        span = ("p. " if first == last else "pp. ") + page_map.page_ranges(list(range(first, last + 1)))
        mark = MARK.format(pages=span, equations=EQUATIONS if equations == "model" else "")
        block = f"{mark}\n\n{body.strip()}\n\n<!-- end of {span} from the PDF -->"
        inserts.setdefault(place(lines, last, refs_page), []).append(block)
    for i in sorted(inserts, reverse=True):
        lines[i:i] = ["\n\n".join(inserts[i]), ""] if i < len(lines) else ["", "\n\n".join(inserts[i])]
    md.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    taken = [p for first, last, _ in runs for p in range(first, last + 1)]
    message = f"missing pages: {len(taken)} taken from the PDF" + (f" (pp. {page_map.page_ranges(taken)})" if taken else "")
    if left:
        message += f", {len(left)} left out as figures only (pp. {page_map.page_ranges(left)})"
    print(message)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
