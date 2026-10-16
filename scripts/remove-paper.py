#!/usr/bin/env python3
"""Take a paper out of the library: its markdown, figures, PDF and note.

    ./scripts/remove-paper.py <paper.md | arxiv-id-or-url | title words> ... [--reason "..."] [--yes]

It first lists what it will delete: the markdown, its images/<Title>-fig* files, the PDF,
notes/<Title>.md and its conversion problems, issues/<Title>.yaml. It also lists
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
import glob
import re
import subprocess
import sys
from pathlib import Path

from paperlib import (
    LIBRARY_DIR, LIBRARY_ROOT, NOTES_DIR, OVERVIEW_DIR, SCRIPTS_DIR, append_skipped,
    find_by_title, issues_path, library_arxiv_ids, load_issues, load_reviews, note_path, paper_index,
    pdf_path_for, read_paper, review_links,
)

ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")


def relative(path):
    return str(path.relative_to(LIBRARY_ROOT)) if path.is_relative_to(LIBRARY_ROOT) else str(path)


def resolve(arg, index):
    """The library papers `arg` names: a markdown file, an arXiv id or title words."""
    path = Path(arg).expanduser()
    if path.suffix == ".md" and path.is_file():
        path = path.resolve()
        if not path.is_relative_to(LIBRARY_DIR.resolve()) or path.name == "README.md":
            sys.exit(f"error: {arg} is not a paper under {LIBRARY_DIR}")
        return [LIBRARY_DIR / path.relative_to(LIBRARY_DIR.resolve())]
    found = ARXIV_ID.search(arg)
    if found:
        path = library_arxiv_ids().get(found.group(1))
        return [path] if path else []
    return find_by_title(arg, {path: meta.get("title") for path, meta in index.items()})


def changed_since_added(pdf, meta):
    """Whether the PDF was written after the day the paper was added (highlights, perhaps)."""
    try:
        added = datetime.date.fromisoformat(str(meta.get("added")))
    except ValueError:
        return False
    return datetime.date.fromtimestamp(pdf.stat().st_mtime) > added


def plan(md, reviews):
    """What removing `md` deletes and what it leaves, from the library as it is."""
    meta = read_paper(md)[0]
    stem = md.stem
    pdf, note = pdf_path_for(md), note_path(md)
    overview = OVERVIEW_DIR / f"{stem}.md" if OVERVIEW_DIR else None
    linking = [scope for scope, review in reviews.items()
               if any(resolved.resolve() == md.resolve() for f in review["files"] for _, resolved, _ in review_links(f))]
    naming = [n.stem for n in sorted(NOTES_DIR.glob("*.md"))
              if n != note and stem in n.read_text(encoding="utf-8")]
    return {
        "md": md, "meta": meta,
        # "-fig" and a number: another paper's title may begin with this one's.
        "figures": sorted(f for f in (md.parent / "images").glob(glob.escape(stem) + "-fig*")
                          if re.fullmatch(r"-fig\d+\.\w+", f.name[len(stem):])),
        "pdf": pdf if pdf.is_file() else None,
        "note": note if note.is_file() else None,
        "issues": issues_path(stem) if load_issues(stem) else None,
        "overview": overview if overview and overview.is_file() else None,
        "reviews": {scope: reviews[scope]["main"] for scope in linking},
        "naming": naming,
    }


def show(p, reason):
    figures = f", {len(p['figures'])} figure{'s' * (len(p['figures']) != 1)}" if p["figures"] else ""
    print(relative(p["md"]))
    print(f"  delete  the markdown{figures}")
    if p["pdf"]:
        changed = " (changed since it was added: it may hold highlights)" \
            if changed_since_added(p["pdf"], p["meta"]) else ""
        print(f"  delete  the PDF: {p['pdf']}{changed}")
    if p["note"]:
        print(f"  delete  the note: {relative(p['note'])}")
    if p["issues"]:
        print(f"  delete  its conversion problems: {relative(p['issues'])}")
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
    entry = dict(title=meta.get("title") or p["md"].stem, arxiv=str(meta.get("arxiv") or "") or None,
                 url=None if meta.get("arxiv") else meta.get("url"), year=int(year) if year.isdigit() else None,
                 topic=str(p["md"].parent.relative_to(LIBRARY_DIR)), reason=reason, date=datetime.date.today())
    return {k: v for k, v in entry.items() if v is not None}


def remove(p):
    for path in [p["md"], *p["figures"], p["pdf"], p["note"], p["issues"]]:
        if path:
            path.unlink()
    images = p["md"].parent / "images"
    if images.is_dir() and not any(images.iterdir()):
        images.rmdir()


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
    plans = [plan(md, reviews) for md in papers]
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
