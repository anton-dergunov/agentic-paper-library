#!/usr/bin/env python3
"""Collect the conversion problems the reader found into catalog/conversion-issues.yaml.

    ./scripts/conversion-issues.py [<scope or paper.md> ...] [--dry-run]

When `paperlib read` writes a note, its `conversion:` line says what is broken in the
paper's markdown: `ok`, a description, or `key-content-broken: <description>` when a part
the paper's findings rest on is missing or wrong (a results table, the main equation, a
section). Every paper in the scope (the whole library when none is named) whose note reports a
problem, and that the catalog does not list yet, is added to it with the reader's
description, and with `key-content-broken: true` when the note says so.

The catalog is the one list of known conversion problems. An entry has two optional flags:

    key-content-broken: true  the note may be wrong too: fix the paper, then read it again
    wont-fix: <reason>        set by the fix-conversions skill: cannot be fixed, or not
                              worth it

Prints the papers added, then the open entries in the scope (those with key content
broken first) and the number marked wont-fix: the list a fix pass works through. --dry-run
changes nothing.
"""

import datetime
import sys
from pathlib import Path

from paperlib import (
    CONVERSION_ISSUES_FILE, LIBRARY_DIR, LIBRARY_ROOT, append_conversion_issues,
    load_conversion_issues, note_conversion, note_path, paper_files,
)


def scope_papers(targets):
    papers = []
    for target in targets or [""]:
        path = Path(target)
        if target and path.is_file():
            papers.append(path.resolve())
        elif (LIBRARY_DIR / target.strip("/")).is_dir():
            papers += [p.resolve() for p in paper_files(LIBRARY_DIR / target.strip("/"))]
        else:
            sys.exit(f"conversion-issues: `{target}` is neither a paper nor a folder of the library")
    return papers


def main(argv):
    dry_run = "--dry-run" in argv
    targets = [a for a in argv if a != "--dry-run"]
    if any(a.startswith("-") for a in targets):
        sys.exit(__doc__)
    papers = scope_papers(targets)

    listed = {e.get("paper") for e in load_conversion_issues() if isinstance(e, dict)}
    today = datetime.date.today().isoformat()
    new = []
    for paper in papers:
        note = note_path(paper)
        if paper.stem in listed or not note.exists():
            continue
        state, description = note_conversion(note.read_text(encoding="utf-8"))
        if state in ("problem", "key-content-broken"):
            new.append({"paper": paper.stem, "problem": description, "found": today,
                        **({"key-content-broken": True} if state == "key-content-broken" else {})})
    for entry in new:
        print(f"  {'would add' if dry_run else 'added'}: {entry['paper']}"
              + (" (key content broken)" if entry.get("key-content-broken") else ""))
    if new and not dry_run:
        append_conversion_issues(new)

    stems = {p.stem: p for p in papers}
    entries = [e for e in load_conversion_issues() if isinstance(e, dict) and e.get("paper") in stems]
    open_entries = sorted((e for e in entries if not e.get("wont-fix")),
                          key=lambda e: not e.get("key-content-broken"))
    broken = sum(1 for e in open_entries if e.get("key-content-broken"))
    print(f"conversion-issues: {len(new)} {'to add' if dry_run else 'added'}; in "
          f"{CONVERSION_ISSUES_FILE.relative_to(LIBRARY_ROOT)} for this scope: {len(open_entries)} open "
          f"({broken} with key content broken), {len(entries) - len(open_entries)} wont-fix")
    for e in open_entries:
        flag = "KEY CONTENT BROKEN " if e.get("key-content-broken") else ""
        print(f"  {flag}{stems[e['paper']].relative_to(LIBRARY_DIR)}: {' '.join(str(e.get('problem', '')).split())}")


if __name__ == "__main__":
    main(sys.argv[1:])
