#!/usr/bin/env python3
"""The conversion problems known in the library: list them, add one, close them.

    paperlib issues [<scope or paper.md> ...] [--kind K] [--key-content] [--new] [--all | --wont-fix] [--counts]
    paperlib issues add <paper.md or stem> <kind | new:<slug>> "<what>" --where "p. N, Table M" [--key-content]
    paperlib issues close <kind> (--state <reconvert.jsonl> | <paper.md or stem> ...)

Each paper with a known problem has issues/<stem>.yaml: a list of records, one problem
each, whose `kind` is the id of a ticket in the engine's tickets/ (one ticket per cause),
or `new` with `suggested: <slug>` until the triage-conversions skill gives it one.
`paperlib read` writes the reader's records; `add` records one a session found, unless the
paper already has one of that kind at that place (a wont-fix one included).

The listing prints the open records in the scope (the whole library when none is named),
one line each, those with key content broken first; `--all` adds the wont-fix ones (a record
marked `wont-fix: <reason>`, or one filed under a ticket whose status is wont-fix),
`--wont-fix` shows only those, with their reasons, `--kind` and `--new` narrow it, and
`--counts` prints papers and records per ticket instead.

`close` deletes the records of one kind once the converter fix has reached the papers:
those that `paperlib reconvert --state <file>` reconverted `ok`, or the papers named. It
marks the notes of the papers whose closed records broke key content to be read again
(`reread:`, which `paperlib reading` counts), since they may rest on the broken part, and
prints the command that reads them.
"""

import datetime
import json
import os
import sys
from collections import Counter
from pathlib import Path

from paperlib import (
    LIBRARY_DIR, all_issues, describe_issue as describe, flag_reread, is_open, load_issues, load_tickets, paper_files,
    paper_stem, save_issues,
)


def scope_stems(targets):
    """{stem: relative path} of the papers in the scope (the whole library when none)."""
    papers = []
    for target in targets or [""]:
        path = Path(target)
        if target and path.is_file():
            papers.append(path.resolve())
        elif (LIBRARY_DIR / target.strip("/")).is_dir():
            papers += [p.resolve() for p in paper_files(LIBRARY_DIR / target.strip("/"))]
        else:
            matches = [p for p in paper_files() if p.stem == target]
            if not matches:
                sys.exit(f"issues: `{target}` is neither a paper nor a folder of the library")
            papers += [p.resolve() for p in matches]
    return {p.stem: p.relative_to(LIBRARY_DIR.resolve()) for p in papers}


def option(argv, name):
    if name not in argv:
        return None
    i = argv.index(name)
    if i + 1 >= len(argv):
        sys.exit(f"issues: {name} needs a value")
    value = argv[i + 1]
    del argv[i:i + 2]
    return value


def list_issues(argv):
    kind = option(argv, "--kind")
    flags = {a for a in argv if a.startswith("--")}
    unknown = flags - {"--key-content", "--new", "--all", "--wont-fix", "--counts"}
    if unknown:
        sys.exit(__doc__)
    stems = scope_stems([a for a in argv if not a.startswith("--")])
    found = all_issues(stems)
    rows = []
    for stem, records in found.items():
        for r in records:
            wanted = (not is_open(r)) if "--wont-fix" in flags else ("--all" in flags or is_open(r))
            if wanted and (not kind or r.get("kind") == kind) \
                    and ("--key-content" not in flags or r.get("key-content")) \
                    and ("--new" not in flags or r.get("kind") == "new"):
                rows.append((stem, r))
    if "--counts" in flags:
        tickets = load_tickets()
        papers, records, key = Counter(), Counter(), Counter()
        for stem, r in rows:
            records[r.get("kind")] += 1
            key[r.get("kind")] += bool(r.get("key-content"))
        for k in records:
            papers[k] = len({s for s, r in rows if r.get("kind") == k})
        print(f"{'kind':32} {'papers':>6} {'records':>7} {'key':>4}  status")
        for k, _ in papers.most_common():
            status = tickets[k].get("status", "?") if k in tickets else ("untriaged" if k == "new" else "NO TICKET")
            print(f"{str(k):32} {papers[k]:6} {records[k]:7} {key[k]:4}  {status}")
        print(f"{len(rows)} records in {len({s for s, _ in rows})} papers")
        return
    rows.sort(key=lambda sr: (not sr[1].get("key-content"), str(stems[sr[0]])))
    for stem, r in rows:
        print(f"{stems[stem]}: {describe(r)}")
    shown = "" if flags & {"--all", "--wont-fix"} else ", wont-fix not shown"
    print(f"issues: {len(rows)} records in {len({s for s, _ in rows})} papers{shown}")


def add_issue(argv):
    where = option(argv, "--where")
    key = "--key-content" in argv
    args = [a for a in argv if a != "--key-content"]
    if len(args) != 3 or not where:
        sys.exit(__doc__)
    paper, kind, what = args
    stem = paper_stem(paper)
    if not any(p.stem == stem for p in paper_files()):
        sys.exit(f"issues: no paper `{stem}` in the library")
    record = {"kind": kind, "where": where, "what": what, "key-content": key, "by": "session",
              "found": datetime.date.today().isoformat()}
    if kind.startswith("new:"):
        record.update(kind="new", suggested=kind[4:])
    elif kind != "new" and kind not in load_tickets():
        sys.exit(f"issues: no ticket `{kind}`; use new:<slug> for a cause without one")
    norm = lambda r: (r.get("kind"), " ".join(str(r.get("where", "")).lower().split()))
    same = [r for r in load_issues(stem) if norm(r) == norm(record)]
    if same:
        print(f"issues: already recorded in {stem}: {describe(same[0])}")
        return
    save_issues(stem, load_issues(stem) + [record])
    print(f"issues: added to {stem}: {describe(record)}")


def close_issues(argv):
    state = option(argv, "--state")
    if not argv or (not state and len(argv) < 2):
        sys.exit(__doc__)
    kind, papers = argv[0], argv[1:]
    stems = {paper_stem(p) for p in papers}
    if state:
        for line in Path(state).read_text(encoding="utf-8").splitlines():
            entry = json.loads(line) if line.strip() else {}
            if entry.get("status") == "ok":
                stems.add(paper_stem(entry["paper"]))
    closed, reread = 0, []
    for stem in sorted(stems):
        records = load_issues(stem)
        kept = [r for r in records if r.get("kind") != kind]
        if len(kept) < len(records):
            closed += len(records) - len(kept)
            broken = [r for r in records if r.get("kind") == kind and r.get("key-content") and is_open(r)]
            if broken:
                reread.append(stem)
                flag_reread(stem, f"{kind} fixed, which broke key content ({broken[0].get('where', '?')})")
            save_issues(stem, kept)
    left = sum(1 for records in all_issues().values() for r in records if r.get("kind") == kind)
    print(f"issues: closed {closed} `{kind}` records; {left} still open in other papers")
    if reread:
        paths = {p.stem: p for p in paper_files()}
        print("Their key content was broken; their notes are marked to be read again:")
        print("  paperlib read --redo " + " ".join(f'"{os.path.relpath(paths[s])}"' for s in reread if s in paths))


def main(argv):
    if argv[:1] == ["add"]:
        add_issue(argv[1:])
    elif argv[:1] == ["close"]:
        close_issues(argv[1:])
    elif any(a in ("-h", "--help") for a in argv):
        print(__doc__)
    else:
        list_issues(list(argv))


if __name__ == "__main__":
    main(sys.argv[1:])
