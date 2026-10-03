#!/usr/bin/env python3
"""Outcomes and throughput of a reconversion run, from its --state file.

    python3 runs.py <state.jsonl> [--split <at> ...]

`scripts/reconvert.py --state` appends one JSON line per paper as it finishes:
{"paper", "status", "message", "at"}, `at` in local time to the second. Running the
same command again appends records for the papers it retries. `--split` starts a new
invocation at the first record with that `at` (an exact value from the file), since
the file itself does not mark where one command ended and the next began.

Prints JSON: per invocation, its records, statuses, first and last record, and the
wall-clock time between them; for the whole file, the status of each paper's last
record, skip reasons, and, for invocations converting papers one at a time, the
seconds between consecutive records, which is each paper's conversion time.

Written after the run to summarise the state files, not part of the run itself.
"""

import collections
import json
import re
import statistics
import sys
from datetime import datetime


def main(argv):
    path, splits = argv[0], set()
    if "--split" in argv:
        splits = set(argv[argv.index("--split") + 1:])
    records = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]

    runs, current = [], []
    for r in records:
        if r["at"] in splits and current:
            runs.append(current)
            current = []
        current.append(r)
    runs.append(current)

    out = {"file": path.rsplit("/", 1)[-1], "records": len(records), "invocations": []}
    for run in runs:
        times = [datetime.fromisoformat(r["at"]) for r in run]
        gaps = [(b - a).total_seconds() for a, b in zip(times, times[1:])]
        converted = sum(r["status"] in ("ok", "partial") for r in run)
        elapsed = (times[-1] - times[0]).total_seconds()
        inv = {
            "first_record": run[0]["at"], "last_record": run[-1]["at"],
            "elapsed_min": round(elapsed / 60, 1),
            "records": len(run),
            "status": dict(collections.Counter(r["status"] for r in run)),
            "converted_per_hour": round(converted / elapsed * 3600) if elapsed else None,
        }
        if len(run) > 20:
            q = statistics.quantiles(gaps, n=10)
            slow = sorted(zip(gaps, run[1:]), key=lambda x: -x[0])[:5]
            inv["seconds_between_records"] = {
                "median": round(statistics.median(gaps), 1), "mean": round(statistics.mean(gaps), 1),
                "p90": round(q[-1], 1), "max": max(gaps),
                "slowest": [{"seconds": g, "paper": r["paper"], "message": r["message"]} for g, r in slow],
            }
        out["invocations"].append(inv)

    last = {}
    for r in records:
        last[r["paper"]] = r
    out["papers"] = len(last)
    out["last_status"] = dict(collections.Counter(r["status"] for r in last.values()))
    out["skip_reasons"] = dict(collections.Counter(r["message"] for r in last.values() if r["status"] == "skipped"))
    out["not_ok"] = [{"paper": r["paper"], "status": r["status"], "message": r["message"]}
                     for r in last.values() if r["status"] in ("partial", "failed")]
    retried = [p for p, n in collections.Counter(r["paper"] for r in records).items() if n > 1]
    out["retried"] = [{"paper": p, "statuses": [r["status"] for r in records if r["paper"] == p]} for p in retried]
    # Words written for PDF papers ("from the PDF, N words") and notes on the conversion.
    words = [int(m.group(1)) for r in last.values() if (m := re.search(r"from the PDF, (\d+) words", r["message"]))]
    if words:
        out["pdf_words"] = {"papers": len(words), "total": sum(words), "median": statistics.median(words)}
        out["pdf_notes"] = [{"paper": r["paper"], "message": r["message"]} for r in last.values()
                            if re.search(r"fell back|equation model failed", r["message"])]
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
