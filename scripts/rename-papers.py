#!/usr/bin/env python3
"""Rename papers whose filename no longer matches their title.

    ./scripts/rename-papers.py [--dry-run] [<paper.md> ...]

For every paper (or the ones given), the expected filename stem is
title_to_filename(<frontmatter title>). When it differs, the markdown, its
figures in images/, the PDF under PDF_ROOT and the notes/ memory file move to
the new stem together, and the figure links inside the markdown are updated.
Run after the filename rule changes; rebuild the indexes afterwards. The
reader's own notes (overview_dir in the config) are not touched: the ones that
exist are listed at the end.
"""

import sys
from pathlib import Path
from urllib.parse import quote

from paperlib import (
    LIBRARY_DIR, NOTES_DIR, OVERVIEW_DIR, paper_files, pdf_path_for, read_paper, title_to_filename,
)


def rename(md, stem, dry_run):
    old = md.stem
    new_md = md.with_name(f"{stem}.md")
    # On a case-insensitive disk a rename that only changes case "exists" already.
    for a, b in ((md, new_md), (pdf_path_for(md), pdf_path_for(new_md))):
        if b.exists() and not (a.exists() and a.samefile(b)):
            return f"skip (target exists): {md.relative_to(LIBRARY_DIR)}"
    if dry_run:
        return f"{old}  ->  {stem}"
    text = md.read_text(encoding="utf-8")
    images = md.parent / "images"
    for img in sorted(images.glob(f"{old}-fig*")) if images.exists() else []:
        suffix = img.name[len(old):]
        new_img = images / f"{stem}{suffix}"
        img.rename(new_img)
        text = text.replace(f"images/{quote(img.name)}", f"images/{quote(new_img.name)}")
    md.write_text(text, encoding="utf-8")
    md.rename(new_md)  # a rename, not write-then-delete: safe when only the case changes
    pdf = pdf_path_for(md)
    if pdf.exists():
        pdf.rename(pdf_path_for(new_md))
    note = NOTES_DIR / f"{old}.md"
    if note.exists():
        note.rename(NOTES_DIR / f"{stem}.md")
    return f"{old}  ->  {stem}"


def main(argv):
    dry_run = "--dry-run" in argv
    paths = [Path(a).resolve() for a in argv if a != "--dry-run"]
    renamed, vault = 0, []
    for md in paths or paper_files():
        title = read_paper(md)[0].get("title")
        stem = title_to_filename(title) if title else md.stem
        if stem == md.stem:
            continue
        print(rename(md, stem, dry_run))
        renamed += 1
        if OVERVIEW_DIR and (OVERVIEW_DIR / f"{md.stem}.md").exists():
            vault.append((md.stem, stem))
    print(f"rename-papers: {renamed} papers {'would be ' if dry_run else ''}renamed")
    for old, new in vault:
        print(f"  overview note to rename by hand: {OVERVIEW_DIR / old}.md -> {new}.md")


if __name__ == "__main__":
    main(sys.argv[1:])
