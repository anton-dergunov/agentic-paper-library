#!/usr/bin/env python3
"""Which tables does the working copy's converter change, against a git ref's?

    uv run python experiments/row-groups-and-continuation-rows/compare.py <library> [--ref HEAD] [--out tables.jsonl]
        [--without pass,...] [--summary summary.tsv]

For every arXiv-HTML paper of the library whose rendering is in the cache, runs the
table passes of html-to-markdown.py (everything before pandoc but the trees and
citations taken from the LaTeX source) with the ref's version and with the working
copy's, and writes one line per table that differs: the paper, the table's caption,
its markdown before and after (pandoc on the table alone) and their lengths in
characters. A LaTeX source is read from the cache only, never downloaded; each paper's
first line says whether the working copy asked for its source, and whether the cache
had it. `--without` leaves the working copy's passes named out (to measure each), and
`--summary` writes the same lines without the tables' text, which is the papers' own.
"""

import argparse
import gzip
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ENGINE / "scripts"))
from paperlib import CACHE_DIR, cache_path  # noqa: E402

PASSES = ["local_links", "clean_math", "drop_invisible", "close_runaway_floats", "drop_style_warnings",
          "split_captions", "tidy_authors", "convert_listings", "span_tabulars_to_tables", "unresolved_refs",
          "drop_undefined_macros", "drop_tex_residue", "fix_text_encoding", "tidy_cells", "merge_continuation_rows",
          "extend_rowspans", "raise_group_labels", "span_group_labels", "source_row_spans", "end_guessed_heads", "span_header_rows",
          "share_panel_labels"]
MODULES = {}


def load(path):
    spec = importlib.util.spec_from_file_location(f"h2m_{len(MODULES)}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tables(module, page):
    article = module.extract_article(page)
    for name in PASSES:
        f = getattr(module, name, None)
        if f is None:
            continue
        if name == "local_links":
            article = f(article, module.paper_version(page))
        elif name == "source_row_spans":
            article = f(article, page)
        else:
            article = f(article)
    out = []
    for m in re.finditer(r"<figure\b[^>]*\bltx_table\b", article):
        end = module.balanced_end(article, m.start(), "figure")
        if end:
            out.append(article[m.start():end])
    return out


def markdown(fragment):
    """The table of a float as the converter writes it, with its own Lua filter."""
    start = fragment.find("<table")
    fragment = fragment[start:fragment.rfind("</table>") + 8] if start >= 0 else fragment
    return subprocess.run(["pandoc", "-f", "html", "-t", "gfm-tex_math_gfm+tex_math_dollars", "--wrap=none",
                           "--lua-filter", str(ENGINE / "scripts" / "arxiv-html.lua")],
                          input=fragment, capture_output=True, text=True).stdout


def compare(job):
    paper, html = job
    old, new = MODULES["old"], MODULES["new"]
    new.asked = None
    page = gzip.decompress(html.read_bytes()).decode("utf-8", "replace")
    try:
        before, after = tables(old, page), tables(new, page)
    except Exception as e:  # a converter crash is a result too
        return [{"paper": paper, "error": repr(e)}]
    if len(before) != len(after):
        return [{"paper": paper, "error": f"{len(before)} tables before, {len(after)} after"}]
    rows = [{"paper": paper, "source": new.asked,
             "cached": bool(new.asked and cache_path(f"https://arxiv.org/e-print/{new.asked}").exists())}]
    for i, (b, a) in enumerate(zip(before, after)):
        if a == b:
            continue
        caption = re.search(r"<figcaption\b.*?</figcaption>", a, re.S)
        mb, ma = markdown(b), markdown(a)
        rows.append({"paper": paper, "table": i, "caption": re.sub(r"<[^>]+>|\s+", " ", caption.group(0)).strip()[:80] if caption else "",
                     "html_before": "<table" in mb, "html_after": "<table" in ma,
                     "chars_before": len(mb), "chars_after": len(ma), "before": mb, "after": ma})
    return rows


def cached_only(url, *args, **kwargs):
    """arXiv downloads from the cache only: a paper whose source is not there has none."""
    path = cache_path(url)
    return gzip.decompress(path.read_bytes()) if path and path.exists() else None


def init(old_path, new_path, without=()):
    MODULES["old"], MODULES["new"] = load(old_path), load(new_path)
    for name in without:
        setattr(MODULES["new"], name, lambda article, *rest: article)
    for module in MODULES.values():
        module.fetch = cached_only
        latex_source = module.latex_source

        def asked(version, latex_source=latex_source, module=module):
            module.asked = version
            return latex_source(version)
        module.latex_source = asked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("library")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--out", default="tables.jsonl")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--without", default="")
    ap.add_argument("--summary")
    args = ap.parse_args()
    jobs = []
    for md in sorted(Path(args.library, "library").rglob("*.md")):
        head = md.read_text(encoding="utf-8")[:3000]
        if md.name == "README.md" or "\nsource: html" not in head:
            continue
        arxiv = re.search(r"\narxiv: '?([\d.]+)", head)
        versions = sorted((CACHE_DIR / "arxiv" / "html").glob(f"{arxiv.group(1)}v*/index.html.gz") if arxiv else [],
                          key=lambda p: int(p.parent.name.rpartition("v")[2]))
        if versions:
            jobs.append((str(md.relative_to(Path(args.library, "library"))), versions[-1]))
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(subprocess.run(["git", "-C", ENGINE, "show", f"{args.ref}:scripts/html-to-markdown.py"],
                               capture_output=True, text=True, check=True).stdout)
    old_path = f.name
    n = 0
    with open(args.out, "w", encoding="utf-8") as out, ProcessPoolExecutor(
            args.jobs, initializer=init,
            initargs=(old_path, ENGINE / "scripts" / "html-to-markdown.py", [w for w in args.without.split(",") if w])) as pool:
        for rows in pool.map(compare, jobs, chunksize=4):
            for row in rows:
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                n += "table" in row
    print(f"{len(jobs)} papers, {n} tables changed -> {args.out}")
    if args.summary:
        keys = ["paper", "table", "caption", "html_before", "html_after", "chars_before", "chars_after"]
        with open(args.out, encoding="utf-8") as rows, open(args.summary, "w", encoding="utf-8") as out:
            out.write("\t".join(keys) + "\n")
            for row in map(json.loads, rows):
                if "table" in row and row["before"] != row["after"]:
                    out.write("\t".join(str(row[k]) for k in keys) + "\n")


if __name__ == "__main__":
    main()
