#!/usr/bin/env python3
"""Measure each conversion of a paper against its PDF.

    PAPER_LIBRARY=<library> uv run python measure.py <papers.tsv> > results/<name>.tsv

For every paper of <papers.tsv> (an `arxiv` column) and each of its
conversions — `library` (what the library holds now: from arXiv's HTML, or
from the PDF where arXiv has none) and those of convert.py — one row:

  chars       characters of the conversion (the library's without frontmatter)
  pages       pages of the PDF with text
  missing     of those, pages whose text the conversion lacks (page-map.py's measure)
  numbers     share of the PDF's decimal numbers ("72.6") found in the conversion
  equations   display equations: $$…$$ in markdown; equation environments, \\[ and $$ in TeX
  katex       maths spans KaTeX cannot parse (markdown only)
  labels      references left as a label or a key: \\ref{…}, \\cite{…}, "LABEL:", "??", and
              pandoc's data-reference links
"""

import collections
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from paperlib import CACHE_DIR, paper_files, pdf_path_for, read_paper  # noqa: E402

spec = importlib.util.spec_from_file_location("page_map", SCRIPTS / "page-map.py")
page_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(page_map)

OUT = CACHE_DIR / "experiments" / "latex-source"
CANDIDATES = {"latexml": "latexml.md", "latexml2": "latexml2.md", "pandoc": "pandoc.md", "tex": "tex.tex"}
NUM = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")
TEX_DISPLAY = re.compile(r"\\begin\{(?:equation|align|gather|multline|eqnarray|displaymath|flalign|alignat)\*?\}|\\\[|\$\$")
LABELS = re.compile(r"\\(?:[a-zA-Z]*ref|[a-zA-Z]*cite[a-zA-Z]*)\*?(?:\[[^\]]*\])*\{|LABEL:|\?\?|data-reference=")


def katex_failures(texts):
    """{name: maths spans KaTeX cannot parse} for markdown texts, by the engine's check."""
    with tempfile.TemporaryDirectory() as tmp:
        for name, text in texts.items():
            Path(tmp, name + ".md").write_text(text, encoding="utf-8")
        out = subprocess.run(["node", SCRIPTS / "katex" / "check.js", tmp], env={**os.environ, "LIST": "1"},
                             capture_output=True, text=True).stdout
    failed = collections.Counter()
    for line in out.splitlines():
        if line.startswith("FAILFILE"):
            _, count, path = re.split(r"\s+", line, maxsplit=2)
            failed[Path(path).stem] = int(count)
    return failed


def measure(name, text, doc, pdf_numbers):
    missing, texty = page_map.missing_pages(doc, text)
    found = collections.Counter(NUM.findall(text))
    if name == "tex":
        equations = len(TEX_DISPLAY.findall(text)) - len(re.findall(r"\$\$", text)) // 2
    else:
        equations = len(re.findall(r"(?<!\\)\$\$.+?\$\$", text, flags=re.S))
    return {"chars": len(text), "pages": texty, "missing": len(missing),
            "numbers": sum((pdf_numbers & found).values()) / max(1, sum(pdf_numbers.values())),
            "equations": equations, "labels": len(LABELS.findall(text))}


def main():
    wanted = [line.split("\t")[0] for line in Path(sys.argv[1]).read_text().splitlines()[1:] if line.strip()]
    by_id = {str(read_paper(md)[0].get("arxiv") or ""): md for md in paper_files()}
    pymupdf.TOOLS.mupdf_display_errors(False)
    print("arxiv\tconversion\tchars\tpages\tmissing\tnumbers\tequations\tkatex\tlabels\ttitle")
    for arxiv_id in wanted:
        md = by_id[arxiv_id]
        texts = {"library": read_paper(md)[1]}
        for name, file in CANDIDATES.items():
            path = OUT / arxiv_id / file
            if path.exists() and path.stat().st_size > 100:
                texts[name] = path.read_text(encoding="utf-8", errors="replace")
        failed = katex_failures({n: t for n, t in texts.items() if n != "tex"})
        with pymupdf.open(pdf_path_for(md)) as doc:
            pdf_numbers = collections.Counter(NUM.findall("\n".join(page.get_text() for page in doc)))
            for name, text in texts.items():
                m = measure(name, text, doc, pdf_numbers)
                katex = "" if name == "tex" else failed[name]
                print(f"{arxiv_id}\t{name}\t{m['chars']}\t{m['pages']}\t{m['missing']}\t{m['numbers']:.2f}\t"
                      f"{m['equations']}\t{katex}\t{m['labels']}\t{md.stem}", flush=True)


if __name__ == "__main__":
    main()
