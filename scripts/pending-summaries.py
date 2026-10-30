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

import sys
from pathlib import Path

from paperlib import LIBRARY_DIR, paper_abstracts, paper_index, read_paper


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

    abstracts = paper_abstracts(paper for paper, _, _ in pending)

    blocks = []
    for n, (md, meta, body) in enumerate(pending, 1):
        abstract = abstracts[md]
        blocks.append(f"### {n}\nfile: {md.relative_to(LIBRARY_DIR)}\ntitle: {meta.get('title')}\n"
                      f"abstract: {abstract}\n")
    out.write_text("\n".join(blocks), encoding="utf-8")
    print(f"{len(pending)} papers need a summary -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
