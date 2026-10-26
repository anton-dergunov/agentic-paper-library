#!/usr/bin/env python3
"""Rename papers whose filename no longer matches their title.

    ./scripts/rename-papers.py [--dry-run] [<paper.txt> ...]

For every paper (or the ones given), the expected filename stem is
title_to_filename(<frontmatter title>). When it differs, the paper's file, the PDF
under PDF_ROOT and the notes/ memory file move to the new stem together. Run after
the filename rule changes; rebuild the indexes afterwards. The reader's own notes
(overview_dir in the config) are not touched: the ones that exist are listed at the
end.
"""

import sys
from pathlib import Path

from paperlib import (
    LIBRARY_DIR, NOTES_DIR, OVERVIEW_DIR, paper_index, paper_stem, pdf_path_for, read_paper, title_to_filename,
)


def rename(paper, stem, dry_run):
    old = paper_stem(paper)
    new_paper = paper.with_name(stem + paper.suffix)
    # On a case-insensitive disk a rename that only changes case "exists" already.
    for a, b in ((paper, new_paper), (pdf_path_for(paper), pdf_path_for(new_paper))):
        if b.exists() and not (a.exists() and a.samefile(b)):
            return f"skip (target exists): {paper.relative_to(LIBRARY_DIR)}"
    if dry_run:
        return f"{old}  ->  {stem}"
    pdf = pdf_path_for(paper)
    paper.rename(new_paper)  # a rename, not write-then-delete: safe when only the case changes
    if pdf.exists():
        pdf.rename(pdf_path_for(new_paper))
    note = NOTES_DIR / f"{old}.md"
    if note.exists():
        note.rename(NOTES_DIR / f"{stem}.md")
    return f"{old}  ->  {stem}"


def main(argv):
    dry_run = "--dry-run" in argv
    paths = [Path(a).resolve() for a in argv if a != "--dry-run"]
    titles = {p: read_paper(p)[0].get("title") for p in paths} if paths else \
        {p: meta.get("title") for p, meta in paper_index().items()}
    renamed, vault = 0, []
    for paper, title in titles.items():
        stem = title_to_filename(title) if title else paper_stem(paper)
        if stem == paper_stem(paper):
            continue
        print(rename(paper, stem, dry_run))
        renamed += 1
        if OVERVIEW_DIR and (OVERVIEW_DIR / f"{paper_stem(paper)}.md").exists():
            vault.append((paper_stem(paper), stem))
    print(f"rename-papers: {renamed} papers {'would be ' if dry_run else ''}renamed")
    for old, new in vault:
        print(f"  overview note to rename by hand: {OVERVIEW_DIR / old}.md -> {new}.md")


if __name__ == "__main__":
    main(sys.argv[1:])
