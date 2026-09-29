#!/usr/bin/env python3
"""Check that the library is consistent. Exits non-zero on any problem.

    ./scripts/check-library.py

Checks:

- every paper has the required frontmatter fields, with a known `source`;
- every paper has its PDF at the mirrored path under PDF_ROOT, and every PDF
  there has a paper (README files aside);
- every relative image link in a paper resolves, and every image is used;
- no PDF is inside the repository.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

from paperlib import LIBRARY_DIR, PDF_ROOT, REPO_ROOT, REQUIRED, SOURCES, paper_files, pdf_path_for, read_paper

# Markdown images, and <img> tags (used inside the HTML tables of complex tables).
IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)|<img\s[^>]*?src=\"([^\"]+)\"")


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

    for pdf in REPO_ROOT.rglob("*.pdf"):
        if ".git" not in pdf.parts:
            problems.append(f"PDF inside the repository: {pdf.relative_to(REPO_ROOT)}")

    for p in problems:
        print(p)
    print(f"check-library: {len(papers)} papers, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
