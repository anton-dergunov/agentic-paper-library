#!/usr/bin/env python3
"""Collect the conversion problems the reader found into catalog/conversion-issues.yaml.

    ./scripts/conversion-issues.py [<scope or paper.md> ...] [--dry-run] [--model ID]

Each note's `conversion:` line grades its paper's markdown: `ok`, `minor: <what>` (the
meaning is still recoverable) or `damaged: <what>` (something a note or a review needs is
missing or unreliable; guide/conversion-grades.md has the rules). Every damaged paper in
the scope (the whole library when none is named) that the catalog does not list yet is
added to it, with the reader's description as the problem.

Notes written before the reader graded problems have only the description. Those are
graded in one model request over all their conversion lines (not the papers), and the
grade is written into the note, so it is asked once.

Prints the damaged papers added, those already listed, and every catalog entry in the
scope: the list a fix pass works through. --dry-run prints the same and changes nothing.
"""

import datetime
import json
import re
import sys
from pathlib import Path

from paperlib import (
    CONFIG, CONVERSION_ISSUES_FILE, ENGINE_ROOT, LIBRARY_DIR, LIBRARY_ROOT, append_conversion_issues,
    ask_model, load_conversion_issues, note_conversion, note_path, paper_files,
)

BATCH = 60  # conversion lines per grading request

PROMPT = """Each numbered line below is a reader's description of what is broken in the markdown conversion of one research paper. Grade each one:

{grades}

Reply with one JSON object and nothing else, mapping each line's number to "minor" or "damaged", as in {{"1": "minor", "2": "damaged"}}.

{lines}
"""


def grade_unclassified(items, model):
    """{paper: grade} for (paper, description) pairs, by one request per BATCH lines."""
    grades_text = (ENGINE_ROOT / "guide" / "conversion-grades.md").read_text(encoding="utf-8").strip()
    graded = {}
    for start in range(0, len(items), BATCH):
        batch = items[start:start + BATCH]
        lines = "\n".join(f"{i}. {desc}" for i, (_, desc) in enumerate(batch, start=1))
        reply, _ = ask_model(model, "You grade conversion problems in research papers.",
                             PROMPT.format(grades=grades_text, lines=lines))
        answer = json.loads(reply[reply.index("{"):reply.rindex("}") + 1])
        for i, (paper, _) in enumerate(batch, start=1):
            grade = str(answer.get(str(i), "")).lower()
            if grade in ("minor", "damaged"):
                graded[paper] = grade
    return graded


def set_grade(paper, grade, description):
    note = note_path(paper)
    text = note.read_text(encoding="utf-8")
    line = f"conversion: {grade}: {description}"
    note.write_text(re.sub(r"^conversion:.*$", lambda _: line, text, count=1, flags=re.M), encoding="utf-8")


def main(argv):
    dry_run = "--dry-run" in argv
    model = CONFIG.get("reader_model") or "opus"
    targets, args = [], [a for a in argv if a != "--dry-run"]
    while args:
        arg = args.pop(0)
        if arg == "--model" and args:
            model = args.pop(0)
        elif arg.startswith("-"):
            sys.exit(__doc__)
        else:
            targets.append(arg)
    papers = []
    for target in targets or [""]:
        path = Path(target)
        if target and path.is_file():
            papers.append(path.resolve())
        elif (LIBRARY_DIR / target.strip("/")).is_dir():
            papers += [p.resolve() for p in paper_files(LIBRARY_DIR / target.strip("/"))]
        else:
            sys.exit(f"conversion-issues: `{target}` is neither a paper nor a folder of the library")

    grades, unclassified = {}, []
    for paper in papers:
        note = note_path(paper)
        if not note.exists() or "## Digest" not in note.read_text(encoding="utf-8"):
            continue
        grade, description = note_conversion(note.read_text(encoding="utf-8"))
        if grade == "unclassified":
            unclassified.append((paper, description))
        elif grade:
            grades[paper] = (grade, description)
    if unclassified:
        print(f"conversion-issues: grading {len(unclassified)} notes written before grades, with {model}")
        if not dry_run:
            for paper, grade in grade_unclassified(unclassified, model).items():
                description = dict(unclassified)[paper]
                set_grade(paper, grade, description)
                grades[paper] = (grade, description)

    listed = {e.get("paper") for e in load_conversion_issues() if isinstance(e, dict)}
    today = datetime.date.today().isoformat()
    new = [{"paper": p.stem, "problem": desc, "found": today}
           for p, (grade, desc) in sorted(grades.items()) if grade == "damaged" and p.stem not in listed]
    counts = {g: sum(1 for grade, _ in grades.values() if grade == g) for g in ("ok", "minor", "damaged")}
    print(f"conversion-issues: {len(grades)} graded notes: {counts['ok']} ok, {counts['minor']} minor, "
          f"{counts['damaged']} damaged" + (f"; {len(unclassified)} ungraded (dry run)" if dry_run and unclassified else ""))
    for entry in new:
        print(f"  {'would add' if dry_run else 'added'}: {entry['paper']}")
    if new and not dry_run:
        append_conversion_issues(new)

    stems = {p.stem: p for p in papers}
    in_scope = [e for e in load_conversion_issues() if isinstance(e, dict) and e.get("paper") in stems]
    print(f"conversion-issues: {len(in_scope)} entries in {CONVERSION_ISSUES_FILE.relative_to(LIBRARY_ROOT)} "
          "for this scope")
    for e in in_scope:
        print(f"  {stems[e['paper']].relative_to(LIBRARY_DIR)}: {' '.join(str(e.get('problem', '')).split())}")


if __name__ == "__main__":
    main(sys.argv[1:])
