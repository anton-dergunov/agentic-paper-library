#!/usr/bin/env python3
"""Can a library's hand edits be kept apart from the paper and applied again to a new conversion?

    PAPER_LIBRARY=~/papers uv run python reapply.py <fresh library dir> [--json results.json]

<fresh library dir> holds the hand-edited papers converted afresh with `paperlib reconvert
--force`, at their paths under library/ (a scratch copy; see README.md). For each paper
with a hand-edited marker in the library:

  then   the edits as captured when they were made: for every commit that added a marker,
         paperlib.diff_corrections(<the paper before it>, <the paper after it>, marked_only)
  fresh  the same edits captured against the fresh conversion: diff_corrections(<fresh>,
         <the paper as it is now>, marked_only), which is what the migration stores

`then` is applied to the fresh conversion (a later converter than the one it was taken
from) and `fresh` to the paper as converted before its first edit (an earlier one): two
independent drifts. Both outcomes are printed per correction, with the similarity of a
drifted match, and `same` says whether applying `then` and `fresh` to the fresh
conversion gives the same paper, which checks that a drifted match replaced the right text.
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from paperlib import (  # noqa: E402
    HAND_EDITED, LIBRARY_DIR, LIBRARY_ROOT, content_lines, apply_corrections, diff_corrections, paper_files,
    read_paper, split_frontmatter,
)


def git(*args):
    return subprocess.run(["git", "-C", str(LIBRARY_ROOT), *args], capture_output=True, text=True).stdout


def body_at(rev, rel):
    text = git("show", f"{rev}:{rel}")
    return split_frontmatter(text)[1] if text else None


def markers(body):
    return [line.strip() for line in (body or "").split("\n") if HAND_EDITED.search(line)]


def captured_then(rel):
    """The edits of every commit that added a marker to the paper: (commit, corrections)."""
    commits = git("log", "--reverse", "--format=%h", "--", rel).split()
    out, before = [], None
    for c in commits:
        after = body_at(c, rel)
        if before is not None and after is not None:
            added = len(markers(after)) > len(markers(before))
            if added:
                out.append((c, diff_corrections(before, after, marked_only=True)))
        before = after
    return out


def first_edit_parent(rel):
    """The paper as converted just before its first marker: an earlier converter's output."""
    commits = git("log", "--reverse", "--format=%h", "--", rel).split()
    before = None
    for c in commits:
        after = body_at(c, rel)
        if before is not None and markers(after) and not markers(before):
            return before
        before = after
    return None


def norm(body):
    return [line for line in content_lines(body)]


def size(c):
    return len(c.get("was") or ""), len(c.get("now") or "")


def main(argv):
    fresh_root = Path(argv[0]).resolve()
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None
    rows, papers = [], []
    state = fresh_root / "run.jsonl"
    converted = {json.loads(line)["paper"] for line in state.read_text(encoding="utf-8").splitlines()
                 if line.strip() and json.loads(line)["status"] == "ok"} if state.exists() else set()
    for p in paper_files():
        meta, body = read_paper(p)
        if not HAND_EDITED.search(body):
            continue
        rel_lib = p.relative_to(LIBRARY_DIR)
        rel = p.relative_to(LIBRARY_ROOT).as_posix()
        fresh_path = fresh_root / "library" / rel_lib
        if not fresh_path.exists() or rel_lib.as_posix() not in converted:
            papers.append({"paper": p.stem, "source": meta.get("source"), "skipped": "not converted afresh"})
            continue
        fresh = read_paper(fresh_path)[1]
        then = [c for _, cs in captured_then(rel) for c in cs]
        now_set = diff_corrections(fresh, body, marked_only=True)
        older = first_edit_parent(rel)
        applied_then, _, out_then = apply_corrections(fresh, then)
        applied_fresh, _, out_fresh = apply_corrections(fresh, now_set)
        out_older = apply_corrections(older, now_set)[2] if older else []
        same = norm(applied_then) == norm(applied_fresh)
        papers.append({
            "paper": p.stem, "source": meta.get("source"), "markers": len(markers(body)),
            "then": len(then), "fresh": len(now_set), "same": same,
            "chars_was": sum(size(c)[0] for c in now_set), "chars_now": sum(size(c)[1] for c in now_set),
            "paper_chars": len(body),
        })
        for c, outcome, sim in out_then:
            rows.append({"paper": p.stem, "set": "then→fresh", "where": c.get("where"), "outcome": outcome,
                         "similarity": sim, "was_lines": len(content_lines(c.get("was"))),
                         "now_lines": len(content_lines(c.get("now")))})
        for c, outcome, sim in out_fresh:
            rows.append({"paper": p.stem, "set": "fresh→fresh", "where": c.get("where"), "outcome": outcome,
                         "similarity": sim, "was_lines": len(content_lines(c.get("was"))),
                         "now_lines": len(content_lines(c.get("now")))})
        for c, outcome, sim in out_older:
            rows.append({"paper": p.stem, "set": "fresh→older", "where": c.get("where"), "outcome": outcome,
                         "similarity": sim, "was_lines": len(content_lines(c.get("was"))),
                         "now_lines": len(content_lines(c.get("now")))})
    for pr in papers:
        if "skipped" in pr:
            print(f"{pr['paper'][:60]:60s} skipped: {pr['skipped']}")
            continue
        print(f"{pr['paper'][:60]:60s} {pr['source']:8s} markers {pr['markers']}, then {pr['then']}, "
              f"fresh {pr['fresh']}, same {pr['same']}, {pr['chars_now']} chars of {pr['paper_chars']}")
        for r in rows:
            if r["paper"] == pr["paper"]:
                sim = f" {r['similarity']}" if r["similarity"] else ""
                print(f"    {r['set']:12s} {r['outcome']:9s}{sim:7s} {r['was_lines']:3d}→{r['now_lines']:<3d} {r['where']}")
    totals = {}
    for r in rows:
        totals.setdefault(r["set"], {}).setdefault(r["outcome"], 0)
        totals[r["set"]][r["outcome"]] += 1
    print(json.dumps(totals, indent=1))
    if out_json:
        Path(out_json).write_text(json.dumps({"papers": papers, "corrections": rows, "totals": totals},
                                             indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
