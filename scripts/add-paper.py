#!/usr/bin/env python3
"""Add arXiv papers without an agent session: a model picks the folder and writes the summary.

    ./scripts/add-paper.py <arxiv-id-or-url> [...] [--model ID] [--dry-run]

For each paper: arXiv's metadata, then one model request (through `claude -p`, no tools) with
the topic tree, the title and the abstract, which answers with a folder and a one-line
summary; then add-arxiv-paper.sh into that folder, and the summary is set. The indexes are
rebuilt and the library checked once at the end.

    --model ID    the filing model (default: `filing_model` in paper-library.yaml, else
                  sonnet; experiments/skill-models compares the candidates)
    --dry-run     print the folder, the reason and the summary, and add nothing

A paper already in the library, or skipped earlier (catalog/skipped.yaml), is not added. No
folder is ever created: when the model finds none that fits, the paper is left out and
reported, for the add-paper skill, where the reader decides on a new folder. Exit code 1
means at least one paper was not added, or the library check failed.
"""

import re
import subprocess
import sys
from urllib.parse import quote

from paperlib import (
    CONFIG, ENGINE_ROOT, LIBRARY_DIR, SCRIPTS_DIR, ask_model, fetch, filing_choice,
    library_arxiv_ids, load_topics, norm_title, paper_files, parse_arxiv_entries, read_paper,
    skipped_index, write_paper,
)

API = "https://export.arxiv.org/api/query"
ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")
SYSTEM = "You are a careful research librarian."
STYLE_SAMPLES = 3


def style_sample():
    """A few summaries already in the library, spread over it, for the model to match."""
    summaries = [s for s in (" ".join(str(read_paper(p)[0].get("summary") or "").split())
                             for p in paper_files()) if s]
    step = max(1, len(summaries) // STYLE_SAMPLES)
    return "\n".join("- " + s for s in summaries[::step][:STYLE_SAMPLES]) or "(none yet)"


def main(argv):
    sys.stdout.reconfigure(line_buffering=True)  # keep our lines in order with the scripts' own
    options = {"--model": None}
    dry_run = "--dry-run" in argv
    args = [a for a in argv if a != "--dry-run"]
    raw = []
    while args:
        arg = args.pop(0)
        if arg in options and args:
            options[arg] = args.pop(0)
        elif ARXIV_ID.search(arg):
            raw.append(arg)
        else:
            sys.exit(f"error: not an arXiv id or URL: {arg}\n\n{__doc__}")
    if not raw:
        sys.exit(__doc__)
    model = options["--model"] or CONFIG.get("filing_model") or "sonnet"
    # The id with its version, if one was given, is what add-arxiv-paper.sh fetches.
    wanted = {ARXIV_ID.search(r).group(1): ARXIV_ID.search(r).group(0) for r in raw}

    data = fetch(f"{API}?id_list={quote(','.join(wanted))}&max_results={len(wanted)}", attempts=5)
    entries = parse_arxiv_entries(data.decode("utf-8")) if data and b"<entry" in data else None
    if entries is None:
        sys.exit("error: arXiv export API gave no usable response")

    topics = load_topics()
    template = (ENGINE_ROOT / "guide" / "filing-prompt.md").read_text(encoding="utf-8")
    tree = "\n".join(f"{folder}: {scope}" for folder, scope in topics.items())
    style = style_sample()
    in_library = library_arxiv_ids()
    skipped_by_id, skipped_by_title = skipped_index()
    added, left = 0, 0

    for arxiv_id, with_version in wanted.items():
        entry = entries.get(arxiv_id)
        if not entry:
            print(f"{arxiv_id}: not found on arXiv")
            left += 1
            continue
        print(f"{arxiv_id}: {entry['title']}")
        if arxiv_id in in_library:
            print(f"  already in library: {in_library[arxiv_id].relative_to(LIBRARY_DIR)}")
            continue
        skip = skipped_by_id.get(arxiv_id) or skipped_by_title.get(norm_title(entry["title"]))
        if skip:
            print(f"  skipped earlier ({skip.get('date', '')}): {skip['reason']}\n"
                  "  not added; remove it from catalog/skipped.yaml to add it")
            left += 1
            continue
        try:
            reply, _ = ask_model(model, SYSTEM, template.format(
                topics=tree, style=style, title=entry["title"], abstract=entry["abstract"]))
            folder, reason, summary = filing_choice(reply, topics)
        except RuntimeError as error:
            print(f"  not added: {error}")
            left += 1
            continue
        if not folder:
            print(f"  not added: no declared folder fits ({reason})\n"
                  "  use the add-paper skill, which proposes a new folder")
            left += 1
            continue
        print(f"  folder:  {folder} ({reason})\n  summary: {summary}")
        if dry_run:
            continue
        code = subprocess.run([str(SCRIPTS_DIR / "add-arxiv-paper.sh"), with_version, folder]).returncode
        path = library_arxiv_ids().get(arxiv_id)
        if code or not path:
            print("  not added: the add command failed")
            left += 1
            continue
        meta, body = read_paper(path)
        meta["summary"] = summary
        write_paper(path, meta, body)
        added += 1

    broken = added and any(subprocess.run([sys.executable, str(SCRIPTS_DIR / script)]).returncode
                           for script in ("build-index.py", "check-library.py"))
    print(f"add: {added} added, {left} not added" + (" (dry run)" if dry_run else ""))
    sys.exit(1 if left or broken else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
