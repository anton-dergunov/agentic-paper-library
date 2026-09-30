#!/usr/bin/env python3
"""Regenerate papers' markdown from arXiv's HTML with the current converter.

    ./scripts/reconvert.py <paper.md> [<paper.md> ...]
    ./scripts/reconvert.py --all
    ./scripts/reconvert.py --all --force     # also papers marked hand-edited

For when the conversion improves: the frontmatter (summary included) and the
PDF are kept; the body and the paper's images/ files are regenerated. The HTML
is fetched at the arXiv version printed on the PDF's first page, so headings
get page numbers from the PDF actually being read. Papers converted from PDF
text are skipped, as are papers containing `<!-- hand-edited -->`, since a
reconversion would drop the edit.
"""

import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pymupdf

from paperlib import fetch, paper_files, pdf_path_for, read_paper, write_paper

SCRIPTS = Path(__file__).resolve().parent
HAND_EDITED = "<!-- hand-edited -->"


def pdf_version(pdf, arxiv_id):
    """The arXiv version stamped in the PDF's margin, e.g. 'v2', or ''."""
    try:
        text = pymupdf.open(pdf)[0].get_text()
    except Exception:
        return ""
    m = re.search(rf"arXiv:{re.escape(arxiv_id)}(v\d+)", text)
    return m.group(1) if m else ""


def fetch_page(url):
    data = fetch(url)
    return data.decode("utf-8", errors="replace") if data else None


def reconvert(md, force):
    meta, body = read_paper(md)
    arxiv_id = str(meta.get("arxiv") or "")
    if meta.get("source") != "html" or not arxiv_id:
        return "skip (not converted from arXiv HTML)"
    if HAND_EDITED in body and not force:
        return "skip (hand-edited; use --force)"

    pdf = pdf_path_for(md)
    version = pdf_version(pdf, arxiv_id)
    page = fetch_page(f"https://arxiv.org/html/{arxiv_id}{version}")
    note = ""
    if version and (not page or "ltx_page_content" not in page):
        # arXiv renders HTML for some versions only; the latest is the best
        # fallback, though its page numbers may drift from the PDF's.
        page = fetch_page(f"https://arxiv.org/html/{arxiv_id}")
        note = f" (no HTML for {version}; used latest, page numbers may be off)"
    if not page or "ltx_page_content" not in page:
        return f"skip (no HTML for {arxiv_id}{version})"

    with tempfile.TemporaryDirectory() as tmp:
        html_path, body_path = Path(tmp) / "paper.html", Path(tmp) / "body.md"
        new_images = Path(tmp) / "images"
        html_path.write_text(page, encoding="utf-8")
        subprocess.run(
            [sys.executable, SCRIPTS / "html-to-markdown.py", html_path, body_path, new_images, md.stem],
            check=True,
        )
        new_body = body_path.read_text(encoding="utf-8")
        if len(new_body) < 4000:
            return f"skip (HTML for {arxiv_id}{version} is a stub)"

        images = md.parent / "images"
        for old in images.glob(f"{glob_escape(md.stem)}-fig*"):
            old.unlink()
        if new_images.exists():
            images.mkdir(exist_ok=True)
            for f in new_images.iterdir():
                f.rename(images / f.name)
        if images.exists() and not any(images.iterdir()):
            images.rmdir()

    write_paper(md, meta, "\n" + new_body)
    out = subprocess.run(
        [sys.executable, SCRIPTS / "page-map.py", pdf, md], capture_output=True, text=True, check=True
    )
    return f"ok {arxiv_id}{version or ' (latest)'}{note}: {out.stdout.splitlines()[0]}"


def glob_escape(s):
    return re.sub(r"([\[\]*?])", r"[\1]", s)


def main(argv):
    force = "--force" in argv
    args = [a for a in argv if not a.startswith("--")]
    papers = paper_files() if "--all" in argv else [Path(a).resolve() for a in args]
    if not papers:
        sys.exit(__doc__)
    for i, md in enumerate(papers):
        print(f"[{i + 1}/{len(papers)}] {md.stem[:70]}: {reconvert(md, force)}", flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
