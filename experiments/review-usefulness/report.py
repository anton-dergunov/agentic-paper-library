"""Tabulate the sessions and their grades per question and condition.

    python3 report.py <sessions.tsv> <judge-dir> [<judge-suffix>]

Prints a markdown table: for each question and condition, the number of sessions and the
mean (and range) over them of input tokens, seconds, pooled points made and wrong
statements, then the same per session. Points count only pooled points whose verdict is
"holds". Answers of another run in the pool (<session>@<label>) have grades and no
session row. <judge-suffix> reads judge-<question>-<suffix>.json, a second judge's grades.
"""
import collections
import csv
import glob
import json
import os
import re
import sys


def spread(values, unit=1, digits=1):
    values = [v / unit for v in values if v is not None]
    if not values:
        return ""
    mean = sum(values) / len(values)
    if len(values) == 1:
        return "%.*f" % (digits, mean)
    return "%.*f (%.*f–%.*f)" % (digits, mean, digits, min(values), digits, max(values))


def main():
    sessions = {row["session"]: row for row in csv.DictReader(open(sys.argv[1]), delimiter="\t") if row.get("input")}
    suffix = "-" + sys.argv[3] if len(sys.argv) > 3 else ""
    cells, held = collections.defaultdict(list), {}
    for path in sorted(glob.glob(os.path.join(sys.argv[2], "judge-q?%s.json" % suffix))):
        graded = json.load(open(path))
        key = re.search(r"judge-(q\d+)", path).group(1)
        holds = {point["id"] for point in graded["points"] if point["verdict"] == "holds"}
        held[key] = (len(holds), len(graded["points"]))
        for name, answer in graded["answers"].items():
            condition, _, repeat, label = re.match(r"(.*)-(q\d+)(?:-r(\d+))?(@.*)?$", name).groups()
            row = sessions.get(name, {})
            cells[key, condition + (label or "")].append({
                "name": name, "input": int(row["input"]) if row else None,
                "seconds": int(row["seconds"]) if row else None,
                "points": len(holds & set(answer["makes"])), "errors": len(answer["errors"]),
                "review_only": answer.get("review_only", "no") != "no",
                "misleading": answer.get("misleading", "no") != "no"})
    print("| Question | Condition | Sessions | Input tokens, K | Seconds | Points made | Wrong statements | Misleading |")
    print("|---|---|---|---|---|---|---|---|")
    for (key, condition), rows in sorted(cells.items()):
        print("| %s (%d points hold of %d) | %s | %d | %s | %s | %s | %s | %d |" % (
            key, *held[key], condition, len(rows), spread([r["input"] for r in rows], 1000, 0),
            spread([r["seconds"] for r in rows], 1, 0), spread([r["points"] for r in rows]),
            spread([r["errors"] for r in rows]), sum(r["misleading"] for r in rows)))
    print("\nsession\tpoints\terrors\treview_only\tmisleading")
    for rows in cells.values():
        for r in sorted(rows, key=lambda r: r["name"]):
            print("%s\t%d\t%d\t%s\t%s" % (r["name"], r["points"], r["errors"], r["review_only"], r["misleading"]))


if __name__ == "__main__":
    main()
