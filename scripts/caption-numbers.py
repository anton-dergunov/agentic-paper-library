#!/usr/bin/env python3
"""Give a paper's table and figure captions the numbers the PDF prints.

    ./scripts/caption-numbers.py <paper.pdf> <paper.md>

arXiv's HTML numbers floats itself, and now and then differently from the PDF:
a plot set beside a table inside one table float is captioned "Table 7", a
caption written with \\captionof gets no number at all, and every later table
or figure is then one off. An agent citing "Table 7" would send the reader to
the wrong table.

Each caption in the markdown ("Table 7: Agreement and win rate ...") is
matched to the PDF caption that starts with the same words. When the PDF
calls it something else ("Figure 2"), the caption is rewritten, and so are
the links that point to it. A "\\captionof" caption gets its label the same
way. A caption that matches no PDF caption, or two equally well, is left
alone. Safe to re-run.
"""

import re
import sys
from pathlib import Path

import pymupdf

LABEL = r"(Table|Figure|Fig\.) ((?:[A-Z]\.?)?\d+(?:\.\d+)?)"
PDF_CAPTION = re.compile(rf"^{LABEL}\s*[:.|]\s*(.+)", re.S)
MD_CAPTION = re.compile(rf"^{LABEL}: (.+)$")
# LaTeXML's rendering of an undefined \captionof{table}{...}.
CAPTIONOF = re.compile(r"^(table|figure)(?=\S)(.+)$")
# A link inside the paper: [7](#S4.T8 "Table 8 ‣ 4.2 ..."), [Figure 1](#S2.F1 "In 2 Results ‣ ...").
LINK = re.compile(r'(?:\b(Tables?|Figures?|Figs?\.|Tab\.)(\s+))?\[([^\]]*)\]\((#[^ )]+)(?: "([^"]*)")?\)')
FLOAT = r"(?:Table|Figure)\s(?:[A-Z]\.?)?\d+(?:\.\d+)?"  # \s: LaTeXML joins them with a no-break space
MIN_WORDS = 4


def words(text, limit=30):
    """The words a caption starts with, markup and mathematics left out."""
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>|\\[a-zA-Z]+|[*_`\\]", " ", text)
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff")
    return re.findall(r"[a-z0-9]+", text.lower())[:limit]


def pdf_captions(pdf_path):
    """[(label, words)] for each caption in the PDF, in reading order."""
    found = []
    for page in pymupdf.open(pdf_path):
        for block in page.get_text("blocks"):
            text = re.sub(r"-\n(?=[a-z])", "", block[4]).strip()
            m = PDF_CAPTION.match(text)
            if m:
                kind = "Figure" if m.group(1) == "Fig." else m.group(1)
                found.append((f"{kind} {m.group(2)}", words(m.group(3))))
    return found


def common_prefix(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def pdf_label(text, label, captions):
    """The PDF's label for the caption starting with `text`, or None.

    The PDF caption sharing the longest run of opening words wins; the run
    must be four words, or the whole of a shorter caption. A tie is settled
    by the label the markdown already has, else nothing is claimed.
    """
    mine = words(text)
    if not mine:
        return None
    scored = [(common_prefix(mine, theirs), pdf) for pdf, theirs in captions]
    best = max((n for n, _ in scored), default=0)
    if best < min(MIN_WORDS, len(mine)) or best == 0:
        return None
    labels = {pdf for n, pdf in scored if n == best}
    if label in labels:
        return label
    return labels.pop() if len(labels) == 1 else None


def main(pdf_path, md_path):
    captions = pdf_captions(pdf_path)
    lines = Path(md_path).read_text(encoding="utf-8").split("\n")
    renamed, labelled = {}, 0  # old label -> new label
    seen = {}
    in_fence = False
    for i, line in enumerate(lines):
        if line.startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        m = MD_CAPTION.match(line)
        if m:
            old = f"{'Figure' if m.group(1) == 'Fig.' else m.group(1)} {m.group(2)}"
            seen[old] = seen.get(old, 0) + 1
            new = pdf_label(m.group(3), old, captions)
            if new and new != old:
                lines[i] = f"{new}: {m.group(3)}"
                renamed[old] = new if seen[old] == 1 else None
            continue
        m = CAPTIONOF.match(line)
        if m and any(prev.strip() == "\\captionof" for prev in lines[max(0, i - 2):i]):
            new = pdf_label(m.group(2), None, captions)
            if new and new.startswith(m.group(1).capitalize()):
                lines[i] = f"{new}: {m.group(2).lstrip()}"
                for j in range(max(0, i - 2), i):
                    if lines[j].strip() == "\\captionof":
                        lines[j] = ""
                labelled += 1

    # A label two captions carried cannot say which of them a link meant.
    renamed = {old: new for old, new in renamed.items() if new and seen[old] == 1}

    def relink(m):
        word, space, text, target, title = m.groups()
        # The float a link means is named at the start of its title
        # ("Table 8 ‣ 4.2 ..."), or is its own text ("[Figure 1](#S2.F1 ...)").
        named = re.match(FLOAT, title or "")
        old = named.group(0) if named else text if re.fullmatch(FLOAT, text) else None
        new = renamed.get(" ".join(old.split())) if old else None
        if not new:
            return m.group(0)
        old_number, new_number = old.split()[1], new.split()[1]
        if re.fullmatch(FLOAT, text):
            text = new.replace(" ", text[len(text.split()[0])])
        elif text.endswith(old_number):
            text = text[: len(text) - len(old_number)] + new_number
        if named:
            title = new + title[len(old):]
        if word and new.split()[0] != old.split()[0] and not word.endswith("s"):
            word = new.split()[0]  # "Table [7]" that is a figure in the PDF
        quoted = f' "{title}"' if title is not None else ""
        return f'{word or ""}{space or ""}[{text}]({target}{quoted})'

    body = "\n".join(lines)
    if labelled:
        body = re.sub(r"\n{3,}", "\n\n", body)
    if renamed:
        body = LINK.sub(relink, body)
    if renamed or labelled:
        Path(md_path).write_text(body, encoding="utf-8")
    print(f"caption-numbers: {len(renamed)} captions renumbered from the PDF, {labelled} given a number")
    for old, new in renamed.items():
        print(f"  {old} -> {new}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
