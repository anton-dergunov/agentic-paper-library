#!/usr/bin/env python3
"""Resolve titles to an arXiv id (arXiv title search) or a DOI (Crossref), then
fetch Semantic Scholar records for every id in batches.

titlecache.json: "<title>" -> {"arxiv"|"doi", "title", "year", "via", "venue", "citations"} or null
s2cache.json:    "id:ARXIV:<id>" / "id:DOI:<doi>" -> Semantic Scholar record (batch endpoint)
"""
import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from resolve import FIELDS, API, cache as s2cache, save as s2save, request, clean_title, url_to_id

HERE = Path(__file__).parent
TCACHE = HERE / "titlecache.json"
tcache = json.loads(TCACHE.read_text()) if TCACHE.exists() else {}
NS = {"a": "http://www.w3.org/2005/Atom"}
STOP = set("a an the of for and with from to in on by via is are its we our at as how what why do does can".split())


def norm(t):
    t = (t or "").lower().replace("∞", "infty")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t).split())


def similar(q, found):
    a, b = norm(q), norm(found)
    if not a or not b:
        return 0.0
    if b.startswith(a) and len(a) >= 25:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def arxiv_search(query):
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": query, "max_results": 5})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                data = r.read()
            if b"<feed" in data:
                root = ET.fromstring(data)
                out = []
                for e in root.findall("a:entry", NS):
                    aid = e.find("a:id", NS).text.rsplit("/abs/", 1)[-1]
                    aid = re.sub(r"v\d+$", "", aid)
                    title = " ".join(e.find("a:title", NS).text.split())
                    out.append((aid, title, e.find("a:published", NS).text[:4]))
                return out
        except Exception as e:
            print(f"    arxiv error {type(e).__name__}: {e}", flush=True)
        time.sleep(4 * (attempt + 1))
    return None


def words_query(t):
    ws = [w for w in norm(t).split() if w not in STOP and len(w) > 1][:12]
    return " AND ".join(f"ti:{w}" for w in ws)


def by_arxiv(t):
    best = None
    for q in (words_query(t), f'ti:"{norm(t)}"'):
        if not q:
            continue
        hits = arxiv_search(q)
        time.sleep(3.1)
        for aid, title, year in hits or []:
            s = similar(t, title)
            if s >= 0.88 and (best is None or s > best[0]):
                best = (s, {"arxiv": aid, "title": title, "year": int(year), "via": "arxiv"})
        if best:
            return best[1]
    return None


def by_crossref(t):
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query.bibliographic": t, "rows": 5,
         "select": "title,DOI,is-referenced-by-count,container-title,issued,type"})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "papers-inventory/0.1"}), timeout=20) as r:
                items = json.loads(r.read())["message"]["items"]
            break
        except Exception as e:
            print(f"    crossref error {type(e).__name__}", flush=True)
            time.sleep(3)
    else:
        return None
    best = None
    for it in items:
        title = (it.get("title") or [""])[0]
        s = similar(t, title)
        if s >= 0.9 and (best is None or s > best[0]):
            parts = (it.get("issued") or {}).get("date-parts") or [[None]]
            best = (s, {"doi": it["DOI"].lower(), "title": title, "year": parts[0][0], "via": "crossref",
                        "venue": (it.get("container-title") or [""])[0],
                        "citations": it.get("is-referenced-by-count"), "type": it.get("type")})
    return best[1] if best else None


def all_titles():
    titles = set()
    for r in (json.loads(l) for l in (HERE / "refs.jsonl").open()):
        if r["kind"] == "title":
            titles.add(clean_title(r["value"]))
    for line in (HERE / "prose_titles.tsv").open():
        titles.add(line.rstrip("\n").split("\t", 1)[1].strip())
    for line in (HERE / "url_titles.tsv").open():
        t = line.rstrip("\n").split("\t", 1)[1]
        if not t.startswith("-"):
            titles.add(t.strip())
    return sorted(titles)


def main():
    titles = all_titles()
    todo = [t for t in titles if t not in tcache]
    print(f"{len(titles)} titles, {len(todo)} to resolve", flush=True)
    for n, t in enumerate(todo, 1):
        t0 = time.time()
        rec = by_arxiv(t) or by_crossref(t)
        tcache[t] = rec
        print(f"  {time.time() - t0:5.1f}s {(rec or {}).get('via', '-'):8} {t[:70]}", flush=True)
        if n % 10 == 0:
            TCACHE.write_text(json.dumps(tcache, ensure_ascii=False, indent=0))
            print(f"  {n}/{len(todo)}", flush=True)
    TCACHE.write_text(json.dumps(tcache, ensure_ascii=False, indent=0))

    ids = {f"ARXIV:{v['arxiv']}" if v.get("arxiv") else f"DOI:{v['doi']}" for v in tcache.values() if v}
    todo = sorted(i for i in ids if f"id:{i}" not in s2cache)
    print(f"{len(todo)} new ids for Semantic Scholar", flush=True)
    for k in range(0, len(todo), 400):
        chunk = todo[k:k + 400]
        res = request(f"{API}/paper/batch?fields={FIELDS}", {"ids": chunk})
        if res == "FAILED" or res is None:
            print("batch failed", file=sys.stderr)
            continue
        for i, rec in zip(chunk, res):
            s2cache[f"id:{i}"] = rec
        s2save()
        time.sleep(2)
    print("done", flush=True)


if __name__ == "__main__":
    main()
