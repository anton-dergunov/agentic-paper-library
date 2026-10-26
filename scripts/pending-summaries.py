#!/usr/bin/env python3
"""Collect the papers that still need a summary, with their abstracts.

    ./scripts/pending-summaries.py <out.md> [<topic-prefix> ...]

Writes one numbered block per paper with an empty `summary:` (under the given
topics, or anywhere): its path, title and abstract. Abstracts of arXiv papers
come from the export API, 100 per request; the others are read from the
paper's own text (the Abstract, or the opening text of its first page). The file is what a
summary writer reads instead of the papers; apply-summaries.py takes the
numbered answers back.
"""

import re
import sys
import time
from pathlib import Path

from paperlib import LIBRARY_DIR, PAGE_MARK, fetch, paper_index, parse_arxiv_entries, read_paper

API = "https://export.arxiv.org/api/query"


def abstract_from_body(body):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)|<[^>]+>", " ", body)
    text = PAGE_MARK.sub("", "\n".join(l for l in text.splitlines() if not l.startswith(">")))  # a web article's note
    m = re.search(r"^#+\s*Abstract[^\n]*\n(.*?)(?=^#+\s|\Z)", text, re.S | re.M | re.I)
    if not m:  # a text layer: an "Abstract" / "ABSTRACT" word opening a line, near the start
        m = re.search(r"^\W*(?:Abstract|ABSTRACT)\b[.:—-]?\s*(.*)", text[:8000], re.S | re.M)
    chunk = m.group(1) if m else text
    return " ".join(chunk.split())[:1500]


def main(argv):
    if not argv:
        sys.exit(__doc__)
    out, prefixes = Path(argv[0]), argv[1:]
    pending = []
    for paper, indexed in paper_index().items():
        topic = paper.parent.relative_to(LIBRARY_DIR).as_posix()
        if prefixes and not any(topic == p or topic.startswith(p.rstrip("/") + "/") for p in prefixes):
            continue
        if not indexed.get("summary"):
            meta, body = read_paper(paper)
            pending.append((paper, meta, body))

    ids = [str(m["arxiv"]) for _, m, _ in pending if m.get("arxiv")]
    abstracts = {}
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        data = fetch(f"{API}?id_list={','.join(chunk)}&max_results={len(chunk)}", attempts=5)
        if data:
            abstracts.update({k: v["abstract"] for k, v in parse_arxiv_entries(data.decode()).items()})
        time.sleep(3)

    blocks = []
    for n, (md, meta, body) in enumerate(pending, 1):
        abstract = abstracts.get(str(meta.get("arxiv"))) or abstract_from_body(body)
        blocks.append(f"### {n}\nfile: {md.relative_to(LIBRARY_DIR)}\ntitle: {meta.get('title')}\n"
                      f"abstract: {abstract}\n")
    out.write_text("\n".join(blocks), encoding="utf-8")
    print(f"{len(pending)} papers need a summary -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
