#!/usr/bin/env python3
"""Where a quote, table, figure or equation is printed in a paper's PDF, as a link that
opens the page with the place marked (experiments/pdf-locations):

    paperlib locate <paper> <target> ...

<paper> is the paper's text file under the library, its PDF, or its title as its file is
named. Each target is `[page:]what`, where `what` is `table.N`, `figure.N`, `eq.N`, a quote
copied from the paper's text, or `table.N>quote` / `figure.N>quote` for a quote inside that
float (a value in a table's cell). The page is tried first, then the whole paper.

Prints one line per target: the target, then the link with `rect=`, or why there is
none and the page's link without it.
"""

import math
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote

try:
    # PyMuPDF 2 finds tables with a layout model run by onnxruntime, which would otherwise send
    # usage events and print warnings into the agent's output.
    import onnxruntime

    onnxruntime.disable_telemetry_events()
    onnxruntime.set_default_logger_severity(3)
except (ImportError, AttributeError):
    pass
import pymupdf

from paperlib import LIBRARY_DIR, PAPER_SUFFIXES, PDF_LINK_BASE, PDF_ROOT, paper_file_for, paper_stem, pdf_path_for

FLOATS = {"table": "table", "tab": "table", "figure": "figure", "fig": "figure",
          "eq": "equation", "equation": "equation"}
_TARGET = re.compile(r"^(?:(\d+):)?(.*)$", re.S)
_FLOAT = re.compile(r"^(table|tab|figure|fig|eq|equation)\.(\w+(?:\.\w+)?)$", re.I)
_WORD = re.compile(r"[A-Za-z]{4,}")
_CAPTION = re.compile(r"^(table|tab\.|figure|fig\.)\s*([A-Z]?\d+(?:\.\d+)?[a-z]?)\s*([:.|—–-]|$)", re.I)

# Growing a float's region from its caption: the most whitespace allowed between two of
# its parts, in points, and how far a table found by PyMuPDF may sit from its caption.
FLOAT_GAP = 18
TABLE_GAP = 30
TABLE_NOTE_GAP = 8
# Kept between a float and the running text it ends at, where a drawing's box reaches into it.
CLEARANCE = 5
EQUATION_GAP = 6
# Running heads and page numbers live in these margins (a share of the page's height).
MARGIN = 0.06


def fold(text):
    """Text as quotes are compared: NFKC (ligatures), lower case, letters and digits only,
    so spacing, hyphenation at line ends and punctuation never decide a match."""
    return "".join(c for c in unicodedata.normalize("NFKC", text).lower() if c.isalnum())


def parse_target(text):
    """`[page:]what` -> (page or None, kind, label, quote): kind is 'quote', 'table',
    'figure' or 'equation'; a float with `>quote` searches the quote inside it."""
    page, what = _TARGET.match(text.strip()).groups()
    page = int(page) if page else None
    head, sep, inner = what.partition(">")
    m = _FLOAT.match(head.strip())
    if m:
        return page, FLOATS[m.group(1).lower()], m.group(2), inner.strip() if sep else None
    return page, "quote", None, what.strip().strip("\"'“”")


def link(pdf, page, rects=None):
    """The `pdf.invalid` link to a page of a PDF, with its rectangles when there are any."""
    try:
        rel = Path(pdf).resolve().relative_to(PDF_ROOT.resolve()).as_posix()
    except ValueError:
        rel = None
    path = quote(rel, safe="/&+'(),;=!$*@~[]") if rel else "open?file=" + quote(str(pdf), safe="/")
    query = f"page={page}"
    if rects:
        query += "&rect=" + ";".join(",".join(str(v) for v in r) for r in rects)
    return f"{PDF_LINK_BASE}{path}{'&' if rel is None else '?'}{query}"


def _box(rects):
    """The smallest box around (x0, y0, x1, y1) boxes."""
    return (min(r[0] for r in rects), min(r[1] for r in rects), max(r[2] for r in rects), max(r[3] for r in rects))


def _contains(outer, inner):
    return outer[0] <= inner[0] and outer[1] <= inner[1] and outer[2] >= inner[2] and outer[3] >= inner[3]


def _outward(r):
    """A box in whole points, rounded outward."""
    return (math.floor(r[0]), math.floor(r[1]), math.ceil(r[2]), math.ceil(r[3]))


class Page:
    """One PDF page as `locate` reads it: its words, lines and graphics, in points from
    the top-left corner of the page's crop box, unrotated (what a link's `rect` holds)."""

    def __init__(self, page):
        self.page = page
        self.number = page.number + 1
        # Text comes in the page's rotated space; links hold the unrotated page.
        self.matrix = page.derotation_matrix if page.rotation else None
        self.width, self.height = page.cropbox.width, page.cropbox.height
        self._words = self._lines = self._layout = None

    def unrotated(self, r):
        if self.matrix is None:
            return tuple(r)
        box = pymupdf.Rect(r) * self.matrix
        return (box.x0, box.y0, box.x1, box.y1)

    @property
    def words(self):
        """[(box, text, block, line)] in the order the PDF draws them, which is reading order
        for the papers measured (experiments/pdf-locations)."""
        if self._words is None:
            self._words = [(self.unrotated(w[:4]), w[4], w[5], w[6])
                           for w in self.page.get_text("words", flags=pymupdf.TEXTFLAGS_WORDS)]
        return self._words

    @property
    def lines(self):
        """[{box, text, size, block, across}] for every line of text; `across` is false for
        text set sideways (an axis label, arXiv's stamp in the margin)."""
        if self._lines is None:
            self._lines = []
            for block in self.page.get_text("dict", flags=pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES)["blocks"]:
                for line in block.get("lines", []):
                    spans = [s for s in line["spans"] if s["text"].strip()]
                    if not spans:
                        continue
                    chars = sum(len(s["text"]) for s in spans)
                    size = sum(s["size"] * len(s["text"]) for s in spans) / chars
                    self._lines.append({"box": self.unrotated(line["bbox"]), "block": block["number"], "size": size,
                                        "text": "".join(s["text"] for s in spans).strip(),
                                        "across": abs(line["dir"][0]) > 0.9})
        return self._lines

    @property
    def layout(self):
        """(left, right, body size, two columns): the text's extent, the size most of the
        text is set in, and whether the page sets its text in two columns."""
        if self._layout is None:
            # Not text set sideways: arXiv's stamp in the left margin would move the text's edge.
            lines = [l for l in self.lines if l["across"] and self.height * MARGIN < l["box"][1] < self.height * (1 - MARGIN)]
            if not lines:
                self._layout = (0, self.width, 10, False)
                return self._layout
            sizes = {}
            for l in lines:
                sizes[round(l["size"], 1)] = sizes.get(round(l["size"], 1), 0) + len(l["text"])
            body = max(sizes, key=sizes.get)
            left = min(l["box"][0] for l in lines)
            right = max(l["box"][2] for l in lines)
            mid = (left + right) / 2
            wide = [l for l in lines if l["box"][2] - l["box"][0] > (right - left) * 0.2]
            halves = sum(1 for l in wide if l["box"][2] < mid + 5 or l["box"][0] > mid - 5)
            self._layout = (left, right, body, bool(wide) and halves > 0.7 * len(wide))
        return self._layout

    def column(self, box):
        """The x-range of the column a box sits in: a half of a two-column page, or the
        whole text width."""
        left, right, _, two = self.layout
        mid = (left + right) / 2
        if two and box[2] <= mid + 10:
            return left, mid
        if two and box[0] >= mid - 10:
            return mid, right
        return left, right

    def find_quote(self, text, within=None):
        """Every place a quote is printed, each as the list of its words. A match starts and
        ends at word boundaries; `within` limits it to words whose middle is in a box."""
        wanted = fold(text)
        if not wanted:
            return []
        words = self.words
        if within:
            words = [w for w in words if within[0] <= (w[0][0] + w[0][2]) / 2 <= within[2]
                     and within[1] <= (w[0][1] + w[0][3]) / 2 <= within[3]]
        stream, owner, starts = [], [], set()
        for i, w in enumerate(words):
            folded = fold(w[1])
            if folded:
                starts.add(len(stream))
                stream.extend(folded)
                owner.extend([i] * len(folded))
        stream = "".join(stream)
        bounded, inside, at = [], [], stream.find(wanted)
        while at >= 0:
            end = at + len(wanted)
            match = [words[i] for i in range(owner[at], owner[end - 1] + 1)]
            if at in starts and (end == len(stream) or end in starts):
                bounded.append(match)
            inside.append(match)
            at = stream.find(wanted, at + 1)
        # Inside words only when nothing matches at word boundaries: some PDFs print a
        # line without spaces, and the whole line is then one word.
        return bounded or inside

    def line_boxes(self, words):
        """Matched words as one box per printed line."""
        boxes = []
        for w in words:
            box = w[0]
            last = boxes[-1] if boxes else None
            # Same printed line: the boxes overlap vertically by most of their height.
            if last and min(last[3], box[3]) - max(last[1], box[1]) > 0.5 * min(last[3] - last[1], box[3] - box[1]) \
                    and box[0] - last[2] < 3 * (box[3] - box[1]):
                boxes[-1] = _box([last, box])
            else:
                boxes.append(box)
        return boxes

    def caption(self, kind, label):
        """The box of a table's or figure's caption, from its first line on: the rest of
        that block, and the lines that continue it in the next blocks. None when the page
        has no such caption."""
        hits = []
        for i, l in enumerate(self.lines):
            m = _CAPTION.match(l["text"])
            if m and m.group(1).lower().startswith(kind[:3]) and m.group(2).lower() == label.lower():
                starts_block = i == 0 or self.lines[i - 1]["block"] != l["block"]
                hits.append((not starts_block, i))
        if not hits:
            return None
        i = min(hits)[1]
        first = self.lines[i]
        lines = [l for l in self.lines[i:] if l["block"] == first["block"]]
        box = _box([l["box"] for l in lines])
        height = first["box"][3] - first["box"][1]
        grew = True
        while grew:
            grew = False
            for l in self.lines:
                b = l["box"]
                if (0 <= b[1] - box[3] <= 0.6 * height and abs(l["size"] - first["size"]) < 0.5
                        and min(b[2], box[2]) - max(b[0], box[0]) > 0.5 * (b[2] - b[0])
                        and not _CAPTION.match(l["text"])):
                    box, grew = _box([box, b]), True
        return box

    def is_prose(self, block_lines, column):
        """Whether a block of lines is the paper's running text, which ends a float."""
        _, _, body, _ = self.layout
        width = column[1] - column[0]
        text = "".join(l["text"] for l in block_lines)
        letters = sum(c.isalpha() for c in text)
        digits = sum(c.isdigit() for c in text)
        if not letters or abs(sum(l["size"] for l in block_lines) / len(block_lines) - body) > 0.6:
            return False
        # Printed rows, not PyMuPDF's lines: a bold run-in heading is a line of its own.
        rows = []
        for l in sorted(block_lines, key=lambda l: l["box"][1]):
            if rows and l["box"][1] < rows[-1][3] - 0.5 * (l["box"][3] - l["box"][1]):
                rows[-1] = _box([rows[-1], l["box"]])
            else:
                rows.append(l["box"])
        # Letters, not words: some PDFs print a justified line without spaces.
        widest = max(r[2] - r[0] for r in rows)
        return widest > 0.8 * width and letters / len(rows) >= 0.5 * width / body and letters > 3 * digits

    @property
    def tables(self):
        """The boxes of the tables PyMuPDF finds on the page."""
        if not hasattr(self, "_tables"):
            self._tables = [self.unrotated(t.bbox) for t in self.page.find_tables().tables]
        return self._tables

    def captioned_tables(self):
        """The tables with a table caption next to them: a figure may be made of tables
        of its own, which do not end it."""
        captions = [self.caption("table", m.group(2)) for l in self.lines
                    if (m := _CAPTION.match(l["text"])) and m.group(1).lower().startswith("tab")]
        return [t for t in self.tables
                if any(min(abs(t[1] - c[3]), abs(c[1] - t[3])) <= TABLE_GAP and min(t[2], c[2]) > max(t[0], c[0])
                       for c in captions)]

    def parts(self, column, stop_at_tables):
        """What may make up a float in a column, each as (box, what): what is 'text',
        'graphic' (a drawn path or an image), or 'stop', which ends a float: running text,
        another float's caption, and with `stop_at_tables` a table."""
        lo, hi = column
        top, bottom = self.height * MARGIN, self.height * (1 - MARGIN)

        def inside(box):
            overlap = min(box[2], hi) - max(box[0], lo)
            return overlap > 0.5 * max(box[2] - box[0], 1) and box[3] > top and box[1] < bottom

        tables = self.captioned_tables() if stop_at_tables else []

        def in_table(box):
            x, y = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            return any(t[0] <= x <= t[2] and t[1] <= y <= t[3] for t in tables)

        parts = []
        blocks = {}
        for l in self.lines:
            blocks.setdefault(l["block"], []).append(l)
        for lines in blocks.values():
            box = _box([l["box"] for l in lines])
            if inside(box):
                stop = self.is_prose(lines, column) or _CAPTION.match(lines[0]["text"]) or in_table(box)
                parts.append((box, "stop" if stop else "text"))
        for d in self.page.get_drawings():
            box = self.unrotated(d["rect"])
            if box[2] - box[0] > 0.9 * self.width and box[3] - box[1] > 0.9 * self.height:
                continue  # a page background
            if inside(box):
                parts.append((box, "stop" if in_table(box) else "graphic"))
        for info in self.page.get_image_info():
            box = self.unrotated(info["bbox"])
            if inside(box):
                parts.append((box, "graphic"))
        return parts

    def grow(self, start, column, up, gap=FLOAT_GAP, text_only=False, stop_at_tables=False):
        """A float's region, grown from a box (its caption) up or down through the parts
        that make it up, while the whitespace between them stays under `gap`; it ends at
        running text or another float, and never reaches into them."""
        parts = [p for p in self.parts(column, stop_at_tables)
                 if (p[0][3] <= start[1] + 2 if up else p[0][1] >= start[3] - 2) and not _contains(start, p[0])]
        parts.sort(key=lambda p: -p[0][3] if up else p[0][1])
        region, edge = None, start[1] if up else start[3]
        for box, what in parts:
            if what == "stop" or ((edge - box[3]) if up else (box[1] - edge)) > gap:
                break
            if text_only and what != "text":
                continue
            region = _box([region, box]) if region else box
            edge = min(edge, box[1]) if up else max(edge, box[3])
        stops = [b for b, what in parts if what == "stop"]
        if region and stops:
            # A drawing's box can reach past the text where the float ends.
            if up:
                region = (region[0], max(region[1], max(b[3] for b in stops) + CLEARANCE), region[2], region[3])
            else:
                region = (region[0], region[1], region[2], min(region[3], min(b[1] for b in stops) - CLEARANCE))
        return region

    def find_float(self, kind, label):
        """A table's or figure's region with its caption, or (None, why)."""
        caption = self.caption(kind, label)
        if not caption:
            return None, f"no caption \"{kind.title()} {label}\""
        column = self.column(caption)
        if kind == "table":
            for box in self.tables:
                near = min(abs(box[1] - caption[3]), abs(caption[1] - box[3]))
                if near <= TABLE_GAP and min(box[2], caption[2]) > max(box[0], caption[0]):
                    region = _box([caption, box])
                    # Rows above the rules and the table's notes below them, which the
                    # table finder leaves out.
                    above = box[1] < caption[1]
                    more = self.grow(region, column, above, gap=TABLE_NOTE_GAP, text_only=True)
                    return _box([region, more]) if more else region, None
        # Tables are captioned above, figures below; the other side is the fallback.
        first = kind != "table"
        for up in (first, not first):
            region = self.grow(caption, column, up, stop_at_tables=kind == "figure")
            if region:
                return _box([caption, region]), None
        return caption, None

    def find_equation(self, label):
        """A display equation's region from its number "(N)" at the column's right, or
        (None, why)."""
        wanted = fold(f"({label})")
        hits = []
        for w in self.words:
            if fold(w[1]) == wanted and w[1].strip().startswith("(") and w[1].strip().endswith(")"):
                lo, hi = self.column(w[0])
                if w[0][2] >= hi - 0.2 * (hi - lo):
                    hits.append(w)
        if not hits:
            return None, f"no equation number ({label})"
        if len(hits) > 1:
            return None, f"{len(hits)} equation numbers ({label})"
        number = hits[0][0]
        column = self.column(number)
        # Printed rows of the column: PyMuPDF splits a line of text where maths interrupts it.
        printed = []
        for l in sorted(self.lines, key=lambda l: (l["box"][1] + l["box"][3]) / 2):
            box = l["box"]
            if min(box[2], column[1]) - max(box[0], column[0]) <= 0 or _contains(box, number):
                continue
            last = printed[-1][0] if printed else None
            if last and min(last[3], box[3]) - max(last[1], box[1]) > 0.5 * min(last[3] - last[1], box[3] - box[1]):
                printed[-1] = (_box([printed[-1][0], box]), printed[-1][1] + " " + l["text"])
            else:
                printed.append((box, l["text"]))
        rows = []
        for box, text in printed:
            words = len(_WORD.findall(text))
            # Running text says words; a display equation, at most "where" or "for all". The
            # end of the sentence that leads into it ("wise computation:") starts the column.
            if words >= 6 or (words >= 2 and box[0] <= column[0] + 15):
                continue
            rows.append(box)
        for d in self.page.get_drawings():
            box = self.unrotated(d["rect"])
            if box[3] - box[1] < 3 and min(box[2], column[1]) - max(box[0], column[0]) > 0:
                rows.append(box)  # fraction bars and rules
        region = number
        grew = True
        while grew:
            grew = False
            for box in rows:
                if box[1] < region[3] + EQUATION_GAP and box[3] > region[1] - EQUATION_GAP and not _contains(region, box):
                    region, grew = _box([region, box]), True
        return region, None


def _find(pages, kind, label, text):
    """A target on some pages: (page, rects, None), or (page or None, None, why)."""
    if kind == "quote":
        found = [(p, m) for p in pages for m in p.find_quote(text)]
        if not found:
            return None, None, "not found"
        if len(found) > 1:
            hit = sorted({p.number for p, _ in found})
            return hit[0], None, f"{len(found)} matches on p. {', '.join(map(str, hit))}: lengthen the quote"
        page, words = found[0]
        return page.number, [_outward(b) for b in page.line_boxes(words)], None
    results, whys = [], []
    for page in pages:
        region, why = page.find_equation(label) if kind == "equation" else page.find_float(kind, label)
        if region:
            results.append((page, region))
        elif why not in whys:
            whys.append(why)
    if not results:
        return None, None, whys[0] if len(whys) == 1 else f"no {kind} {label}"
    if len(results) > 1:
        return results[0][0].number, None, f"{kind} {label} on p. {', '.join(str(p.number) for p, _ in results)}: give the page"
    page, region = results[0]
    if text is None:
        return page.number, [_outward(region)], None
    found = page.find_quote(text, within=region)
    if len(found) != 1:
        why = "not found" if not found else f"{len(found)} matches: lengthen the quote"
        return page.number, None, f"\"{text}\" in {kind} {label}: {why}"
    return page.number, [_outward(b) for b in page.line_boxes(found[0])], None


def locate(doc, target):
    """One target in an open PDF: (page, rects, why). The page a target names is tried
    first, then the whole paper: an agent often names the page that mentions a table rather
    than the one it is printed on. `rects` is None when the target is not found once, and
    `why` says why; `page` is where it was found, or the page to link to without a mark."""
    page_no, kind, label, text = parse_target(target)
    if kind == "quote" and not fold(text or ""):
        return page_no, None, "an empty quote"
    if page_no is not None and not 1 <= page_no <= doc.page_count:
        page_no = None
    every = [Page(p) for p in doc]
    if page_no:
        page, rects, why = _find([every[page_no - 1]], kind, label, text)
        if rects or page:
            return page, rects, why
    page, rects, why = _find(every, kind, label, text)
    if not rects and not page:
        return page_no, None, f"{why} in the paper"
    return page, rects, why


def pdf_for(arg):
    """The PDF for a paper given as its text file, its PDF, a path under the library, or its
    file's name alone (the title, as a filename)."""
    path = Path(arg).expanduser()
    if path.suffix.lower() == ".pdf":
        return path
    if not path.is_absolute() and not path.exists():
        if (LIBRARY_DIR / path).exists() or paper_file_for(LIBRARY_DIR / path).exists():
            path = LIBRARY_DIR / path
        elif len(path.parts) == 1:
            stem = paper_stem(path)
            named = [p for suffix in PAPER_SUFFIXES for p in LIBRARY_DIR.rglob(f"*{suffix}")
                     if paper_stem(p) == stem]
            if len(named) == 1:
                path = named[0]
    return pdf_path_for(paper_file_for(path))


def main(argv):
    if len(argv) < 2 or argv[0] in {"-h", "--help"}:
        print(__doc__.strip())
        return 0 if argv[:1] in (["-h"], ["--help"]) else 2
    try:
        pdf = pdf_for(argv[0])
    except ValueError:
        print(f"paperlib locate: {argv[0]} is not a paper under {LIBRARY_DIR}", file=sys.stderr)
        return 2
    if not pdf.is_file():
        print(f"paperlib locate: no PDF for {paper_stem(argv[0])} (looked at {pdf})", file=sys.stderr)
        return 2
    failed = 0
    with pymupdf.open(pdf) as doc:
        for target in argv[1:]:
            page, rects, why = locate(doc, target)
            asked = parse_target(target)[0]
            moved = f"(on p. {page}) " if page and asked and page != asked else ""
            if rects:
                print(f"{target}  {moved}{link(pdf, page, rects)}")
            else:
                failed += 1
                print(f"{target}  {why}" + (f"; page link: {link(pdf, page)}" if page else ""))
    return 1 if failed == len(argv) - 1 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
