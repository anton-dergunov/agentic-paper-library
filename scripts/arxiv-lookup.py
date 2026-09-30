#!/usr/bin/env python3
"""Look papers up on arXiv before adding them: metadata, abstract, and whether
the library already has them.

    ./scripts/arxiv-lookup.py <arxiv-id-or-url> [...]
    ./scripts/arxiv-lookup.py --title "words from the title" [--title ...]
    ./scripts/arxiv-lookup.py --no-abstract ...

Ids and URLs (abs/, pdf/, html/, with or without a version) go to the export
API in one request. Each --title is a separate search that prints its best
matches, since a title can match several papers. For every paper it prints the
id and latest version, the publication date, the title, where it already is in
the library if it is, whether it was skipped earlier (catalog/skipped.yaml) and
why, and the abstract.
"""

import re
import sys
import textwrap
import time
from urllib.parse import quote

from paperlib import LIBRARY_DIR, fetch, library_arxiv_ids, norm_title, parse_arxiv_entries, skipped_index

API = "https://export.arxiv.org/api/query"
ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5})(?:v\d+)?")
STOP_WORDS = set("the and for with from into via are its our their this that not can how what when why who".split())


def query(params):
    data = fetch(f"{API}?{params}", attempts=5)
    if data is None or b"<entry" not in data:
        return None
    return parse_arxiv_entries(data.decode("utf-8"))


def show(arxiv_id, entry, in_library, skipped, abstract):
    version = f"v{entry['version']}" if entry.get("version") else ""
    print(f"{arxiv_id}{version} | {entry['published']} | {entry['title']}")
    if arxiv_id in in_library:
        print(f"  already in library: {in_library[arxiv_id].relative_to(LIBRARY_DIR)}")
    by_id, by_title = skipped
    skip = by_id.get(arxiv_id) or by_title.get(norm_title(entry["title"]))
    if skip:
        print(f"  skipped earlier ({skip.get('date', '')}): {skip['reason']}")
    if abstract:
        print(textwrap.indent(textwrap.fill(entry["abstract"], 100), "  "))
    print()


def main(argv):
    abstract = "--no-abstract" not in argv
    args = [a for a in argv if a != "--no-abstract"]
    titles, ids = [], []
    while args:
        arg = args.pop(0)
        if arg == "--title" and args:
            titles.append(args.pop(0))
        elif ARXIV_ID.search(arg):
            ids.append(ARXIV_ID.search(arg).group(1))
        else:
            sys.exit(f"error: not an arXiv id or URL: {arg}\n\n{__doc__}")
    if not ids and not titles:
        sys.exit(__doc__)

    in_library = library_arxiv_ids()
    skipped = skipped_index()
    failed = False

    if ids:
        entries = query(f"id_list={','.join(dict.fromkeys(ids))}&max_results={len(ids)}")
        if entries is None:
            print("error: arXiv export API gave no usable response", file=sys.stderr)
            failed = True
        else:
            for arxiv_id in dict.fromkeys(ids):
                if arxiv_id in entries:
                    show(arxiv_id, entries[arxiv_id], in_library, skipped, abstract)
                else:
                    print(f"{arxiv_id} | not found on arXiv\n")
                    failed = True

    for title in titles:
        if ids or title is not titles[0]:
            time.sleep(3)  # the export API asks for a pause between requests
        # The whole title as a phrase first; for a loose or partial title, all
        # its content words. Stop words make an AND search match nothing.
        words = re.findall(r"\w+", title)
        entries = query(f"search_query=ti:%22{'+'.join(quote(w) for w in words)}%22&max_results=5")
        if not entries:
            time.sleep(3)
            content = [w for w in words if len(w) > 2 and w.lower() not in STOP_WORDS]
            entries = query(f"search_query={'+AND+'.join(f'ti:{quote(w)}' for w in content)}&max_results=5")
        print(f"== title search: {title}\n")
        if not entries:
            print("  no matches\n")
            failed = True
            continue
        for arxiv_id, entry in entries.items():
            show(arxiv_id, entry, in_library, skipped, abstract)

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
