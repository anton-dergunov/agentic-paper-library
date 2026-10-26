#!/usr/bin/env python3
"""Tier H: a paper's note written from its PDF's text layer against one written from its
markdown, both with today's guide/reading-prompt.md and the same model.

    PAPER_LIBRARY=<library> uv run python notes.py write [r]      # two notes per paper, into the cache
    PAPER_LIBRARY=<library> uv run python notes.py compare [r]    # one blind comparison per paper

r (default 1) is the repetition: r2 and r3 write each note again and compare them pair by
pair, to tell the format's effect from the reader's variance.

The markdown note is what `paperlib read` would write now: the reading view (references
and what follows cut), the prompt as it is. The text-layer note gets `pdftotext -layout`
with a line "[page N]" at each page, cut at the reference list the same way, and the
prompt with its lines about the markdown changed to describe the text layer (TXT_PROMPT).
The library's own notes are not used: they were written under older prompts.

The comparison sends the PDF and both notes, in an order shuffled with a fixed seed and
without saying where each came from, and asks for each note's errors checked against the
PDF and what each has that the other lacks. Each note's `## Conversion` section is left
out of it: the two list the problems of different inputs. Notes stay in the cache (they
quote the paper); the comparisons go to results/notes/.
"""

import importlib.util
import json
import random
import re
import sys

import inputs
import run

NOTES = inputs.OUT / "notes"
COMPARE = run.HERE / "results" / "notes"
PAPERS = ("soap", "ebr", "atma", "judgeshift")
FORMS = ("md", "txt")
# The prompt's lines that describe the markdown, and what the text-layer note gets instead.
TXT_PROMPT = [
    ("converted to markdown, with the PDF page on each heading (`## 3 Method (p. 4)`).",
     "as its PDF's text layer (`pdftotext -layout`, two-column pages side by side), with a line `[page N]` where "
     "each page starts."),
    ("Take the page from the nearest heading above the passage; for a section over several pages, give its range.",
     "Take the page from the nearest `[page N]` line above the passage."),
    ("`## Conversion` lists what the conversion broke in the markdown,", "`## Conversion` lists what the text layer broke,"),
    ("is missing or wrong in the markdown:", "is missing or wrong in the text layer:"),
]
# A reference heading alone on its line, or beside the other column's text.
REFERENCES = re.compile(r"^\s*(?:\d+\.?\s+)?(?:References|REFERENCES|Bibliography|BIBLIOGRAPHY)\s*$", re.M)
REFERENCES_IN_COLUMN = re.compile(r"(?:^|\s{3,})(?:\d+\.?\s+)?(?:References|REFERENCES|Bibliography|BIBLIOGRAPHY)(?:\s{3,}|$)", re.M)

COMPARE_SYSTEM = "You check notes on a research paper against the paper itself. Reply with JSON only."
COMPARE_PROMPT = """Above is a research paper's PDF. Below are two notes on it, A and B, written by a model for a research library, each from a different text extraction of the paper. Check both against the PDF.

For each note, list:
- "wrong": statements that the PDF contradicts or does not support (a wrong claim, a misattributed result, a mechanism described wrongly). For each, the claim in a few words, what the PDF says, and its page.
- "wrong_numbers": numbers that differ from the PDF (digits, units, which row or column, which baseline). The note's value, the PDF's value, the page.
- "wrong_pages": numbers or claims cited to a page more than one page away from where the PDF prints them. The item, the cited page, the right page.
- "garbled": equations or notation in the note that are malformed or have a wrong term.
- "only_here": substantive points this note has and the other lacks (a result, a caveat, a definition, an inconsistency in the paper), each in a few words. Leave out wording and order.

Then "verdict": "A", "B" or "equal" (equal when the differences are minor or balance out), and "why" in at most 40 words.

Reply with JSON only: {{"A": {{"wrong": [], "wrong_numbers": [], "wrong_pages": [], "garbled": [], "only_here": []}}, "B": {{...}}, "verdict": "...", "why": "..."}}

===== NOTE A =====
{a}

===== NOTE B =====
{b}
"""


def reader():
    """scripts/read-papers.py as a module (its name has a hyphen)."""
    spec = importlib.util.spec_from_file_location("read_papers", inputs.HERE.parents[1] / "scripts" / "read-papers.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def text_view(paper):
    """The text layer with page markers, cut at the reference list like the reading view: at
    its heading when that stands alone on its line, else (two columns) after the page it is on."""
    pages = inputs.txt(paper).read_text(encoding="utf-8").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    text = "".join("[page %d]\n%s\n" % (n, page) for n, page in enumerate(pages, 1))
    alone = [m for m in REFERENCES.finditer(text) if m.start() > len(text) // 3]
    beside = [m for m in REFERENCES_IN_COLUMN.finditer(text) if m.start() > len(text) // 3]
    following = beside and re.search(r"^\[page \d+\]$", text[beside[0].end():], re.M)
    if alone:
        cut = alone[0].start()
    elif following:
        cut = beside[0].end() + following.start()
    else:
        return text.rstrip() + "\n\n[End of the text layer. Nothing was left out: the references end it.]\n", "nothing"
    dropped = len(re.findall(r"^\[page \d+\]$", text[cut:], re.M))
    what = "the references" if alone else "the rest of the references"
    return (text[:cut].rstrip() + "\n\n[End of the main text. Left out: %s and whatever follows them, %d page%s.]\n"
            % (what, dropped, "s" * (dropped != 1)), "%d pages" % dropped)


def system_prompt(rp, paper, form, tickets):
    template = ((inputs.HERE.parents[1] / "guide" / "reading-prompt.md").read_text(encoding="utf-8")
                .replace("{{kinds}}", rp.kinds_list(tickets)).replace("{{wont_fix}}", rp.kinds_list(tickets, "wont-fix")))
    if form == "txt":
        for old, new in TXT_PROMPT:
            assert old in template, "reading-prompt.md changed: " + old
            template = template.replace(old, new)
    md = inputs.md_path(paper)
    return rp.SYSTEM + "\n\n" + template.replace("{{focus}}", "").replace("{{related}}", rp.related_list(md, md.parent))


def note_file(paper, form, rep):
    return NOTES / ("%s.%s%s.md" % (paper, form, "" if rep == 1 else ".r%d" % rep))


def write(rep=1):
    rp = reader()
    tickets = rp.load_tickets()
    for paper in PAPERS:
        for form in FORMS:
            target = note_file(paper, form, rep)
            if target.exists():
                continue
            if form == "md":
                meta, body = inputs.read_paper(inputs.md_path(paper))
                view, left = rp.read_view(meta, body), "the reading view's"
            else:
                view, left = text_view(paper)
            note, usage = rp.ask(run.MODEL, system_prompt(rp, paper, form, tickets), "The paper:\n\n" + view)
            NOTES.mkdir(parents=True, exist_ok=True)
            target.write_text(note.strip() + "\n", encoding="utf-8")
            log = COMPARE / "usage.jsonl"
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("a") as out:
                out.write(json.dumps(dict(usage, paper=paper, form=form, rep=rep, step="note", left_out=left,
                                          model=run.MODEL)) + "\n")
            print("%s %s r%d: %d in, %d out, $%.2f" % (paper, form, rep, usage["input"], usage["output"], usage["usd"] or 0),
                  flush=True)


def without_conversion(note):
    return re.sub(r"^## Conversion[ \t]*\n.*?(?=^## |\Z)", "", note.strip("`\n"), flags=re.M | re.S).strip()


def compare(rep=1):
    for paper in PAPERS:
        target = COMPARE / ("%s%s.json" % (paper, "" if rep == 1 else ".r%d" % rep))
        if target.exists():
            continue
        forms = list(FORMS)
        random.Random(paper if rep == 1 else "%s r%d" % (paper, rep)).shuffle(forms)
        notes = [without_conversion(note_file(paper, f, rep).read_text()) for f in forms]
        content = [run.document(inputs.pdf(paper)),
                   {"type": "text", "text": COMPARE_PROMPT.format(a=notes[0], b=notes[1])}]
        result, _ = run.request(COMPARE_SYSTEM, content)
        reply = result.get("result") or ""
        parsed = json.loads(reply[reply.index("{"):reply.rindex("}") + 1])
        by_form = {forms[0]: parsed["A"], forms[1]: parsed["B"]}
        verdict = {"A": forms[0], "B": forms[1]}.get(parsed.get("verdict"), "equal")
        COMPARE.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"rep": rep, "order": forms, "verdict": verdict, "why": parsed.get("why"), "notes": by_form,
                                      "usd": result.get("total_cost_usd"), "model": run.MODEL},
                                     ensure_ascii=False, indent=1))
        print("%s r%d: %s (%s)  %s  $%.2f" % (paper, rep, verdict, parsed.get("why"), "  ".join(
            "%s: %d wrong, %d numbers, %d pages, %d garbled, %d only here" % (
                f, len(n["wrong"]), len(n["wrong_numbers"]), len(n["wrong_pages"]), len(n["garbled"]),
                len(n["only_here"])) for f, n in by_form.items()), result.get("total_cost_usd") or 0), flush=True)


if __name__ == "__main__":
    {"write": write, "compare": compare}[sys.argv[1]](int(sys.argv[2]) if len(sys.argv) > 2 else 1)
