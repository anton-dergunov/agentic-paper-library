#!/usr/bin/env python3
"""Aggregate counts from the resolvers' caches; prints JSON, no titles.

    python3 cache_summary.py <dir with titlecache.json, s2cache.json and resolve_titles.log>

Makes no requests.
"""
import collections
import json
import re
import statistics
import sys
from pathlib import Path

d = Path(sys.argv[1])
titles = json.loads((d / "titlecache.json").read_text())
s2 = json.loads((d / "s2cache.json").read_text())

out = {"titles": {"total": len(titles)}}
via = collections.Counter((v or {}).get("via", "none") for v in titles.values())
out["titles"].update(via)
out["titles"]["crossref_types"] = dict(collections.Counter(
    v.get("type") for v in titles.values() if v and v.get("via") == "crossref").most_common())

ids = {k: v for k, v in s2.items() if k.startswith("id:")}
out["s2_batch"] = {}
for prefix in ("ARXIV", "DOI", "ACL"):
    kk = [k for k in ids if k.startswith(f"id:{prefix}:")]
    out["s2_batch"][prefix] = {"asked": len(kk), "found": sum(1 for k in kk if ids[k])}
recs = [v for v in ids.values() if v]
out["s2_batch"]["records_with"] = {
    "year": sum(1 for r in recs if r.get("year")),
    "venue": sum(1 for r in recs if r.get("venue")),
    "citationCount": sum(1 for r in recs if r.get("citationCount") is not None),
}
tt = [k for k in s2 if k.startswith("title:")]
out["s2_title_search"] = {"asked": len(tt), "found": sum(1 for k in tt if s2[k])}

# Per-title timing of the last resolve_titles.py run: "  3.1s arxiv    <title>"
times = collections.defaultdict(list)
for line in (d / "resolve_titles.log").read_text().splitlines():
    m = re.match(r"^\s+([\d.]+)s (\S+)\s", line)
    if m:
        times[m.group(2)].append(float(m.group(1)))
out["last_run_seconds_per_title"] = {
    k: {"n": len(v), "median": round(statistics.median(v), 1)} for k, v in times.items()}
print(json.dumps(out, indent=2))
