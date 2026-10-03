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
  PDF's raw text in a block marked as such.
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


def read_blocks(pdf_path, boxes):
    """What pdf-equations.py reads in each box; None if it cannot run."""
    if not boxes or not MARKER_PYTHON.exists():
        return None
    try:
        run = subprocess.run(
            [str(MARKER_PYTHON), str(Path(__file__).with_name("pdf-equations.py")), str(pdf_path)],
            input=json.dumps(boxes), capture_output=True, text=True, timeout=1800,
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
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling_core.types.doc import DocItemLabel as Label

    options = PdfPipelineOptions()
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
    pages = pymupdf.open(pdf_path) if inline_math else None
    for n, item in enumerate(items):
        text = getattr(item, "text", "") or ""
        item_boxes = []
        for prov in item.prov:
            box = prov.bbox.to_top_left_origin(page_height=doc.pages[prov.page_no].size.height)
            item_boxes.append((prov.page_no, [box.l, box.t, box.r, box.b]))
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
    for n, reading in zip(owners, (read_blocks(pdf_path, boxes) or []) if equation_model else []):
        if reading.strip():
            readings.setdefault(n, []).append(reading.strip())
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
            table = item.export_to_markdown(doc).strip()
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
            if label == Label.CAPTION:
                if text in captions:
                    continue
                captions.add(text)
            parts.append(text)

    parts = join_split_tables(parts)
    # Consecutive list items form one list.
    out = []
    for prev, part in zip([""] + parts, parts):
        is_item = re.match(r"(?:-|\d+[.)]) ", part) is not None
        was_item = re.match(r"(?:-|\d+[.)]) ", prev) is not None
        out.append(("\n" if is_item and was_item else "\n\n") + part)
    return "".join(out).strip() + "\n", equations


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


if __name__ == "__main__":
    main()
