#!/usr/bin/env python3
"""Regenerate papers' markdown from arXiv's HTML with the current converter.

    ./scripts/reconvert.py <paper.md> [<paper.md> ...]
    ./scripts/reconvert.py --all
    ./scripts/reconvert.py --all --force     # also papers marked hand-edited
    ./scripts/reconvert.py --all --pdf-text  # re-extract the PDF-text papers

For when the conversion improves: the frontmatter (summary included) and the
PDF are kept; the body and the paper's images/ files are regenerated. The HTML
is fetched at the arXiv version printed on the PDF's first page, so headings
get page numbers from the PDF actually being read. A paper converted from
PDF text that is on arXiv is converted from the HTML instead once arXiv has a
rendering of it (it becomes `source: html`). Otherwise it is skipped unless
--pdf-text is given, which regenerates its body from the PDF with the current
scripts/pdf-to-markdown.py (keeping the warning banner); `--all --pdf-text`
does just those papers. Papers containing `<!-- hand-edited -->` are skipped,
since a reconversion would drop the edit.
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


def reconvert_pdf_text(md, meta, body):
    """Regenerate a PDF-text paper's body from its PDF, keeping the warning banner."""
    banner = re.match(r"\s*((?:>.*\n)+)", body)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "body.md"
        subprocess.run([sys.executable, SCRIPTS / "pdf-to-markdown.py", pdf_path_for(md), out], check=True)
        text = out.read_text(encoding="utf-8")
    write_paper(md, meta, "\n" + (banner.group(1) + "\n" if banner else "") + text)
    return f"ok (from PDF text, {len(text.split())} words)"


def reconvert(md, force, pdf_text=False):
    meta, body = read_paper(md)
    arxiv_id = str(meta.get("arxiv") or "")
    if HAND_EDITED in body and not force:
        return "skip (hand-edited; use --force)"
    if meta.get("source") == "pdf-text":
        result = from_html(md, dict(meta, source="html"), arxiv_id) if arxiv_id else None
        if result and result.startswith("ok"):
            return result + " (was PDF text)"
        return reconvert_pdf_text(md, meta, body) if pdf_text else "skip (PDF text; use --pdf-text)"
    if meta.get("source") != "html" or not arxiv_id:
        return "skip (not converted from arXiv HTML)"
    return from_html(md, meta, arxiv_id)


def from_html(md, meta, arxiv_id):
    """Rewrite the body from arXiv's HTML at the PDF's version, with `meta` as frontmatter."""
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
    force, pdf_text = "--force" in argv, "--pdf-text" in argv
    args = [a for a in argv if not a.startswith("--")]
    papers = paper_files() if "--all" in argv else [Path(a).resolve() for a in args]
    if pdf_text and "--all" in argv:  # only the PDF-text papers
        papers = [p for p in papers if read_paper(p)[0].get("source") == "pdf-text"]
    if not papers:
        sys.exit(__doc__)
    for i, md in enumerate(papers):
        print(f"[{i + 1}/{len(papers)}] {md.stem[:70]}: {reconvert(md, force, pdf_text)}", flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
