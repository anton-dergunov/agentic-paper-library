#!/usr/bin/env python3
"""How tables use cell shading, over every cached arXiv rendering.

    uv run python shading.py [<cache>/arxiv/html] > shading.tsv

One row per table float with a shaded cell, classified by the converter's own
functions (shaded_cells, shading_pattern in scripts/html-to-markdown.py): the
paper, the float's id, the pattern, shaded and all cells, the number of
shading colours, whether the caption refers to a colour or to shading, and the
<mark>s the rules "caption" and "all" would write. The summary goes to stderr.
"""

import collections
import gzip
import importlib.util
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("html_to_markdown", SCRIPTS / "html-to-markdown.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


def main(cache):
    print("paper\tfloat\tpattern\tshaded cells\tcells\tcolours\tcaption names it\tmarks, caption rule\tmarks, all rule")
    patterns, papers, named = collections.Counter(), collections.defaultdict(set), collections.Counter()
    marks = collections.Counter()
    marked_papers = collections.defaultdict(set)
    floats = pages = 0
    for path in sorted(cache.glob("*/index.html.gz")):
        page = gzip.open(path, "rt", encoding="utf-8", errors="replace").read()
        try:
            article = converter.span_tabulars_to_tables(converter.extract_article(page))
        except SystemExit:
            continue
        pages += 1
        for m in converter.TABLE_FLOAT.finditer(article):
            end = converter.balanced_end(article, m.start(), "figure")
            if end is None:
                continue
            floats += 1
            body = article[m.start():end]
            rows = [[shaded for _, _, shaded in row] for row in converter.shaded_cells(body)]
            if not any(map(any, rows)):
                continue
            kind = converter.shading_pattern(rows)
            caption = converter.cell_text(" ".join(re.findall(r"<figcaption\b.*?</figcaption>", body, re.S))).lower()
            says = bool(converter.NAMES_SHADING.search(caption))
            colours = len(set(c.lower() for c in re.findall(r"--ltx-bg-color:\s*(#[0-9A-Fa-f]{6})", body)))
            by_rule = {rule: converter.mark_shading(body, rule).count("<mark>") for rule in ("caption", "all")}
            patterns[kind] += 1
            papers[kind].add(path.parent.name)
            named[kind] += says
            for rule, n in by_rule.items():
                marks[rule] += n
                marks[rule + " tables"] += n > 0
                if n:
                    marked_papers[rule].add(path.parent.name)
            float_id = re.search(r'\bid="([^"]+)"', m.group(0))
            print(f"{path.parent.name}\t{float_id.group(1) if float_id else ''}\t{kind}\t{sum(map(sum, rows))}"
                  f"\t{sum(map(len, rows))}\t{colours}\t{'yes' if says else 'no'}\t{by_rule['caption']}\t{by_rule['all']}")
    every = set().union(*papers.values()) if papers else set()
    print(f"{pages} renderings, {floats} table floats; {sum(patterns.values())} with shaded cells in {len(every)} papers",
          file=sys.stderr)
    for kind, n in patterns.most_common():
        print(f"  {kind:16} {n:5} tables {len(papers[kind]):4} papers, caption names it in {named[kind]}", file=sys.stderr)
    for rule in ("caption", "all"):
        print(f"  rule {rule!r}: {marks[rule]} marks in {marks[rule + ' tables']} tables of {len(marked_papers[rule])} papers",
              file=sys.stderr)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "~/.cache/papers/arxiv/html").expanduser())
