#!/usr/bin/env python3
"""Move a library from markdown conversions to text layers (docs/design.md, 2026-10-26).

    PAPER_LIBRARY=<library> uv run python migrate.py [step ...]     # all steps by default

Steps, each safe to run again:

- text: every paper converted from arXiv's HTML or its PDF (`source: html | pdf-text`)
  becomes <stem>.txt: its frontmatter (`source: pdf`), then its PDF's text layer; the .md
  goes. An unreadable text layer is marked `text-layer: broken`.
- broken: the papers whose issue records say the text layer itself is broken
  (`pdf-broken-text-layer`) are marked `text-layer: broken`.
- web: every web article is converted again from its page, by the engine's web converter,
  keeping its file name, frontmatter and PDF.
- clean: the figure folders, issues/ and corrections/ go.
- notes: the `- Conversion: …` line of a note's digest goes.
- reviews: figures embedded from the papers' images/ go (their captions keep the page link);
  links to papers' markdown become links to their text (review-status --fix-links).
- vscode: `**/images` leaves the library's search excludes.
- stats: what the reading view keeps of each text layer, into results/stats.json.

Then run `paperlib build-index` and `paperlib check`.
"""

import concurrent.futures
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parents[1]
sys.path.insert(0, str(ENGINE / "scripts"))

import paperlib  # noqa: E402
from paperlib import (  # noqa: E402
    LIBRARY_DIR, LIBRARY_ROOT, NOTES_DIR, REVIEWS_DIR, paper_files, pdf_path_for, read_paper,
    render_frontmatter, text_view, write_paper, write_text_paper,
)

ISSUES_DIR = LIBRARY_ROOT / "issues"
CORRECTIONS_DIR = LIBRARY_ROOT / "corrections"
RESULTS = HERE / "results"


def pdf_for(paper):
    """The paper's PDF, found also when the synced folder stores its name in another Unicode form."""
    pdf = pdf_path_for(paper)
    if pdf.exists():
        return pdf
    want = unicodedata.normalize("NFC", pdf.name)
    for other in pdf.parent.iterdir() if pdf.parent.is_dir() else []:
        if unicodedata.normalize("NFC", other.name) == want:
            return other
    return None


def text():
    papers = [p for p in paper_files() if p.suffix == ".md" and read_paper(p)[0].get("source") in ("html", "pdf-text")]

    def one(md):
        meta = read_paper(md)[0]
        pdf = pdf_for(md)
        if not pdf:
            return md, "no PDF"
        meta["source"] = "pdf"
        try:
            problem = write_text_paper(md.with_suffix(".txt"), meta, pdf)
        except RuntimeError as error:
            return md, f"failed: {error}"
        md.unlink()
        return md, problem

    flagged = {}
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count() or 4) as pool:
        for md, problem in pool.map(one, papers):
            if problem:
                flagged[md.stem] = problem
    print(f"text: {len(papers)} papers to text layers; flagged: {flagged or 'none'}")
    return flagged


def broken():
    stems = sorted(p.stem for p in ISSUES_DIR.glob("*.yaml")
                   if re.search(r"^- kind: pdf-broken-text-layer$", p.read_text(encoding="utf-8"), re.M)) \
        if ISSUES_DIR.is_dir() else []
    by_stem = {paperlib.paper_stem(p): p for p in paper_files()}
    for stem in stems:
        paper = by_stem.get(stem)
        if not paper or paper.suffix != ".txt":
            print(f"broken: {stem}: no text-layer paper")
            continue
        meta, body = read_paper(paper)
        meta["text-layer"] = "broken"
        write_paper(paper, meta, body)
    print(f"broken: marked {stems}")


def web():
    spec = importlib.util.spec_from_file_location("add_web", ENGINE / "scripts" / "add-web-article.py")
    add_web = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(add_web)
    done, failed = 0, []
    for md in [p for p in paper_files() if p.suffix == ".md"]:
        meta = read_paper(md)[0]
        if meta.get("source") != "web":
            continue
        url = meta["url"]
        dom = add_web.chrome(url, "--dump-dom")
        title = (re.search(r"<title[^>]*>(.*?)</title>", dom[:20000], re.S | re.I) or [None, ""])[1]
        if len(dom) < 1000 or add_web.BOT_CHECK.search(title or ""):
            failed.append((md.name, "no page or a bot check"))
            continue
        try:
            body = add_web.to_markdown(dom, url).strip() + "\n"
        except SystemExit as error:
            failed.append((md.name, str(error)))
            continue
        note = (f"> **A web article** ({url}), converted to markdown without its figures and interactive "
                f"parts; open the original for them.\n\n")
        heading = "" if re.search(r"^#\s+\S", body[:2000], re.M) else f"# {meta['title']}\n\n"
        old = md.read_text(encoding="utf-8")
        md.write_text(render_frontmatter(meta) + "\n" + heading + note + body, encoding="utf-8")
        print(f"web: {md.name}: {len(old):,} -> {md.stat().st_size:,} characters")
        done += 1
    print(f"web: {done} converted again; failed: {failed or 'none'}")


def clean():
    folders = sorted(LIBRARY_DIR.rglob("images"))
    for folder in folders:
        shutil.rmtree(folder)
    for folder in (ISSUES_DIR, CORRECTIONS_DIR):
        if folder.is_dir():
            shutil.rmtree(folder)
    print(f"clean: {len(folders)} figure folders, issues/ and corrections/ removed")


def notes():
    changed = 0
    for note in sorted(NOTES_DIR.glob("*.md")):
        old = note.read_text(encoding="utf-8")
        new = re.sub(r"^- Conversion: .*\n", "", old, flags=re.M)
        if new != old:
            note.write_text(new, encoding="utf-8")
            changed += 1
    print(f"notes: the conversion line taken out of {changed} notes")


def reviews():
    removed = 0
    for review in sorted(REVIEWS_DIR.rglob("*.md")):
        old = review.read_text(encoding="utf-8")
        new = re.sub(r"^!\[[^\]]*\]\([^)]*/images/[^)]*\)\n\n?", "", old, flags=re.M)
        if new != old:
            removed += old.count("/images/") - new.count("/images/")
            review.write_text(new, encoding="utf-8")
    print(f"reviews: {removed} embedded figures removed")
    env = dict(os.environ, PATH=str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"])
    subprocess.run([sys.executable, str(ENGINE / "scripts" / "review-status.py"), "--fix-links"], env=env)


def vscode():
    path = LIBRARY_ROOT / ".vscode" / "settings.json"
    if not path.exists():
        return
    settings = json.loads(path.read_text())
    if settings.get("search.exclude", {}).pop("**/images", None) is not None:
        path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        print("vscode: **/images no longer excluded from search")


def stats():
    """Per paper: pages, characters, the share the reading view keeps, and how it was cut."""
    rows = []
    for paper in paper_files():
        if paper.suffix != ".txt":
            continue
        meta, body = read_paper(paper)
        view = text_view(meta, body)
        last = view.rstrip().rsplit("\n", 1)[-1]
        cut = ("alone" if "Left out: the references" in last else "column" if "the rest of the references" in last
               else "none")
        rows.append({"paper": paper.stem, "pages": len(paperlib.PAGE_MARK.findall(body)), "chars": len(body),
                     "view": len(view), "cut": cut, "broken": meta.get("text-layer") == "broken"})
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "stats.json").write_text(json.dumps(rows, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    n = len(rows)
    cuts = {k: sum(r["cut"] == k for r in rows) for k in ("alone", "column", "none")}
    kept = sorted(r["view"] / r["chars"] for r in rows)
    print(f"stats: {n} text layers, {sum(r['pages'] for r in rows):,} pages, {sum(r['chars'] for r in rows):,} characters; "
          f"cut {cuts}; the view keeps a median {kept[n // 2]:.0%} (10th percentile {kept[n // 10]:.0%})")


STEPS = {"text": text, "broken": broken, "web": web, "clean": clean, "notes": notes, "reviews": reviews,
         "vscode": vscode, "stats": stats}

if __name__ == "__main__":
    for step in sys.argv[1:] or list(STEPS):
        STEPS[step]()
