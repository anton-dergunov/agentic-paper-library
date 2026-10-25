#!/usr/bin/env python3
"""Tables of the results so far: results/summary.md, and the generated part of PROGRESS.md.

    PAPER_LIBRARY=<library> uv run python report.py

Scores count first answers (r1) unless said otherwise: correct 1, partial 0.5. Where a
question was asked three times in a condition, "majority" is the score two of three runs
share.
"""

import collections
import json
import re

import run
import judge

HERE = run.HERE
LETTER = {"correct": "C", "partial": "P", "wrong": "W", "declined": "D", None: "·"}
VALUE = {"correct": 1, "partial": 0.5, "wrong": 0, "declined": 0}


def records():
    return [json.loads(p.read_text()) for p in sorted(run.RUNS.glob("*/*/*.json"))]


def all_grades():
    out = {}
    for path in judge.JUDGE.glob("*.json"):
        out.update(json.loads(path.read_text())["grades"])
    return out


def run_id(r):
    return "%s/%s/%s-r%d" % (r["exp"], r["cond"], r["qid"], r["rep"])


def table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def scores_grid(recs, grades, exp, conds):
    """Per question, per condition: the letters of r1, r2, r3."""
    cells = collections.defaultdict(dict)
    for r in recs:
        if r["exp"] == exp and r["cond"] in conds:
            g = grades.get(run_id(r), {})
            mark = "TL" if r["status"] == "too_long" else LETTER[g.get("score")]
            if g.get("confident_wrong"):
                mark += "!"
            cells[r["qid"]].setdefault(r["cond"], {})[r["rep"]] = mark
    rows = []
    for qid in [q["id"] for q in run.inputs.QUESTIONS if q["id"] in cells]:
        q = run.Q[qid]
        rows.append([qid, q["kind"]] + [" ".join(cells[qid].get(c, {}).get(n, "") for n in sorted(cells[qid].get(c, {})))
                                       or "" for c in conds])
    return table(["Q", "kind"] + list(conds), rows)


def score_summary(recs, grades, exp, conds):
    by = collections.defaultdict(list)
    for r in recs:
        if r["exp"] == exp and r["cond"] in conds and r["rep"] == 1:
            score = grades.get(run_id(r), {}).get("score")
            if score:
                by[("all", r["cond"])].append(score)
                by[(run.Q[r["qid"]]["kind"], r["cond"])].append(score)
    kinds = sorted({k for k, _ in by}, key=lambda k: (k != "all", k))
    rows = []
    for kind in kinds:
        row = [kind]
        for c in conds:
            s = by.get((kind, c), [])
            row.append("%.1f / %d" % (sum(VALUE[x] for x in s), len(s)) if s else "")
        rows.append(row)
    return table(["kind (score / n)"] + list(conds), rows)


def costs(recs, exp, conds):
    """Per paper and condition: tokens of the first request, and the requests' total."""
    by = collections.defaultdict(list)
    for r in recs:
        if r["exp"] == exp and r["cond"] in conds:
            by[(r["paper"], r["cond"])].append(r)
    rows = []
    for (paper, cond), rs in sorted(by.items()):
        first = min(rs, key=lambda r: r["date"])
        rows.append([paper, cond, len(rs), "{:,}".format(max(r["input"] for r in rs)),
                     "{:,}".format(sum(r["cache_read"] or 0 for r in rs)),
                     round(sum(r["output"] or 0 for r in rs) / len(rs)), "%.2f" % sum(r["usd"] or 0 for r in rs),
                     "%.0f" % (sum(r["seconds"] for r in rs) / len(rs))])
        del first
    return table(["paper", "condition", "requests", "input tokens", "read from cache", "mean output",
                  "$", "mean s"], rows)


def e0(recs):
    rows = [[r["cond"], r["qid"], r["rep"], "{:,}".format(r["input"]), r["cache_read"], r["output"], "%.3f" % (r["usd"] or 0),
             (r["answer"] or "")[:80].replace("\n", " ").replace("|", "/")]
            for r in recs if r["exp"] == "E0"]
    return table(["condition", "question", "r", "input tokens", "from cache", "output", "$", "answer starts"], rows)


def main():
    recs, grades = records(), all_grades()
    spent = sum(r["usd"] or 0 for r in recs)
    judged = sum(json.loads(p.read_text()).get("usd") or 0 for p in judge.JUDGE.glob("*.json"))
    window = [r["five_hour"] for r in sorted(recs, key=lambda r: r["date"]) if r["five_hour"] is not None]
    parts = ["Requests: %d, $%.2f; judge (latest grading of each question) $%.2f; last five-hour utilisation seen: %s." % (
        len(recs), spent, judged, "%.0f%%" % (100 * window[-1]) if window else "?"),
        "Marks: C correct, P partial, W wrong, D declined, TL too long for the context, `!` confidently wrong; "
        "several marks are r1 r2 r3."]
    seen = [r for r in recs if r["paper"] not in run.UNSEEN]
    unseen = [r for r in recs if r["paper"] in run.UNSEEN]
    for rs, exp, conds, title in (
            (seen, "E1", run.E1_ALL, "E1: single paper, format only"),
            (unseen, "E1", run.E1_CORE, "E1, tier B2: papers published after the training cutoff"),
            (recs, "E4", ("md-old", "md", "pdf", "txt"), "E4: conversion fixes"),
            (seen, "E5", ("page", "img1255", "img2576", "md"), "E5: small print"),
            (unseen, "E5", ("page", "img1255", "img2576", "md", "txt"), "E5, tier C2: small print on the unseen papers"),
            (recs, "E6", ("pdf", "txt", "md"), "E6: equation structure")):
        if any(r["exp"] == exp for r in rs):
            parts += ["## " + title, score_summary(rs, grades, exp, conds), scores_grid(rs, grades, exp, conds),
                      "Cost", costs(rs, exp, conds)]
    if any(r["exp"] == "E0" for r in recs):
        parts += ["## E0: token cost and page resolution", e0(recs)]
    notes = [(run_id(r), grades[run_id(r)]["note"]) for r in recs
             if grades.get(run_id(r), {}).get("note") and grades[run_id(r)]["score"] != "correct"]
    if notes:
        parts += ["## The judge's notes on answers not graded correct",
                  "\n".join("- `%s`: %s" % (name, note) for name, note in notes)]
    summary = "# Results so far\n\nGenerated by `report.py`.\n\n" + "\n\n".join(parts) + "\n"
    (HERE / "results" / "summary.md").write_text(summary)
    progress = HERE / "PROGRESS.md"
    if progress.exists():
        text = progress.read_text()
        block = "<!-- report.py -->\n" + "\n\n".join(parts[:1]) + "\n" + _status() + "\n<!-- /report.py -->"
        text = re.sub(r"<!-- report.py -->.*<!-- /report.py -->", lambda m: block, text, flags=re.S)
        progress.write_text(text)
    print(summary)


def _status():
    import contextlib
    import io
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        run.status()
    return "\n```\n" + out.getvalue().strip() + "\n```"


if __name__ == "__main__":
    main()
