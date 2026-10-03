"""Count the image <object> elements in the arXiv HTML of every html-sourced paper.

    python3 scan_objects.py <scripts dir> <out.tsv>

<scripts dir> holds paperlib.py and reconvert.py (paper list, PDF version, fetch).
Appends "<paper.md>\t<arxiv id+version>\t<objects>\t<hand>" per paper to <out.tsv>
and resumes from it; <objects> is -1 when there is no HTML rendering. Fetches
arXiv's HTML at the PDF's version, 0.7 s apart.
"""
import re, sys, time, importlib.util
from pathlib import Path
SCRIPTS = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(SCRIPTS))
from paperlib import fetch, paper_files, pdf_path_for, read_paper
spec = importlib.util.spec_from_file_location("reconvert", SCRIPTS / "reconvert.py")
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
OUT = Path(sys.argv[2]); OUT.touch()
out = open(OUT, "a")
done = {l.split("\t")[0] for l in open(OUT)} if OUT.stat().st_size else set()
for md in paper_files():
    if str(md) in done: continue
    meta, body = read_paper(md)
    if meta.get("source") != "html" or not meta.get("arxiv"): continue
    aid = str(meta["arxiv"]); v = rc.pdf_version(pdf_path_for(md), aid)
    data = fetch(f"https://arxiv.org/html/{aid}{v}")
    page = data.decode("utf-8", "replace") if data else ""
    if v and "ltx_page_content" not in page:
        data = fetch(f"https://arxiv.org/html/{aid}"); page = data.decode("utf-8", "replace") if data else ""
    n = len(re.findall(r'<object\b[^>]*\btype="image/', page)) if "ltx_page_content" in page else -1
    out.write(f"{md}\t{aid}{v}\t{n}\t{'hand' if '<!-- hand-edited -->' in body else ''}\n"); out.flush()
    time.sleep(0.7)
