#!/usr/bin/env python3
"""The paper in each form a condition sends, built on demand into the cache (paper text
is never committed).

    PAPER_LIBRARY=<library> uv run python inputs.py build     # every input, with sizes
    PAPER_LIBRARY=<library> uv run python inputs.py check     # gold values on their PDF pages

Forms: pdf (the library's PDF), txt (`pdftotext -layout`), html (arXiv's HTML <article>,
scripts and styles removed, otherwise raw), md (the library's markdown as it is), md-old
(the markdown at the revision in questions.yaml's old_revs), md-noanchors (in-document
links reduced to their text), page<N>.pdf (one page), page<N>-<px>.png (one page, long
edge <px>).
"""

import glob
import gzip
import re
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
from paperlib import CACHE_DIR, LIBRARY_DIR, LIBRARY_ROOT, pdf_path_for, read_paper  # noqa: E402

OUT = CACHE_DIR / "experiments" / "reading-formats"
SPEC = yaml.safe_load((HERE / "questions.yaml").read_text())
PAPERS, OLD_REVS = SPEC["papers"], SPEC["old_revs"]
# A question with `source` rewords another (tier F names its paper) and takes the rest from it.
_SOURCES = {q["id"]: q for q in SPEC["questions"]}
QUESTIONS = [{**_SOURCES[q["source"]], **q} if q.get("source") else q for q in SPEC["questions"]]


def md_path(paper):
    return LIBRARY_DIR / PAPERS[paper]


def pdf(paper):
    return pdf_path_for(md_path(paper))


def _cached(paper, name, make):
    path = OUT / "inputs" / paper / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        data = make()
        if data is None:
            return None
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
        tmp.rename(path)
    return path


def txt(paper):
    return _cached(paper, "layout.txt", lambda: subprocess.run(
        ["pdftotext", "-layout", str(pdf(paper)), "-"], capture_output=True, check=True).stdout)


def html(paper):
    """arXiv's <article>, or None for a paper without arXiv HTML."""
    def make():
        from lxml import html as lxml_html
        arxiv = str(read_paper(md_path(paper))[0].get("arxiv") or "")
        found = sorted(glob.glob(str(CACHE_DIR / "arxiv" / "html" / (arxiv + "v*") / "index.html.gz")))
        if not arxiv or not found:
            return None
        tree = lxml_html.fromstring(gzip.open(found[-1]).read())
        article = tree.find(".//article")
        for bad in article.xpath(".//script|.//style"):
            bad.getparent().remove(bad)
        return lxml_html.tostring(article, encoding="unicode")
    return _cached(paper, "article.html", make)


def md(paper):
    return md_path(paper)


def md_old(paper):
    rel = str(md_path(paper).relative_to(LIBRARY_ROOT))
    return _cached(paper, "old.md", lambda: subprocess.run(
        ["git", "-C", str(LIBRARY_ROOT), "show", "%s:%s" % (OLD_REVS[paper], rel)],
        capture_output=True, check=True).stdout)


def md_noanchors(paper):
    # [31](#bib.bib31) -> [31]; [3](#S3.E3) -> 3: a link to the paper's own anchors
    return _cached(paper, "noanchors.md", lambda: re.sub(
        r"\[([^\]]*)\]\(#[^)]*\)", lambda m: m.group(1) if m.group(1).startswith("[") else m.group(1),
        md_path(paper).read_text(encoding="utf-8")))


def page_pdf(paper, page):
    def make():
        tmp = OUT / "inputs" / paper / ("page%d.tmp.pdf" % page)
        subprocess.run(["qpdf", str(pdf(paper)), "--pages", ".", str(page), "--", str(tmp)], check=True)
        data = tmp.read_bytes()
        tmp.unlink()
        return data
    return _cached(paper, "page%d.pdf" % page, make)


def page_png(paper, page, px):
    def make():
        stem = OUT / "inputs" / paper / ("page%d-%d.tmp" % (page, px))
        subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-singlefile", "-png",
                        "-scale-to", str(px), str(pdf(paper)), str(stem)], check=True)
        png = Path(str(stem) + ".png")
        data = png.read_bytes()
        png.unlink()
        return data
    return _cached(paper, "page%d-%d.png" % (page, px), make)


def page_text(paper, page):
    done = subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf(paper)), "-"],
                          capture_output=True, text=True)
    return done.stdout if done.returncode == 0 else ""  # past the last page


def build():
    for paper in PAPERS:
        sizes = {"pdf": pdf(paper).stat().st_size}
        for name, make in (("txt", txt), ("html", html), ("md", md)):
            path = make(paper)
            sizes[name] = len(path.read_text(encoding="utf-8")) if path else None
        if paper in OLD_REVS:
            sizes["md-old"] = len(md_old(paper).read_text(encoding="utf-8"))
        print(paper, sizes)
    md_noanchors("dpo")
    for page in (1, 2, 9):
        page_pdf("dpo", page)
    for px in (1255, 2576):
        page_png("dpo", 9, px)
    for paper, page in (("qwen3vl", 15), ("litm", 7)):
        page_pdf(paper, page)
        for px in (1255, 2576):
            page_png(paper, page, px)
    print("inputs in", OUT / "inputs")


def numbers(text):
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*\.?\d*", text) if len(n.strip(".,")) > 1}


def check():
    """Every number of a gold answer on its PDF page or the next (pdftotext)."""
    for q in QUESTIONS:
        if "paper" not in q or "page" not in q or q.get("answerable") is False or q.get("source"):
            continue
        pages = {p for p in (q["page"], q["page"] + 1, q["page"] - 1) if p > 0}
        text = "".join(page_text(q["paper"], p) for p in pages).replace(",", "")
        gold = re.sub(r"\((Table|Tables|Figure|Eq\.|pp?\.)[^)]*\)", "", q["gold"])
        missing = sorted(n for n in numbers(gold) if n not in text)
        print("%-3s p.%-3s %s" % (q["id"], q["page"], "ok" if not missing else "not on the page: " + " ".join(missing)))


if __name__ == "__main__":
    {"build": build, "check": check}[sys.argv[1]]()
