#!/usr/bin/env python3
"""What is known about a paper, whether or not the library has it. It reports along fixed
axes and never recommends: whether to read or add a paper is the reader's call.

    ./scripts/paper-info.py <arxiv-id-or-url | title words> [...] [--json] [--facts] [--again]

A paper in the library is answered from the library alone, with no network: where its
markdown, note, overview and review are, and its summary. Title words find library papers
only. A paper skipped earlier (catalog/skipped.yaml) is answered with the reason.

For any other arXiv paper it collects, without a model: arXiv's metadata; Semantic Scholar's
venue and citation counts, with a grade of the citation rate (UPTAKE below); and which of
the library's papers, notes and reviews name the title. Then two small requests through
`claude -p`, no tools: the filing request of `paperlib add`, for the folder it would go in,
and one that says what the paper proposes, its type and character, and how it relates to the
nearest papers of that folder (guide/info-prompt.md).

    --json     one JSON object per paper, on one line each, for another program
    --facts    no model requests: everything above them, in about two seconds
    --again    ignore the saved answer for a paper not in the library
    --model ID the model (default: `info_model` in paper-library.yaml, else sonnet)

Answers for papers not in the library are kept in the cache, per library.
"""

import datetime
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from paperlib import (
    CACHE_DIR, CONFIG, ENGINE_ROOT, LIBRARY_DIR, LIBRARY_ROOT, NOTES_DIR, OVERVIEW_DIR, REVIEWS_DIR,
    TYPES, ask_model, fetch, filing_choice, filing_prompts, library_arxiv_ids, load_reviews,
    load_topics, norm_title, note_path, paper_files, parse_arxiv_entries, read_paper, review_for,
    skipped_index,
)

API = "https://export.arxiv.org/api/query"
S2_BATCH = ("https://api.semanticscholar.org/graph/v1/paper/batch?fields=venue,year,citationCount,"
            "influentialCitationCount,authors.name,authors.hIndex,title,abstract,publicationDate")
ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")
# The grade of a citation rate: the first band whose floor (citations a year) it reaches.
# Fixed and field-blind on purpose, so that it reads the same for every paper; a paper
# under a year old has no rate yet.
UPTAKE = [(150, "very high"), (30, "high"), (5, "modest"), (0, "low")]
RELATIONS = {"same-idea", "builds-on", "alternative", "predecessor", "successor", "same-problem"}


def semantic_scholar(arxiv_ids):
    """Map arXiv id -> Semantic Scholar record (venue, citation counts, authors), where found.

    The batch endpoint answers anonymous scripts where the search one does not
    (experiments/metadata-sources). A failure gives {}: the paper then has no citation data.
    """
    body = json.dumps({"ids": [f"ARXIV:{i}" for i in arxiv_ids]})
    for _ in range(2):
        done = subprocess.run(
            ["curl", "-s", "--max-time", "20", "-X", "POST", S2_BATCH,
             "-H", "Content-Type: application/json", "-d", body], capture_output=True, text=True)
        try:
            records = json.loads(done.stdout)
        except ValueError:
            continue
        if isinstance(records, list):
            return {i: r for i, r in zip(arxiv_ids, records) if r}
    return {}


def relative(path):
    return str(path.relative_to(LIBRARY_ROOT)) if path.is_relative_to(LIBRARY_ROOT) else str(path)


def named_in(title):
    """The library's papers, notes and reviews that name `title`, as paths from the root."""
    folders = [str(f) for f in (LIBRARY_DIR, NOTES_DIR, REVIEWS_DIR) if f.is_dir()]
    if not folders or len(norm_title(title)) < 8:
        return []
    done = subprocess.run(["grep", "-rliF", "--include=*.md", "--", title, *folders],
                          capture_output=True, text=True)
    return sorted(p for p in done.stdout.splitlines() if not p.endswith("/README.md"))


def in_library(path):
    """A library paper, from the library alone."""
    meta = read_paper(path)[0]
    folder = str(path.parent.relative_to(LIBRARY_DIR))
    scope = review_for(folder, load_reviews())
    overview = OVERVIEW_DIR / f"{path.stem}.md" if OVERVIEW_DIR else None
    return {
        "status": "in library", "arxiv": str(meta.get("arxiv") or "") or None, "title": meta.get("title"),
        "published": str(meta.get("published") or "") or None, "folder": folder,
        "paper": relative(path),
        "note": relative(note_path(path)) if note_path(path).exists() else None,
        "overview": str(overview) if overview and overview.exists() else None,
        "review": relative(load_reviews()[scope]["main"]) if scope else None,
        "type": meta.get("type"), "source": meta.get("source"),
        "summary": " ".join(str(meta.get("summary") or "").split())}


def facts(arxiv_id, entry, record):
    """Everything that needs no model, for a paper not in the library."""
    days = (datetime.date.today() - entry["published"]).days if entry["published"] else 0
    years = round(days / 365.25, 1)
    info = {
        "status": "not in library", "arxiv": arxiv_id, "title": entry["title"],
        "authors": entry["authors"], "published": str(entry["published"]), "age_years": years,
        "categories": entry.get("categories") or [], "comment": entry.get("comment") or None,
        "venue": None, "citations": None, "influential_citations": None, "citations_per_year": None,
        "uptake": "no citation data", "authors_h_index": []}
    if record:
        cites = record.get("citationCount") or 0
        venue = record.get("venue") or None
        info.update(venue=None if venue == "arXiv.org" else venue, citations=cites,
                    influential_citations=record.get("influentialCitationCount") or 0,
                    authors_h_index=sorted((a.get("hIndex") or 0 for a in record.get("authors") or []), reverse=True))
        if days >= 365:
            rate = round(cites / years, 1)
            info.update(citations_per_year=rate, uptake=next(name for floor, name in UPTAKE if rate >= floor))
        else:
            info["uptake"] = "under a year old"
    named = named_in(entry["title"])
    info["named_in_library"] = {
        "papers": sum(p.startswith(str(LIBRARY_DIR)) for p in named),
        "notes_and_reviews": sum(not p.startswith(str(LIBRARY_DIR)) for p in named),
        "by": [relative(Path(p)) for p in named[:8]]}
    info["abstract"] = entry["abstract"]
    return info


def describe(info, topics, model, prompts):
    """Add what a model says: the folder, what the paper proposes, and the nearest papers.

    Raises RuntimeError when a request fails or the reply is not JSON."""
    filing, (system, the_paper) = prompts
    reply, used = ask_model(model, filing[0], filing[1].format(title=info["title"], abstract=info["abstract"]))
    folder, reason, _ = filing_choice(reply, topics)
    listed = []
    if folder:
        for path in paper_files(LIBRARY_DIR / folder):
            if path.parent == LIBRARY_DIR / folder:
                listed.append((path, read_paper(path)[0]))
    lines = [f"{n}. {meta.get('title')} ({str(meta.get('published') or '')[:4]}): "
             f"{' '.join(str(meta.get('summary') or '').split())}" for n, (_, meta) in enumerate(listed, 1)]
    reply, used2 = ask_model(model, system, the_paper.format(
        title=info["title"], comment=info["comment"] or "none", abstract=info["abstract"],
        folder=folder or "none fits", scope=topics.get(folder, reason), neighbours="\n".join(lines) or "(none)"))
    try:
        answer = json.loads(reply[reply.index("{"):reply.rindex("}") + 1])
    except ValueError:
        raise RuntimeError("the model did not reply with JSON: " + reply.strip()[:200])
    nearest = []
    for item in answer.get("nearest") or []:
        n = item.get("n") if isinstance(item, dict) else None
        if isinstance(n, int) and 1 <= n <= len(listed):
            path, meta = listed[n - 1]
            relation = str(item.get("relation") or "")
            nearest.append({"title": meta.get("title"), "paper": relative(path),
                            "relation": relation if relation in RELATIONS else "same-problem",
                            "how": " ".join(str(item.get("how") or "").split())})
    kind = str(answer.get("type") or "").strip().lower()
    text = lambda key: " ".join(str(answer.get(key) or "").split())
    info.update(folder=folder, folder_papers=len(listed), type=kind if kind in TYPES else None,
                character=text("character"), proposes=text("proposes"), evidence=text("evidence"),
                releases=text("releases"), nearest=nearest,
                usage={k: (used.get(k) or 0) + (used2.get(k) or 0) for k in ("input", "output", "usd")})
    return info


def table(info):
    """The answer as aligned lines for a person; a markdown renderer shows them as they are."""
    rows = [("Paper", info["title"])]
    add = lambda name, value: rows.append((name, str(value))) if value not in (None, "", []) else None
    if info["status"] == "in library":
        add("Status", "in library")
        add("arXiv", f"{info['arxiv']}, submitted {info['published']}" if info["arxiv"] else info["published"])
        for name in ("paper", "note", "overview", "review", "type", "summary"):
            add(name.capitalize(), info[name])
    elif info["status"] == "skipped":
        add("Status", f"skipped earlier ({info['skipped']['date']}): {info['skipped']['reason']}")
        add("arXiv", f"{info['arxiv']}, submitted {info['published']}")
    else:
        age = f"{info['age_years']} years" if info["age_years"] >= 1 else f"{round(info['age_years'] * 12)} months"
        add("Status", "not in library" + (f"; looked at {info['looked']}" if info.get("looked") else ""))
        add("arXiv", f"{info['arxiv']}, submitted {info['published']} ({age} old)")
        add("Authors", ", ".join(info["authors"][:6]) + (" and others" if len(info["authors"]) > 6 else ""))
        add("Venue", info["venue"] or ("arXiv only" if info["citations"] is not None else None))
        add("Comment", info["comment"])
        if info["citations"] is not None:
            rate = f", {info['citations_per_year']:g} a year" if info["citations_per_year"] is not None else ""
            add("Citations", f"{info['citations']} in total{rate}, "
                f"{info['influential_citations']} where the citing paper builds on this one")
        add("Uptake", info["uptake"])
        add("h-index", ", ".join(map(str, info["authors_h_index"][:6])))
        named = info["named_in_library"]
        names = "; ".join(p.rsplit("/", 1)[-1][:-3] for p in named["by"][:4])
        add("Named by", f"{named['papers']} library papers, {named['notes_and_reviews']} notes or reviews"
            + (f": {names}" if names else ""))
        if "proposes" in info:
            add("Folder", f"{info['folder']} ({info['folder_papers']} paper{'' if info['folder_papers'] == 1 else 's'})" if info["folder"] else "no declared folder fits")
            add("Type", ", ".join(filter(None, [info["type"], info["character"]])))
            add("Proposes", info["proposes"])
            add("Evidence", info["evidence"])
            add("Releases", info["releases"])
            for item in info["nearest"]:
                add("Nearest", f"{item['title']} [{item['relation']}]: {item['how']}")
    width = max(len(name) for name, _ in rows)
    return "\n".join(f"{name:<{width}}  {value}" for name, value in rows)


def find_by_title(words, files):
    """Library papers whose title holds all the words given."""
    wanted = norm_title(words).split()
    return [p for p in files if all(w in norm_title(read_paper(p)[0].get("title")).split() for w in wanted)]


def main(argv):
    sys.stdout.reconfigure(line_buffering=True)
    flags = {name: name in argv for name in ("--json", "--facts", "--again")}
    args = [a for a in argv if a not in flags]
    model = CONFIG.get("info_model") or "sonnet"
    if "--model" in args:
        at = args.index("--model")
        model = args[at + 1] if at + 1 < len(args) else model
        del args[at:at + 2]
    if not args:
        sys.exit(__doc__)
    show = (lambda info: print(json.dumps(info, ensure_ascii=False))) if flags["--json"] else \
        (lambda info: print(table(info) + "\n"))

    library = library_arxiv_ids()
    skipped_by_id, _ = skipped_index()
    files, todo, failed = None, [], False
    for arg in args:
        found = ARXIV_ID.search(arg)
        if not found:
            files = files or paper_files()
            matches = find_by_title(arg, files)
            for path in matches[:5]:
                show(in_library(path))
            if not matches:
                show({"status": "not found", "title": arg, "note": "no library paper has these title words; "
                      "give an arXiv id or URL for a paper outside the library"}) if flags["--json"] else \
                    print(f"{arg}: no library paper has these title words; give an arXiv id or URL "
                          "for a paper outside the library\n")
                failed = True
        elif found.group(1) in library:
            show(in_library(library[found.group(1)]))
        else:
            todo.append(found.group(1))
    todo = list(dict.fromkeys(todo))
    saved = lambda arxiv_id: CACHE_DIR / "info" / LIBRARY_ROOT.name / f"{arxiv_id}.json"
    fresh = []
    for arxiv_id in todo:
        if saved(arxiv_id).exists() and not flags["--again"]:
            info = json.loads(saved(arxiv_id).read_text(encoding="utf-8"))
            if "proposes" in info or flags["--facts"]:
                info["looked"] = str(datetime.date.fromtimestamp(saved(arxiv_id).stat().st_mtime))
                show(info)
                continue
        fresh.append(arxiv_id)
    if not fresh:
        sys.exit(1 if failed else 0)

    # arXiv's export API throttles for minutes at a time; Semantic Scholar then supplies the
    # title, abstract and date as well, without the categories and the authors' comment.
    data = fetch(f"{API}?id_list={quote(','.join(fresh))}&max_results={len(fresh)}", attempts=2)
    entries = parse_arxiv_entries(data.decode("utf-8")) if data and b"<entry" in data else {}
    records = semantic_scholar([i for i in fresh if i not in skipped_by_id or i not in entries])
    for arxiv_id, record in records.items():
        if arxiv_id not in entries and record.get("title") and record.get("abstract"):
            date = record.get("publicationDate")
            entries[arxiv_id] = {
                "title": record["title"], "abstract": " ".join(record["abstract"].split()),
                "authors": [a.get("name") for a in record.get("authors") or []],
                "published": datetime.date.fromisoformat(date) if date else None}
    if not entries:
        sys.exit("error: neither arXiv's export API nor Semantic Scholar gave a usable response")
    wanted = [i for i in fresh if i in entries and i not in skipped_by_id]
    topics = load_topics()
    prompts = None
    if wanted and not flags["--facts"]:
        rules, the_paper = (ENGINE_ROOT / "guide" / "info-prompt.md").read_text(encoding="utf-8").split("THE PAPER")
        prompts = filing_prompts(topics), (rules.strip(), "THE PAPER" + the_paper)
    for arxiv_id in fresh:
        entry = entries.get(arxiv_id)
        if not entry:
            show({"status": "not found", "arxiv": arxiv_id, "title": f"{arxiv_id}: not found"})
            failed = True
            continue
        if arxiv_id in skipped_by_id:
            skip = skipped_by_id[arxiv_id]
            show({"status": "skipped", "arxiv": arxiv_id, "title": entry["title"], "published": str(entry["published"]),
                  "skipped": {"reason": skip.get("reason", ""), "date": str(skip.get("date", ""))}})
            continue
        info = facts(arxiv_id, entry, records.get(arxiv_id))
        if prompts:
            try:
                describe(info, topics, model, prompts)
            except RuntimeError as error:
                print(f"{arxiv_id}: facts only, the description failed: {error}", file=sys.stderr)
                failed = True
        saved(arxiv_id).parent.mkdir(parents=True, exist_ok=True)
        saved(arxiv_id).write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
        show(info)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
