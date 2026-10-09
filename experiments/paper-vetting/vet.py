#!/usr/bin/env python3
"""The `paperlib vet` command as measured here on 9 Oct 2026, kept as apparatus: the engine
replaced it with `paperlib info`, which reports and does not recommend.

A first opinion on a paper before it is added: what it is, how it was received, how the
library covers its area, how it fits the reader's interests.

    vet.py <arxiv-id-or-url> [...] [--why "..."] [--again] [--model ID]

It stops as early as it can. A paper in the library, skipped earlier (catalog/skipped.yaml)
or vetted before is reported from what is already known, with no model request. Otherwise
it collects signals without a model (arXiv's metadata, Semantic Scholar's venue and citation
counts, and which of the library's own papers, notes and reviews name the title), then makes
two small requests through `claude -p`, no tools: the filing request of `paperlib add`, for
the folder, and one for the verdict, given the signals, the reader's interests
(`interests` in paper-library.yaml) and that folder's papers.

    --why "..."   the reader's reason for looking at the paper, given to the model
    --again       vet a paper again, ignoring the saved verdict
    --model ID    the model (default: `vetting_model` in paper-library.yaml, else sonnet)

The verdict informs and never blocks: `paperlib add` works whatever it says. It is written
from the abstract, so it cannot tell whether the paper's evidence holds.
"""

import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from paperlib import (
    CACHE_DIR, CATALOG_DIR, CONFIG, LIBRARY_DIR, LIBRARY_ROOT, NOTES_DIR,
    REVIEWS_DIR, ask_model, fetch, filing_choice, filing_prompts, library_arxiv_ids, load_topics,
    norm_title, note_path, paper_files, parse_arxiv_entries, read_paper, skipped_index,
)

API = "https://export.arxiv.org/api/query"
S2_BATCH = ("https://api.semanticscholar.org/graph/v1/paper/batch?fields=venue,year,citationCount,"
            "influentialCitationCount,publicationTypes,authors.name,authors.hIndex")
ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")
VERDICT = re.compile(r"\*\*Recommendation:\s*(add|skip|read first)\b", re.I)
# The reader's interests, as the measured design had them: `interests:` in paper-library.yaml.
INTERESTS_FILE = Path(os.path.expanduser(str(CONFIG.get("interests") or CATALOG_DIR / "interests.md")))
NO_INTERESTS = "(not written down: judge fit against the library's topic tree alone, and say so)"


def semantic_scholar(arxiv_ids):
    """Map arXiv id -> Semantic Scholar record (venue, citation counts, authors), where found.

    The batch endpoint answers anonymous scripts where the search one does not
    (experiments/metadata-sources). A failure gives {}: the verdict then says there is no
    citation data.
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


def named_in(title, exclude=()):
    """The library's papers, notes and reviews that name `title`, as paths under the root."""
    folders = [str(f) for f in (LIBRARY_DIR, NOTES_DIR, REVIEWS_DIR) if f.is_dir()]
    if not folders or len(norm_title(title)) < 8:
        return []
    done = subprocess.run(["grep", "-rliF", "--include=*.md", "--", title, *folders],
                          capture_output=True, text=True)
    skip = {str(p) for p in exclude}
    return sorted(str(p) for p in done.stdout.splitlines()
                  if p not in skip and not p.endswith("/README.md"))


def age_of(published, today=None):
    """(years as a float, "3.4 years old") for a publication date."""
    days = ((today or datetime.date.today()) - published).days if published else 0
    years = days / 365.25
    return years, (f"{years:.1f} years old" if days >= 365 else f"{max(days // 30, 0)} months old")


def signal_lines(entry, record, named):
    """The no-model signals as the lines the model and the reader see."""
    years, _ = age_of(entry["published"])
    lines = []
    if record:
        cites = record.get("citationCount") or 0
        rate = f", {cites / years:.0f} a year" if years >= 1 else ""
        lines.append(f"- Semantic Scholar: venue {record.get('venue') or 'none recorded'}; "
                     f"{cites} citations{rate}, {record.get('influentialCitationCount') or 0} influential")
        ranked = sorted((a.get("hIndex") or 0 for a in record.get("authors") or []), reverse=True)
        if ranked:
            lines.append(f"- Authors' h-index, highest first: {', '.join(map(str, ranked[:6]))}")
    else:
        lines.append("- Semantic Scholar: no citation data")
    papers = [p for p in named if p.startswith(str(LIBRARY_DIR))]
    others = [p for p in named if not p.startswith(str(LIBRARY_DIR))]
    if named:
        names = "; ".join(p.rsplit("/", 1)[-1][:-3] for p in named[:5])
        lines.append(f"- Named in the library by {len(papers)} papers and {len(others)} notes or reviews: {names}")
    else:
        lines.append("- Named in the library by no paper, note or review")
    return lines


def neighbours(folder, exclude=None):
    """The papers of a folder as `title (year): summary` lines."""
    lines = []
    for path in paper_files(LIBRARY_DIR / folder):
        if path.parent != LIBRARY_DIR / folder or path == exclude:
            continue
        meta = read_paper(path)[0]
        year = str(meta.get("published") or "")[:4]
        lines.append(f"- {meta.get('title')} ({year}): {' '.join(str(meta.get('summary') or '').split())}")
    return lines


def interests():
    return INTERESTS_FILE.read_text(encoding="utf-8").strip() if INTERESTS_FILE.is_file() else NO_INTERESTS


def vetting_prompts():
    """(system prompt, paper template): prompt.md, with the reader's interests.

    The rules and the interests are the system prompt, the same for every paper, so a run
    of several reads them from the prompt cache.
    """
    rules, the_paper = (Path(__file__).resolve().parent / "prompt.md").read_text(encoding="utf-8").split("THE PAPER")
    system = rules.replace("{reader}", str(CONFIG.get("reader") or "the reader")).replace("{interests}", interests())
    return system.strip(), "THE PAPER" + the_paper


def vet(arxiv_id, entry, record, topics, model, why="", exclude=None, prompts=None):
    """The verdict on one paper: a dict with folder, summary, signals, verdict, recommendation
    and the requests' usage. `exclude` hides a library paper from the signals and the folder
    (for measuring on papers already there). Raises RuntimeError when a request fails."""
    filing, vetting = prompts or (filing_prompts(topics), vetting_prompts())
    reply, used = ask_model(model, filing[0], filing[1].format(title=entry["title"], abstract=entry["abstract"]))
    folder, reason, summary = filing_choice(reply, topics)
    named = named_in(entry["title"], exclude=[exclude] if exclude else [])
    if exclude:
        named = [p for p in named if p != str(note_path(exclude))]
    signals = signal_lines(entry, record, named)
    listed = neighbours(folder, exclude) if folder else []
    _, age = age_of(entry["published"])
    prompt = vetting[1].format(
        title=entry["title"], authors=", ".join(entry["authors"][:8]), arxiv=arxiv_id,
        published=entry["published"], age=age, categories=" ".join(entry.get("categories") or []),
        comment=f"; authors' comment: {entry['comment']}" if entry.get("comment") else "",
        abstract=entry["abstract"], signals="\n".join(signals),
        folder=folder or "none fits", scope=topics.get(folder, reason),
        neighbours="\n".join(listed) or "(none)",
        why=f"\n{CONFIG.get('reader') or 'The reader'}'s reason for looking at it: {why}\n" if why else "")
    verdict, used2 = ask_model(model, vetting[0], prompt)
    found = VERDICT.search(verdict)
    return {"arxiv": arxiv_id, "title": entry["title"], "folder": folder, "summary": summary,
            "signals": signals, "verdict": verdict.strip(),
            "recommendation": found.group(1).lower() if found else None,
            "usage": {k: (used.get(k) or 0) + (used2.get(k) or 0) for k in ("input", "output", "usd")}}


def saved_path(arxiv_id):
    """Where a verdict is kept: in the cache, per library, since it depends on the library."""
    return CACHE_DIR / "vet" / LIBRARY_ROOT.name / f"{arxiv_id}.md"


def main(argv):
    sys.stdout.reconfigure(line_buffering=True)
    options = {"--model": None, "--why": ""}
    again = "--again" in argv
    args = [a for a in argv if a != "--again"]
    wanted = []
    while args:
        arg = args.pop(0)
        if arg in options and args:
            options[arg] = args.pop(0)
        elif ARXIV_ID.search(arg):
            wanted.append(ARXIV_ID.search(arg).group(1))
        else:
            sys.exit(f"error: not an arXiv id or URL: {arg}\n\n{__doc__}")
    wanted = list(dict.fromkeys(wanted))
    if not wanted:
        sys.exit(__doc__)
    model = options["--model"] or CONFIG.get("vetting_model") or "sonnet"

    in_library = library_arxiv_ids()
    skipped_by_id, skipped_by_title = skipped_index()
    data = fetch(f"{API}?id_list={quote(','.join(wanted))}&max_results={len(wanted)}", attempts=5)
    entries = parse_arxiv_entries(data.decode("utf-8")) if data and b"<entry" in data else None
    if entries is None:
        sys.exit("error: arXiv export API gave no usable response")

    # Stage 1: what is already known needs no model.
    todo, failed = [], False
    for arxiv_id in wanted:
        entry = entries.get(arxiv_id)
        if not entry:
            print(f"{arxiv_id}: not found on arXiv\n")
            failed = True
            continue
        print(f"{arxiv_id} | {entry['published']} | {entry['title']}")
        skip = skipped_by_id.get(arxiv_id) or skipped_by_title.get(norm_title(entry["title"]))
        saved = saved_path(arxiv_id)
        if arxiv_id in in_library:
            path = in_library[arxiv_id]
            print(f"  already in library: {path.relative_to(LIBRARY_ROOT)}")
            if note_path(path).exists():
                print(f"  its note: {note_path(path).relative_to(LIBRARY_ROOT)}")
            print()
        elif skip:
            print(f"  skipped earlier ({skip.get('date', '')}): {skip['reason']}\n")
        elif saved.exists() and not again:
            when = datetime.date.fromtimestamp(saved.stat().st_mtime)
            print(f"  vetted {when} (--again to redo):\n\n{saved.read_text(encoding='utf-8')}\n")
        else:
            todo.append(arxiv_id)
    if not todo:
        sys.exit(1 if failed else 0)

    # Stages 2 and 3: the signals, then the two requests.
    records = semantic_scholar(todo)
    topics = load_topics()
    prompts = filing_prompts(topics), vetting_prompts()
    if not INTERESTS_FILE.is_file():
        print(f"note: no interests file at {INTERESTS_FILE}; fit is judged from the topic tree alone\n")
    for arxiv_id in todo:
        entry = entries[arxiv_id]
        try:
            result = vet(arxiv_id, entry, records.get(arxiv_id), topics, model, options["--why"], prompts=prompts)
        except RuntimeError as error:
            print(f"{arxiv_id}: not vetted: {error}\n")
            failed = True
            continue
        text = "\n".join([f"# {entry['title']}", "",
                          f"arXiv {arxiv_id}, {entry['published']}. Would be filed in "
                          f"`{result['folder'] or 'no declared folder'}`.", "",
                          *result["signals"], "", result["verdict"]])
        saved = saved_path(arxiv_id)
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_text(text + "\n", encoding="utf-8")
        used = result["usage"]
        print(f"\n{text}\n\n({used['input']:,} tokens in, {used['output']:,} out"
              + (f", ${used['usd']:.3f}" if used["usd"] else "") + ")\n")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
