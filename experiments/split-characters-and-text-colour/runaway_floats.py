#!/usr/bin/env python3
"""Which cached arXiv renderings have a float that swallowed later sections.

    uv run python runaway_floats.py [<cache>/arxiv/html] > runaway-floats.tsv

One row per paper that close_runaway_floats (scripts/html-to-markdown.py)
changes: the paper and the floats it closes early.
"""

import gzip
import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("html_to_markdown", SCRIPTS / "html-to-markdown.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


def main(cache):
    print("paper\tfloats closed early")
    papers = 0
    for path in sorted(Path(cache).glob("*/index.html.gz")):
        papers += 1
        html = gzip.open(path, "rt", encoding="utf-8", errors="replace").read()
        closed = converter.close_runaway_floats(html).count("</figure><section") - html.count("</figure><section")
        if closed:
            print(f"{path.parent.name}\t{closed}")
    print(f"{papers} renderings", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else Path.home() / ".cache/papers/arxiv/html")
