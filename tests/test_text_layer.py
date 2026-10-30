#!/usr/bin/env python3
"""The text layer: how a paper file is made from its PDF, and what a reader is shown.

    paperlib test   (or: python3 tests/test_text_layer.py)

The cases on strings need nothing installed; the ones on tests/fixtures/small-paper.pdf
(three pages: the main text, the references, an appendix; printed by Chrome from
small-paper.html beside it) need poppler's pdftotext and are skipped without it. No network
is used.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ENGINE / "scripts"))
os.environ.setdefault("PAPER_LIBRARY", tempfile.mkdtemp())  # paperlib reads a library when it loads

import paperlib  # noqa: E402

FIXTURE = ENGINE / "tests" / "fixtures" / "small-paper.pdf"
# A reference list, as the cut finds one: the heading, then entries with their years.
REFS = "".join(f"[{n}] A. Author. Paper {n}. {2010 + n}.\n" for n in range(1, 7))
META = {"title": "A Small Paper", "source": "pdf"}
failures = 0


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f": {detail}" if detail and not ok else ""))


def two_column(left, right):
    return "\n".join(f"{a:<40}{b}" for a, b in zip(left, right))


def strings():
    text = paperlib.pages_text("Title\nAbstract\n\fIntro\n\f")
    check("a [page N] line before each page", text == "[page 1]\nTitle\nAbstract\n\n[page 2]\nIntro\n\n", repr(text))
    check("a last empty page is kept, the trailing form feed is not",
          paperlib.pages_text("a\f\f").count("[page ") == 2)

    body = paperlib.pages_text("Intro text " * 40 + "\f" + "Results text " * 40 + "\nReferences\n" + REFS + "\fAppendix A\n\f")
    view = paperlib.text_view(META, body)
    check("cut at a references heading alone on its line",
          "Paper 1." not in view and "Results text" in view and "Appendix A" not in view
          and "Left out: the references and whatever follows them, 1 page." in view, view[-200:])
    whole = paperlib.text_view(META, body, appendix=True)
    check("--appendix keeps everything", "Paper 1." in whole and "Appendix A" in whole)

    page2 = two_column(["Results text"] * 20 + ["", "the end."] + [""] * 6,
                       ["more results"] * 20 + ["References"] + REFS.splitlines() + [""])
    body = paperlib.pages_text("Intro text " * 80 + "\f" + page2 + "\f" + "[7] B. 2021.\nAppendix B\n\f")
    view = paperlib.text_view(META, body)
    check("in two columns, cut after the page the heading is on",
          "the end." in view and "Appendix B" not in view and "the rest of the references" in view, view[-200:])

    early = paperlib.pages_text("Related work, see References\nReferences\n" + REFS + "\f" + "Method text " * 200 + "\f")
    check("a references heading in the first tenth is not the cut",
          "Method text" in paperlib.text_view(META, early))
    label = paperlib.pages_text("Intro text " * 200 + "\f" + "References     the counts, we obtain\n" + "More text " * 300 + "\f")
    check("a heading with no years after it (a figure's label) is not the cut",
          "More text" in paperlib.text_view(META, label))
    check("no reference list: the whole text, said so",
          "Nothing was left out" in paperlib.text_view(META, paperlib.pages_text("Text " * 100 + "\f")))

    web = {"title": "An Article", "source": "web"}
    article = "# An Article\n\n" + "Prose. " * 200 + "\n\n## References\n\n1. A cited work.\n"
    check("a web article is cut at its references heading",
          "A cited work" not in paperlib.text_view(web, article))

    check("text quality: no text", paperlib.text_quality(paperlib.pages_text("\f\f\f")) == "no text")
    check("text quality: unmapped glyphs",
          "unmapped" in paperlib.text_quality(paperlib.pages_text(("word �� " * 300) + "\f")))
    check("text quality: fine", paperlib.text_quality(paperlib.pages_text(("A sentence of words. " * 50) + "\f")) == "")

    check("paper_stem strips the paper suffixes, and nothing else",
          [paperlib.paper_stem(s) for s in ("x/Zep. A Graph.txt", "Zep. A Graph", "Q.md", "Q.pdf", "v2.0")]
          == ["Zep. A Graph", "Zep. A Graph", "Q", "Q", "v2.0"])
    check("paper_stem is NFC", paperlib.paper_stem("Мей.txt") == "Мей")

    with tempfile.TemporaryDirectory() as tmp:
        paper = Path(tmp) / "A Small Paper.txt"
        body = "[page 1]\nInventory: 3\r\n  efficiency.\r\nmore\rtext\n"
        paperlib.write_paper(paper, META, body)
        meta, read = paperlib.read_paper(paper)
        paperlib.write_paper(paper, {**meta, "type": "method"}, read)
        check("a frontmatter edit leaves the text layer's carriage returns as they were",
              read == body and paper.read_bytes().endswith(body.encode()), repr(read))


def fixture():
    if not shutil.which("pdftotext"):
        print("skip the fixture PDF: pdftotext is not installed (brew install poppler)")
        return
    text = paperlib.text_layer(FIXTURE)
    check("the fixture's three pages are marked",
          paperlib.PAGE_MARK.findall(text) == ["1", "2", "3"] and text.startswith("[page 1]\n"), text[:200])
    check("the fixture's page count agrees with pdfinfo", paperlib.page_count(FIXTURE) == 3)
    with tempfile.TemporaryDirectory() as tmp:
        paper = Path(tmp) / "A Small Paper.txt"
        problem = paperlib.write_text_paper(paper, {**META, "summary": "s", "added": "2026-10-26",
                                                    "text-layer": "broken"}, FIXTURE)
        meta, body = paperlib.read_paper(paper)
        check("a paper file: frontmatter, then the text layer", body == text and meta["title"] == META["title"])
        check("a readable text layer keeps a `text-layer: broken` mark set by hand",
              not problem and meta.get("text-layer") == "broken")
        view = paperlib.text_view(meta, body)
        check("the fixture's view stops at its references",
              "47.9" in view and "An earlier paper" not in view and "batch size 64" not in view, view[-300:])


if __name__ == "__main__":
    strings()
    fixture()
    sys.exit(1 if failures else 0)
