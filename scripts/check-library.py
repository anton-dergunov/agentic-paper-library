#!/usr/bin/env python3
"""Check that the library is consistent. Exits non-zero on any problem.

    ./scripts/check-library.py

Checks:

- every paper has the required frontmatter fields, with a known `source` (and
  a known `type`, if it has one);
- every file in notes/ is named after a paper in the library;
- every paper has its PDF at the mirrored path under PDF_ROOT, and every PDF
  there has a paper (README files aside);
- every relative image link in a paper resolves, and every image is used;
- no PDF is inside the repository;
- catalog/topics.yaml declares well-formed folder paths whose parents are also
  declared, every declared folder exists, and every paper is in a declared
  folder;
- every entry in catalog/skipped.yaml has a title and a reason, names a
  declared topic if it names one, and is not a paper that is in the library.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

from paperlib import (
    LIBRARY_DIR, NOTES_DIR, PDF_ROOT, REPO_ROOT, REQUIRED, SOURCES, TOPIC_PATH, TYPES,
    load_skipped, load_topics, norm_title, paper_files, pdf_path_for, read_paper,
)

# Markdown images, and <img> tags (used inside the HTML tables of complex tables).
IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)|<img\s[^>]*?src=\"([^\"]+)\"")


def check_catalog(papers):
    problems = []
    topics = load_topics()
    if not topics:
        return ["catalog/topics.yaml is missing or empty"]
    for topic in topics:
        if not TOPIC_PATH.match(topic):
            problems.append(f"catalog/topics.yaml: malformed folder path `{topic}`")
        elif "/" in topic and topic.rsplit("/", 1)[0] not in topics:
            problems.append(f"catalog/topics.yaml: `{topic}` has an undeclared parent")
        if not (LIBRARY_DIR / topic).is_dir():
            problems.append(f"declared folder missing (run build-index.py): {topic}")

    ids, titles = {}, {}
    for md in papers:
        topic = md.parent.relative_to(LIBRARY_DIR).as_posix()
        if topic not in topics:
            problems.append(f"{md.relative_to(LIBRARY_DIR)}: folder `{topic}` is not in catalog/topics.yaml")
        meta = read_paper(md)[0]
        if meta.get("arxiv"):
            ids[str(meta["arxiv"])] = md
        titles[norm_title(meta.get("title"))] = md

    for i, entry in enumerate(load_skipped()):
        name = f"catalog/skipped.yaml entry {i + 1}"
        if not isinstance(entry, dict) or not entry.get("title") or not entry.get("reason"):
            problems.append(f"{name}: needs a title and a reason")
            continue
        if entry.get("topic") and entry["topic"] not in topics:
            problems.append(f"{name} ({entry['title']}): undeclared topic `{entry['topic']}`")
        md = ids.get(str(entry.get("arxiv"))) or titles.get(norm_title(entry["title"]))
        if md:
            problems.append(f"{name} ({entry['title']}): skipped but in the library at "
                            f"{md.relative_to(LIBRARY_DIR)}")
    return problems


def main():
    problems = []
    papers = paper_files()

    for md in papers:
        rel = md.relative_to(LIBRARY_DIR)
        meta, body = read_paper(md)
        if not meta:
            problems.append(f"{rel}: no frontmatter")
        else:
            for field in REQUIRED:
                if not meta.get(field):
                    problems.append(f"{rel}: missing or empty `{field}`")
            if meta.get("source") and meta["source"] not in SOURCES:
                problems.append(f"{rel}: unknown source `{meta['source']}`")
            if meta.get("type") and meta["type"] not in TYPES:
                problems.append(f"{rel}: unknown type `{meta['type']}`")
        if not pdf_path_for(md).exists():
            problems.append(f"{rel}: no PDF at {pdf_path_for(md)}")
        for groups in IMAGE_LINK.findall(body):
            target = groups[0] or groups[1]
            if re.match(r"^[a-z]+:", target):
                continue
            if not (md.parent / unquote(target)).exists():
                problems.append(f"{rel}: broken image link {target}")

    referenced = set()
    for md in papers:
        for groups in IMAGE_LINK.findall(read_paper(md)[1]):
            target = groups[0] or groups[1]
            if not re.match(r"^[a-z]+:", target):
                referenced.add((md.parent / unquote(target)).resolve())
    for img in LIBRARY_DIR.rglob("images/*"):
        if img.resolve() not in referenced:
            problems.append(f"image not used by any paper: {img.relative_to(LIBRARY_DIR)}")

    expected = {pdf_path_for(md) for md in papers}
    if PDF_ROOT.exists():
        for pdf in PDF_ROOT.rglob("*.pdf"):
            if pdf not in expected:
                problems.append(f"PDF without a paper: {pdf.relative_to(PDF_ROOT)}")

    problems += check_catalog(papers)

    stems = {md.stem for md in papers}
    for note in sorted(NOTES_DIR.glob("*.md")):
        if note.name != "README.md" and note.stem not in stems:
            problems.append(f"notes/{note.name}: no paper with this name in the library")

    for pdf in REPO_ROOT.rglob("*.pdf"):
        if ".git" not in pdf.parts:
            problems.append(f"PDF inside the repository: {pdf.relative_to(REPO_ROOT)}")

    for p in problems:
        print(p)
    print(f"check-library: {len(papers)} papers, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
