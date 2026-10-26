#!/usr/bin/env python3
"""Tables of the results so far: results/summary.md, and the generated part of PROGRESS.md.

    PAPER_LIBRARY=<library> uv run python report.py

Scores count first answers (r1) unless said otherwise: correct 1, partial 0.5. Where a
question was asked three times in a condition, "majority" is the score two of three runs
share.
"""

import collections
import fnmatch
import functools
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
            mark = {"too_long": "TL", "over_budget": "OB"}.get(r["status"]) or LETTER[g.get("score")]
            if g.get("confident_wrong"):
                mark += "!"
            cells[r["qid"]].setdefault(r["cond"], {})[r["rep"]] = mark
    rows = []
    for qid in [q["id"] for q in run.inputs.QUESTIONS if q["id"] in cells]:
        q = run.Q[qid]
        kind = q["kind"] + (", text layer %s" % q["text_layer"] if q.get("text_layer") else "")
        rows.append([qid, kind] + [" ".join(cells[qid].get(c, {}).get(n, "") for n in sorted(cells[qid].get(c, {})))
                                       or "" for c in conds])
    return table(["Q", "kind"] + list(conds), rows)


def score_summary(recs, grades, exp, conds, key="kind"):
    by = collections.defaultdict(list)
    for r in recs:
        if r["exp"] == exp and r["cond"] in conds and r["rep"] == 1:
            score = grades.get(run_id(r), {}).get("score")
            if score:
                by[("all", r["cond"])].append(score)
                by[(run.Q[r["qid"]][key], r["cond"])].append(score)
    kinds = sorted({k for k, _ in by}, key=lambda k: (k != "all", k))
    rows = []
    for kind in kinds:
        row = [kind]
        for c in conds:
            s = by.get((kind, c), [])
            row.append("%.1f / %d" % (sum(VALUE[x] for x in s), len(s)) if s else "")
        rows.append(row)
    return table(["%s (score / n)" % key.replace("_", " ")] + list(conds), rows)


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


FILE = re.compile(r"[\"']([^\"']+\.(?:md|pdf|txt))[\"']|([^\s\"'|;&<>()=]+\.(?:md|pdf|txt))\b")
KINDS = ("paper md", "note", "review", "index", "catalog", "pdf", "txt")


@functools.lru_cache(maxsize=None)
def copy_files(cond):
    copy = run.inputs.OUT / "copies" / ("lib-asis" if run.AGENT_COPIES.get(cond) == "lib" else run.AGENT_COPIES.get(cond, ""))
    return tuple(str(f.relative_to(copy)) for f in copy.rglob("*") if f.is_file()) if cond in run.AGENT_COPIES else ()


def expand(name, cond):
    """A name with a wildcard (notes/RULER*.md) as the copy's files it matches, by its last
    folder and file name; a plain name as itself."""
    if "*" not in name and "?" not in name:
        return {name}
    if re.fullmatch(r"\*+\.\w+", name.rsplit("/", 1)[-1]):
        return set()  # find -name "*.pdf": a listing of the tree, not a file named
    parts = name.rsplit("/", 2)
    tail, folder = parts[-1], (parts[-2] if len(parts) > 1 and "*" not in parts[-2] else "")
    return {f for f in copy_files(cond)
            if fnmatch.fnmatch(f.rsplit("/", 1)[-1], tail) and (not folder or "/%s/" % folder in "/" + f)}


def files_named(stream, cond):
    """The distinct files a session's tool calls name (a Read's path, or a path or wildcard
    in a shell command or a Grep), by kind. A file seen only in a tool's output, reached
    through a shell variable, or covered by a bare "*.pdf" listing or a search of the whole
    tree, is not counted."""
    found = set()
    if not stream.exists():
        return {}
    for line in stream.read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") != "assistant":
            continue
        for part in event["message"].get("content", []):
            if part.get("type") == "tool_use":
                given = part.get("input") or {}
                text = " ".join(str(given.get(k) or "") for k in ("file_path", "command", "path", "glob"))
                for a, b in FILE.findall(text):
                    if "$" not in (a or b):
                        found |= expand(a or b, cond)
    kinds = collections.Counter()
    for path in {f.rsplit("/", 1)[-1]: f for f in found}.values():
        if path.endswith(".pdf"):
            kinds["pdf"] += 1
        elif path.endswith(".txt"):
            kinds["txt"] += 1
        elif "notes/" in path:
            kinds["note"] += 1
        elif "reviews/" in path:
            kinds["review"] += 1
        elif "catalog/" in path:
            kinds["catalog"] += 1
        elif path.endswith("README.md") or path.endswith("AGENTS.md") or path.endswith("CLAUDE.md"):
            kinds["index"] += 1
        else:
            kinds["paper md"] += 1
    return kinds


def recall(r):
    """For a question with `items`: the share of them the answer names."""
    items = run.Q[r["qid"]].get("items")
    if not items:
        return ""
    named = sum(bool(re.search(rx, r["answer"] or "", re.I)) for rx in items.values())
    return "%d/%d" % (named, len(items))


def pages_seen(r):
    """Tier F: the pages a session rendered ("rendered p. 7") and the pictures it looked at:
    a PDF's pages ("p. 7"), a whole PDF, or a number of images."""
    seen = []
    for call in r.get("renders") or []:
        first, last = re.search(r"-f\s*(\d+)", call), re.search(r"-l\s*(\d+)", call)
        span = first.group(1) + ("–" + last.group(1) if last and last.group(1) != first.group(1) else "") if first else "?"
        seen.append("rendered p. " + span)
    images = 0
    for call in r.get("page_views") or []:
        pages = re.search(r"\[pages ([^\]]+)\]", call)
        if pages:
            seen.append("p. " + pages.group(1))
        elif re.search(r"(?i)\.pdf\b", call):
            seen.append("whole PDF")
        else:
            images += 1
    return ", ".join(seen + (["%d image%s" % (images, "s" * (images > 1))] if images else []))


def sessions(recs, exp="E3"):
    """Tiers D and F: one row per session or request, with what an agent did."""
    kinds_shown = KINDS if exp == "E3" else ("pdf", "txt")
    rows = []
    for r in sorted((r for r in recs if r["exp"] == exp and r["cond"] in run.AGENT_COPIES),
                    key=lambda r: (r["qid"], r["cond"], r["rep"])):
        kinds = files_named(run.STREAMS / exp / r["cond"] / ("%s-r%d.jsonl" % (r["qid"], r["rep"])), r["cond"])
        row = [r["qid"], r["cond"], r["rep"], r.get("turns") or "", len(r.get("calls") or []),
               "{:,}".format(r["input"]), "%.2f" % (r["usd"] or 0), "%.0f" % r["seconds"]]
        row += [kinds.get(k) or "" for k in kinds_shown]
        row += [pages_seen(r)] if exp != "E3" else ["yes" if r.get("opened_pdf") else ""]
        row += [len(r.get("outside") or []) or ""] + ([recall(r)] if exp == "E3" else [])
        rows.append(row)
    return table(["Q", "condition", "r", "turns", "tool calls", "input tokens", "$", "s"]
                 + ["files: " + k for k in kinds_shown]
                 + (["pages looked at"] if exp != "E3" else ["opened a PDF"])
                 + ["calls outside the copy"] + (["recall"] if exp == "E3" else []), rows)


def canary_table(recs, grades, conds):
    by = {(r["qid"], r["cond"]): r for r in recs if r["exp"] == "E7" and r["rep"] == 1}
    rows = []
    for qid in run.CANARY:
        row = [qid, run.Q[qid]["kind"]]
        for c in conds:
            r = by.get((qid, c))
            row.append("%s; %s; $%.2f" % (LETTER[grades.get(run_id(r), {}).get("score")], pages_seen(r) or "no page",
                                          r["usd"] or 0) if r else "")
        rows.append(row)
    clis = {c: next((r["cli"].split()[0] for (q, cc), r in by.items() if cc == c), "?") for c in conds}
    return table(["Q", "kind"] + ["%s (%s)" % (c, clis[c]) if c == "f-plain" else c for c in conds], rows)


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
    if any(r["exp"] == "E3" for r in recs):
        conds = ("x-lib", "x-pdf", "x-txt", "x-att")
        parts += ["## E3: across papers", score_summary(recs, grades, "E3", conds),
                  scores_grid(recs, grades, "E3", conds), "Sessions", sessions(recs)]
    if any(r["exp"] == "E7" for r in recs):
        conds = ("f-plain", "f-hint")
        parts += ["## E7, tier F: figures with the PDF at hand", score_summary(recs, grades, "E7", conds),
                  scores_grid(recs, grades, "E7", conds), "Sessions", sessions(recs, "E7")]
    if any(r["exp"] == "E8" for r in recs):
        conds = ("c0", "txt", "md", "f-plain")
        parts += ["## E8, tier G: where the text layer is weak", score_summary(recs, grades, "E8", conds, "text_layer"),
                  score_summary(recs, grades, "E8", conds), scores_grid(recs, grades, "E8", conds),
                  "Cost", costs(recs, "E8", conds), "Sessions (f-plain)", sessions(recs, "E8")]
    canary = sorted({r["cond"] for r in recs if r["cond"].startswith("f-plain@")})
    if canary:
        parts += ["### Canary: f-plain on each Claude Code release",
                  "Score, pages looked at and cost of each canary question; the first column is tier F's run.",
                  canary_table(recs, grades, ["f-plain"] + canary)]
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
