#!/usr/bin/env python3
"""Look every title up in OpenAlex (title filter; anonymous full search is paused).

oacache.json: "<title>" -> {"title", "year", "citations", "doi", "arxiv", "venue", "type"} or null.
Gives venue, citation count and DOI for papers that are not on arXiv, and an
independent second opinion for those that are.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from resolve_titles import all_titles, norm, similar

HERE = Path(__file__).parent
CACHE = HERE / "oacache.json"
cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
SELECT = "display_name,publication_year,cited_by_count,doi,locations,primary_location,type"


def fetch(t):
    words = " ".join(norm(t).split()[:20])
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"filter": f"title.search:{words}", "per-page": 10, "select": SELECT})
    delay = 2
    for _ in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "papers-inventory/0.1"}), timeout=60) as r:
                d = json.loads(r.read())
            if "results" in d:
                return d["results"]
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            pass
        time.sleep(delay)
        delay = min(delay * 2, 60)
    return None


def pick(t, results):
    cands = []
    for w in results:
        s = similar(t, w.get("display_name"))
        if s < 0.9:
            continue
        arxiv = None
        for loc in w.get("locations") or []:
            u = loc.get("landing_page_url") or ""
            if "arxiv.org/abs/" in u:
                arxiv = u.rsplit("/abs/", 1)[1].split("v")[0]
        venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        cands.append((s, w.get("cited_by_count") or 0, {
            "title": w["display_name"], "year": w.get("publication_year"),
            "citations": w.get("cited_by_count"), "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower() or None,
            "arxiv": arxiv, "venue": venue, "type": w.get("type")}))
    if not cands:
        return None
    cands.sort(key=lambda c: (-round(c[0], 2), -c[1]))
    best = cands[0][2]
    # Citations are split across duplicate records (preprint vs proceedings); report the total.
    best["citations_all"] = sum(c[1] for c in cands if c[0] >= 0.97)
    best["arxiv"] = best["arxiv"] or next((c[2]["arxiv"] for c in cands if c[2]["arxiv"]), None)
    return best


def main():
    titles = all_titles()
    todo = [t for t in titles if t not in cache]
    print(f"{len(todo)} titles", flush=True)
    for n, t in enumerate(todo, 1):
        res = fetch(t)
        if res is None:
            continue
        cache[t] = pick(t, res)
        if n % 25 == 0:
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0))
            print(f"  {n}/{len(todo)}", flush=True)
        time.sleep(0.3)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0))
    print("done", flush=True)


if __name__ == "__main__":
    main()
