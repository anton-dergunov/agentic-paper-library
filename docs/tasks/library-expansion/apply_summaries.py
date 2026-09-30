#!/usr/bin/env python3
"""Write summaries back into the papers.

    python3 docs/tasks/library-expansion/apply_summaries.py <pending.md> <summaries.tsv>

<summaries.tsv> has one line per paper, `<number>\\t<summary>`, numbered as in
the <pending.md> file from pending_summaries.py. Papers that already have a
summary are left alone.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
from paperlib import LIBRARY_DIR, read_paper, write_paper  # noqa: E402


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    files = dict(re.findall(r"^### (\d+)\nfile: (.+)$", Path(argv[0]).read_text(encoding="utf-8"), re.M))
    written, problems = 0, []
    for line in Path(argv[1]).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        n, _, summary = line.partition("\t")
        summary = " ".join(summary.split())
        if n.strip() not in files or not summary:
            problems.append(line[:80])
            continue
        path = LIBRARY_DIR / files[n.strip()]
        meta, body = read_paper(path)
        if meta.get("summary"):
            continue
        meta["summary"] = summary
        write_paper(path, meta, body)
        written += 1
    print(f"{written} summaries written")
    for p in problems:
        print(f"  not applied: {p}")


if __name__ == "__main__":
    main(sys.argv[1:])
