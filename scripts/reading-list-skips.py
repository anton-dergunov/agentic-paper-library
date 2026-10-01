#!/usr/bin/env python3
"""Record what a reviewed reading list leaves out in catalog/skipped.yaml.

    ./scripts/reading-list-skips.py <list.md> [--strike 3,7,12-15] [--reason "..."] [--write]

Reads <list.md> and the <list.tsv> next to it. Papers struck by number go to
skipped.yaml with --reason (or a default naming the list), and their status in
the TSV becomes `struck`, so add-batch.py passes them over. The rows of the
"Considered, not proposed" table go to skipped.yaml with the table's "Why not";
their titles come from arXiv where there is an id.

Papers already in the library or in skipped.yaml are left out, and so is a
considered paper that any list in the same folder proposes, so a rerun records
nothing twice. Without --write it only prints what it would do.
"""

import datetime
import re
import sys
from pathlib import Path

import yaml

from paperlib import (
    SKIPPED_FILE, fetch, library_arxiv_ids, load_topics, norm_title, paper_files,
    parse_arxiv_entries, read_paper, skipped_index,
)

ARXIV_ID = re.compile(r"\b(\d{4}\.\d{4,5})\b")
URL = re.compile(r"https?://\S+")
COLUMNS = ["number", "arxiv", "url", "title", "year", "folder", "source", "status"]


class NoAliases(yaml.SafeDumper):
    """Write the shared date in full each time: appended anchors would clash."""

    def ignore_aliases(self, data):
        return True


def parse_numbers(spec):
    out = set()
    for part in filter(None, (p.strip() for p in spec.split(","))):
        lo, _, hi = part.partition("-")
        out.update(range(int(lo), int(hi or lo) + 1))
    return out


def proposed(tsv):
    rows = []
    for line in tsv.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cells = (line.split("\t") + [""] * len(COLUMNS))[:len(COLUMNS)]
            rows.append(dict(zip(COLUMNS, (c.strip() for c in cells))))
    return rows


def considered(md):
    """Rows of the "Considered, not proposed" table: (title, year, ids cell, folder, why)."""
    section = md.read_text(encoding="utf-8").split("## Considered, not proposed", 1)
    if len(section) < 2:
        return []
    rows = []
    for line in section[1].splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and cells[0] not in ("Paper", "") and not set(cells[0]) <= set("-:"):
            rows.append(cells)
    return rows


def split_titles(title, n):
    """Pair a merged row's titles with its n ids, when they can be paired."""
    if n <= 1:
        return [title]
    for sep in ("; ", " / ", ", "):
        parts = [p.strip() for p in title.split(sep)]
        if len(parts) == n:
            return parts
    return [title] * n


def nearest_topic(folder, topics):
    while folder and folder not in topics:
        folder = folder.rpartition("/")[0]
    return folder or None


def arxiv_titles(ids):
    out = {}
    ids = sorted(ids)
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        data = fetch(f"https://export.arxiv.org/api/query?id_list={','.join(chunk)}"
                     f"&max_results={len(chunk)}", attempts=5)
        if data and b"<entry" in data:
            out.update({k: v["title"] for k, v in parse_arxiv_entries(data.decode()).items()})
    return out


def main(argv):
    write = "--write" in argv
    argv = [a for a in argv if a != "--write"]
    strike, reason = set(), None
    if "--strike" in argv:
        i = argv.index("--strike")
        strike = parse_numbers(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if "--reason" in argv:
        i = argv.index("--reason")
        reason = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 1:
        sys.exit(__doc__)
    md = Path(argv[0])
    tsv = md.with_suffix(".tsv")
    reason = reason or f"Struck by Anton from the {md.stem} reading list"
    today = datetime.date.today()

    topics = load_topics()
    lib_ids = set(library_arxiv_ids())
    lib_titles = {norm_title(read_paper(p)[0].get("title")) for p in paper_files()}
    skip_ids, skip_titles = skipped_index()

    def known(arxiv, title):
        return (arxiv and (arxiv in lib_ids or arxiv in skip_ids)
                or norm_title(title) in lib_titles or norm_title(title) in skip_titles)

    rows = proposed(tsv)
    unknown = strike - {int(r["number"]) for r in rows}
    if unknown:
        sys.exit(f"--strike names numbers not in the list: {sorted(unknown)}")
    skips = []
    for r in rows:
        if int(r["number"]) not in strike:
            continue
        r["status"] = "struck"
        if not known(r["arxiv"], r["title"]):
            skips.append(dict(title=r["title"], arxiv=r["arxiv"] or None, url=r["url"] or None,
                              year=int(r["year"]) if r["year"].isdigit() else None,
                              topic=nearest_topic(r["folder"], topics), reason=reason, date=today))

    # A paper another list proposes is not skipped here, whichever list is reviewed first.
    every_list = [r for other in md.parent.glob("*.tsv") for r in proposed(other)]
    proposed_ids = {r["arxiv"] for r in every_list if r["arxiv"]}
    proposed_titles = {norm_title(r["title"]) for r in every_list}
    cons = considered(md)
    real_titles = arxiv_titles({i for c in cons for i in ARXIV_ID.findall(c[2])} - proposed_ids)
    for title, year, ids_cell, folder, why_not in cons:
        ids = ARXIV_ID.findall(ids_cell)
        urls = URL.findall(ids_cell)
        m = re.search(r"\d{4}", year)
        for part, arxiv in zip(split_titles(title, len(ids)), ids or [None]):
            name = real_titles.get(arxiv, part)
            if arxiv in proposed_ids or norm_title(name) in proposed_titles or known(arxiv, name):
                continue
            skips.append(dict(title=name, arxiv=arxiv, url=None if arxiv else (urls[0] if urls else None),
                              year=int(m.group()) if m else None, topic=nearest_topic(folder, topics),
                              reason=why_not, date=today))
            skip_titles[norm_title(name)] = True
            if arxiv:
                skip_ids[arxiv] = True

    print(f"{md.stem}: {len(rows)} proposed, {len(strike)} struck, {len(cons)} considered rows")
    print(f"  to skipped.yaml: {len(skips)}")
    if not write:
        for s in skips:
            print(f"    skip {s['arxiv'] or s['url'] or '-'}  {s['title']}  [{s['topic']}]")
        print("dry run; pass --write to save")
        return
    if strike:
        lines = ["\t".join(r[c] for c in COLUMNS).rstrip("\t") for r in rows]
        tsv.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if skips:
        entries = [{k: v for k, v in s.items() if v is not None} for s in skips]
        with SKIPPED_FILE.open("a", encoding="utf-8") as f:
            f.write(yaml.dump(entries, Dumper=NoAliases, sort_keys=False, allow_unicode=True,
                              width=100))
    print("saved")


if __name__ == "__main__":
    main(sys.argv[1:])
