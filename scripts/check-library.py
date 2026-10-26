#!/usr/bin/env python3
"""Check that the library is consistent. Exits non-zero on any problem.

    ./scripts/check-library.py

Checks:

- every paper has the required frontmatter fields, with a known `source` (and
  a known `type` and `text-layer`, if it has them); a `.txt` paper is a PDF's
  text layer (`source: pdf`, a "[page 1]" line after the frontmatter), a `.md`
  paper a web article (`source: web`), and no paper has both;
- every file in notes/ is named after a paper in the library;
- every paper has its PDF at the mirrored path under PDF_ROOT, and every PDF
  there has a paper (README files aside);
- no PDF is inside the library's repository;
- catalog/topics.yaml declares well-formed folder paths whose parents are also
  declared, every declared folder exists, and every paper is in a declared
  folder;
- every entry in catalog/skipped.yaml has a title and a reason, names a
  declared topic if it names one, and is not a paper that is in the library;
- every review in reviews/ names a declared scope, and every local link in it
  (to a paper, a page in a paper's PDF, another review) resolves.
"""

import os
import sys
import unicodedata
from pathlib import Path

from paperlib import (
    LIBRARY_DIR, LIBRARY_ROOT, NOTES_DIR, PDF_ROOT, REQUIRED, SOURCES, TEXT_LAYER_STATES, TOPIC_PATH, TYPES,
    load_reviews, load_skipped, load_topics, norm_title, paper_index, paper_stem, pdf_path_for,
    split_frontmatter, review_links,
)


def check_catalog(index):
    problems = []
    topics = load_topics()
    if not topics:
        # A new library has no topics yet; papers without one are reported below.
        return ["catalog/topics.yaml is missing or empty"] if index else []
    for topic in topics:
        if not TOPIC_PATH.match(topic):
            problems.append(f"catalog/topics.yaml: malformed folder path `{topic}`")
        elif "/" in topic and topic.rsplit("/", 1)[0] not in topics:
            problems.append(f"catalog/topics.yaml: `{topic}` has an undeclared parent")
        if not (LIBRARY_DIR / topic).is_dir():
            problems.append(f"declared folder missing (run build-index.py): {topic}")

    ids, titles = {}, {}
    for paper, meta in index.items():
        topic = paper.parent.relative_to(LIBRARY_DIR).as_posix()
        if topic not in topics:
            problems.append(f"{paper.relative_to(LIBRARY_DIR)}: folder `{topic}` is not in catalog/topics.yaml")
        if meta.get("arxiv"):
            ids[str(meta["arxiv"])] = paper
        titles[norm_title(meta.get("title"))] = paper

    for i, entry in enumerate(load_skipped()):
        name = f"catalog/skipped.yaml entry {i + 1}"
        if not isinstance(entry, dict) or not entry.get("title") or not entry.get("reason"):
            problems.append(f"{name}: needs a title and a reason")
            continue
        if entry.get("topic") and entry["topic"] not in topics:
            problems.append(f"{name} ({entry['title']}): undeclared topic `{entry['topic']}`")
        paper = ids.get(str(entry.get("arxiv"))) or titles.get(norm_title(entry["title"]))
        if paper:
            problems.append(f"{name} ({entry['title']}): skipped but in the library at "
                            f"{paper.relative_to(LIBRARY_DIR)}")
    return problems


def check_reviews():
    problems = []
    topics = load_topics()
    for scope, review in load_reviews().items():
        name = review["main"].relative_to(LIBRARY_ROOT)
        if scope not in topics:
            problems.append(f"{name}: scope `{scope}` is not in catalog/topics.yaml")
        for f in review["files"]:
            for target, _, ok in review_links(f):
                if not ok:
                    problems.append(f"{f.relative_to(LIBRARY_ROOT)}: broken link {target} "
                                    "(scripts/review-status.py --fix-links)")
    return problems


def check_paper(paper, meta):
    """The problems of one paper's file and frontmatter."""
    rel = paper.relative_to(LIBRARY_DIR)
    if not meta:
        return [f"{rel}: no frontmatter"]
    problems = [f"{rel}: missing or empty `{field}`" for field in REQUIRED if not meta.get(field)]
    if meta.get("source") and meta["source"] not in SOURCES:
        problems.append(f"{rel}: unknown source `{meta['source']}`")
    if meta.get("type") and meta["type"] not in TYPES:
        problems.append(f"{rel}: unknown type `{meta['type']}`")
    if meta.get("text-layer") and meta["text-layer"] not in TEXT_LAYER_STATES:
        problems.append(f"{rel}: unknown text-layer `{meta['text-layer']}`")
    wanted = "pdf" if paper.suffix == ".txt" else "web"
    if meta.get("source") in SOURCES and meta["source"] != wanted:
        problems.append(f"{rel}: a {paper.suffix} paper has `source: {wanted}`, not `{meta['source']}`")
    if paper.suffix == ".txt":
        with open(paper, encoding="utf-8") as file:
            body = split_frontmatter(file.read(65536))[1]
        if not body.startswith("[page 1]\n"):
            problems.append(f"{rel}: no text layer after the frontmatter (paperlib text {rel})")
    return problems


def main():
    problems = []
    index = paper_index()
    papers = sorted(index)
    # A PDF tree with no PDFs in it means they are not on this machine (a fresh
    # clone, a cloud session): the papers' files are still checked, the PDFs are not.
    have_pdfs = PDF_ROOT.exists() and next(PDF_ROOT.rglob("*.pdf"), None) is not None
    if not have_pdfs:
        print(f"check-library: no PDFs under {PDF_ROOT}; PDF checks skipped")

    seen = {}
    for paper in papers:
        problems += check_paper(paper, index[paper])
        key = paper.with_suffix("")
        if key in seen:
            problems.append(f"{paper.relative_to(LIBRARY_DIR)}: also in the library as {seen[key].name}")
        seen[key] = paper
        if have_pdfs and not pdf_path_for(paper).exists():
            problems.append(f"{paper.relative_to(LIBRARY_DIR)}: no PDF at {pdf_path_for(paper)}")

    # A synced folder may store a name decomposed ("й" as two code points).
    expected = {unicodedata.normalize("NFC", str(pdf_path_for(p))) for p in papers}
    if PDF_ROOT.exists():
        for pdf in PDF_ROOT.rglob("*.pdf"):
            if unicodedata.normalize("NFC", str(pdf)) not in expected:
                problems.append(f"PDF without a paper: {pdf.relative_to(PDF_ROOT)}")

    problems += check_catalog(index)

    stems = {paper_stem(p) for p in papers}
    for note in sorted(NOTES_DIR.glob("*.md")):
        if note.name != "README.md" and paper_stem(note) not in stems:
            problems.append(f"notes/{note.name}: no paper with this name in the library")

    problems += check_reviews()

    # os.walk does not follow symlinks, so the pdf/ link to PDF_ROOT is skipped,
    # and so is PDF_ROOT itself when it is a (git-ignored) folder in the library.
    for folder, dirs, files in os.walk(LIBRARY_ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules") and Path(folder, d) != PDF_ROOT]
        for name in files:
            if name.lower().endswith(".pdf"):
                pdf = Path(folder) / name
                problems.append(f"PDF inside the repository: {pdf.relative_to(LIBRARY_ROOT)}")

    for p in problems:
        print(p)
    print(f"check-library: {len(papers)} papers, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
