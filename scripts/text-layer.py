#!/usr/bin/env python3
"""Make papers' text layers again from their PDFs, keeping the frontmatter.

    ./scripts/text-layer.py <paper.txt | scope> ... [--dry-run]

For every paper named, or under a scope (a folder of the library), the text after the
frontmatter is replaced by the PDF's text layer as `paperlib add` writes it (pdftotext
-layout, a "[page N]" line where each page starts). A paper is written only when its text
changed: after its PDF was replaced (a new arXiv version), or after poppler was upgraded,
which changes the text of papers already in the library (run it on a few papers first and
look at the diff). `text-layer: broken` is set when the new text looks unreadable;
a mark is never taken off by a program, only by hand. Web
articles (.md) are left alone: `paperlib add-web <url> <topic> --force` converts one again.

    --dry-run   list the papers whose text would change, and write nothing
"""

import sys
from pathlib import Path

from paperlib import LIBRARY_DIR, paper_files, pdf_path_for, read_paper, text_layer, write_text_paper


def main(argv):
    dry_run = "--dry-run" in argv
    targets = [a for a in argv if a != "--dry-run"]
    if not targets or any(t.startswith("-") for t in targets):
        sys.exit(__doc__)
    papers = []
    for target in targets:
        path = Path(target)
        if path.is_file() and path.suffix == ".txt":
            papers.append(path.resolve())
        elif (LIBRARY_DIR / target.strip("/")).is_dir():
            papers += [p for p in paper_files(LIBRARY_DIR / target.strip("/")) if p.suffix == ".txt"]
        else:
            sys.exit(f"text: `{target}` is neither a text-layer paper nor a folder of the library")
    changed = missing = 0
    for paper in papers:
        pdf = pdf_path_for(paper)
        if not pdf.exists():
            print(f"  no PDF: {paper.relative_to(LIBRARY_DIR)}")
            missing += 1
            continue
        meta, body = read_paper(paper)
        try:
            if text_layer(pdf) == body:
                continue
            if not dry_run:
                write_text_paper(paper, meta, pdf)
        except RuntimeError as error:
            sys.exit(f"text: {error}")
        changed += 1
        print(f"  {'would change' if dry_run else 'changed'}: {paper.relative_to(LIBRARY_DIR)}")
    print(f"text: {len(papers)} papers, {changed} {'would change' if dry_run else 'changed'}"
          + (f", {missing} without a PDF" if missing else ""))
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
