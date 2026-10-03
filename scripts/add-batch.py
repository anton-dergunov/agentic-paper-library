#!/usr/bin/env python3
"""Add the papers of a reviewed reading list, one at a time.

    ./scripts/add-batch.py <list.tsv> [--limit N]

<list.tsv> has one paper per line, tab-separated, no header:

    number, arxiv id, url, title, year, folder, source, status

The last two columns may be missing. A paper with an arXiv id goes through
add-arxiv-paper.sh. Without one, `source` says how to add it: `web` runs
add-web-article.py on its url, a path to a PDF runs add-pdf-paper.sh with the
url as its source. Rows without either are marked `needs a PDF`; fill in their
source and run again.

Rows whose status is `added`, `in library` or `struck` are left alone; every
other row is tried, so a rerun resumes an interrupted batch and retries the
failures. Each row's status becomes `added`, `in library`, `needs a PDF` or
`failed: <last line of output>`, saved after every paper. Summaries are not
written here (see pending-summaries.py); rebuild the indexes and check the
library after the batch.
"""

import subprocess
import sys
import time
from pathlib import Path

from paperlib import LIBRARY_DIR, LIBRARY_ROOT, SCRIPTS_DIR, library_arxiv_ids, norm_title, paper_files, read_paper, write_paper

COLUMNS = ["number", "arxiv", "url", "title", "year", "folder", "source", "status"]
DONE = {"added", "in library", "struck"}


def load(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cells = (line.split("\t") + [""] * len(COLUMNS))[:len(COLUMNS)]
            rows.append(dict(zip(COLUMNS, (c.strip() for c in cells))))
    return rows


def save(path, rows):
    lines = ["\t".join(r[c] for c in COLUMNS).rstrip("\t") for r in rows]
    tmp = path.with_suffix(".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp.replace(path)


def command(row):
    script = SCRIPTS_DIR
    if row["arxiv"]:
        return [str(script / "add-arxiv-paper.sh"), row["arxiv"], row["folder"]]
    if row["source"] == "web" and row["url"]:
        return [str(script / "add-web-article.py"), row["url"], row["folder"], "--title", row["title"]]
    if row["source"] and row["source"] != "web":
        cmd = [str(script / "add-pdf-paper.sh"), str(Path(row["source"]).expanduser()), row["folder"],
               "--title", row["title"]]
        return cmd + (["--source", row["url"]] if row["url"] else [])
    return None


def set_year(stdout, row):
    """A paper added from a PDF has no date; take the year from the list."""
    lines = [l.strip() for l in stdout.splitlines() if l.strip().endswith(".md")]
    if not lines or not row["year"].isdigit():
        return
    md = Path(lines[-1])
    md = md if md.is_absolute() else LIBRARY_ROOT / md
    if md.exists() and LIBRARY_DIR in md.parents:
        meta, body = read_paper(md)
        if not meta.get("published"):
            meta["published"] = int(row["year"])
            write_paper(md, meta, body)


def main(argv):
    limit = None
    if "--limit" in argv:
        i = argv.index("--limit")
        limit = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 1:
        sys.exit(__doc__)
    path = Path(argv[0])
    rows = load(path)
    lib_ids = set(library_arxiv_ids())
    lib_titles = {norm_title(read_paper(md)[0].get("title")) for md in paper_files()}

    counts = dict.fromkeys(["added", "in library", "needs a PDF", "failed"], 0)
    tried = 0
    for row in rows:
        if row["status"] in DONE:
            continue
        if limit is not None and tried >= limit:
            break
        if row["arxiv"] in lib_ids or norm_title(row["title"]) in lib_titles:
            row["status"] = "in library"
        elif (cmd := command(row)) is None:
            row["status"] = "needs a PDF"
        else:
            tried += 1
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=LIBRARY_ROOT)
            out = (result.stdout + result.stderr).strip().splitlines()
            if result.returncode == 0:
                row["status"] = "added"
                if not row["arxiv"]:
                    set_year(result.stdout, row)
                note = next((l for l in out if "falling back" in l), "")
                print(f"added   {row['folder']}: {row['title'][:70]}" + (f"  [{note}]" if note else ""),
                      flush=True)
            else:
                row["status"] = "failed: " + (out[-1] if out else f"exit {result.returncode}")[:200]
                print(f"FAILED  {row['folder']}: {row['title'][:70]}\n        {row['status']}", flush=True)
            if row["arxiv"]:
                time.sleep(3)  # the arXiv export API asks for a pause between requests
        counts[row["status"].split(":")[0]] += 1
        save(path, rows)

    print("\n" + ", ".join(f"{k} {v}" for k, v in counts.items()))
    for row in rows:
        if row["status"] == "needs a PDF":
            print(f"  needs a PDF: #{row['number']} {row['title']}  {row['url']}")


if __name__ == "__main__":
    main(sys.argv[1:])
