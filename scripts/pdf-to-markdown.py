#!/usr/bin/env python3
"""Convert a PDF into markdown, for papers that have no HTML rendering.

    ./scripts/pdf-to-markdown.py <input.pdf> <output.md> [<images-dir> <basename>]
    ./scripts/pdf-to-markdown.py --fast <input.pdf> <output.md> ...
    ./scripts/pdf-to-markdown.py --raw-equations <input.pdf> <output.md> ...
    ./scripts/pdf-to-markdown.py --text-layer <input.pdf> <output.md>

Used by `add-arxiv-paper.sh` when arXiv has no HTML for a paper, by
`add-pdf-paper.sh` for papers that were never on arXiv, and by
`reconvert.py --pdf-text`. The output starts with a note saying how it was
converted and what to check in the PDF.

The conversion is docling's layout analysis (convert_layout): a layout model
finds the headings, paragraphs, lists, tables, figures and equations on each
page and their reading order, and a table model rebuilds each table's rows and
columns. The words and numbers themselves are the PDF's own text layer, not
OCR, so a number in a table is the number in the PDF. From docling's document
this script writes:
- headings, levelled by their numbering, each with the page it is on, "(p. N)",
  so scripts/page-map.py is not needed for these papers;
- tables as markdown tables, lists, code blocks and footnotes;
- figures as files in <images-dir>, named <basename>-figNN.webp, followed by
  their captions (left out when no images dir is given);
- equations as LaTeX, read from each equation's image by the model marker
  uses (scripts/pdf-equations.py, about two seconds an equation). A PDF's
  text layer holds an equation only as scattered glyphs, so a model is the
  only way to get it; it can misread, and the note at the top says so. With
  --raw-equations, or when that model is not installed, an equation is the
  PDF's raw text in a block marked as such. An equation read as only its
  number ("(7)") is read again from a crop 2 points wider, and, where its
  box is narrow (a formula with no text in the text layer), from the band
  between the blocks above and below (reread_number_only);
- bold, italics and underlining in table cells, which docling drops, from the
  font of each character under the cell and the rules drawn under it;
- text blocks whose mathematics the text layer lost (a PDF made with Word
  leaves "a task _ ~ ( )" where the symbols were) read by the same model, with
  the mathematics as $...$. A reading replaces the text layer's text only if
  it keeps the block's words and every number in it.
- every other text block with mathematics in it (text set in a mathematics
  font) read the same way, so that inline mathematics is LaTeX ("$q \\in
  \\mathbb{R}^n$") instead of the text layer's bare letters ("q ∈ R n"). On
  papers that also have arXiv HTML this reproduced 76-84% of the inline
  formulas and changed no prose or number (docs/library.md). It takes about
  eight seconds a paragraph, minutes for a paper with much mathematics;
  --fast leaves it out, for converting hundreds of papers at once.

docling does everything but the equations because it scored best against
arXiv's HTML on papers that have both (docs/library.md): every table number in
its table, the PDF's own digits. marker reads equations far better than
docling's own formula model, but splits decimals across table cells.

--text-layer, and any PDF docling fails on, uses the older extraction of the
text layer alone (convert_text_layer below), which keeps the prose but loses
section structure, tables and figures:

Reading order comes from pymupdf4llm's column detection (column_boxes): each
page is split into text regions in reading order, so a two-column paper reads
down the left column and then the right, instead of interleaving the two line
by line as a plain position sort does. The text itself is still PyMuPDF's raw
extraction, which keeps equations (flattened) where pymupdf4llm's own markdown
drops display maths (docs/library.md). A page whose
regions miss much of its text falls back to the plain sort.

Within a region, lines are rebuilt into:
- paragraphs, from line spacing and ragged line ends, with hyphenation undone;
- fenced code blocks, for runs of lines in a monospace font or that read as
  pseudocode (assignment arrows, "procedure", "for ... do"), with indentation
  kept from the lines' horizontal positions;
- one line per run of very short fragments (the cells of a figure or table),
  instead of one paragraph per number.
Lines repeated at the top or bottom of many pages (running headers, page
numbers) are dropped.
"""

import io
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote

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
MONO = re.compile(r"mono|courier|typewriter|cmtt|consol|menlo|inconsolata|lmtt|txtt|sourcecode", re.I)
ARROW = re.compile(r"←|:=")
KEYWORD = re.compile(
    r"^\s*(procedure|function|algorithm|for|foreach|while|repeat|until|if|else|elif|end|begin|"
    r"return|in parallel|def|do|then)\b", re.I)
SHORT = 12  # a "fragment" line: a figure or table cell


class Line:
    def __init__(self, bbox, text, mono, size, narrow):
        self.bbox, self.text, self.mono, self.size, self.narrow = bbox, text, mono, size, narrow

    @property
    def codey(self):
        # A keyword opening a line counts only on a short line: prose lines starting
        # "for example" or "if" run the full width of the column.
        return self.mono or bool(ARROW.search(self.text)) or (self.narrow and bool(KEYWORD.search(self.text)))


def region_lines(page, box):
    lines = []
    for block in page.get_text("dict", clip=box, sort=True)["blocks"]:
        for line in block.get("lines", []):
            spans = [s for s in line["spans"] if s["text"].strip()]
            text = "".join(s["text"] for s in line["spans"]).strip()
            if not text:
                continue
            mono_chars = sum(len(s["text"]) for s in spans if MONO.search(s["font"]))
            size = max((s["size"] for s in spans), default=10)
            narrow = line["bbox"][2] - line["bbox"][0] < 0.7 * (box[2] - box[0])
            lines.append(Line(line["bbox"], text, mono_chars > 0.6 * len(text), size, narrow))
    return lines


def join_prose(lines, box):
    """Lines of running text joined into paragraphs, from their geometry."""
    pitches = sorted(b.bbox[3] - a.bbox[3] for a, b in zip(lines, lines[1:]) if b.bbox[3] > a.bbox[3])
    pitch = pitches[len(pitches) // 2] if pitches else 12
    width = box[2] - box[0]
    paragraphs, current, prev = [], "", None
    for line in lines:
        text = line.text
        if prev is not None:
            step = line.bbox[3] - prev.bbox[3]
            short = prev.bbox[2] < box[2] - 0.12 * width
            if step > 1.4 * pitch or step < 0 or short:  # a gap, a jump back up, or a short last line
                paragraphs.append(current)
                current = ""
        if current.endswith("-") and text[:1].islower():
            # "personal-" + "isation" joins; a compound ("cost-per-" + "click") keeps its hyphen.
            last = current.rsplit(" ", 1)[-1]
            current = current + text if "-" in last[:-1] else current[:-1] + text
        else:
            current = f"{current} {text}" if current else text
        prev = line
    paragraphs.append(current)
    return paragraphs


def code_block(lines):
    """A fenced block keeping each line's indentation from its x position."""
    left = min(l.bbox[0] for l in lines)
    char = max(sorted(l.size for l in lines)[len(lines) // 2] * 0.5, 3)
    rows, prev = [], None
    for l in lines:
        col = round((l.bbox[0] - left) / char)
        if prev is not None and abs(l.bbox[3] - prev.bbox[3]) < 0.5 * l.size and rows:
            # Same baseline (e.g. a right-hand comment): continue the previous row.
            rows[-1] = rows[-1].ljust(col) if len(rows[-1]) < col else rows[-1] + "  "
            rows[-1] += l.text
        else:
            rows.append(" " * col + l.text)
        prev = l
    return "```text\n" + "\n".join(rows) + "\n```"


CODE_PUNCT = re.compile(r"[{}();=\[\]<>]|←|:=|\b(def|return|if|for|while|else)\b")


def looks_like_code(block):
    """Guards against runs that are code-like only on the surface."""
    text = "".join(l.text for l in block)
    if sum(c.isalpha() for c in text) < 0.3 * max(len(text), 1):
        return False  # numbers only: axis ticks, table columns
    if not any(l.narrow for l in block) and not any(CODE_PUNCT.search(l.text) for l in block):
        return False  # full-width lines with nothing code-like: prose set in a monospace font
    return True


def region_markdown(lines, box):
    """Split a region's lines into code runs, fragment runs and prose."""
    out, i = [], 0
    while i < len(lines):
        # A code run: two or more code-like lines, allowing one short plain line in between.
        j = i
        while j < len(lines) and (lines[j].codey or (
                j > i and j + 1 < len(lines) and lines[j + 1].codey and lines[j].narrow)):
            j += 1
        if j - i >= 2 and sum(l.codey for l in lines[i:j]) >= 2 and looks_like_code(lines[i:j]):
            out.append(code_block(lines[i:j]))
            i = j
            continue
        # A fragment run: three or more very short lines, e.g. the numbers in a figure.
        j = i
        while j < len(lines) and len(lines[j].text) <= SHORT and not lines[j].codey:
            j += 1
        if j - i >= 3:
            out.append(" ".join(l.text for l in lines[i:j]))
            i = j
            continue
        # Prose up to the next code or fragment run.
        j = i + 1
        while j < len(lines) and not lines[j].codey and not (
            len(lines[j].text) <= SHORT and j + 2 < len(lines)
            and len(lines[j + 1].text) <= SHORT and len(lines[j + 2].text) <= SHORT
        ):
            j += 1
        out.extend(join_prose(lines[i:j], box))
        i = j
    return out


def page_regions(page):
    """A page's text regions in reading order, or None to use the plain sort."""
    if column_boxes is None:
        return None
    try:
        boxes = column_boxes(page, footer_margin=MARGIN, header_margin=MARGIN)
    except Exception:
        return None
    regions = [(box, region_lines(page, box)) for box in boxes]
    covered = sum(len(l.text.replace(" ", "")) for _, ls in regions for l in ls)
    plain = len("".join(page.get_text("text", sort=True).split()))
    # Only trust the regions if they hold nearly all of the page's text (the
    # margins legitimately drop a header line and a page number).
    return regions if covered >= 0.9 * plain - 200 else None


def repeated_edges(doc, pages):
    """Texts that recur at the top or bottom of pages: running heads, page numbers."""
    seen = Counter()
    for page, regions in zip(doc, pages):
        if not regions:
            continue
        lines = sorted((l for _, ls in regions for l in ls), key=lambda l: l.bbox[1])
        edge = lines[:3] + lines[-2:]
        for l in edge:
            if l.bbox[1] < 0.15 * page.rect.height or l.bbox[3] > 0.88 * page.rect.height:
                seen[re.sub(r"\d+", "#", l.text)] += 1
    threshold = max(3, len(doc) // 4)
    return {t for t, n in seen.items() if n >= threshold or re.fullmatch(r"[#ivxlc.\s]+", t)}


def convert_text_layer(pdf_path):
    doc = pymupdf.open(pdf_path)
    pages = [page_regions(page) for page in doc]
    drop = repeated_edges(doc, pages)
    parts = []
    for page, regions in zip(doc, pages):
        if regions is None:
            text = page.get_text("text", sort=True)
            text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
            for block in re.split(r"\n\s*\n", text):
                joined = " ".join(line.strip() for line in block.splitlines() if line.strip())
                if joined:
                    parts.append(joined)
            continue
        for box, lines in regions:
            h = page.rect.height
            lines = [l for l in lines if not (
                re.sub(r"\d+", "#", l.text) in drop and (l.bbox[1] < 0.15 * h or l.bbox[3] > 0.88 * h))]
            if lines:
                parts.extend(p for p in region_markdown(lines, box) if p.strip())
    return "\n\n".join(parts) + "\n"


LAYOUT_NOTE = """> **Converted from the PDF by layout analysis** (docling), because this paper
> has no HTML rendering. The text and the numbers are the PDF's own; the
> structure of tables and the reading order are reconstructed by a model.
> {equations}Check the PDF (same topic path in the PDF folder) before
> relying on a table whose columns look misaligned."""
EQUATION_NOTES = {
    "model": "Equations, and text whose symbols the PDF's text layer lacks, were read\n> from the page image by a model and can be wrong in a symbol or an index:\n> check the PDF before quoting one.\n> ",
    "raw": "Equations are the PDF's raw text, not LaTeX: read them in the PDF.\n> ",
    None: "",
}
TEXT_LAYER_NOTE = """> **Converted from the PDF text layer**, because this paper has no HTML
> rendering. Section structure, tables and figures did not survive the
> conversion; check the original PDF (same topic path in the PDF folder) before
> relying on any number or table from this file."""

# Unnumbered headings that are sections of their own, not parts of the one before.
TOP_LEVEL = re.compile(
    r"(abstract|introduction|related work|background|methods?|methodology|experiments?|results|"
    r"discussion|limitations|conclusions?|acknowledge?ments?|references|bibliography|"
    r"appendix|appendices|supplementary materials?|significance|ethics statement|impact statement)\b", re.I)


def heading_level(text, roman, last_numbered):
    """A heading's markdown level (2-6) from its numbering.

    "3 Method" is 2, "3.1 Setup" 3, "A.2 Proofs" 3. In an IEEE paper "II.
    Background" is 2, "A. Surveys" 3 and "1) Details" 4. An unnumbered heading
    is a section if it has a section's name ("Abstract", "References"), and
    otherwise a part of the last numbered heading.
    """
    if roman:
        if re.match(r"[IVXL]+\.?\s", text):
            return 2
        if re.match(r"[A-Z]\.\s", text):
            return 3
        if re.match(r"\d+\)\s", text):
            return 4
    m = re.match(r"(?:Appendix\s+)?((?:\d+|[A-Z])(?:\.\d+)*)\.?\s+\S", text)
    if m and (m.group(1)[0].isdigit() or "." in m.group(1) or text.startswith("Appendix")):
        return min(2 + m.group(1).count("."), 6)
    if TOP_LEVEL.match(text) or last_numbered is None:
        return 2
    return min(last_numbered + 1, 6)


def tidy(text):
    """Text as docling returns it, with the spaces a PDF puts inside numbers removed."""
    text = " ".join(text.split())
    return re.sub(r"(?<=\d) \. (?=\d)", ".", text)  # "32 . 3", a number set in math mode


# The Python of the environment marker is installed in (pdf-equations.py runs there).
def _marker_python():
    from paperlib import CACHE_DIR  # the venv lives next to the download cache
    return Path(os.environ.get("PAPERS_MARKER_PYTHON") or CACHE_DIR / "venvs" / "marker" / "bin" / "python")


MARKER_PYTHON = _marker_python()


# Signs that the text layer lost a block's mathematics: an underscore standing
# alone where a symbol was ("a task _ ~ ( )"), a replacement character, or the
# Unicode sub- and superscripts a Word-made PDF writes ("ᵢˢᵘᵖᵖᵒʳᵗ").
GARBLED = re.compile(r"(?<![\w\\])_(?![\w{])|\ufffd|[\u2070-\u209f\u1d2c-\u1d6a\u02b0-\u02e4]")
# Mathematics the text layer kept as Unicode: Greek, operators, letterlike symbols.
MATH_CHARS = re.compile(r"[\u0370-\u03ff\u2100-\u214f\u2190-\u22ff\u27c0-\u27ef\U0001d400-\U0001d7ff]")
WORD = re.compile(r"[A-Za-z]{3,}")
NUMBER = re.compile(r"\d+\.\d+|\d{2,}")


# Fonts mathematics is set in (the same hints marker uses): a block using one
# has inline mathematics, which the text layer gives as plain letters ("K q").
MATH_FONT = re.compile(r"cmmi|cmsy|cmex|msam|msbm|stix|mathjax|math|symbol", re.I)


def has_math_font(page, box):
    """Whether any text inside the box (top-left origin, points) is in a mathematics font."""
    for block in page.get_text("dict", clip=pymupdf.Rect(*box))["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if span["text"].strip() and MATH_FONT.search(span["font"]):
                    return True
    return False


def needs_reading(text, inline_math, math_font=False):
    """Whether a text block should be read from the page image instead: its
    mathematics is garbled in the text layer, or (unless --fast) it has
    mathematics worth writing as LaTeX: text in a mathematics font, or more
    than 2% mathematical characters."""
    if GARBLED.search(text):
        return True
    return inline_math and (math_font or len(MATH_CHARS.findall(text)) > 0.02 * len(text))


def trusted_reading(original, reading):
    """Whether the model's reading of a text block can replace the text layer's.

    The text layer is exact where it has the characters, so the reading must
    keep the block's words (it was not cut short and did not wander) and every
    number in it (a digit misread would be silent).
    """
    words = Counter(w.lower() for w in WORD.findall(original))
    read_words = Counter(w.lower() for w in WORD.findall(reading))
    kept = sum((words & read_words).values())
    if words and kept < 0.8 * sum(words.values()):
        return False
    plain = re.sub(r"[\s,{}\\]", "", reading)
    return all(n in plain for n in NUMBER.findall(original))


# An equation's number as the model or the text layer writes it: "(3)",
# "(2.1)", "(A.4)", "(3a)", "\tag{3}", or a bare "3" standing alone.
EQ_NUMBER = re.compile(r"\\tag\*?\{\s*\(?\s*([A-Z]?\d+(?:\.\d+)*[a-z]?)\s*\)?\s*\}"
                       r"|\(\s*([A-Z]?\d+(?:\.\d+)*[a-z]?)\s*\)|^\s*(\d+(?:\.\d+)*)\s*$")
# What else a crop holding only the number yields: spacing, an arrow, a stray mark.
EQ_FILLER = re.compile(r"\\(?:q?quad|hspace\*?\{[^}]*\}|[,;:! ]|(?:up|down|left|right)arrow)")


def equation_number(text):
    """The last equation number in an equation's text, or None."""
    found = [next(g for g in m.groups() if g) for m in EQ_NUMBER.finditer(text or "")]
    return found[-1] if found else None


def number_only(text):
    """Whether an equation's text is its number and nothing else ("(7)", "\\tag{3}", "↑ (4)")."""
    if equation_number(text) is None:
        return False
    rest = EQ_FILLER.sub("", EQ_NUMBER.sub("", text))
    return not re.search(r"[A-Za-z0-9\\]", rest)


def keeps_number(reading, number, own_box=False):
    """Whether a new reading of a number-only equation can replace it: it has
    more than the number, and the same number, so it is that equation (a crop
    over an empty margin can make the model invent a sentence). A reading of
    the equation's own box, grown a little, may leave the number out (CG's
    Eq. 5) if it reads as mathematics: an "=" or a TeX command."""
    if not reading or number_only(reading):
        return False
    found = equation_number(reading)
    return found == number or (own_box and found is None and bool(re.search(r"=|\\[A-Za-z]", reading)))


# How far a band crop reaches above and below a number-only equation (points).
BAND_REACH = 60


def retry_boxes(box, neighbours):
    """Crops to read a number-only equation again, tightest first.

    A crop that held the formula can still read as its number alone: the
    model is sensitive to a point of margin (GPT-1's Eq. 5), so the box grown
    by 2 points comes first. A formula without text in the PDF's text layer
    (Word's, mostly) gets a box only around its number, since docling fits a
    box to the text it holds; then the formula is in the band between the
    blocks above and below, across their column. neighbours: the boxes of
    every other block on the page; all boxes (x0, y0, x1, y1), top-left origin.
    """
    x0, y0, x1, y1 = box
    crops = [[x0 - 2, y0 - 2, x1 + 2, y1 + 2]]
    centre = (x0 + x1) / 2
    others = [b for b in neighbours if list(b) != list(box)]
    # The column: that of the nearest block across the box's centre. A line
    # ending short of the number (a ragged paragraph) is in it all the same.
    seeds = [b for b in others if b[0] <= centre <= b[2]]
    if not seeds:
        return crops
    nearest = min(seeds, key=lambda b: max(b[1] - y1, y0 - b[3]))
    left, right = nearest[0], max(nearest[2], x1)
    if x1 - x0 >= 0.5 * (right - left):
        return crops
    column = [b for b in others if min(b[2], right) - max(b[0], left) >= 0.5 * min(b[2] - b[0], right - left)]
    above = [b for b in column if b[3] <= y0 + 1]
    below = [b for b in column if b[1] >= y1 - 1]
    top = max([b[3] + 1 for b in above] + [y0 - BAND_REACH])
    bottom = min([b[1] - 1 for b in below] + [y1 + BAND_REACH])
    crops.append([left, min(top, y0), right, max(bottom, y1)])
    return crops


# Fonts a table's marks are set in. Bold also comes from the span's flags
# (PyMuPDF sets bit 16 from the font's descriptor).
BOLD_FONT = re.compile(r"bold|black|heavy|demi|medi|cmbx|sfbx|lmbx|ptmb", re.I)
ITALIC_FONT = re.compile(r"italic|oblique|slant|cmti|cmsl|sfti|ptmri|-it\b", re.I)


def page_rules(page):
    """The page's horizontal rules as (x0, x1, y): drawn lines and thin rectangles."""
    rules = []
    for path in page.get_drawings():
        for entry in path["items"]:
            if entry[0] == "l" and abs(entry[1].y - entry[2].y) < 0.5:
                rules.append((min(entry[1].x, entry[2].x), max(entry[1].x, entry[2].x), entry[1].y))
            elif entry[0] == "re" and entry[1].height <= 1.5 and entry[1].width > 0:
                rules.append((entry[1].x0, entry[1].x1, entry[1].y1))
    return rules


def cell_marks(page, box, rules):
    """The marks of a table cell's text in the PDF: a set of "bold", "italic", "underline".

    Bold or italic when every letter and digit inside the box (by its centre)
    is set in such a font; a dagger or an asterisk in a symbol font does not
    count. Underlined when a rule runs just under the text and no further
    than its ends: a table's own rules, \\cmidrule's included, run past them.
    Mathematics fonts are never italic.
    """
    chars = []
    for block in page.get_text("rawdict", clip=pymupdf.Rect(*box))["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                for ch in span["chars"]:
                    cx, cy = (ch["bbox"][0] + ch["bbox"][2]) / 2, (ch["bbox"][1] + ch["bbox"][3]) / 2
                    if ch["c"].isalnum() and box[0] <= cx <= box[2] and box[1] <= cy <= box[3]:
                        chars.append((ch["bbox"], span["font"], span["flags"]))
    if not chars:
        return set()
    marks = set()
    if all(BOLD_FONT.search(font) or flags & 16 for _, font, flags in chars):
        marks.add("bold")
    if all(ITALIC_FONT.search(font) and not MATH_FONT.search(font) for _, font, _ in chars):
        marks.add("italic")
    left, right = min(b[0] for b, _, _ in chars), max(b[2] for b, _, _ in chars)
    bottom, width = max(b[3] for b, _, _ in chars), right - left
    for x0, x1, y in rules:
        overlap = min(x1, right) - max(x0, left)
        if bottom - 2 <= y <= bottom + 3 and overlap >= 0.7 * width and x0 >= left - 4 and x1 <= right + 4:
            marks.add("underline")
            break
    return marks


MARKED = Counter()  # table cells given a mark, by mark


def mark_table_cells(table, page, page_height):
    """Write the bold, italic and underline of a docling table's cells into their text.

    docling keeps a cell's text but not its weight, so the bold that marks a
    best or significant result is lost; the PDF's text layer still has it, in
    the font of each character. Header cells are left plain, and so is a mark
    every body cell has (it distinguishes nothing).
    """
    rules = page_rules(page)
    found = []
    for cell in table.data.table_cells:
        if cell.bbox is None or not cell.text.strip() or cell.column_header:
            continue
        box = cell.bbox
        if box.coord_origin.name == "BOTTOMLEFT":
            box = box.to_top_left_origin(page_height=page_height)
        found.append((cell, cell_marks(page, (box.l, box.t, box.r, box.b), rules)))
    everywhere = set.intersection(*(m for _, m in found)) if found else set()
    for cell, marks in found:
        marks -= everywhere
        if not marks:
            continue
        text = cell.text.strip()
        if "bold" in marks and "italic" in marks:
            text = f"***{text}***"
        elif "bold" in marks:
            text = f"**{text}**"
        elif "italic" in marks:
            text = f"*{text}*"
        if "underline" in marks:
            text = f"<u>{text}</u>"
        cell.text = text
        MARKED.update(marks)


def read_blocks(pdf_path, boxes):
    """What pdf-equations.py reads in each box; None if it cannot run."""
    if not boxes or not MARKER_PYTHON.exists():
        return None
    try:
        # A box takes two to eight seconds; a long paper read with its inline
        # mathematics has thousands, so the limit grows with them.
        run = subprocess.run(
            [str(MARKER_PYTHON), str(Path(__file__).with_name("pdf-equations.py")), str(pdf_path)],
            input=json.dumps(boxes), capture_output=True, text=True, timeout=max(1800, 20 * len(boxes)),
        )
    except subprocess.TimeoutExpired:
        print("warning: equation model failed: timed out", file=sys.stderr)
        return None
    try:
        latex = json.loads(run.stdout)
    except ValueError:
        latex = None
    if run.returncode or not isinstance(latex, list) or len(latex) != len(boxes):
        print(f"warning: equation model failed: {run.stderr.strip().splitlines()[-1:]}", file=sys.stderr)
        return None
    return latex


def convert_layout(pdf_path, images_dir=None, basename=None, equation_model=True, inline_math=True):
    """(markdown, how equations were written) from docling's document for the PDF.

    The second value is "model", "raw" or None (the paper has no equations);
    see the module docstring.
    """
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import OcrMacOptions, PdfPipelineOptions, RapidOcrOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling_core.types.doc import DocItemLabel as Label

    options = PdfPipelineOptions()
    # RapidOCR reads tables and code that are images in the PDF. Named here,
    # because docling's default picks Apple's OCR when ocrmac is installed,
    # which also reads logos and chart labels into the text. PAPERLIB_OCR
    # (ocrmac, off) is for comparing them: experiments/ocr-engines.
    ocr = os.environ.get("PAPERLIB_OCR", "rapidocr")
    if ocr == "off":
        options.do_ocr = False
    else:
        options.ocr_options = {"ocrmac": OcrMacOptions, "rapidocr": RapidOcrOptions}[ocr]()
    options.generate_picture_images = bool(images_dir)
    options.images_scale = 2.0
    converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)})
    doc = converter.convert(pdf_path).document

    items = [item for item, _ in doc.iterate_items()]
    headings = [tidy(i.text) for i in items if i.label in (Label.SECTION_HEADER, Label.TITLE)]
    # "I.INTRODUCTION": IEEE numbering, sometimes set without the space.
    headings = [re.sub(r"^([IVXL]+\.)(?=\S)", r"\1 ", h) for h in headings]
    roman = any(re.match(r"(?:II|III|IV|VI?)\.?\s", h) for h in headings)

    # What the model reads from the page image: every equation docling found,
    # and the text blocks whose mathematics the text layer lost. A block with
    # hardly a word in it is an equation docling took for text. A paragraph
    # running over a column or page break has a box for each part.
    readable = (Label.TEXT, Label.PARAGRAPH, Label.LIST_ITEM, Label.CAPTION, Label.FOOTNOTE)
    boxes, owners = [], []  # owners[k]: the index in items of the block box k belongs to
    kinds = {}
    on_page = {}  # page number: the boxes of every block on it
    pages = pymupdf.open(pdf_path)
    for n, item in enumerate(items):
        text = getattr(item, "text", "") or ""
        item_boxes = []
        for prov in item.prov:
            box = prov.bbox.to_top_left_origin(page_height=doc.pages[prov.page_no].size.height)
            item_boxes.append((prov.page_no, [box.l, box.t, box.r, box.b]))
            on_page.setdefault(prov.page_no, []).append([box.l, box.t, box.r, box.b])
        if item.label == Label.FORMULA:
            kinds[n] = "equation"
        elif item.label in readable and needs_reading(
                text, inline_math,
                inline_math and any(has_math_font(pages[page_no - 1], box) for page_no, box in item_boxes)):
            kinds[n] = "text" if len(WORD.findall(text)) >= 3 else "equation"
        else:
            continue
        for page_no, box in item_boxes:
            boxes.append({"page": page_no, "bbox": box, "kind": kinds[n]})
            owners.append(n)
    readings = {}
    read = read_blocks(pdf_path, boxes) if equation_model else None
    for n, reading in zip(owners, read or []):
        if reading.strip():
            readings.setdefault(n, []).append(reading.strip())
    if read is not None:
        reread_number_only(pdf_path, items, kinds, boxes, owners, readings, on_page)
    equations = None

    from paperlib import to_webp

    parts, figures, last_numbered, titled = [], 0, None, False
    captions = set()  # docling yields a caption with its table or figure, and again on its own
    for n, item in enumerate(items):
        page = item.prov[0].page_no if item.prov else None
        label = item.label
        if kinds.get(n) == "equation" and label != Label.FORMULA:
            label = Label.FORMULA  # an equation docling took for text
        if label in (Label.SECTION_HEADER, Label.TITLE):
            text = re.sub(r"^([IVXL]+\.)(?=\S)", r"\1 ", tidy(item.text))
            text = re.sub(r"^(\d+) ?\. ?(\d)", r"\1.\2", text)  # "4 .1 Evaluation"
            if not titled and (label == Label.TITLE or page == 1) and not re.match(r"\d|abstract", text, re.I):
                parts.append(f"# {text}")  # the paper's title
                titled = True
                continue
            titled = True
            level = heading_level(text, roman, last_numbered)
            if re.match(r"(?:Appendix\s+)?(?:\d|[IVXL]+\.?\s|[A-Z]\.)", text):
                last_numbered = level
            parts.append(f"{'#' * level} {text}" + (f" (p. {page})" if page else ""))
        elif label == Label.TABLE:
            if item.prov:
                mark_table_cells(item, pages[page - 1], doc.pages[page].size.height)
            table = item.export_to_markdown(doc).strip()
            # docling writes the table's caption above it, and yields the
            # caption again as an item of its own.
            kept = []
            for line in table.split("\n"):
                if line.strip() and not line.lstrip().startswith("|"):
                    key = " ".join(line.split())
                    if key in captions:
                        continue
                    captions.add(key)
                kept.append(line)
            table = "\n".join(kept).strip()
            if table:  # docling sometimes finds empty fragments around a table
                parts.append(re.sub(r"(?<=\d) \. (?=\d)", ".", table))
        elif label in (Label.PICTURE, Label.CHART):
            image = item.get_image(doc) if images_dir else None
            if image is None or min(image.size) < 120:  # a logo or an icon
                continue
            buffer = io.BytesIO()
            image.save(buffer, "PNG")
            figures += 1
            name = f"{basename}-fig{figures:02d}.webp"
            Path(images_dir).mkdir(parents=True, exist_ok=True)
            (Path(images_dir) / name).write_bytes(to_webp(buffer.getvalue()))
            parts.append(f"![](images/{quote(name)})")
        elif label == Label.FORMULA:
            raw = " ".join((getattr(item, "orig", "") or item.text or "").split())
            lines = [line.strip() for part in readings.get(n, []) for line in part.split("\n") if line.strip()]
            if len(lines) > 1:  # a lone character is a neighbouring line the crop clipped
                lines = [line for line in lines if len(line.replace(" ", "")) >= 3] or lines
            if lines:
                tex = lines[0] if len(lines) == 1 else "\\begin{gathered}" + " \\\\ ".join(lines) + "\\end{gathered}"
                parts.append(f"$${tex}$$")
                equations = "model"
            elif raw:
                parts.append(f"<!-- equation: the PDF's raw text, not LaTeX; check the PDF"
                             + (f", p. {page}" if page else "") + f" -->\n```text\n{raw}\n```")
                equations = equations or "raw"
        elif label == Label.CODE:
            parts.append(f"```text\n{item.text}\n```")
        elif label == Label.LIST_ITEM:
            marker = item.marker if getattr(item, "enumerated", False) and item.marker else "-"
            parts.append(f"{marker} {reading_or_text(item, readings.get(n))}")
            equations = "model" if n in readings else equations
        elif getattr(item, "text", "").strip():
            text = reading_or_text(item, readings.get(n))
            if not any(c.isalnum() for c in text):  # a stray bullet glyph, a rule
                continue
            equations = "model" if n in readings else equations
            # The second copy is not always labelled a caption, so a block
            # that reads as one ("Table 1: ...") counts too.
            if label == Label.CAPTION or re.match(r"(?:Table|Figure|Fig\.) \d+[:.] ", text):
                key = " ".join(text.split())
                if key in captions:
                    continue
                captions.add(key)
            parts.append(text)

    parts = join_split_tables(parts)
    # Consecutive list items form one list.
    out = []
    for prev, part in zip([""] + parts, parts):
        is_item = re.match(r"(?:-|\d+[.)]) ", part) is not None
        was_item = re.match(r"(?:-|\d+[.)]) ", prev) is not None
        out.append(("\n" if is_item and was_item else "\n\n") + part)
    return "".join(out).strip() + "\n", equations


REREAD = Counter()  # number-only equations read again: "fixed", "raw" (the text layer's text), "left"


def reread_number_only(pdf_path, items, kinds, boxes, owners, readings, on_page):
    """Read again the equations whose reading is only their number, from the
    crops retry_boxes gives, and keep the first reading that is that equation.
    When none is, the text layer's raw text is written instead if it holds
    more than the number. Changes readings in place."""
    candidates = []  # (item index, number, crops)
    for n, kind in kinds.items():
        mine = [k for k, owner in enumerate(owners) if owner == n]
        if kind != "equation" or len(mine) != 1:
            continue
        raw = " ".join((getattr(items[n], "orig", "") or items[n].text or "").split())
        text = "\n".join(readings.get(n, [])) or raw
        if not number_only(text):
            continue
        page, box = boxes[mine[0]]["page"], boxes[mine[0]]["bbox"]
        candidates.append((n, equation_number(text), page, retry_boxes(box, on_page[page])))
    if not candidates:
        return
    crops = [{"page": page, "bbox": crop, "kind": "equation"}
             for _, _, page, item_crops in candidates for crop in item_crops]
    read = iter(read_blocks(pdf_path, crops) or [""] * len(crops))
    for n, number, _, item_crops in candidates:
        found = [reading.strip() for _, reading in zip(item_crops, read)]
        better = next((r for k, r in enumerate(found) if keeps_number(r, number, own_box=k == 0)), None)
        raw = " ".join((getattr(items[n], "orig", "") or items[n].text or "").split())
        if better:
            if equation_number(better) is None:
                better += f" \\quad ({number})"
            readings[n] = [better]
            REREAD["fixed"] += 1
        elif raw and not number_only(raw):
            readings.pop(n, None)  # the raw-text block is written instead
            REREAD["raw"] += 1
        else:
            REREAD["left"] += 1


def join_split_tables(parts):
    """Rejoin a table docling split in two.

    The second piece then has a row of data where its header should be
    ("| SFT | 0.699 | 0.537 |" above the rule). Two tables in a row with the
    same number of columns, the second headed by numbers, are one table.
    """
    out = []
    for part in parts:
        lines = part.split("\n")
        if out and part.startswith("|") and out[-1].startswith("|") and len(lines) >= 2:
            cells = [c.strip() for c in lines[0].strip("|").split("|")]
            numeric = sum(bool(re.fullmatch(r"[-+]?[\d.,]+%?", c)) for c in cells[1:])
            same_width = lines[0].count("|") == out[-1].split("\n")[0].count("|")
            if same_width and cells[1:] and numeric >= 0.5 * len(cells[1:]):
                out[-1] += "\n" + "\n".join([lines[0]] + lines[2:])
                continue
        out.append(part)
    return out


READ = Counter()  # text blocks the model read: "kept", or "rejected" for the text layer's text


def reading_or_text(item, reading):
    """A text block's text: the model's reading if there is one to trust, else the text layer's.
    A leading "#" is escaped ("# weights" in a table's legend is not a heading)."""
    text = re.sub(r"^#", r"\\#", tidy(item.text))
    reading = " ".join(reading or [])
    if not reading:
        return text
    trusted = trusted_reading(text, reading)
    READ["kept" if trusted else "rejected"] += 1
    return reading if trusted else text


def main():
    args = sys.argv[1:]
    text_layer = "--text-layer" in args
    raw_equations, inline_math = "--raw-equations" in args, "--fast" not in args
    args = [a for a in args if not a.startswith("--")]
    if len(args) not in (2, 4):
        sys.exit(__doc__)
    pdf_path, out_path = args[0], args[1]
    images_dir, basename = (args[2], args[3]) if len(args) == 4 else (None, None)
    body, equations = None, None
    if not text_layer:
        try:
            body, equations = convert_layout(pdf_path, images_dir, basename, not raw_equations, inline_math)
        except Exception as e:  # docling missing, or a PDF it cannot read
            print(f"warning: layout conversion failed ({type(e).__name__}: {e}); using the text layer",
                  file=sys.stderr)
    if body is not None and len(body.split()) >= 200:
        note = LAYOUT_NOTE.format(equations=EQUATION_NOTES[equations])
    else:
        if body is not None:
            print("warning: layout conversion found almost no text; using the text layer", file=sys.stderr)
        note, body = TEXT_LAYER_NOTE, convert_text_layer(pdf_path)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(note + "\n\n" + body)
    if READ:
        print(f"text blocks read by the model: {READ['kept']} kept, {READ['rejected']} rejected "
              "(words or numbers differed from the text layer)", file=sys.stderr)
    if REREAD:
        print(f"number-only equations read again: {REREAD['fixed']} fixed, {REREAD['raw']} as raw text, "
              f"{REREAD['left']} left", file=sys.stderr)
    if MARKED:
        print("table cells marked: " + ", ".join(f"{n} {mark}" for mark, n in sorted(MARKED.items())),
              file=sys.stderr)


if __name__ == "__main__":
    main()
