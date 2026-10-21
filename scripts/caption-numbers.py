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
alone. The titles of the paper's links, which name the float each one means
until this point, are then removed. Safe to re-run.
"""

import re
import sys
from pathlib import Path

import pymupdf

LABEL = r"(Table|Figure|Fig\.) ((?:[A-Z]\.?)?\d+(?:\.\d+)?)"
PDF_CAPTION = re.compile(rf"^{LABEL}\s*[:.|]\s*(.+)", re.S)
SUBCAPTION = re.compile(r"\(?[a-z]\)")
MD_CAPTION = re.compile(rf"^{LABEL}: (.+)$")
# The label alone: LaTeXML numbers a float that has no caption (an algorithm set as a table).
BARE_LABEL = re.compile(rf"^{LABEL}:\s*$")
# LaTeXML's rendering of an undefined \captionof{table}{...}.
CAPTIONOF = re.compile(r"^(table|figure)(?=\S)(.+)$")
# A link inside the paper: [7](#S4.T8 "Table 8 ‣ 4.2 ..."), [Figure 1](#S2.F1 "In 2 Results ‣ ...").
LINK = re.compile(r'(?:\b(Tables?|Figures?|Figs?\.|Tab\.)(\s+))?\[([^\]]*)\]\((#[^ )]+)(?: "([^"]*)")?\)')
# The title of a link inside the paper, in markdown and in an HTML table.
LINK_TITLE = re.compile(r'(\]\(#[^ )]+) "[^"]*"(?=\))|(<a href="#[^"]*") title="[^"]*"')
FLOAT = r"(?:Table|Figure)\s(?:[A-Z]\.?)?\d+(?:\.\d+)?"  # \s: LaTeXML joins them with a no-break space
MIN_WORDS = 4
# A link to a place in the paper whose text is a number ("[4](#S4.F4)", "[Table 5](#...)",
# "[3(c)](#...)", "[(2)](#S2.E2)"); a citation's link is not one.
REF_LINK = re.compile(r'\[([^\]\n]*)\]\((#(?!bib\.)[^ )]+)(?: "[^"]*")?\)')
REF_TEXT = re.compile(r"^(\D*?\(?)((?:[A-Z]\.?)?\d+(?:\.\d+)*)(\)?\s*\(?([a-z])?\)?)$")
# Words, and numbers with their dots and an appendix letter ("a.1", "b2"), as both texts are compared.
TOKEN = re.compile(r"[a-z]\.?\d+(?:\.\d+)*|\d+(?:\.\d+)*|[a-z]+")
PDF_REF = re.compile(r"(?:[a-z]\.?)?\d{1,3}(?:\.\d{1,3})*")
REF_CONTEXT = (8, 6, 5)  # words before a reference that must match the PDF's, longest first
# What a reference names, from the word before it, and the places in the markdown with
# such a number: a caption ("Table 3:"), a heading ("### 4.3 ...", "###### Theorem 1 (...)").
REF_KIND = {"fig": "figure", "tab": "table", "sec": "section", "appendix": "section", "app": "section",
            "chapter": "section", **dict.fromkeys(("lemma", "proposition", "corollary", "assumption", "definition",
                                                  "example", "remark", "condition", "claim"), "theorem")}
# What a LaTeXML anchor is: "#S4.F4" a figure, "#A3.T5" a table, "#S4.SS3" a section,
# "#S3.Thmtheorem2" a theorem, "#alg1.l17" a line of an algorithm, "#footnote8".
ANCHOR_KIND = [(r"\.l\d+$", "line"), (r"(?:^#|\.)F\d", "figure"), (r"(?:^#|\.)T\d", "table"), (r"Thm", "theorem"),
               (r"^#alg", "algorithm"), (r"footnote", "footnote"), (r"(?:^#|\.)E\d", "equation"),
               (r"^#(?:S|A|Ch|Sx)\d+(?:\.(?:SS|SSS|P)\d+)*$", "section")]
TARGET = re.compile(r"^(?:#+ +(?:([A-Z][a-z]+) +)?|(Table|Figure|Algorithm) +)((?:[A-Z]\.?)?\d+(?:\.\d+)*)(?=[:. (]|$)", re.M)


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
            if not m and SUBCAPTION.match(text):
                # "(b) LoTTE results." above the caption, in one block with it.
                at = re.search(rf"^(?={LABEL}\s*[:.|])", text, re.M)
                m = PDF_CAPTION.match(text[at.start():]) if at else None
            if m:
                kind = "Figure" if m.group(1) == "Fig." else m.group(1)
                found.append((f"{kind} {m.group(2)}", words(m.group(3))))
    return found


def tokens(text):
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff").replace("§", " section ")
    return TOKEN.findall(text.lower())


def pdf_tokens(pdf_path):
    return tokens(" ".join(re.sub(r"-\n(?=[a-z])", "", page.get_text()) for page in pymupdf.open(pdf_path)))


FORMULA = "zzformulazz"


def md_tokens(text):
    """The words of markdown as the PDF prints them: link text kept, markup left out, and a
    formula a word no PDF holds, as its symbols are printed otherwise there."""
    text = re.sub(r"\$\$.*?\$\$|\$[^$\n]*\$", f" {FORMULA} ", text, flags=re.S)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return tokens(re.sub(r"<[^>]+>|\\[a-zA-Z]+", " ", text))


def pdf_references(body, pdf):
    """Give each link to a place in the paper the number the PDF prints there.

    arXiv's HTML can number a reference differently from the PDF: two figures
    set in one float share its anchor, so a reference to either names the
    second; a \\label the HTML attached to a section or a line gives that
    one's number. The words before the reference (where a paragraph or a
    formula leaves few, the words after it) are looked up in the PDF's text, and the
    number next to them there is taken, when the words occur once (or always
    with the same number). The number must label a place
    of the kind the reference names in the markdown too, and a section or a
    theorem the link reaches by its own anchor keeps the HTML's number, as its
    heading in the markdown does.
    """
    index = {}
    k0 = min(REF_CONTEXT)
    for i in range(len(pdf) - k0):
        index.setdefault(tuple(pdf[i:i + k0]), []).append(i + k0)
    def kind_of(word):
        word = word.lower().rstrip("s")
        return REF_KIND.get(word, word)

    targets = {(kind_of(m.group(1) or m.group(2) or "section"), m.group(3).lower()) for m in TARGET.finditer(body)}
    out, pos, fixed, paragraph = [], 0, 0, ""

    def emit(text):
        nonlocal paragraph
        out.append(text)
        paragraph = text[text.rfind("\n\n") + 2:] if "\n\n" in text else paragraph + text

    for m in REF_LINK.finditer(body):
        parts = REF_TEXT.match(m.group(1))
        if not parts:
            continue
        before, label, after, sub = parts.groups()
        emit(body[pos:m.start()])
        pos = m.start()
        # A formula is printed otherwise in the PDF's text: the words match up to it.
        context = md_tokens(paragraph + " " + before)
        context = context[len(context) - context[::-1].index(FORMULA):] if FORMULA in context else context
        named = next((w for w in reversed(context[-4:]) if w.isalpha() and len(w) > 2 and w not in ("and", "the")), "")
        kind = kind_of(named)
        # The places in the PDF's words where the number stands: after the words
        # before the reference, or, where few words precede it (a paragraph's start, a formula),
        # before the words after it, those few words before the number.
        ends = []
        for k in REF_CONTEXT:
            if len(context) >= k:
                ends = [at for at in index.get(tuple(context[-k0:]), []) if at >= k and pdf[at - k:at] == context[-k:]]
            if ends:  # a shorter run would match only more places
                break
        following = md_tokens(body[m.end():body.find("\n\n", m.end())])
        following = following[:following.index(FORMULA)] if FORMULA in following else following
        if 0 < len(context) < k0 and not sub:
            for k in REF_CONTEXT:
                if len(following) >= k:
                    ends = [at - k0 - 1 for at in index.get(tuple(following[:k0]), [])
                            if pdf[at - k0:at - k0 + k] == following[:k]
                            and pdf[max(0, at - k0 - 1 - len(context)):at - k0 - 1] == context]
                if ends:
                    break
        # Words the PDF prints twice, with two numbers: the words after the reference choose.
        if len({pdf[at] for at in ends}) > 1 and len(following) >= 3:
            ends = [at for at in ends if pdf[at + 1:at + 4] == following[:3]]
        numbers = {pdf[at] for at in ends}
        found = numbers.pop() if len(numbers) == 1 and PDF_REF.fullmatch(pdf[ends[0]]) else None
        if not found or found == label.lower() or (kind, found) not in targets:
            continue
        # A section, a theorem or an equation the link reaches by its own anchor is numbered
        # the HTML's way in the markdown too; a figure or a table the PDF's way (above).
        anchor = next((name for pattern, name in ANCHOR_KIND if re.search(pattern, m.group(2))), None)
        if anchor == "equation" or (kind not in ("figure", "table") and anchor == kind):
            continue
        if sub and pdf[ends[0] + 1:ends[0] + 2] != [sub]:
            after = ""  # "Figure 3(c)" where the PDF prints "Figure 4"
        new = found[0].upper() + found[1:]
        emit(f"[{before}{new}{after}](" + body[m.start(2):m.end()])
        pos = m.end()
        fixed += 1
    return "".join(out) + body[pos:], fixed


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
    found = []  # (line index, label, caption text, the PDF's label for it)
    bare = []  # (line index, label)
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
            found.append((i, old, m.group(3), pdf_label(m.group(3), old, captions)))
            continue
        m = BARE_LABEL.match(line)
        if m:
            bare.append((i, f"{'Figure' if m.group(1) == 'Fig.' else m.group(1)} {m.group(2)}"))
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

    # A label with no caption, which a captioned float carries too, is not the PDF's.
    dropped = [i for i, label in bare if label in seen]
    for i in dropped:
        lines[i] = ""

    # A PDF caption is one caption's. When the PDF's own caption was not found
    # (it follows a sub-table's "(b)"), a caption opening with the same few
    # words as a later one would take that one's number: the longest opening
    # run wins, and a label another caption keeps is not given out again.
    def opening_run(text, label):
        return max(common_prefix(words(text), theirs) for pdf, theirs in captions if pdf == label)

    runs = {}
    for _, _, text, new in found:
        if new:
            runs.setdefault(new, []).append(opening_run(text, new))
    kept = {old for _, old, _, new in found if new in (None, old)}
    for i, old, text, new in found:
        if not new or new == old or new in kept:
            continue
        if opening_run(text, new) < max(runs[new]) or runs[new].count(max(runs[new])) > 1:
            continue
        lines[i] = f"{new}: {text}"
        renamed[old] = new

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
    if labelled or dropped:
        body = re.sub(r"\n{3,}", "\n\n", body)
    if renamed:
        body = LINK.sub(relink, body)
    body, references = pdf_references(body, pdf_tokens(pdf_path))
    # A title named its link's float for the step above; an agent reads the
    # float's number in the text, so the title goes.
    untitled = LINK_TITLE.sub(lambda m: m.group(1) or m.group(2), body)
    if renamed or labelled or dropped or references or untitled != body:
        Path(md_path).write_text(untitled, encoding="utf-8")
    print(f"caption-numbers: {len(renamed)} captions renumbered from the PDF, {labelled} given a number, "
          f"{references} references renumbered")
    for old, new in renamed.items():
        print(f"  {old} -> {new}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
