#!/usr/bin/env python3
"""Count the recommendations per class of label, and the cost, from results/<model>.jsonl.

    python3 experiments/paper-vetting/score.py [--disagreements]
"""
import json
import sys
from collections import Counter
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"
CLASSES = ["skipped", "kept-reviewed", "kept-unreviewed"]
AGREES = {"skipped": "skip", "kept-reviewed": "add", "kept-unreviewed": "add"}

for path in sorted(RESULTS.glob("*.jsonl")):
    if path.name == "sample.jsonl":
        continue
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    print(f"\n{path.stem}: {len(rows)} papers")
    print("| Label | Papers | add | read first | skip | Agrees |\n|---|---|---|---|---|---|")
    for name in CLASSES:
        group = [r for r in rows if r["class"] == name]
        said = Counter(r["recommendation"] for r in group)
        agree = said[AGREES[name]]
        print(f"| {name} | {len(group)} | {said['add']} | {said['read first']} | {said['skip']} | "
              f"{agree} of {len(group)} |")
    usd = [r["usage"]["usd"] or 0 for r in rows]
    print(f"per paper: {sum(r['usage']['input'] for r in rows) / len(rows):,.0f} tokens in, "
          f"{sum(r['usage']['output'] for r in rows) / len(rows):,.0f} out, ${sum(usd) / len(rows):.3f}; "
          f"total ${sum(usd):.2f}")
    if "--disagreements" in sys.argv:
        for r in rows:
            if r["recommendation"] != AGREES[r["class"]]:
                last = r["verdict"].split("**Recommendation")[-1].replace("\n", " ")[:400]
                print(f"\n[{r['class']}: {r['label']}] {r['title']} ({r['arxiv']})\n  {' | '.join(r['signals'])}\n  Recommendation{last}")
