# Experiment · which metadata services resolve a paper title from a script?

**Question.** Adding papers in bulk starts from titles: links and citations collected in notes,
reading lists, a folder of old PDFs. Which public services turn a title into an arXiv id or a DOI,
and an id into year, venue and citation count, when called anonymously from a script — and which
refuse?

**Status.** Run 30 Sep 2026 while building a 997-paper inventory, counted again from the saved
caches on 3 Oct: **arXiv's title search resolved 623 of 819 titles (76%), Crossref 100 more (12%),
96 (12%) neither; Semantic Scholar's batch endpoint returned 893 of 911 ids with year, venue and
citations.** Semantic Scholar's title search managed 20 titles in an hour; OpenAlex's anonymous
search was paused and DBLP sat behind a bot check. Publishers' sites refused scripted PDF
downloads. One run, one day, one network: availability is the finding, and it changes.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#metadata).

## Method

- **Corpus.** Every paper reference in the owner's notes, plans and old PDF folder: 446 arXiv,
  DOI or ACL ids taken from links, and 819 distinct titles from link text, prose citations and
  file names. The references come from private notes, so neither they nor the caches are
  committed; [`summary.json`](summary.json) holds the aggregate counts.
- **Apparatus**, as run (no changes):
  - [`resolve.py`](resolve.py): ids to Semantic Scholar records with `POST /paper/batch`, 400 ids a
    call; titles with `/paper/search/match`, falling back to `/paper/search`, 1.1 s apart, backing
    off on 429.
  - [`resolve_titles.py`](resolve_titles.py), which replaced the title half of `resolve.py`: arXiv's
    export API first (all content words as a `ti:` AND query, then the whole title as a `ti:`
    phrase, 3.1 s apart), then Crossref's `query.bibliographic`. A hit counts when its normalised
    title matches at similarity 0.88 (arXiv) or 0.9 (Crossref), or starts with a query of 25+
    characters. The ids found then go to the Semantic Scholar batch endpoint.
  - [`resolve_openalex.py`](resolve_openalex.py): the OpenAlex resolver written as a second
    opinion and stopped after its test (below).
  - Their inputs (`refs.jsonl`, `prose_titles.tsv`, `url_titles.tsv`) were extracted from the
    private notes and are not here.
  - [`cache_summary.py`](cache_summary.py) recomputes the counts from the caches and the last run's
    log, offline:

    ```bash
    python3 experiments/metadata-sources/cache_summary.py <dir with titlecache.json, s2cache.json, resolve_titles.log>
    ```

- **Probes.** The service checks below were single `curl` calls from the session, recovered from its
  transcript; the PDF-download findings come from two agent runs that looked for open copies of
  papers not on arXiv (26 papers on 30 Sep, 32 on 1 Oct).

## Results

### Title to identifier

| Service | Call | Outcome |
|---|---|---|
| **arXiv export API** | `search_query=ti:w1 AND ti:w2 …`, then `ti:"<title>"` | **623 of 819 titles.** Median 3.3 s a title, almost all of it the 3 s pause arXiv asks for |
| **Crossref** | `/works?query.bibliographic=<title>` | **100 more**: 43 journal articles, 42 proceedings papers, 9 book chapters, 6 other. Median 7.4 s a title, counting the arXiv misses before it |
| neither | | 96 titles, 12%; a sample of 30 was a mix of titles cut short or suffixed in file names ("…Case Studies at", "…Self-Improve2"), papers off arXiv whose Crossref record fell below the threshold or which have no DOI (BLEU, The Google File System, Ad Click Prediction), and arXiv papers the queries missed (LongNet, FastText.zip) |
| Semantic Scholar | `/paper/search/match` | 20 titles in an hour, 19 found. Six requests in a row: `200 429 429 429 429 200`. Stopped |
| OpenAlex | `/works?search=` | `"Anonymous search is paused while the search cluster recovers from heavy load"` |
| OpenAlex | `/works?filter=title.search:` | answered at first ("ad click prediction": 30 hits, the 2013 paper first), then `503` and the "paused" message when the resolver was tested. Stopped |
| DBLP | `/search/publ/api` | an HTML bot challenge ("Making sure you're not a bot!") instead of JSON |

Two details of the arXiv query mattered:

- **Stop words break an AND query.** `ti:ready AND ti:for AND ti:agent` returns nothing where the
  same query without `for` finds the paper, so the word query drops stop words. The phrase query
  `ti:"<whole title>"` keeps them and works, and it is what `scripts/arxiv-lookup.py` tries first.
- **Retries need short timeouts.** The first resolver waited 60 s per attempt with five retries
  and slowed to about 3 titles a minute, mostly asleep in back-off. With a 20 s timeout and three
  attempts the 709 remaining titles took about an hour.

### Identifier to record

| Ids sent to `POST /paper/batch` | Found |
|---|---|
| arXiv | 795 of 802 |
| DOI | 93 of 104 |
| ACL Anthology | 5 of 5 |
| **all** | **893 of 911**, every one with a citation count, 892 with a year, 867 with a venue |

The batch endpoint was not rate-limited at 400 ids a call with 1.5–2 s between calls, while the
search endpoint on the same host was.

### A matched title can be a different paper

Reviewing the 997 resolved papers by topic found six whose match was another paper with the same or
a similar title. Three were classics that are not on arXiv, matched to a later arXiv paper of the
same name: *Long Short-Term Memory* (1997) to `2105.06756`, *Stochastic Neighbor Embedding* (2002)
to `1811.01247`, *The Unreasonable Effectiveness of Data* (2009) to `2604.06420`. Another was
*Adaptive Mixtures of Local Experts* (1991), matched to a paper titled "Adaptive mixtures of local
experts are source coding solutions". A year far from the one cited is the signal; the resolver did
not check it.

### PDFs for papers not on arXiv

| Route | Outcome |
|---|---|
| Publisher sites: `dl.acm.org`, `onlinelibrary.wiley.com`, `link.springer.com`, `tandfonline.com`, `sciencedirect.com`, `papers.ssrn.com` | bot checks; ACM serves Cloudflare's "Just a moment…" page even to headless Chrome |
| `openreview.net` | `403` |
| Semantic Scholar `openAccessPdf` | for 20 DOIs, 11 URLs, every one back to the publisher (`doi.org`, `dl.acm.org`, Wiley, Taylor & Francis); on 1 Oct, empty for 31 of 32 |
| Unpaywall | rejects a placeholder email; with a real one, no open copy for any of 32 papers |
| Wayback Machine `id_` URLs (`web.archive.org/web/2022id_/<url>`) | worked for one ACM open-access PDF and for old author-hosted files |
| Authors' and institutions' pages, found by web search | 14 of 26 papers on 30 Sep, 27 of 32 on 1 Oct |

The papers no route reached were downloaded by hand in a browser, or skipped.

## Files

| File | Holds |
|---|---|
| [`resolve.py`](resolve.py), [`resolve_titles.py`](resolve_titles.py), [`resolve_openalex.py`](resolve_openalex.py) | the resolvers as run |
| [`cache_summary.py`](cache_summary.py) | the counts above, from the caches |
| [`summary.json`](summary.json) | its output |

## Limits

- One afternoon from one residential connection. OpenAlex's pause was temporary by its own message,
  and an API key would change the Semantic Scholar result; neither was retried.
- "Resolved" means a title match above the threshold, not a checked identity; the six wrong matches
  were found by reading, so there may be more.
- The 819 titles lean to well-known ML papers, most of which are on arXiv. A corpus of older or
  non-ML papers would lean on Crossref more.
