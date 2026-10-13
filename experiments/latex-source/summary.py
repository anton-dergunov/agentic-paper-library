#!/usr/bin/env python3
"""The tables of the write-up, from the records of convert.py and measure.py.

    python3 summary.py no-html > results/summary-no-html.txt
    python3 summary.py control > results/summary-control.txt
"""

import collections
import csv
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
name = sys.argv[1]
records = [json.loads(line) for line in (HERE / "results" / f"convert-{name}.jsonl").read_text().splitlines()]
rows = collections.defaultdict(dict)
for row in csv.DictReader((HERE / "results" / f"measure-{name}.tsv").open(encoding="utf-8"), delimiter="\t"):
    rows[row["arxiv"]][row["conversion"]] = row


def complete(arxiv_id, form):
    """A conversion that lacks no more pages of the PDF than the library's own."""
    row = rows[arxiv_id].get(form)
    return bool(row) and int(row["missing"]) <= int(rows[arxiv_id]["library"]["missing"])


outcome = collections.Counter()
for r in records:
    if r.get("error"):
        outcome["no usable source: " + r["error"].split(" (")[0]] += 1
        continue
    a = r["arxiv"]
    if complete(a, "latexml"):
        outcome["LaTeXML: whole paper"] += 1
    elif complete(a, "latexml2"):
        outcome["LaTeXML: whole paper once the limit of 100 errors is lifted"] += 1
    elif "timed" in r.get("latexml", "") or r.get("latexml_s", 0) >= 300:
        outcome["LaTeXML: timed out at 5 minutes"] += 1
    else:
        outcome["LaTeXML: failed or lost pages"] += 1
    outcome["pandoc: whole paper" if complete(a, "pandoc") else
            "pandoc: failed or timed out" if "pandoc" not in rows[a] else "pandoc: lost pages"] += 1
print(f"{len(records)} papers")
for key, n in sorted(outcome.items()):
    print(f"{n:4d}  {key}")

print("\nform\tpapers\tchars against library (median)\tpages lacking\tformulas KaTeX cannot parse (median)\tlabels left (median)")
for form in ("library", "latexml", "latexml2", "pandoc", "tex"):
    have = [(v[form], v["library"]) for v in rows.values() if form in v and len(v) > 1]
    if not have:
        continue
    katex = [int(f["katex"]) for f, _ in have if f["katex"] != ""]
    print(f"{form}\t{len(have)}\t{statistics.median(int(f['chars']) / int(l['chars']) for f, l in have):.2f}\t"
          f"{sum(int(f['missing']) for f, _ in have)} of {sum(int(f['pages']) for f, _ in have)}\t"
          f"{statistics.median(katex) if katex else ''}\t{statistics.median(int(f['labels']) for f, _ in have)}")

seconds = [r["latexml_s"] for r in records if "latexml_s" in r and r["latexml_s"] < 300]
if seconds:
    print(f"\nLaTeXML runs that ended by themselves: {len(seconds)}, median {statistics.median(seconds):.0f} s, "
          f"longest {max(seconds):.0f} s")
pandoc = [r["pandoc_s"] for r in records if "pandoc_s" in r and "pandoc" not in r]
if pandoc:
    print(f"pandoc runs that converted: {len(pandoc)}, median {statistics.median(pandoc):.1f} s, longest {max(pandoc):.1f} s")
