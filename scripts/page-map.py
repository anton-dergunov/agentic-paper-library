#!/usr/bin/env python3
"""Annotate a paper's markdown headings with the PDF page they start on.

    ./scripts/page-map.py <paper.pdf> <paper.md>

Turns `### 4.3 LongMemEval (LME)` into `### 4.3 LongMemEval (LME) (p. 6)`, so
an agent reading the markdown can always tell the reader where something is in
the PDF they are holding.

Three ways to place a heading, in order:

1. The PDF's named destinations. LaTeX with hyperref writes one per numbered
   section (`section.4`, `subsection.4.3`, `subsubsection.2.2.3`, and
   `appendix.A` / `subsection.A.1` for appendices), which is exact.
2. The PDF's outline (the bookmarks a viewer shows in its sidebar), also
   exact, for PDFs without such destinations. A bookmark is believed only
   when its page prints the heading. A numbered heading takes the
   page of the next unused bookmark with its section number. Unnumbered
   headings are not matched to bookmarks: a paragraph heading ("User Consent")
   often shares its words with a bookmark for a different, later section.
3. Searching the page text for the heading, starting from the page of the
   previous placed heading, since headings appear in reading order. A
   numbered heading counts as found when "<number> <title>" appears in the
   page text, the number printed as the PDF prints it ("4.3", "4.3.", "II.",
   "A." under an IEEE Roman section); an unnumbered one when a line of the
   page is the heading, or starts with it and a full stop or colon (a run-in
   paragraph heading), or (five or more words) when a line starts the
   heading and the next few lines finish it. Pages that look
   like a table of contents (five or more dot-leader lines) are never searched,
   since every numbered heading appears there too (a "Contents" heading is the
   exception). Unnumbered headings are
   short and also occur in running text, so they are only searched up to the
   next exactly-known heading, and, under five words, at most two pages on.

Headings neither method places are left alone and reported. Existing `(p. N)`
suffixes are replaced, so the script is safe to re-run.
"""

import re
import sys
from pathlib import Path

import pymupdf

HEADING = re.compile(r"^(#{2,6}) (.+?)\s*$")
PAGE_SUFFIX = re.compile(r"\s*\(p\. \d+\)$")
NUMBER = re.compile(r"^(?:Appendix\s+)?((?:\d+|[A-Z])(?:\.\d+)*)\.?\s+(.+)$")
# IEEE numbering: "II Background", "II-A Surveys", "IV-B1 Details".
ROMAN = re.compile(r"^([IVXL]+)(?:-([A-Z])(\d+)?)?\.?\s+(.+)$")
ROMAN_PAPER = re.compile(r"^(?:II|III|IV|VI?)(?:-[A-Z]\d*)?\s")
ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50}
DEPTH_NAMES = ["section", "subsection", "subsubsection"]
# A table-of-contents line: a title run out to its page number with dots.
DOT_LEADER = re.compile(r"(?:\.\s*){4,}\d*\s*$", re.M)


def normalise(text):
    text = text.replace("­", "").replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = re.sub(r"-\n(\w)", r"\1", text)  # rejoin words hyphenated across lines
    return " ".join(text.lower().split())


def plain_title(title):
    """Heading text as it would appear in the PDF: no markdown, no math."""
    if "$`" in title:
        return None
    title = re.sub(r"[*_`]", "", title)
    title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title)
    return normalise(title.rstrip("."))


def starts_a_line(title, lines, span=4):
    """Whether the title begins one of the lines, running on over the next few."""
    for i in range(len(lines)):
        text = re.sub(r"(\w)- (?=\w)", r"\1", " ".join(lines[i:i + span]))
        if text.startswith(title):
            return True
    return False


class Outline:
    """The PDF's numbered bookmarks, consumed in reading order as headings match."""

    def __init__(self, doc):
        self.entries = []  # (section number, page)
        for _, title, page in doc.get_toc(simple=True):
            numbered = NUMBER.match(" ".join(title.split()))
            if numbered and page >= 1:
                self.entries.append((numbered.group(1), page))
        self.cursor = 0

    def page_of(self, number, min_page):
        """The page of the next bookmark with this section number, or None."""
        for j in range(self.cursor, len(self.entries)):
            if self.entries[j][0] == number:
                if self.entries[j][1] < min_page:
                    return None
                self.cursor = j + 1
                return self.entries[j][1]
        return None


def roman_to_int(roman):
    values = [ROMAN_VALUES[c] for c in roman]
    return sum(-v if i + 1 < len(values) and v < values[i + 1] else v for i, v in enumerate(values))


def heading_number(text, top_level, roman):
    """(section number as in destinations, title, the number as printed) or None.

    The number as printed is one or more forms ("ii", "a" for "II-A") that the
    search tries before the title.
    """
    m = ROMAN.match(text) if roman else None
    if m:
        number, printed = [str(roman_to_int(m.group(1)))], [m.group(1).lower()]
        if m.group(2):
            number.append(str(ord(m.group(2)) - ord("A") + 1))
            printed = [m.group(2).lower(), f"{m.group(1)}-{m.group(2)}".lower()]
        if m.group(3):
            number.append(m.group(3))
            printed = [m.group(3), f"{m.group(2)}{m.group(3)}".lower()]
        return ".".join(number), m.group(4), printed
    m = NUMBER.match(text)
    # A bare letter is an appendix number only on a top-level heading
    # ("## B Proofs"); deeper down, "A Harmless Assistant" is just an article.
    if not m or (m.group(1).isalpha() and not text.startswith("Appendix") and not top_level):
        return None
    return m.group(1), m.group(2), [m.group(1).lower()]


def dest_candidates(number):
    parts = number.split(".")
    depth = len(parts) - 1
    names = []
    if depth < len(DEPTH_NAMES):
        names.append(f"{DEPTH_NAMES[depth]}.{number}")
    if depth == 0 and parts[0].isalpha():
        names.append(f"appendix.{number}")
    return names


def main(pdf_path, md_path):
    doc = pymupdf.open(pdf_path)
    if not doc.is_pdf:  # MuPDF also opens HTML, and crashes on its PDF-only calls
        sys.exit(f"error: {pdf_path} is not a PDF")
    dests = {
        name: target["page"] + 1
        for name, target in doc.resolve_names().items()
        if target.get("page", -1) >= 0
    }
    outline = Outline(doc)
    raw = [page.get_text() for page in doc]
    contents = {p for p, text in enumerate(raw) if len(DOT_LEADER.findall(text)) >= 5}
    pages = [normalise(text) for text in raw]
    ordered_lines = [[normalise(line) for line in text.splitlines() if line.strip()] for text in raw]
    page_lines = [set(lines) for lines in ordered_lines]

    lines = Path(md_path).read_text(encoding="utf-8").split("\n")
    roman = any(
        (m := HEADING.match(line)) and ROMAN_PAPER.match(PAGE_SUFFIX.sub("", m.group(2)))
        for line in lines
    )

    # First pass: every heading, and the exact page of those a destination or a
    # bookmark names. The outline is matched even when a destination already
    # gave the page, so that its cursor stays level with the headings.
    headings = []  # (line index, hashes, text, number match, exact page)
    from_outline = 0
    exact_so_far = 1
    in_fence = False
    for i, line in enumerate(lines):
        if line.startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        m = HEADING.match(line)
        if not m:
            continue
        text = PAGE_SUFFIX.sub("", m.group(2))
        numbered = heading_number(text, m.group(1) == "##", roman)
        dest_page = None
        if numbered:
            for name in dest_candidates(numbered[0]):
                if name in dests:
                    dest_page = dests[name]
                    break
        outline_page = outline.page_of(numbered[0], exact_so_far) if numbered else None
        # A bookmark can point at the wrong page: hyperref gives appendix "A.7"
        # the destination of section 7 when the counters collide. Believe it
        # only when the heading is printed on that page.
        if outline_page is not None:
            title = plain_title(numbered[1])
            if title and title not in pages[outline_page - 1]:
                outline_page = None
        if dest_page is None and outline_page is not None:
            dest_page = outline_page
            from_outline += 1
        if dest_page:
            exact_so_far = max(exact_so_far, dest_page)
        headings.append((i, m.group(1), text, numbered, dest_page))

    last_page = 1
    placed = unplaced = 0
    missing = []

    for k, (i, hashes, text, numbered, page) in enumerate(headings):
        if page is None:
            # Search forward from the previous heading. An unnumbered heading
            # ("Objective.", "Tasks.") is short and also appears in tables of
            # contents and running text, so it may only land before the next
            # heading whose page is known exactly; a numbered one is specific
            # enough to search to the end.
            # A long unnumbered heading is specific enough to search as far as
            # the next exactly-known heading, and may wrap across lines in the
            # PDF, so it also counts when a line starts it and the next few
            # finish it.
            title = plain_title(numbered[1] if numbered else text)
            wraps = bool(title) and not numbered and len(title.split()) >= 5
            upper = len(pages)
            if not numbered:
                later = [h[4] for h in headings[k + 1:] if h[4]]
                upper = min(later[0] if later else len(pages), len(pages))
                if not wraps:
                    upper = min(upper, last_page + 2)
            if title:
                # "4.3 title", "4.3. title", and IEEE's "1) title".
                full = [f"{n}{sep} {title}" for n in numbered[2] for sep in ("", ".", ")")] if numbered else []
                for p in range(last_page - 1, upper):
                    if p in contents and title not in ("contents", "table of contents"):
                        continue
                    if not numbered and title in page_lines[p]:
                        page = p + 1
                        break
                    # A run-in heading (\paragraph): "Setup. We evaluate ...".
                    if not numbered and any(line.startswith((title + ". ", title + ": ")) or line in (title + ".", title + ":")
                                            for line in ordered_lines[p]):
                        page = p + 1
                        break
                    if any(f in pages[p] for f in full):
                        page = p + 1
                        break
                    if wraps and starts_a_line(title, ordered_lines[p]):
                        page = p + 1
                        break

        if page is None:
            lines[i] = f"{hashes} {text}"
            if numbered:
                unplaced += 1
                missing.append(text)
            continue
        lines[i] = f"{hashes} {text} (p. {page})"
        last_page = page
        placed += 1

    Path(md_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"page-map: {placed} headings placed, {unplaced} numbered headings unplaced")
    if from_outline:
        print(f"  {from_outline} placed from the PDF outline")
    if contents:
        print(f"  contents pages not searched: {', '.join(str(p + 1) for p in sorted(contents))}")
    for text in missing[:10]:
        print(f"  unplaced: {text}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
