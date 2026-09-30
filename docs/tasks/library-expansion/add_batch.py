#!/usr/bin/env python3
"""Add the inventory's `add` rows under one or more topics, one paper at a time.

    python3 docs/tasks/library-expansion/add_batch.py <topic-prefix> [...] [--limit N]
                                                      [--pdfs <map.tsv>]

For each row with action `add` and status `todo` whose topic starts with a given
prefix: an arXiv paper goes through scripts/add-arxiv-paper.sh, a paper with only
a local PDF in Papers_old/ through scripts/add-pdf-paper.sh. Rows with neither
are left `todo` and listed at the end: they need a PDF from the web. Once
found, pass them with --pdfs: a TSV of `<key>\t<pdf path>\t<source url>` lines
(key as in inventory.tsv). Each row's
status becomes `added`, or `failed: <last line of output>`, and inventory.tsv is
saved after every paper so an interrupted run resumes where it stopped.

Summaries are not written here; see pending_summaries.py. Rebuild the indexes
and check the library after the batch.
"""

import csv
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from paperlib import LIBRARY_DIR, read_paper, write_paper  # noqa: E402

INVENTORY = HERE / "inventory.tsv"
PAPERS_OLD = Path.home() / "Yandex.Disk.localized" / "Papers_old"


def load():
    with INVENTORY.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        return reader.fieldnames, list(reader)


def save(fields, rows):
    tmp = INVENTORY.with_suffix(".tmp")
    with tmp.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(INVENTORY)


def command(row, pdf_map):
    if row["key"] in pdf_map:
        path, url = pdf_map[row["key"]]
        cmd = [str(REPO / "scripts/add-pdf-paper.sh"), path, row["topic"], "--title", row["title"]]
        return cmd + (["--source", url or row["url"]] if (url or row["url"]) else [])
    if row["arxiv"]:
        return [str(REPO / "scripts/add-arxiv-paper.sh"), row["arxiv"], row["topic"]]
    pdfs = [PAPERS_OLD / f"{stem}.pdf" for stem in row["local_pdf"].split("; ") if stem]
    pdfs = [p for p in pdfs if p.exists()]
    if pdfs:
        cmd = [str(REPO / "scripts/add-pdf-paper.sh"), str(pdfs[0]), row["topic"], "--title", row["title"]]
        if row["url"]:
            cmd += ["--source", row["url"]]
        return cmd
    return None


def set_year(out, row):
    """A paper added from a local PDF has no date; take the year from the inventory."""
    if row["arxiv"] or not row["year"]:
        return
    md = Path(out[-1].strip()) if out and out[-1].strip().endswith(".md") else None
    if md and not md.is_absolute():
        md = REPO / md
    if md and md.exists() and LIBRARY_DIR in md.parents:
        meta, body = read_paper(md)
        if not meta.get("published"):
            meta["published"] = int(row["year"])
            write_paper(md, meta, body)


def main(argv):
    limit, pdf_map = None, {}
    if "--pdfs" in argv:
        i = argv.index("--pdfs")
        for line in Path(argv[i + 1]).read_text().splitlines():
            key, path, url = (line.split("\t") + ["", ""])[:3]
            pdf_map[key] = (path, url)
        argv = argv[:i] + argv[i + 2:]
    if "--limit" in argv:
        i = argv.index("--limit")
        limit = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if not argv:
        sys.exit(__doc__)
    fields, rows = load()
    todo = [r for r in rows if r["action"] == "add" and r["status"] == "todo"
            and any(r["topic"] == p or r["topic"].startswith(p.rstrip("/") + "/") for p in argv)]
    web, done, failed = [], 0, 0
    for row in todo:
        if limit is not None and done + failed >= limit:
            break
        cmd = command(row, pdf_map)
        if cmd is None:
            web.append(row)
            continue
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
        out = (result.stdout + result.stderr).strip().splitlines()
        if result.returncode == 0:
            row["status"] = "added"
            set_year(result.stdout.strip().splitlines(), row)
            done += 1
            note = next((l for l in out if "falling back" in l or l.startswith("skip (exists)")), "")
            print(f"added   {row['topic']}: {row['title'][:70]}" + (f"  [{note}]" if note else ""), flush=True)
        else:
            row["status"] = "failed: " + (out[-1] if out else f"exit {result.returncode}")[:200]
            failed += 1
            print(f"FAILED  {row['topic']}: {row['title'][:70]}\n        {row['status']}", flush=True)
        save(fields, rows)
        if row["arxiv"]:
            time.sleep(3)  # the arXiv export API asks for a pause between requests
    print(f"\nadded {done}, failed {failed}, need a PDF from the web {len(web)}")
    for row in web:
        print(f"  web: {row['topic']}: {row['title']}  {row['url']}")


if __name__ == "__main__":
    main(sys.argv[1:])
