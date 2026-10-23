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
# A caption set in a style with no punctuation after its label ("Table 1 Evaluation on ...",
# "Table2 Zero-shot ..."); body text can open the same way, so it counts only for a label
# no punctuated caption has.
LOOSE_CAPTION = re.compile(r"^(Table|Figure|Fig\.) ?((?:[A-Z]\.?)?\d+(?:\.\d+)?)\s+(?=[A-Z])(.+)", re.S)
SUBCAPTION = re.compile(r"\(?[a-z]\)")
# After the figure's pictures, where they share its line ("![](...) Figure 4: ...").
IMAGES = r"(?:!\[[^\]]*\]\([^)]*\)\s*)*"
MD_CAPTION = re.compile(rf"^{IMAGES}{LABEL}: (.+)$")
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
# The word naming a float before its number, which the HTML can get wrong ("Figure [1]" for
# Table 1, "[Footnote 18]" for Figure 7): the PDF's is taken. A reference after any other
# word must follow the same words in the PDF.
FLOAT_WORDS = {"figure", "figures", "fig", "figs", "table", "tables", "tab", "tabs"}
MISNAMED = FLOAT_WORDS | {"footnote", "section", "sec"}
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
TARGET = re.compile(r"^(?:!\[[^\]]*\]\([^)]*\)\s*)*(?:#+ +(?:([A-Z][a-z]+) +)?|(Table|Figure|Algorithm) +)((?:[A-Z]\.?)?\d+(?:\.\d+)*)(?=[:. (]|$)", re.M)


def words(text, limit=30):
    """The words a caption starts with, markup, mathematics and citations left out:
    "[Lin et al. \\[2018\\]](#bib.bib46)" in the markdown is "[46]" in the PDF."""
    text = re.sub(r"\[(?:[^\]\\]|\\.)*\]\(#bib\.[^)]*\)|\[\d+(?:\s*[,–-]\s*\d+)*\]", " ", text)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>|\\[a-zA-Z]+|[*_`\\]", " ", text)
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff")
    return re.findall(r"[a-z0-9]+", text.lower())[:limit]


def pdf_captions(pdf_path):
    """[(label, words)] for each caption in the PDF, in reading order."""
    found, loose = [], []
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
            elif m := LOOSE_CAPTION.match(text):
                kind = "Figure" if m.group(1) == "Fig." else m.group(1)
                found.append((f"{kind} {m.group(2)}", words(m.group(3))))
                loose.append(len(found) - 1)
    punctuated = {label for i, (label, _) in enumerate(found) if i not in loose}
    return [c for i, c in enumerate(found) if i not in loose or c[0] not in punctuated]


def tokens(text):
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff").replace("§", " section ")
    return TOKEN.findall(text.lower())


def pdf_tokens(pdf_path):
    return tokens(" ".join(re.sub(r"-\n(?=[a-z])", "", page.get_text()) for page in pymupdf.open(pdf_path)))


FORMULA = "zzformulazz"


def formula(m):
    """A formula's words: a number or a letter as the PDF prints it ("$20\\%$", "$b=1$"),
    else a word no PDF holds, as its symbols are printed otherwise there."""
    plain = re.sub(r"\\[%,;! ]|[{}]", " ", m.group(0).strip("$"))
    return f" {plain} " if re.fullmatch(r"[\w\s.,=+\-<>()/]*", plain) and "\n" not in plain else f" {FORMULA} "


def md_tokens(text):
    """The words of markdown as the PDF prints them: link text kept, markup left out, and a
    formula one word no PDF holds unless it is a plain number or letter (see formula)."""
    text = re.sub(r"\$\$.*?\$\$", f" {FORMULA} ", text, flags=re.S)
    text = re.sub(r"\$[^$\n]*\$", formula, text)
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
    index, kinded = {}, {}  # the k0 words before a place -> the places; kinded: before its float word
    k0 = min(REF_CONTEXT)
    for i in range(len(pdf) - k0):
        index.setdefault(tuple(pdf[i:i + k0]), []).append(i + k0)
        if pdf[i + k0] in FLOAT_WORDS and i + k0 + 1 < len(pdf):
            kinded.setdefault(tuple(pdf[i:i + k0]), []).append(i + k0 + 1)
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
        # The word naming the float, which the PDF may print otherwise: matched as any float word.
        misnamed = context[-1] if context and context[-1] in MISNAMED else None
        base = context[:-1] if misnamed else context

        def preceded(at, k):
            """Whether the k words before the number at `at` are the context's."""
            if not misnamed:
                return at >= k and pdf[at - k:at] == context[-k:]
            # Another word for the same kind ("Figs." for "Figures") is not taken: the PDF can
            # print a list of references otherwise ("Figs. 13 and 15 to 18").
            return (at > k and (pdf[at - 1] == misnamed
                                or pdf[at - 1] in FLOAT_WORDS and kind_of(pdf[at - 1]) != kind_of(misnamed))
                    and pdf[at - 1 - (k - 1):at - 1] == base[len(base) - (k - 1):])
        # The places in the PDF's words where the number stands: after the words
        # before the reference, or, where few words precede it (a paragraph's start, a formula),
        # before the words after it, those few words before the number.
        ends = []
        for k in REF_CONTEXT:
            if len(context) >= k:
                places = (index.get(tuple(context[-k0:]), []) + kinded.get(tuple(base[-k0:]), [])
                          if misnamed else index.get(tuple(context[-k0:]), []))
                ends = sorted({at for at in places if preceded(at, k)})
            if ends:  # a shorter run would match only more places
                break
        following = md_tokens(body[m.end():body.find("\n\n", m.end())])
        following = following[:following.index(FORMULA)] if FORMULA in following else following
        if 0 < len(context) < k0 and not sub:
            for k in REF_CONTEXT:
                if len(following) >= k:
                    ends = [at - k0 - 1 for at in index.get(tuple(following[:k0]), [])
                            if pdf[at - k0:at - k0 + k] == following[:k] and preceded(at - k0 - 1, len(context))]
                if ends:
                    break
        # Words the PDF prints twice, with two numbers: the words after the reference choose.
        if len({pdf[at] for at in ends}) > 1 and len(following) >= 3:
            ends = [at for at in ends if pdf[at + 1:at + 4] == following[:3]]
        numbers = {(kind_of(pdf[at - 1]) if misnamed else kind, pdf[at]) for at in ends}
        found = None
        if len(numbers) == 1 and PDF_REF.fullmatch(pdf[ends[0]]):
            printed, found = numbers.pop()
        if not found or (found == label.lower() and (not misnamed or printed == kind_of(misnamed))):
            continue
        renamed = misnamed and printed != kind_of(misnamed)
        kind = printed if misnamed else kind
        if (kind, found) not in targets:
            continue
        # A section, a theorem or an equation the link reaches by its own anchor is numbered
        # the HTML's way in the markdown too; a figure or a table the PDF's way (above).
        anchor = next((name for pattern, name in ANCHOR_KIND if re.search(pattern, m.group(2))), None)
        if anchor == "equation" or (kind not in ("figure", "table") and anchor == kind):
            continue
        if sub and pdf[ends[0] + 1:ends[0] + 2] != [sub]:
            after = ""  # "Figure 3(c)" where the PDF prints "Figure 4"
        new = found[0].upper() + found[1:]
        if renamed:  # the float word, in the link's text or just before the link
            word = kind.capitalize() + ("s" if misnamed in ("figures", "tables", "figs", "tabs") else "")
            named_at = re.compile(r"(?:Fig(?:ure)?s?|Tab(?:le)?s?|Footnote|Sec(?:tion)?)\.?(\s*)$", re.I)
            if named_at.search(before):
                before = named_at.sub(lambda w: word + w.group(1), before)
            else:
                out[-1] = named_at.sub(lambda w: word + w.group(1), out[-1])
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


def tied(text, captions):
    """The PDF's labels whose captions open with the longest run of `text`'s
    words, in reading order; none if the run is too short to count."""
    mine = words(text)
    scored = [(common_prefix(mine, theirs), pdf) for pdf, theirs in captions]
    best = max((n for n, _ in scored), default=0)
    if not mine or best == 0 or best < min(MIN_WORDS, len(mine)):
        return ()
    return tuple(pdf for n, pdf in scored if n == best)


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
    if len(labels) > 1 and label:  # "FFHQ-64", a table's caption and a figure's: the kind decides
        labels = {pdf for pdf in labels if pdf.split()[0] == label.split()[0]}
    return labels.pop() if len(labels) == 1 else None


def main(pdf_path, md_path):
    captions = pdf_captions(pdf_path)
    lines = Path(md_path).read_text(encoding="utf-8").split("\n")
    renamed, labelled, changed = {}, 0, 0  # old label -> new label
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

    # Captions that open alike ("Induction Heads. Models are trained on ...") match the
    # same PDF captions best. When as many PDF captions open as they all do (four
    # words), they are paired in reading order: the main text's figure and the
    # appendix's table with the same caption get one number each.
    groups = {}
    for j, (_, _, text, _) in enumerate(found):
        if best := tied(text, captions):
            groups.setdefault(best, []).append(j)
    for members in groups.values():
        alike = [words(found[j][2]) for j in members]
        near = [pdf for pdf, theirs in captions
                if all(common_prefix(mine, theirs) >= min(MIN_WORDS, len(mine)) for mine in alike)]
        if len(members) > 1 and len(near) == len(members):
            for j, new in zip(members, near):
                found[j] = found[j][:3] + (new,)

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
    # A label the PDF confirms stays its caption's; one a caption only had from the
    # HTML, matching no PDF caption, may go to the caption the PDF gives it.
    kept = {old for _, old, _, new in found if new == old}
    for i, old, text, new in found:
        if not new or new == old or new in kept:
            continue
        if opening_run(text, new) < max(runs[new]) or runs[new].count(max(runs[new])) > 1:
            continue
        lines[i] = lines[i][:MD_CAPTION.match(lines[i]).start(1)] + f"{new}: {text}"
        renamed[old] = new
        changed += 1

    # A label two captions carried says which of them a link meant only with
    # the "#2" the converter adds to its title: each caption's label, in order.
    shared = {}
    for i, old, _, _ in found:
        shared.setdefault(old, []).append(MD_CAPTION.match(lines[i]))
    shared = {old: [f"{'Figure' if m.group(1) == 'Fig.' else m.group(1)} {m.group(2)}" for m in caps]
              for old, caps in shared.items() if len(caps) > 1}
    shown = dict(renamed)
    renamed = {old: new for old, new in renamed.items() if new and seen[old] == 1}

    def relink(m):
        word, space, text, target, title = m.groups()
        # The float a link means is named at the start of its title
        # ("Table 8 ‣ 4.2 ..."), or is its own text ("[Figure 1](#S2.F1 ...)").
        named = re.match(FLOAT + r"(?: #(\d+))?", title or "")
        plural = re.fullmatch(r"(Table|Figure)s\s(\S+)", text)  # \cref's "Figures 16", titled "In E.5 ..."
        old = (named.group(0) if named else text if re.fullmatch(FLOAT, text)
               else f"{plural.group(1)} {plural.group(2)}" if plural else None)
        if named and named.group(1):
            old = old[:old.index(" #")]
            nth = shared.get(" ".join(old.split()), [])
            k = int(named.group(1))
            new = nth[k - 1] if k <= len(nth) and nth[k - 1] != " ".join(old.split()) else None
        else:
            new = renamed.get(" ".join(old.split())) if old else None
        if not new:
            return m.group(0)
        old_number, new_number = old.split()[1], new.split()[1]
        if re.fullmatch(FLOAT, text):
            text = new.replace(" ", text[len(text.split()[0])])
        elif text.endswith(old_number):
            text = text[: len(text) - len(old_number)] + new_number
        if named:
            title = new + title[named.end():]
        if word and new.split()[0] != old.split()[0] and not word.endswith("s"):
            word = new.split()[0]  # "Table [7]" that is a figure in the PDF
        quoted = f' "{title}"' if title is not None else ""
        return f'{word or ""}{space or ""}[{text}]({target}{quoted})'

    body = "\n".join(lines)
    if labelled or dropped:
        body = re.sub(r"\n{3,}", "\n\n", body)
    if renamed or shared:
        body = LINK.sub(relink, body)
    body, references = pdf_references(body, pdf_tokens(pdf_path))
    # A title named its link's float for the step above; an agent reads the
    # float's number in the text, so the title goes.
    untitled = LINK_TITLE.sub(lambda m: m.group(1) or m.group(2), body)
    if changed or labelled or dropped or references or untitled != body:
        Path(md_path).write_text(untitled, encoding="utf-8")
    print(f"caption-numbers: {changed} captions renumbered from the PDF, {labelled} given a number, "
          f"{references} references renumbered")
    for old, new in shown.items():
        print(f"  {old} -> {new}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
