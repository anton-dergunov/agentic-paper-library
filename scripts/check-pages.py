#!/usr/bin/env python3
"""Check the pages that notes and reviews give for tables and figures:

    paperlib check-pages [--fix] [--list] [<scope or note> ...]

A note's "(p. 8, Table 1)" and a review's "[p. 8, Table 1](…?dest=table.1&page=8)" are
right when page 8 prints the caption "Table 1". The caption's page is found in the paper's
text layer, and in its PDF (as `paperlib locate` finds it) when the text layer has no such
caption or several. A range ("p. 8–9, Table 1") is right when it holds the caption's page.

Prints, per note or review with a wrong page, how its citations are shifted, and a total.
--list prints each wrong citation. --fix rewrites what the captions prove: a page becomes
the caption's page; a range grows to hold it. A caption further than MAX_SHIFT pages away
is reported as "far", not fixed: such a citation usually gives the page of the text that
discusses the float (an appendix figure discussed in the main text). With no scope, every
note and review is checked. Exits 1 when a page is wrong and --fix is not given.
"""

import importlib.util
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from paperlib import (LIBRARY_DIR, LIBRARY_ROOT, NOTES_DIR, PAGE_MARK, PDF_LINK_BASE, load_reviews, paper_files,
                      paper_stem, pdf_path_for, read_paper)

MAX_SHIFT = 5

# A page reference: "p. 8", "pp. 8–9", "p. 8-9".
_PAGES = re.compile(r"\b(pp?\.)[ \t]*(\d+)(?:[ \t]*([–—-])[ \t]*(\d+))?")
_MORE_PAGES = re.compile(r"[ \t]*,[ \t]*(\d+)(?:[ \t]*([–—-])[ \t]*(\d+))?(?=[ \t]*(?:[,;)]|$))")
_LABEL = r"(?:[A-Z]\.?)?\d+(?:\.\d+)?[a-z]?|[IVXL]+\b"
# A table or figure named in a citation: "Table 1", "Tables 1–2", "Figs. 3 and 4", "Fig. 3b".
_FLOATS = re.compile(rf"\b(Tables?|Tab\.|Figures?|Figs?\.?)[ \t]*({_LABEL})"
                     rf"(?:[ \t]*(?:[–—-]|,|and)[ \t]*({_LABEL}))?")
# A parenthesised citation in a note: anything in parentheses that names a page.
_GROUP = re.compile(r"\(([^()]*\bpp?\.[ \t]*\d[^()]*)\)")
# A caption's first words where a text-layer segment (a column of a line) starts.
_CAPTION = re.compile(rf"^(Table|TABLE|Tab\.|Figure|FIGURE|Fig\.|FIG\.)[ \t]*({_LABEL})"
                      rf"[ \t]*(?:([:|—–])|(\.)(?=[ \t]+[A-Z(]|[ \t]*$)|$)")
_COLUMN_GAP = re.compile(r"[ \t]{3,}")
# Review links, as `review-refs --inline` writes them.
_REVIEW_LINK = re.compile(r"(?<!\!)\[((?:\\.|[^\]\\])*)\]\((" + re.escape(PDF_LINK_BASE) + r"[^)\s]+)\)")


def kind_of(word):
    return "table" if word.lower().startswith("tab") else "figure"


def base_label(label):
    """A float's number as its caption prints it: "3b" (a panel) is Figure 3."""
    return re.sub(r"(?<=\d)[a-z]$", "", label).upper()


@dataclass
class Ref:
    """A page reference in a citation, with the tables and figures it names."""
    start: int  # where "p. 8" or "pp. 8–9" is in the text
    end: int
    prefix: str
    first: int
    last: int
    dash: str
    floats: list = field(default_factory=list)  # [(kind, label)]

    def text(self, first, last):
        """The reference as written, with other pages."""
        pages = f"{first}" if first == last else f"{first}{self.dash or '–'}{last}"
        return f"{self.prefix} {pages}" if self.prefix else pages


def float_labels(text):
    """[(kind, label)] for the tables and figures a piece of citation names; a range
    "Tables 1–3" is spelled out."""
    out = []
    for m in _FLOATS.finditer(text):
        kind, a, b = kind_of(m.group(1)), m.group(2), m.group(3)
        out.append((kind, a))
        if b:
            if a.isdigit() and b.isdigit() and 0 < int(b) - int(a) <= 6 and "," not in m.group(0) \
                    and "and" not in m.group(0):
                out += [(kind, str(n)) for n in range(int(a) + 1, int(b) + 1)]
            else:
                out.append((kind, b))
    return out


def parse_item(text, offset):
    """The page references in one citation item ("p. 8, Table 1"), each with the floats
    named after it (or before it, when the item has one page)."""
    refs = []
    for m in _PAGES.finditer(text):
        first = int(m.group(2))
        last = int(m.group(4)) if m.group(4) else first
        if last >= first:
            refs.append(Ref(offset + m.start(), offset + m.end(), m.group(1), first, last, m.group(3) or ""))
        # Bare pages continuing the list: "pp. 3, 9".
        at = m.end()
        while c := _MORE_PAGES.match(text, at):
            first = int(c.group(1))
            last = int(c.group(3)) if c.group(3) else first
            if last >= first:
                refs.append(Ref(offset + c.start(1), offset + c.end(), "", first, last, c.group(2) or ""))
            at = c.end()
    if not refs:
        return []
    for m in _FLOATS.finditer(text):
        at = offset + m.start()
        before = [r for r in refs if r.end <= at]
        owner = before[-1] if before else (refs[0] if len(refs) == 1 else None)
        if owner:
            owner.floats += float_labels(m.group(0))
    return refs


def note_refs(text):
    """Every page reference in a note's parenthesised citations; items are split at ";"."""
    refs = []
    for g in _GROUP.finditer(text):
        offset = g.start(1)
        for item in g.group(1).split(";"):
            refs += parse_item(item, offset)
            offset += len(item) + 1
    return refs


def text_pages(body):
    """{page number: text} from a text layer's "[page N]" lines."""
    marks = list(PAGE_MARK.finditer(body))
    return {int(m.group(1)): body[m.end():marks[i + 1].start() if i + 1 < len(marks) else len(body)]
            for i, m in enumerate(marks)}


def caption_pages(pages):
    """{(kind, label): {page: strength}}: where the text layer prints a caption's first
    words at the start of a column; strength 2 after ":" or "|", 1 after "." or alone."""
    found = defaultdict(dict)
    for n, text in pages.items():
        for line in text.splitlines():
            for seg in _COLUMN_GAP.split(line.strip()):
                m = _CAPTION.match(seg)
                if m:
                    key = (kind_of(m.group(1)), m.group(2).upper())
                    found[key][n] = max(found[key].get(n, 0), 2 if m.group(3) else 1)
    return found


class Paper:
    """A paper's caption pages, from its text layer, and from its PDF when needed."""

    def __init__(self, path, use_pdf=True):
        self.path = path
        self.pages = text_pages(read_paper(path)[1])
        self.captions = caption_pages(self.pages)
        self.use_pdf = use_pdf
        self._doc = self._every = None
        self._cache = {}

    def caption_page(self, kind, label):
        """(page, None), or (None, why)."""
        key = (kind, base_label(label))
        if key not in self._cache:
            self._cache[key] = self._find(*key)
        return self._cache[key]

    def _find(self, kind, label):
        hits = self.captions.get((kind, label), {})
        strong = [p for p, s in hits.items() if s == 2]
        if len(hits) == 1:
            return next(iter(hits)), None
        if len(strong) == 1:
            return strong[0], None
        page, why = self._pdf_find(kind, label)
        if page:
            return page, None
        return None, ("no caption" if not hits else f"captions on p. {', '.join(map(str, sorted(hits)))}") \
            + (f"; PDF: {why}" if why else "")

    def _pdf_find(self, kind, label):
        if not self.use_pdf:
            return None, None
        if self._every is None:
            import locate
            pdf = pdf_path_for(self.path)
            if not pdf.is_file():
                self._every = []
                return None, "no PDF"
            import pymupdf
            self._doc = pymupdf.open(pdf)
            self._every = [locate.Page(p) for p in self._doc]
        if not self._every:
            return None, "no PDF"
        import locate
        page, rects, why = locate._find(self._every, kind, label, None)
        return (page, None) if rects else (None, why)

    def close(self):
        if self._doc:
            self._doc.close()


@dataclass
class Check:
    """One page reference checked: right, wrong (with the pages the captions are on), or
    unprovable (with why)."""
    ref: Ref
    verdict: str  # "right", "wrong", "far", "unknown"
    pages: tuple = ()
    why: str = ""

    @property
    def fixed(self):
        """The page reference as the captions prove it."""
        lo, hi = min(self.pages), max(self.pages)
        if self.ref.first == self.ref.last:
            return self.ref.text(lo, hi)
        return self.ref.text(min(lo, self.ref.first), max(hi, self.ref.last))

    @property
    def shift(self):
        return min(self.pages) - self.ref.first if self.ref.first == self.ref.last else None


def check_ref(ref, paper):
    if not ref.floats:
        return None
    pages, whys = set(), []
    for kind, label in ref.floats:
        page, why = paper.caption_page(kind, label)
        if page:
            pages.add(page)
        else:
            whys.append(f"{kind.title()} {label}: {why}")
    if whys:
        return Check(ref, "unknown", tuple(sorted(pages)), "; ".join(whys))
    if all(ref.first <= p <= ref.last for p in pages) and (ref.first != ref.last or len(pages) == 1):
        return Check(ref, "right", tuple(sorted(pages)))
    far = max(abs(p - ref.first) for p in pages) > MAX_SHIFT if ref.first == ref.last else \
        any(p < ref.first - MAX_SHIFT or p > ref.last + MAX_SHIFT for p in pages)
    return Check(ref, "far" if far else "wrong", tuple(sorted(pages)))


def apply(text, fixes):
    """The text with page references replaced: [(Ref, new text)]."""
    for ref, new in sorted(fixes, key=lambda f: -f[0].start):
        text = text[:ref.start] + new + text[ref.end:]
    return text


# --- notes -----------------------------------------------------------------------------

def papers_by_stem():
    return {paper_stem(p): p for p in paper_files() if p.suffix == ".txt"}


def check_note(note, paper):
    text = note.read_text(encoding="utf-8")
    return text, [c for r in note_refs(text) if (c := check_ref(r, paper))]


# --- reviews ---------------------------------------------------------------------------

def _review_refs_module():
    spec = importlib.util.spec_from_file_location("review_refs", Path(__file__).with_name("review-refs.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def review_link_refs(inline):
    """(Ref, paper stem, link match) for each page link in a review written inline: the
    reference is read from the link's text, with the float its `dest` names when the text
    names none, and checked against the link's `page`."""
    from urllib.parse import unquote
    out = []
    for m in _REVIEW_LINK.finditer(inline):
        label, url = m.group(1), m.group(2)
        parts = urlsplit(url)
        query = parse_qs(parts.query)
        refs = parse_item(label, m.start(1))
        if len(refs) != 1:
            continue
        ref = refs[0]
        dest = query.get("dest", [""])[0]
        dm = re.match(r"^(table|figure)\.(.+)$", dest)
        if not ref.floats and dm:
            ref.floats = [(dm.group(1), dm.group(2))]
        out.append((ref, paper_stem(unquote(parts.path)), m))
    return out


def fix_review_text(inline, fixes):
    """The inline review with each fixed link's text and `page=` rewritten: [(Ref, link
    match, new reference text, new page)]."""
    for ref, m, new, page in sorted(fixes, key=lambda f: -f[0].start):
        url = re.sub(r"([?&]page=)\d+", rf"\g<1>{page}", m.group(2))
        label = m.group(1)[:ref.start - m.start(1)] + new + m.group(1)[ref.end - m.start(1):]
        inline = inline[:m.start()] + f"[{label}]({url})" + inline[m.end():]
    return inline


# --- the command -----------------------------------------------------------------------

def scope_filter(args):
    """(notes to check, review files to check) for the arguments."""
    stems = papers_by_stem()
    notes = sorted(NOTES_DIR.glob("*.md"))
    reviews = [f for r in load_reviews().values() for f in r["files"]]
    if not args:
        return notes, reviews
    chosen_notes, chosen_reviews = [], []
    for arg in args:
        path = Path(arg).expanduser()
        if path.suffix == ".md" and path.exists():
            (chosen_reviews if "reviews" in path.resolve().parts else chosen_notes).append(path.resolve())
            continue
        scope = arg.strip("/")
        chosen_notes += [n for n in notes if n.stem in stems
                         and (stems[n.stem].parent.relative_to(LIBRARY_DIR).as_posix() + "/").startswith(scope + "/")]
        for s, r in load_reviews().items():
            if (s + "/").startswith(scope + "/"):
                chosen_reviews += r["files"]
    return chosen_notes, chosen_reviews


def describe(check):
    floats = ", ".join(f"{k.title()} {l}" for k, l in check.ref.floats)
    return f"{check.ref.text(check.ref.first, check.ref.last)}, {floats}"


def main(argv):
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__.strip())
        return 0
    fix = "--fix" in argv
    listing = "--list" in argv
    args = [a for a in argv if not a.startswith("--")]
    notes, reviews = scope_filter(args)
    stems = papers_by_stem()
    papers = {}

    def paper(stem):
        if stem not in papers:
            papers[stem] = Paper(stems[stem]) if stem in stems else None
        return papers[stem]

    totals = {"notes": Counter(), "reviews": Counter()}
    shifts = {"notes": Counter(), "reviews": Counter()}
    files_wrong = Counter()

    def report(name, checks, where):
        counts = Counter(c.verdict for c in checks)
        totals[where].update(counts)
        for c in checks:
            if c.verdict == "wrong" and c.shift is not None:
                shifts[where][c.shift] += 1
        bad = [c for c in checks if c.verdict in ("wrong", "far")]
        if bad:
            files_wrong[where] += any(c.verdict == "wrong" for c in bad)
            moved = Counter(f"{c.shift:+d}" if c.shift is not None else "range" for c in bad if c.verdict == "wrong")
            far = sum(c.verdict == "far" for c in bad)
            print(f"{name}: {len(bad)} of {len(checks)} wrong"
                  + (f" ({', '.join(f'{k}: {v}' for k, v in sorted(moved.items()))})" if moved else "")
                  + (f", {far} far" if far else ""))
            if listing:
                for c in bad:
                    print(f"  {describe(c)} -> {'p. ' + ', '.join(map(str, c.pages))}{' (far)' if c.verdict == 'far' else ''}")
        if listing:
            for c in checks:
                if c.verdict == "unknown":
                    print(f"  ? {describe(c)}: {c.why}")

    for note in notes:
        p = paper(note.stem)
        if not p:
            continue
        text, checks = check_note(note, p)
        report(note.relative_to(LIBRARY_ROOT), checks, "notes")
        if fix:
            fixes = [(c.ref, c.fixed) for c in checks if c.verdict == "wrong"]
            if fixes:
                note.write_text(apply(text, fixes), encoding="utf-8")

    if reviews:
        rr = _review_refs_module()
    for review in reviews:
        old = review.read_text(encoding="utf-8")
        inline = rr.to_inline(old)
        checks, fixes = [], []
        for ref, stem, m in review_link_refs(inline):
            p = paper(stem)
            c = p and check_ref(ref, p)
            if not c:
                continue
            checks.append(c)
            if c.verdict == "wrong":
                page = min(c.pages) if ref.first == ref.last else min(min(c.pages), ref.first)
                fixes.append((ref, m, c.fixed, page))
        report(review.relative_to(LIBRARY_ROOT), checks, "reviews")
        if fix and fixes:
            review.write_text(rr.to_references(fix_review_text(inline, fixes), review), encoding="utf-8")

    for p in papers.values():
        if p:
            p.close()
    print()
    for where in ("notes", "reviews"):
        t = totals[where]
        checked = sum(t.values())
        if not checked:
            continue
        common = ", ".join(f"{s:+d}: {n}" for s, n in shifts[where].most_common(4))
        wrong = f"{t['wrong']} wrong in {files_wrong[where]} files ({common})" if t["wrong"] else "0 wrong"
        print(f"{where}: {checked} citations of a table or figure; {t['right']} right, {wrong}, "
              f"{t['far']} far, {t['unknown']} unprovable" + (" — fixed the wrong ones" if fix and t["wrong"] else ""))
    return 1 if any(t["wrong"] for t in totals.values()) and not fix else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
