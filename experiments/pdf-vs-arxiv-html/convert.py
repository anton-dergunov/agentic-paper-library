#!/usr/bin/env python3
"""The three conversions compared on 29 Sep 2026.

    python3 convert.py html <arxiv-id> <name>   # -> <name>_html.md
    python3 convert.py pdf <paper.pdf> <name>   # -> <name>_pdftext.md, <name>_p4llm.md

html: fetch arXiv's HTML rendering, cut out LaTeXML's ltx_page_content <div>,
      and convert it with `pandoc -f html -t gfm-raw_html --wrap=none` (the
      library's add-arxiv-paper.sh pipeline at the time; needs pandoc on PATH).
pdf:  PyMuPDF's raw text, page by page with sort=True, and pymupdf4llm's
      markdown (needs `pip install pymupdf pymupdf4llm`).

Reassembled from the shell commands of the session that ran the comparison:
the code is as run, wrapped in two functions with the paper as an argument.
In that run only Zep's HTML was converted here (2501.13956v1); DPO's and
SimPO's _html.md were copies of the markdown an earlier library had made with
the same pipeline.
"""
import re
import subprocess
import sys
import urllib.request


def html(arxiv_id, name):
    page = urllib.request.urlopen(f"https://arxiv.org/html/{arxiv_id}").read().decode("utf-8")
    s = re.search(r"<div[^>]*\bltx_page_content\b[^>]*>", page); pos = s.end(); d = 1
    for m in re.finditer(r"<div\b|</div>", page[pos:]):
        d += -1 if m.group() == "</div>" else 1
        if d == 0: end = pos + m.end(); break
    open(f"{name}_article.html", "w").write(page[s.start():end])
    subprocess.run(["pandoc", f"{name}_article.html", "-f", "html", "-t", "gfm-raw_html",
                    "--wrap=none", "-o", f"{name}_html.md"], check=True)


def pdf(path, name):
    import pymupdf, pymupdf4llm
    d = pymupdf.open(path)
    open(f"{name}_pdftext.md", "w").write("\n\n".join(p.get_text("text", sort=True) for p in d))
    open(f"{name}_p4llm.md", "w").write(pymupdf4llm.to_markdown(path, show_progress=False))
    print(name, d.page_count, "pages")


if __name__ == "__main__":
    {"html": html, "pdf": pdf}[sys.argv[1]](sys.argv[2], sys.argv[3])
