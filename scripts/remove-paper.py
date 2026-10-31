#!/usr/bin/env python3
"""Take a paper out of the library: its text, PDF and note.

    ./scripts/remove-paper.py <paper.txt | arxiv-id-or-url | title words> ... [--reason "..."] [--yes]

It first lists what it will delete: the paper's file (its text layer, or a web article's
markdown), the PDF and notes/<Title>.md. It also lists
what it leaves for a person to decide: the reader's own overview note, the reviews that
link the paper and the other notes that name it. On a terminal it then asks; anywhere else
it deletes only with --yes.

    --reason "..."  also record the paper in catalog/skipped.yaml with this reason, so it
                    is not proposed or added again. Leave it out for a duplicate or a mistake.
    --yes           delete without asking

Title words must match one paper. Afterwards it regenerates the indexes and runs the
check, which fails while a review still links the paper.
"""

import datetime
import subprocess
import sys

from paperlib import (
    LIBRARY_DIR, LIBRARY_ROOT, NOTES_DIR, OVERVIEW_DIR, SCRIPTS_DIR, append_skipped,
    load_reviews, note_path, paper_index, paper_stem, papers_named,
    pdf_path_for, read_paper, review_links,
)


def relative(path):
    return str(path.relative_to(LIBRARY_ROOT)) if path.is_relative_to(LIBRARY_ROOT) else str(path)


def resolve(arg, index):
    try:
        return papers_named(arg, index)
    except ValueError as error:
        sys.exit(f"error: {error}")


def changed_since_added(pdf, meta):
    """Whether the PDF was written after the day the paper was added (highlights, perhaps)."""
    try:
        added = datetime.date.fromisoformat(str(meta.get("added")))
    except ValueError:
        return False
    return datetime.date.fromtimestamp(pdf.stat().st_mtime) > added


def plan(paper, reviews):
    """What removing `paper` deletes and what it leaves, from the library as it is."""
    meta = read_paper(paper)[0]
    stem = paper_stem(paper)
    pdf, note = pdf_path_for(paper), note_path(paper)
    overview = OVERVIEW_DIR / f"{stem}.md" if OVERVIEW_DIR else None
    linking = [scope for scope, review in reviews.items()
               if any(resolved.resolve() == paper.resolve() for f in review["files"] for _, resolved, _ in review_links(f))]
    naming = [n.stem for n in sorted(NOTES_DIR.glob("*.md"))
              if n != note and stem in n.read_text(encoding="utf-8")]
    return {
        "paper": paper, "meta": meta,
        "pdf": pdf if pdf.is_file() else None,
        "note": note if note.is_file() else None,
        "overview": overview if overview and overview.is_file() else None,
        "reviews": {scope: reviews[scope]["main"] for scope in linking},
        "naming": naming,
    }


def show(p, reason):
    print(relative(p["paper"]))
    print("  delete  " + ("the markdown" if p["paper"].suffix == ".md" else "the text layer"))
    if p["pdf"]:
        changed = " (changed since it was added: it may hold highlights)" \
            if changed_since_added(p["pdf"], p["meta"]) else ""
        print(f"  delete  the PDF: {p['pdf']}{changed}")
    if p["note"]:
        print(f"  delete  the note: {relative(p['note'])}")
    if reason:
        print(f"  record  in catalog/skipped.yaml: {reason}")
    if p["overview"]:
        print(f"  left    the overview note: {p['overview']}")
    for scope, main in p["reviews"].items():
        print(f"  left    {relative(main)} links it: /literature-review update {scope}")
    if p["naming"]:
        print(f"  left    notes that name it: {'; '.join(p['naming'])}")


def skip_entry(p, reason):
    meta = p["meta"]
    year = str(meta.get("published") or "")[:4]
    entry = dict(title=meta.get("title") or paper_stem(p["paper"]), arxiv=str(meta.get("arxiv") or "") or None,
                 url=None if meta.get("arxiv") else meta.get("url"), year=int(year) if year.isdigit() else None,
                 topic=str(p["paper"].parent.relative_to(LIBRARY_DIR)), reason=reason, date=datetime.date.today())
    return {k: v for k, v in entry.items() if v is not None}


def remove(p):
    for path in [p["paper"], p["pdf"], p["note"]]:
        if path:
            path.unlink()


def main(argv):
    yes = "--yes" in argv
    argv = [a for a in argv if a != "--yes"]
    reason = None
    if "--reason" in argv:
        at = argv.index("--reason")
        reason = " ".join(" ".join(argv[at + 1:at + 2]).split())
        if not reason:
            sys.exit("error: --reason needs the reason")
        del argv[at:at + 2]
    if not argv or any(a.startswith("-") for a in argv):
        sys.exit(__doc__)

    index, papers = paper_index(), []
    for arg in argv:
        found = resolve(arg, index)
        if len(found) != 1:
            print(f"{arg}: " + ("no paper in the library" if not found else "several papers, name one:"),
                  file=sys.stderr)
            for path in found:
                print(f"  {relative(path)}", file=sys.stderr)
            sys.exit(1)
        papers += [path for path in found if path not in papers]

    reviews = load_reviews()
    plans = [plan(paper, reviews) for paper in papers]
    for p in plans:
        show(p, reason)
    if not yes:
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            print("nothing removed; pass --yes to remove")
            return 0
        count = "this paper" if len(plans) == 1 else f"these {len(plans)} papers"
        if input(f"Remove {count}? [y/N] ").strip().lower() not in ("y", "yes"):
            print("nothing removed")
            return 0

    if reason:
        append_skipped([skip_entry(p, reason) for p in plans])
    for p in plans:
        remove(p)
    print(f"removed: {len(plans)}", flush=True)
    code = subprocess.run([sys.executable, str(SCRIPTS_DIR / "build-index.py")]).returncode
    return code or subprocess.run([sys.executable, str(SCRIPTS_DIR / "check-library.py")]).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
