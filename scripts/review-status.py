#!/usr/bin/env python3
"""Report on the literature reviews in reviews/, and help write and repair them.

    ./scripts/review-status.py                 every review: coverage and broken links
    ./scripts/review-status.py <scope>         one scope: its review and the papers it
                                               does not cover, and the reading progress
                                               in reviews/.work/<scope>/
    ./scripts/review-status.py --links <scope> every paper in the scope as a markdown
                                               link from reviews/<scope>.md, with its
                                               pdf.invalid base, grouped by folder
    ./scripts/review-status.py --fix-links     repair links to papers that moved

A paper is covered when the review's "## Paper map" section links it. A broken
link whose filename still exists elsewhere in the library (the paper moved, so
its stem is unchanged) is rewritten by --fix-links; a renamed paper is reported
for a manual fix. Reading batches in reviews/.work/<scope>/ hold one
"## <stem>" section per paper read.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit

from paperlib import (
    LIBRARY_DIR, LIBRARY_ROOT, PDF_LINK_BASE, REVIEWS_DIR, load_reviews, load_topics,
    paper_files, read_paper, review_coverage, review_links,
)


def rel(path):
    return Path(path).relative_to(LIBRARY_ROOT).as_posix()


def md_link(paper, from_file):
    return quote(os.path.relpath(paper, Path(from_file).parent))


def pdf_link(paper):
    return PDF_LINK_BASE + quote(
        paper.relative_to(LIBRARY_DIR).with_suffix(".pdf").as_posix(), safe="/&+")


def work_progress(scope):
    """(stems read so far, number of batch files) from reviews/.work/<scope>/."""
    folder = REVIEWS_DIR / ".work" / scope
    batches = sorted(folder.glob("batch-*.md")) if folder.exists() else []
    read = set()
    for batch in batches:
        read |= set(re.findall(r"^## (.+?)\s*$", batch.read_text(encoding="utf-8"), re.M))
    return read, len(batches)


def report(scope, review):
    in_scope, listed = review_coverage(review)
    missing = sorted(in_scope - listed)
    broken = [(f, t) for f in review["files"] for t, _, ok in review_links(f) if not ok]
    print(f"{scope}: {rel(review['main'])}, updated {review['meta'].get('updated', '?')}, "
          f"{len(listed)} of {len(in_scope)} papers covered, {len(broken)} broken links")
    for p in missing:
        print(f"  not covered: {p.relative_to(LIBRARY_DIR)}")
    for f, t in broken:
        print(f"  broken link in {rel(f)}: {t}")
    return bool(missing or broken)


def scope_report(scope):
    topics, reviews = load_topics(), load_reviews()
    if scope not in topics:
        sys.exit(f"error: `{scope}` is not a folder in catalog/topics.yaml")
    papers = paper_files(LIBRARY_DIR / scope)
    in_scope_stems = {p.stem for p in papers}
    if scope in reviews:
        report(scope, reviews[scope])
        # An update reads only the papers the review does not cover yet.
        in_scope, listed = review_coverage(reviews[scope])
        papers = sorted(in_scope - listed)
    read, batches = work_progress(scope)
    if scope not in reviews or batches:
        remaining = [p for p in papers if p.stem not in read]
        to_read = "uncovered papers" if scope in reviews else "papers"
        print(f"{scope}: {len(papers)} {to_read}; reading: {len(papers) - len(remaining)} "
              f"read in {batches} batches, {len(remaining)} remaining")
        for p in remaining:
            print(f"  remaining: {p.relative_to(LIBRARY_DIR)}")
        stale = read - in_scope_stems
        for stem in sorted(stale):
            print(f"  read but no longer in scope: {stem}")


def links(scope):
    target = REVIEWS_DIR / f"{scope}.md"
    by_folder = {}
    for p in paper_files(LIBRARY_DIR / scope):
        by_folder.setdefault(p.parent.relative_to(LIBRARY_DIR).as_posix(), []).append(p)
    for folder, papers in by_folder.items():
        print(f"\n### {folder}\n")
        for p in papers:
            title = " ".join(str(read_paper(p)[0].get("title") or p.stem).split())
            print(f"- [{title}]({md_link(p, target)}) · pdf: {pdf_link(p)}")


def fix_links():
    by_stem = {}
    for p in paper_files():
        by_stem.setdefault(p.stem, []).append(p)
    fixed = unresolved = 0
    for review in load_reviews().values():
        for f in review["files"]:
            text = f.read_text(encoding="utf-8")
            new = text
            for target, resolved, ok in review_links(f):
                if ok:
                    continue
                candidates = by_stem.get(resolved.stem, [])
                if len(candidates) != 1:
                    print(f"cannot fix in {rel(f)}: {target}")
                    unresolved += 1
                    continue
                paper = candidates[0]
                if target.startswith(PDF_LINK_BASE):
                    query = urlsplit(target).query
                    replacement = pdf_link(paper) + (f"?{query}" if query else "")
                else:
                    anchor = "#" + target.split("#", 1)[1] if "#" in target else ""
                    replacement = md_link(paper, f) + anchor
                new = new.replace(f"]({target})", f"]({replacement})")
                new = new.replace(f"]: {target}\n", f"]: {replacement}\n")
                fixed += 1
            if new != text:
                f.write_text(new, encoding="utf-8")
    print(f"review-status: {fixed} links fixed, {unresolved} need a manual fix")
    return unresolved


def main(argv):
    if argv == ["--fix-links"]:
        sys.exit(1 if fix_links() else 0)
    if len(argv) == 2 and argv[0] == "--links":
        links(argv[1].strip("/"))
    elif len(argv) == 1 and not argv[0].startswith("-"):
        scope_report(argv[0].strip("/"))
    elif not argv:
        reviews = load_reviews()
        if not reviews:
            print("review-status: no reviews yet")
        for scope, review in reviews.items():
            report(scope, review)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
