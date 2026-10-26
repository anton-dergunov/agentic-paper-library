#!/usr/bin/env python3
"""Build the copies that the agent sessions of tiers D and F run in, in the cache (paper
text is never committed).

    PAPER_LIBRARY=<library> uv run python copies.py [lib] [pdf] [txt] [txtpdf]     # all by default

- lib: the library as an agent finds it: the guide, catalog/, notes/, reviews/ and the
  paper markdown without figures or PDFs (review-usefulness/copies.py, condition "asis").
- pdf: the PDFs under the same topic tree, as APFS clones (no extra disk), and a one-line
  CLAUDE.md.
- txt: each PDF's text layer (`pdftotext -layout`) under the same tree, with a line
  "[page N]" where each page starts, and a one-line CLAUDE.md: the cheap pipeline an agent
  could build for itself, page numbers included.
- txtpdf (tier F): the txt copy with each PDF beside its text file, twice: txtpdf-plain,
  whose CLAUDE.md says only what the files are, and txtpdf-hint, whose CLAUDE.md adds that a
  value drawn in a figure is read from the PDF's page. Built from the txt copy.

Each copy is made read-only, so that a session cannot write to it through the shell. An
existing copy is rebuilt.
"""

import concurrent.futures
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import inputs

COPIES = inputs.OUT / "copies"
PDF_ROOT = (inputs.LIBRARY_ROOT / "pdf").resolve()
CLAUDE_MD = {
    "pdf": "Papers are PDFs under the topic folders; answer with page citations.\n",
    "txt": ("Papers are the text layers of their PDFs, one .txt file each under the topic folders; a line "
            "\"[page N]\" marks where page N starts. Answer with page citations.\n"),
    "txtpdf-plain": ("Each paper is here as its PDF (.pdf) and as the PDF's text layer (.txt, same name) under the "
                     "topic folders; in the text layer a line \"[page N]\" marks where page N starts. Answer with "
                     "page citations.\n"),
}
CLAUDE_MD["txtpdf-hint"] = CLAUDE_MD["txtpdf-plain"] + "A value drawn in a figure is not in the text: read that page of the PDF.\n"


def path(name):
    return COPIES / ("lib-asis" if name == "lib" else name)


def lock(copy, locked):
    subprocess.run(["chmod", "-R", "a-w" if locked else "u+w", str(copy)], check=True)


def fresh(copy):
    if copy.exists():
        lock(copy, False)
        shutil.rmtree(copy)
    copy.mkdir(parents=True)


def build_lib():
    spec = importlib.util.spec_from_file_location("rucopies", inputs.HERE.parent / "review-usefulness" / "copies.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    COPIES.mkdir(parents=True, exist_ok=True)
    module.build(str(inputs.LIBRARY_ROOT), str(COPIES), "asis", "asis")


def pdfs():
    return sorted(p for p in PDF_ROOT.rglob("*.pdf") if not p.name.startswith("."))


def build_pdf():
    copy = path("pdf")
    fresh(copy)
    for source in pdfs():
        target = copy / source.relative_to(PDF_ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cp", "-c", str(source), str(target)], check=True)  # a clone on APFS
    (copy / "CLAUDE.md").write_text(CLAUDE_MD["pdf"])
    lock(copy, True)
    print("pdf: %s, %d PDFs" % (copy, len(pdfs())))


def text_layer(source, target):
    done = subprocess.run(["pdftotext", "-layout", str(source), "-"], capture_output=True)
    pages = done.stdout.decode("utf-8", "replace").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    target.write_text("".join("[page %d]\n%s\n" % (n, page) for n, page in enumerate(pages, 1)), encoding="utf-8")
    return done.returncode


def build_txt():
    copy = path("txt")
    fresh(copy)
    jobs = []
    for source in pdfs():
        target = (copy / source.relative_to(PDF_ROOT)).with_suffix(".txt")
        target.parent.mkdir(parents=True, exist_ok=True)
        jobs.append((source, target))
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count() or 4) as pool:
        failed = sum(code != 0 for code in pool.map(lambda job: text_layer(*job), jobs))
    (copy / "CLAUDE.md").write_text(CLAUDE_MD["txt"])
    lock(copy, True)
    print("txt: %s, %d text layers, %d with pdftotext errors" % (copy, len(jobs), failed))


def build_txtpdf():
    for variant in ("txtpdf-plain", "txtpdf-hint"):
        copy = path(variant)
        fresh(copy)
        copy.rmdir()
        subprocess.run(["cp", "-cR", str(path("txt")), str(copy)], check=True)  # clones on APFS
        lock(copy, False)
        for source in pdfs():
            subprocess.run(["cp", "-c", str(source), str(copy / source.relative_to(PDF_ROOT))], check=True)
        (copy / "CLAUDE.md").write_text(CLAUDE_MD[variant])
        lock(copy, True)
        print("%s: %s, %d PDFs beside their text layers" % (variant, copy, len(pdfs())))


if __name__ == "__main__":
    for name in sys.argv[1:] or ["lib", "pdf", "txt", "txtpdf"]:
        {"lib": build_lib, "pdf": build_pdf, "txt": build_txt, "txtpdf": build_txtpdf}[name]()
