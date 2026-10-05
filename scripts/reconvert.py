#!/usr/bin/env python3
"""Regenerate papers' markdown from arXiv's HTML with the current converter.

    ./scripts/reconvert.py <paper.md | folder> [...]
    ./scripts/reconvert.py --all
    ./scripts/reconvert.py --all --force     # also papers marked hand-edited
    ./scripts/reconvert.py --all --pdf-text  # re-extract the PDF-text papers
    ./scripts/reconvert.py --pdf-text --inline-math <paper.md>   # the thorough PDF conversion
    ./scripts/reconvert.py --all --jobs 3 --state run.jsonl   # a long run, resumable

For when the conversion improves: the frontmatter (summary included) and the
PDF are kept; the body and the paper's images/ files are regenerated. The HTML
is fetched at the arXiv version printed on the PDF's first page, so headings
get page numbers from the PDF actually being read. A paper converted from
PDF text that is on arXiv is converted from the HTML instead once arXiv has a
rendering of it (it becomes `source: html`). Otherwise it is skipped unless
--pdf-text is given, which regenerates its body, figures and conversion note
from the PDF with the current scripts/pdf-to-markdown.py; `--all --pdf-text`
does just those papers. That is the quick PDF conversion; add --inline-math
for the one the add scripts use, which also has the model read every
paragraph with mathematics (minutes more for a paper with much of it). Papers containing `<!-- hand-edited -->` are skipped,
since a reconversion would drop the edit.

Downloads are cached (paperlib.CACHE_DIR), so reconverting again later needs
no network. --jobs N converts N papers at a time. --state FILE records each
paper's outcome as a JSON line; run the same command again and it skips the
papers already converted (or skipped for good) and retries the rest: those
whose HTML could not be fetched, whose figures did not all download, or whose
conversion failed. A progress bar shows the run; failures are printed as they
happen.
"""

import datetime
import json
import re
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pymupdf
from tqdm import tqdm

from paperlib import LIBRARY_DIR, fetch, paper_files, pdf_path_for, read_paper, write_paper

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


def replace_images(md, new_images):
    """Swap a paper's figure files for the ones a conversion just wrote."""
    images = md.parent / "images"
    for old in images.glob(f"{glob_escape(md.stem)}-fig*"):
        old.unlink()
    if new_images.exists():
        images.mkdir(exist_ok=True)
        for f in new_images.iterdir():
            f.rename(images / f.name)
    if images.exists() and not any(images.iterdir()):
        images.rmdir()


def reconvert_pdf_text(md, meta, inline_math=False):
    """Regenerate a PDF paper's body, figures and conversion note from its PDF."""
    with tempfile.TemporaryDirectory() as tmp:
        out, new_images = Path(tmp) / "body.md", Path(tmp) / "images"
        run = subprocess.run(
            [sys.executable, SCRIPTS / "pdf-to-markdown.py", *([] if inline_math else ["--fast"]),
             pdf_path_for(md), out, new_images, md.stem],
            capture_output=True, text=True, timeout=3600,  # a PDF that hangs must not stop a long run
        )
        if run.returncode:
            raise RuntimeError(f"pdf-to-markdown: {run.stderr.strip().splitlines()[-1:]}")
        text = out.read_text(encoding="utf-8")
        replace_images(md, new_images)
    write_paper(md, meta, "\n" + text)
    fallback = "; fell back to the text layer" if "using the text layer" in run.stderr else ""
    fallback += "; equation model failed, equations are raw text" if "equation model failed" in run.stderr else ""
    return f"from the PDF, {len(text.split())} words{fallback}"


def reconvert(md, force, pdf_text=False, inline_math=False):
    """Reconvert one paper. Returns (status, message); the status is "ok",
    "partial" (some figures did not download), "failed" (no HTML fetched, or
    an error), or "skipped" (nothing to do, and a retry would not change that)."""
    meta, body = read_paper(md)
    arxiv_id = str(meta.get("arxiv") or "")
    if HAND_EDITED in body and not force:
        return "skipped", "hand-edited; use --force"
    if meta.get("source") == "pdf-text":
        status, message = from_html(md, dict(meta, source="html"), arxiv_id) if arxiv_id else (None, "")
        if status in ("ok", "partial"):
            return status, message + " (was PDF text)"
        if pdf_text:
            return "ok", reconvert_pdf_text(md, meta, inline_math)
        return "skipped", "PDF text, no arXiv HTML; use --pdf-text"
    if meta.get("source") != "html" or not arxiv_id:
        return "skipped", "not converted from arXiv HTML"
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
        return "failed", f"no HTML for {arxiv_id}{version}"

    with tempfile.TemporaryDirectory() as tmp:
        html_path, body_path = Path(tmp) / "paper.html", Path(tmp) / "body.md"
        new_images = Path(tmp) / "images"
        html_path.write_text(page, encoding="utf-8")
        run = subprocess.run(
            [sys.executable, SCRIPTS / "html-to-markdown.py", html_path, body_path, new_images, md.stem],
            capture_output=True, text=True, timeout=600,  # a page that hangs must not stop a long run
        )
        if run.returncode:
            return "failed", f"html-to-markdown: {run.stderr.strip().splitlines()[-1:]}"
        warnings = " ".join(line.removeprefix("warning: ") for line in run.stderr.splitlines() if line.startswith("warning"))
        new_body = body_path.read_text(encoding="utf-8")
        if len(new_body) < 4000:
            return "skipped", f"HTML for {arxiv_id}{version} is a stub"

        replace_images(md, new_images)

    write_paper(md, meta, "\n" + new_body)
    out = subprocess.run(
        [sys.executable, SCRIPTS / "page-map.py", pdf, md], capture_output=True, text=True, check=True
    )
    captions = subprocess.run(
        [sys.executable, SCRIPTS / "caption-numbers.py", pdf, md], capture_output=True, text=True, check=True
    ).stdout.splitlines()[0].removeprefix("caption-numbers: ")
    message = f"{arxiv_id}{version or ' (latest)'}{note}: {out.stdout.splitlines()[0]}"
    if not captions.startswith("0 captions renumbered from the PDF, 0 "):
        message += f"; {captions}"
    if "could not be downloaded" in warnings:
        return "partial", f"{message}; {warnings}"
    return "ok", message + (f"; {warnings}" if warnings else "")


def glob_escape(s):
    return re.sub(r"([\[\]*?])", r"[\1]", s)


def option(argv, name, default=None):
    """The value after `name` in argv (and both removed), or default."""
    if name not in argv:
        return default
    i = argv.index(name)
    if i + 1 >= len(argv):
        sys.exit(f"error: {name} needs a value")
    value = argv[i + 1]
    del argv[i:i + 2]
    return value


def load_state(path):
    """The last recorded outcome of each paper in a state file: {path: status}."""
    done = {}
    if path and path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                done[record["paper"]] = record["status"]
    return done


def main(argv):
    argv = list(argv)
    jobs = int(option(argv, "--jobs", "1"))
    state = option(argv, "--state")
    state = Path(state).expanduser().resolve() if state else None
    force, pdf_text, inline_math = "--force" in argv, "--pdf-text" in argv, "--inline-math" in argv
    args = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        papers = paper_files()
    else:
        papers = []
        for a in map(Path, args):
            # A folder means every paper under it.
            papers += paper_files(a.resolve()) if a.is_dir() else [a.resolve()]
    if pdf_text and "--all" in argv:  # only the PDF-text papers
        papers = [p for p in papers if read_paper(p)[0].get("source") == "pdf-text"]
    if not papers:
        sys.exit(__doc__)

    def key(md):
        return str(md.relative_to(LIBRARY_DIR)) if md.is_relative_to(LIBRARY_DIR) else str(md)

    done = load_state(state)
    todo = [md for md in papers if done.get(key(md)) not in ("ok", "skipped")]
    if len(todo) < len(papers):
        print(f"{len(papers) - len(todo)} papers already done in {state}; {len(todo)} to go", flush=True)
    lock = threading.Lock()
    counts = {"ok": 0, "partial": 0, "failed": 0, "skipped": 0}

    def work(md):
        try:
            result = reconvert(md, force, pdf_text, inline_math)
        except Exception as e:  # one paper's failure must not stop the run
            result = "failed", f"{type(e).__name__}: {e}"
        time.sleep(1)  # be gentle with arXiv
        return md, result

    bar = tqdm(total=len(todo), unit="paper", dynamic_ncols=True)
    pool = ThreadPoolExecutor(max_workers=jobs)
    try:
        for future in as_completed([pool.submit(work, md) for md in todo]):
            md, (status, message) = future.result()
            counts[status] += 1
            if status in ("failed", "partial") or len(todo) <= 30:
                bar.write(f"{status:8s}{md.stem[:60]}: {message}")
            if state:
                record = {"paper": key(md), "status": status, "message": message,
                          "at": datetime.datetime.now().isoformat(timespec="seconds")}
                with lock, state.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            bar.set_postfix(counts, refresh=False)
            bar.update()
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        bar.close()
        sys.exit("interrupted; run the same command again to continue" if state else "interrupted")
    pool.shutdown()
    bar.close()
    print(", ".join(f"{n} {status}" for status, n in counts.items()))
    if counts["failed"] or counts["partial"]:
        print("Some papers failed or lost figures"
              + ("; run the same command again to retry them." if state else "."))


if __name__ == "__main__":
    main(sys.argv[1:])
