#!/usr/bin/env python3
"""Hand corrections of papers, kept apart from the conversion and applied again by reconvert.

    paperlib corrections [<scope or paper.md> ...] [--stale | --drifted]
    paperlib corrections capture <paper.md> [--why "<why>"] [--where "p. 8, Table 4"] [--base <file>] [--marked]
    paperlib corrections retire <paper.md or stem> "<where>"

A paper corrected by hand (a table rewritten from the PDF, a cropped figure, an equation)
has corrections/<stem>.yaml: one correction per edit, which replaces the converter's text
`was` with `now`, located by that text and by landmarks around it (paperlib.py describes
the format). `paperlib reconvert` converts such a paper afresh and applies its corrections
again: one whose text the converter no longer writes but whose `now` it does is retired,
one it cannot place stays in the file, marked `stale`, and the paper gets a line saying so
under its conversion note. The reapply-corrections skill goes through the stale ones.

The listing prints each correction on a line: paper · where · why, with `stale` or
`drifted` (placed by its landmarks, its text a little changed) where it is.

`capture` records the edits made to a paper since it was last committed: commit the
paper, edit it, run `capture`. Each run of changed lines becomes a correction, and its
marker, `<!-- hand-edited: <why> -->`, is put in the paper. `--base` diffs against another
file instead of the paper at HEAD; `--marked` keeps only the runs beside a marker (when
the base is a fresh conversion, the rest is the converter's own change). A run that
overlaps a correction already applied replaces it, keeping its converter text.

`retire` deletes the corrections whose `where` is the one given (the paper is left as it is).
"""

import subprocess
import sys
from pathlib import Path

from paperlib import (
    LIBRARY_DIR, LIBRARY_ROOT, content_lines, BodyLines, block_start, is_marker, marker_line, all_corrections,
    diff_corrections, load_corrections, paper_files, paper_stem, read_paper, save_corrections,
    split_frontmatter, write_paper,
)


def option(argv, name):
    if name not in argv:
        return None
    i = argv.index(name)
    if i + 1 >= len(argv):
        sys.exit(__doc__)
    value = argv[i + 1]
    del argv[i:i + 2]
    return value


def list_corrections(argv):
    stale, drifted = "--stale" in argv, "--drifted" in argv
    targets = [a for a in argv if not a.startswith("--")]
    stems = None
    if targets:
        stems = set()
        for t in targets:
            path = Path(t)
            folder = path if path.is_dir() else LIBRARY_DIR / t.strip("/")
            stems |= {p.stem for p in paper_files(folder)} if folder.is_dir() else {paper_stem(t)}
    count = papers = 0
    for stem, corrections in all_corrections().items():
        if stems is not None and stem not in stems:
            continue
        shown = [c for c in corrections if (not stale or c.get("stale")) and (not drifted or c.get("drifted"))]
        if not shown:
            continue
        papers += 1
        for c in shown:
            count += 1
            state = (f" · stale since {c['stale']}" if c.get("stale") else "") + \
                    (f" · drifted {c['drifted']}" if c.get("drifted") else "")
            why = " ".join(str(c.get("why") or "").split())
            print(f"{stem} · {c.get('where') or '?'}{state} · {why}")
    print(f"corrections: {count} in {papers} papers")


def head_text(paper):
    rel = Path(paper).resolve().relative_to(LIBRARY_ROOT.resolve()).as_posix()
    run = subprocess.run(["git", "-C", str(LIBRARY_ROOT), "show", f"HEAD:{rel}"], capture_output=True, text=True)
    if run.returncode:
        sys.exit(f"corrections: {rel} is not committed; commit it before editing, or give --base")
    return run.stdout


def merge(existing, found):
    """The corrections after a capture: a new run that holds an applied correction's `now`
    takes that correction's `was` (the converter's text) in its place; a run inside an
    applied `now` changes that `now`. Returns (corrections, how many were merged)."""
    kept, merged = list(existing), 0
    for new in found:
        for i, old in enumerate(kept):
            old_now = old.get("now") or ""
            if old_now and old_now in new["was"]:
                new = {**new, "was": new["was"].replace(old_now, old.get("was") or "", 1)}
                kept[i] = None
                merged += 1
            elif new["was"] and old_now and new["was"] in old_now:
                kept[i] = {**old, "now": old_now.replace(new["was"], new["now"], 1)}
                new = None
                merged += 1
                break
        kept = [c for c in kept if c is not None]
        if new:
            kept.append(new)
    return kept, merged


def mark(edited, corrections):
    """The edited body with each new correction's marker above its block, where missing."""
    raw = edited.split("\n")
    for c in corrections:
        now = content_lines(c.get("now"))
        lines = BodyLines("\n".join(raw))
        hits = lines.find(now) if now else []
        if not hits:
            continue
        start = block_start(lines.raw, lines.idx[hits[0]])
        if start > 0 and is_marker(lines.raw[start - 1]):
            continue
        raw = lines.raw[:start] + [marker_line(c)] + lines.raw[start:]
    return "\n".join(raw)


def capture(argv):
    why, where, base_file = option(argv, "--why"), option(argv, "--where"), option(argv, "--base")
    marked = "--marked" in argv
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1 or not Path(args[0]).is_file():
        sys.exit(__doc__)
    paper = Path(args[0])
    meta, edited = read_paper(paper)
    base = split_frontmatter(Path(base_file).read_text(encoding="utf-8") if base_file else head_text(paper))[1]
    found = diff_corrections(base, edited, marked_only=marked, why=why or "", where=where or "")
    if not found:
        print(f"corrections: no edits found in {paper.stem} against {'the base' if base_file else 'HEAD'}")
        return
    kept, merged = merge(load_corrections(paper), found)
    save_corrections(paper, kept)
    write_paper(paper, meta, mark(edited, found))
    for c in found:
        print(f"corrections: {paper.stem} · {c['where'] or '?'}: {len(content_lines(c['was']))} lines → "
              f"{len(content_lines(c['now']))}" + ("" if c.get("why") else " (no --why given)"))
    if merged:
        print(f"corrections: {merged} earlier corrections merged with these")


def retire(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    paper, where = argv
    corrections = load_corrections(paper)
    kept = [c for c in corrections if (c.get("where") or "") != where]
    if len(kept) == len(corrections):
        sys.exit(f"corrections: {paper_stem(paper)} has no correction at `{where}`")
    save_corrections(paper, kept)
    print(f"corrections: retired {len(corrections) - len(kept)} of {paper_stem(paper)}")


def main(argv):
    if argv[:1] == ["capture"]:
        capture(argv[1:])
    elif argv[:1] == ["retire"]:
        retire(argv[1:])
    elif any(a in ("-h", "--help") for a in argv):
        print(__doc__)
    else:
        list_corrections(list(argv))


if __name__ == "__main__":
    main(sys.argv[1:])
