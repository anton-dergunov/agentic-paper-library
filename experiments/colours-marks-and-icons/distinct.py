"""How many small pictures the cache holds, and how many distinct ones a reconversion would send to the model."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import gzip, re, hashlib, importlib.util, base64, collections, os
spec = importlib.util.spec_from_file_location("h2m", Path(__file__).resolve().parents[2] / "scripts/html-to-markdown.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
from paperlib import fetch, CACHE_DIR
from paperlib import CACHE_DIR; root = CACHE_DIR / "arxiv" / "html"
svgs, files, uses, papers, named_obj, named_obj_papers = set(), set(), 0, set(), 0, set()
for f in sorted(root.glob("*/index.html.gz")):
    pid = f.parent.name
    art = h.extract_article(gzip.decompress(f.read_bytes()).decode("utf-8", "replace"))
    for m in re.finditer(r"<svg\b[^>]*class=\"ltx_picture\"[^>]*>", art):
        svg = art[m.start():h.balanced_end(art, m.start(), "svg")]
        size = [float(v) for v in re.findall(r'\b(?:width|height)="([\d.]+)"', m.group(0))]
        if len(size) == 2 and max(size) <= h.ICON_SIDE and h.picture_kind(svg) == "image" and not any(map(h.words, h.foreign_objects(svg))):
            svgs.add(hashlib.sha256(h.repair_svg(re.sub(r'\s(?:xml:)?id="[^"]*"', "", svg)).encode()).hexdigest()); uses += 1; papers.add(pid)
    for m in re.finditer(r'<(img|object)\b[^>]*>', art):
        tag = m.group(0); size = [int(v) for v in re.findall(r'\b(?:width|height)="(\d+)"', tag)]
        src = re.search(r'\b(?:src|data)="([^"]+)"', tag)
        if len(size) != 2 or max(size) > h.ICON_SIDE or not src or src.group(1).startswith("/static"): continue
        if m.group(1) == "img" and "Uncaptioned" not in tag: continue
        p = src.group(1); name = Path(p).stem if not p.startswith("data:") else ""
        if name and not h.GENERIC_NAME.fullmatch(name):
            if m.group(1) == "object": named_obj += 1; named_obj_papers.add(pid)
            continue
        files.add(p if not p.startswith("data:") else hashlib.sha256(p.encode()).hexdigest()); uses += 1; papers.add(pid)
cached = len(list((CACHE_DIR / "icons").glob("*.txt"))) if (CACHE_DIR / "icons").exists() else 0
print(f"to read: {uses} uses in {len(papers)} papers, {len(svgs)} distinct drawings + {len(files)} files; named objects {named_obj} in {len(named_obj_papers)} papers; already cached {cached}")
