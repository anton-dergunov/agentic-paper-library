"""What the splice of missing pages did to papers reconverted with it.

    PAPER_LIBRARY=<library> uv run python measure.py <paper.md> ... > results/measure.tsv

For each paper: the PDF pages whose text the markdown lacked at the library's HEAD and
lacks now (page-map.py's missing_pages), the pages the runs hold, the words they add, and
their display and inline formulas KaTeX cannot draw (scripts/katex/check.js on a copy of
the runs alone). Run in the library after `paperlib reconvert`, before committing.
"""

import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from paperlib import LIBRARY_ROOT, pdf_path_for  # noqa: E402

spec = importlib.util.spec_from_file_location("page_map", SCRIPTS / "page-map.py")
page_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(page_map)
pymupdf.TOOLS.mupdf_display_errors(False)
RUN = re.compile(r"<!-- (pp?\. [^ ]+) from the PDF.*?-->\n(.*?)<!-- end of \1 from the PDF -->", re.S)


def katex_failures(text):
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "runs.md").write_text("---\ntitle: x\nsource: html\n---\n" + text, encoding="utf-8")
        out = subprocess.run(["node", SCRIPTS / "katex" / "check.js", tmp], capture_output=True, text=True)
        m = re.search(r"math spans (\d+), failed (\d+)", out.stdout)
        return (int(m.group(2)), int(m.group(1))) if m else (None, None)


print("paper\tpages\tlacking before\tlacking after\ttaken\twords added\tKaTeX failures (of formulas)")
for arg in sys.argv[1:]:
    md = Path(arg).resolve()
    now = md.read_text(encoding="utf-8")
    then = subprocess.run(["git", "-C", LIBRARY_ROOT, "show", f"HEAD:{md.relative_to(LIBRARY_ROOT)}"],
                          capture_output=True, text=True).stdout
    with pymupdf.open(pdf_path_for(md)) as doc:
        before, _ = page_map.missing_pages(doc, then)
        after, _ = page_map.missing_pages(doc, now)
        pages = len(doc)
    runs = RUN.findall(now)
    taken = ", ".join(span for span, _ in runs) or "-"
    added = sum(len(body.split()) for _, body in runs)
    failed, total = katex_failures("\n\n".join(body for _, body in runs)) if runs else (0, 0)
    print(f"{md.stem[:50]}\t{pages}\t{len(before)}\t{len(after)}\t{taken}\t{added}\t{failed} ({total})")
