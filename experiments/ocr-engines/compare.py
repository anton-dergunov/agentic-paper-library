#!/usr/bin/env python3
"""Summarise run.py's output: crashes and time per setting, and what OCR adds.

    python3 experiments/ocr-engines/compare.py <out-dir>

Per paper (first attempt of each setting): seconds and words, and against the
conversion without OCR, the lines each engine adds or removes, split into
lines inside tables and other lines.
"""

import collections
import difflib
import json
import sys
from pathlib import Path


def lines(path):
    return [line for line in path.read_text(encoding="utf-8").split("\n") if line.strip()] if path.exists() else None


def main(out_dir):
    out_dir = Path(out_dir)
    runs = [json.loads(line) for line in open(out_dir / "runs.jsonl")]
    by_setting = collections.defaultdict(list)
    for r in runs:
        by_setting[r["setting"]].append(r)
    print("setting    runs  crashed  fell back  seconds (sum)")
    for setting, rs in by_setting.items():
        print(f"{setting:<10}{len(rs):>5}{sum(r['exit'] != 0 for r in rs):>9}"
              f"{sum(r['text_layer_fallback'] for r in rs):>11}{sum(r['seconds'] for r in rs):>15.0f}")
    print("\npaper | seconds rapidocr/ocrmac/off | words rapidocr/ocrmac/off | "
          "lines added, removed against off: rapidocr (in tables), ocrmac (in tables)")
    papers = list(dict.fromkeys(r["paper"] for r in runs))
    for paper in papers:
        first = {}
        for r in runs:
            if r["paper"] == paper and r["exit"] == 0:
                first.setdefault(r["setting"], r)
        off = lines(out_dir / "off" / f"{paper[:60]}.{first['off']['attempt']}.md") if "off" in first else None
        cells = []
        for setting in ("rapidocr", "ocrmac"):
            if setting not in first or off is None:
                cells.append("-")
                continue
            new = lines(out_dir / setting / f"{paper[:60]}.{first[setting]['attempt']}.md")
            diff = [d for d in difflib.unified_diff(off, new, lineterm="", n=0) if d[:1] in "+-" and d[:3] not in ("+++", "---")]
            added = [d for d in diff if d[0] == "+"]
            removed = [d for d in diff if d[0] == "-"]
            table = lambda ds: sum(d[1:].lstrip().startswith(("|", "<t")) for d in ds)  # noqa: E731
            cells.append(f"+{len(added)} ({table(added)}), -{len(removed)} ({table(removed)})")
        secs = "/".join(str(round(first[s]["seconds"])) if s in first else "-" for s in ("rapidocr", "ocrmac", "off"))
        words = "/".join(str(first[s]["words"]) if s in first else "-" for s in ("rapidocr", "ocrmac", "off"))
        print(f"{paper[:55]} | {secs} | {words} | {cells[0]} | {cells[1]}")


if __name__ == "__main__":
    main(sys.argv[1])
