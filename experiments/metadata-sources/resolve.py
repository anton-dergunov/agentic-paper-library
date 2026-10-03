#!/usr/bin/env python3
"""Resolve every reference to a Semantic Scholar record.

Inputs: refs.jsonl (extract.py), prose_titles.tsv (hand-extracted), url_titles.tsv
(hand titles for URLs without usable link text). Output: s2cache.json, keyed by
query ("id:ARXIV:1706.03762", "title:<text>"), so reruns only fetch what is new.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
CACHE = HERE / "s2cache.json"
API = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,year,venue,citationCount,externalIds,publicationDate,publicationTypes,authors"

cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}


def save():
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0))


def request(url, data=None, tries=8):
    delay = 2
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            if e.code == 400:
                return None
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(delay)
            delay = min(delay * 2, 60)
    return "FAILED"


def url_to_id(u):
    m = re.search(r"(?:doi\.org/|dl\.acm\.org/doi/(?:fullHtml/|abs/|pdf/)?)(10\.\d{4,5}/[^\s?#]+)", u)
    if m:
        return "DOI:" + m.group(1).rstrip("/")
    m = re.search(r"aclanthology\.org/([A-Z0-9.\-]+?)(?:\.pdf)?/?$|aclweb\.org/anthology/([A-Z0-9.\-]+?)/?$", u)
    if m:
        return "ACL:" + (m.group(1) or m.group(2))
    return None


def clean_title(t):
    t = re.sub(r"\s*\(\d{4}-\d{2}-\d{2} [\d-]+\)$", "", t)  # "(2026-08-16 11-53-48)" copies
    t = re.sub(r"\s+-\s+v\d+$", "", t)
    t = t.replace(" - ", ": ").replace("$-infty$", "∞").replace("_", " ")
    return t.strip()


def main():
    refs = [json.loads(l) for l in (HERE / "refs.jsonl").open()]
    ids, titles = set(), set()
    for r in refs:
        if r["kind"] == "arxiv":
            ids.add("ARXIV:" + r["value"])
        elif r["kind"] == "title":
            titles.add(clean_title(r["value"]))
        elif r["kind"] == "url":
            i = url_to_id(r["value"])
            if i:
                ids.add(i)
    for line in (HERE / "prose_titles.tsv").open():
        titles.add(line.rstrip("\n").split("\t", 1)[1].strip())
    ut = HERE / "url_titles.tsv"
    if ut.exists():
        for line in ut.open():
            parts = line.rstrip("\n").split("\t")
            if len(parts) > 1 and parts[1] and not parts[1].startswith("-"):
                titles.add(parts[1].strip())

    todo = [i for i in sorted(ids) if f"id:{i}" not in cache]
    print(f"{len(ids)} ids ({len(todo)} to fetch), {len(titles)} titles", flush=True)
    for k in range(0, len(todo), 400):
        chunk = todo[k:k + 400]
        res = request(f"{API}/paper/batch?fields={FIELDS}", {"ids": chunk})
        if res == "FAILED":
            print("batch failed", file=sys.stderr)
            continue
        for i, rec in zip(chunk, res or [None] * len(chunk)):
            cache[f"id:{i}"] = rec
        save()
        time.sleep(1.5)

    todo = [t for t in sorted(titles) if f"title:{t}" not in cache]
    print(f"{len(todo)} titles to fetch", flush=True)
    for n, t in enumerate(todo, 1):
        q = urllib.parse.quote(t[:300])
        res = request(f"{API}/paper/search/match?query={q}&fields={FIELDS}")
        rec = None
        if isinstance(res, dict) and res.get("data"):
            rec = res["data"][0]
        elif res is None or (isinstance(res, dict) and not res.get("data")):
            # No exact-ish match: fall back to relevance search, keep the top hit for review.
            time.sleep(1.1)
            res2 = request(f"{API}/paper/search?query={q}&limit=1&fields={FIELDS}")
            if isinstance(res2, dict) and res2.get("data"):
                rec = dict(res2["data"][0], fallback=True)
        if res == "FAILED":
            continue
        cache[f"title:{t}"] = rec
        if n % 20 == 0:
            save()
            print(f"  {n}/{len(todo)}", flush=True)
        time.sleep(1.1)
    save()
    print("done")


if __name__ == "__main__":
    main()
