"""Sample distinct small pictures (generic names, tiny TikZ drawings) from the cache into icons/sample."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import gzip, re, hashlib, random, importlib.util, base64, json
spec = importlib.util.spec_from_file_location("h2m", Path(__file__).resolve().parents[2] / "scripts/html-to-markdown.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
from paperlib import fetch
from paperlib import CACHE_DIR; root = CACHE_DIR / "arxiv" / "html"
out = Path("icons/sample"); out.mkdir(parents=True, exist_ok=True)
seen = {}; per_paper = {}
random.seed(7)
files = sorted(root.glob("*/index.html.gz"))
for f in files:
    pid = f.parent.name
    page = gzip.decompress(f.read_bytes()).decode("utf-8", "replace")
    art = h.extract_article(page)
    items = []
    for m in re.finditer(r"<svg\b[^>]*class=\"ltx_picture\"[^>]*>", art):
        end = h.balanced_end(art, m.start(), "svg")
        svg = art[m.start():end]
        size = [float(v) for v in re.findall(r'\b(?:width|height)="([\d.]+)"', m.group(0))]
        if len(size) == 2 and max(size) <= 40 and h.picture_kind(svg) == "image" and not any(map(h.words, h.foreign_objects(svg))):
            items.append(("svg", h.repair_svg(svg).encode()))
    for m in re.finditer(r'<(img|object)\b[^>]*>', art):
        tag = m.group(0)
        size = [int(v) for v in re.findall(r'\b(?:width|height)="(\d+)"', tag)]
        src = re.search(r'\b(?:src|data)="([^"]+)"', tag)
        if len(size) != 2 or max(size) > 40 or not src: continue
        if m.group(1) == "img" and "Uncaptioned" not in tag: continue
        p = src.group(1); name = Path(p).stem
        if p.startswith("/static"): continue
        if not p.startswith("data:") and not h.GENERIC_NAME.fullmatch(name): continue
        items.append(("file", p))
    for kind, x in items:
        per_paper.setdefault(pid, []).append((kind, x))
print(len(per_paper), "papers;", sum(map(len, per_paper.values())), "uses")
# sample: up to 3 distinct per paper, 45 overall
picked = []
for pid in random.sample(sorted(per_paper), min(30, len(per_paper))):
    for kind, x in per_paper[pid][:40]:
        if kind == "file":
            data = base64.b64decode(x.partition(",")[2]) if x.startswith("data:") else fetch("https://arxiv.org/html/" + x)
            if not data: continue
        else:
            data = x
        k = hashlib.sha256(data).hexdigest()[:12]
        if k in seen: continue
        seen[k] = 1
        ext = "svg" if data.lstrip()[:4] in (b"<svg", b"<?xm") else "img"
        (out / f"{pid}_{k}.{ext}").write_bytes(data)
        picked.append(f"{pid}_{k}.{ext}")
        if sum(p.startswith(pid) for p in picked) >= 3: break
print(len(picked), "icons sampled")
