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

import re
import sys
from collections import Counter

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


def convert(pdf_path):
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


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: pdf-to-markdown.py <input.pdf> <output.md>")
    pdf_path, out_path = sys.argv[1], sys.argv[2]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(convert(pdf_path))


if __name__ == "__main__":
    main()
