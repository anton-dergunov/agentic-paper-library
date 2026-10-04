#!/usr/bin/env python3
"""Convert papers from LaTeXML's MathML instead of its TeX, and compare.

    PAPER_LIBRARY=<library> uv run python experiments/katex-equation-check/mathml.py <out-dir> <paper.md> ...

For each paper (source: html, its arXiv HTML in the cache) the real
html-to-markdown.py runs twice: on the page as it is ("tex"), and on the page
with every equation's TeX removed ("mathml"): both the alttext attribute and
the <annotation encoding="application/x-tex"> element, so that pandoc has only
the MathML to read. The run of 30 Sep 2026 removed the attribute alone and
pandoc read the annotation, so both outputs were the same file; this script
fails if every paper comes out the same by both routes.

Writes <out-dir>/tex/<arxiv id>.md and <out-dir>/mathml/<arxiv id>.md, and
prints one line per paper: maths spans by each route, and whether the files differ. Run scripts/katex/check.js on
the two folders for the KaTeX failures.
"""

import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from paperlib import pdf_path_for, read_paper  # noqa: E402

spec = importlib.util.spec_from_file_location("reconvert", SCRIPTS / "reconvert.py")
reconvert = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reconvert)

MATH = re.compile(r"\$\$.+?\$\$|(?<![\\$])\$(?!\$)(?:\\.|[^$\\\n])+?\$(?!\$)", re.S)


def without_tex(page):
    page = re.sub(r'<annotation encoding="application/x-tex"[^>]*>.*?</annotation>', "", page, flags=re.S)
    return re.sub(r'(<math\b[^>]*?)\salttext="[^"]*"', r"\1", page)


def convert(page, out):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "paper.html").write_text(page, encoding="utf-8")
        subprocess.run([sys.executable, SCRIPTS / "html-to-markdown.py", tmp / "paper.html", tmp / "body.md",
                        tmp / "images", "paper"], check=True, capture_output=True)
        out.write_text((tmp / "body.md").read_text(encoding="utf-8"), encoding="utf-8")
    return out.read_text(encoding="utf-8")


def main(out_dir, papers):
    out_dir = Path(out_dir)
    for route in ("tex", "mathml"):
        (out_dir / route).mkdir(parents=True, exist_ok=True)
    same = converted = 0
    for md in map(Path, papers):
        meta, _ = read_paper(md)
        arxiv_id = str(meta["arxiv"])
        version = reconvert.pdf_version(pdf_path_for(md), arxiv_id)
        page = reconvert.fetch_page(f"https://arxiv.org/html/{arxiv_id}{version}")
        if not page or "ltx_page_content" not in page:
            page = reconvert.fetch_page(f"https://arxiv.org/html/{arxiv_id}")
        if not page or "ltx_page_content" not in page:
            print(f"no HTML\t{arxiv_id}")
            continue
        tex = convert(page, out_dir / "tex" / f"{arxiv_id}.md")
        mathml = convert(without_tex(page), out_dir / "mathml" / f"{arxiv_id}.md")
        n_tex, n_mathml = len(MATH.findall(tex)), len(MATH.findall(mathml))
        same += tex == mathml
        converted += 1
        print(f"{arxiv_id}\t{n_tex}\t{n_mathml}\t{'same' if tex == mathml else 'differ'}\t{md.stem}", flush=True)
    # A paper with a handful of one-letter formulas can come out the same by
    # both routes; all of them the same means the MathML was not read.
    if converted and same == converted:
        sys.exit("both routes gave the same files, so the MathML was not read")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
