#!/usr/bin/env python3
"""Turn a reviewed reading list into inventory rows and skip records.

    python3 docs/tasks/library-expansion/import_reading_list.py <area>
            [--strike 3,7,12-15] [--reason "..."] [--write]

Reads reading-lists/<area>.tsv and <area>.md. Every proposed paper not struck
becomes an inventory.tsv row with action `add`, status `todo`, sources
`literature-pass:<area>` and the list's folder as topic, keyed `arxiv:<id>` or
`title:<normalised title>`; add_batch.py then adds it. Struck papers and the
"Considered, not proposed" table go to catalog/skipped.yaml, with --reason (or
a default) for struck ones and the list's "Why not" for the others; their
titles come from arXiv where there is an id.

Papers already in the inventory, the library or skipped.yaml are left out, so a
rerun adds nothing twice; a considered paper that any list proposes is not skipped. Without --write it only prints what it would do.
"""

import csv
import datetime
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from paperlib import (  # noqa: E402
    SKIPPED_FILE, fetch, library_arxiv_ids, load_topics, norm_title, paper_files,
    parse_arxiv_entries, read_paper, skipped_index,
)

INVENTORY = HERE / "inventory.tsv"
LISTS = HERE / "reading-lists"
ARXIV_ID = re.compile(r"\b(\d{4}\.\d{4,5})\b")
URL = re.compile(r"https?://\S+")


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


def proposed(area):
    rows = []
    for line in (LISTS / f"{area}.tsv").read_text().splitlines():
        if line.strip():
            num, arxiv, url, title, year, folder = (line.split("\t") + [""] * 6)[:6]
            rows.append(dict(num=int(num), arxiv=arxiv.strip(), url=url.strip(),
                             title=title.strip(), year=year.strip(), folder=folder.strip()))
    return rows


def considered(area):
    """Rows of the "Considered, not proposed" table: (title, year, ids cell, folder, why)."""
    text = (LISTS / f"{area}.md").read_text()
    section = text.split("## Considered, not proposed", 1)
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
    area = argv[0]
    reason = reason or f"Struck by Anton from the {area} reading list"
    today = datetime.date.today()

    topics = load_topics()
    with INVENTORY.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        fields, inventory = reader.fieldnames, list(reader)
    inv_keys = {r["key"] for r in inventory}
    inv_ids = {r["arxiv"] for r in inventory if r["arxiv"]}
    inv_titles = {norm_title(r["title"]) for r in inventory}
    lib_ids = set(library_arxiv_ids())
    lib_titles = {norm_title(read_paper(md)[0].get("title")) for md in paper_files()}
    skip_ids, skip_titles = skipped_index()

    def known(arxiv, title):
        """Why a paper is left out, or None when it is new."""
        if arxiv and arxiv in lib_ids or norm_title(title) in lib_titles:
            return "in library"
        if arxiv and arxiv in skip_ids or norm_title(title) in skip_titles:
            return "skipped earlier"
        if arxiv and arxiv in inv_ids or norm_title(title) in inv_titles:
            return "in inventory"
        return None

    rows = proposed(area)
    unknown = strike - {r["num"] for r in rows}
    if unknown:
        sys.exit(f"--strike names numbers not in the list: {sorted(unknown)}")
    new_rows, skips, left_out = [], [], []
    for r in rows:
        why = known(r["arxiv"], r["title"])
        if why:
            left_out.append(f"  {r['num']:>3}  {why}: {r['title']}")
            continue
        if r["folder"] not in topics:
            sys.exit(f"#{r['num']} {r['title']}: undeclared folder {r['folder']}")
        if r["num"] in strike:
            skips.append(dict(title=r["title"], arxiv=r["arxiv"] or None, url=r["url"] or None,
                              year=int(r["year"]) if r["year"].isdigit() else None,
                              topic=r["folder"], reason=reason, date=today))
            continue
        key = f"arxiv:{r['arxiv']}" if r["arxiv"] else f"title:{norm_title(r['title'])}"
        if key in inv_keys:
            left_out.append(f"  {r['num']:>3}  in inventory: {r['title']}")
            continue
        row = dict.fromkeys(fields, "")
        row.update(key=key, title=r["title"], year=r["year"], arxiv=r["arxiv"],
                   url=r["url"] or (f"https://arxiv.org/abs/{r['arxiv']}" if r["arxiv"] else ""),
                   sources=f"literature-pass:{area}", topic=r["folder"], action="add",
                   status="todo")
        new_rows.append(row)
        inv_keys.add(key)

    # A paper another list proposes is not skipped here, whichever list is imported first.
    every_list = [r for tsv in LISTS.glob("*.tsv") for r in proposed(tsv.stem)]
    proposed_ids = {r["arxiv"] for r in every_list if r["arxiv"]}
    proposed_titles = {norm_title(r["title"]) for r in every_list}
    cons = considered(area)
    real_titles = arxiv_titles({i for c in cons for i in ARXIV_ID.findall(c[2])} - proposed_ids)
    for title, year, ids_cell, folder, why_not in cons:
        ids = ARXIV_ID.findall(ids_cell)
        urls = URL.findall(ids_cell)
        m = re.search(r"\d{4}", year)
        topic = nearest_topic(folder, topics)
        for part, arxiv in zip(split_titles(title, len(ids)), ids or [None]):
            name = real_titles.get(arxiv, part)
            if arxiv in proposed_ids or norm_title(name) in proposed_titles or known(arxiv, name):
                continue
            skips.append(dict(title=name, arxiv=arxiv, url=None if arxiv else (urls[0] if urls else None),
                              year=int(m.group()) if m else None, topic=topic,
                              reason=why_not, date=today))
            skip_titles[norm_title(name)] = True
            if arxiv:
                skip_ids[arxiv] = True

    print(f"{area}: {len(rows)} proposed, {len(strike)} struck, {len(cons)} considered rows")
    print(f"  to inventory: {len(new_rows)}")
    print(f"  to skipped.yaml: {len(skips)}")
    if left_out:
        print("  left out of the inventory:\n" + "\n".join(left_out))
    if not write:
        for s in skips:
            print(f"    skip {s['arxiv'] or s['url'] or '-'}  {s['title']}  [{s['topic']}]")
        print("dry run; pass --write to save")
        return
    if new_rows:
        with INVENTORY.open("a", newline="") as f:
            csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n").writerows(new_rows)
    if skips:
        entries = [{k: v for k, v in s.items() if v is not None} for s in skips]
        with SKIPPED_FILE.open("a", encoding="utf-8") as f:
            f.write(yaml.dump(entries, Dumper=NoAliases, sort_keys=False, allow_unicode=True,
                              width=100))
    print("saved")


if __name__ == "__main__":
    main(sys.argv[1:])
