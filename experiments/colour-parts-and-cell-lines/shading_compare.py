"""Old against new mark_shading over every cached arXiv rendering: per float, the marks
each makes, and why a new one is there (a cell, a part of a cell, a header row, a legend,
an algorithm).

    git show <commit>^:scripts/html-to-markdown.py > h2m_old.py && uv run python shading_compare.py
"""
import sys; from pathlib import Path
ENGINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ENGINE / "scripts"))
import gzip, re, collections, importlib.util, json
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
old = load(Path(__file__).parent / "h2m_old.py", "h2m_old")
new = load(ENGINE / "scripts/html-to-markdown.py", "h2m_new")
from paperlib import CACHE_DIR; root = CACHE_DIR / "arxiv" / "html"
MARK = re.compile(r"<mark\b[^>]*>(.*?)</mark>", re.S)
def floats(h, art):
    pats = [h.TABLE_FLOAT] + ([h.ALGORITHM_FLOAT] if hasattr(h, "ALGORITHM_FLOAT") else [])
    for m in sorted((m for p in pats for m in p.finditer(art)), key=lambda m: m.start()):
        end = h.balanced_end(art, m.start(), "figure")
        if end: yield art[m.start():end]
def marks(h, art):
    out = {}
    for f in floats(h, art):
        n = f.count("<mark")
        if n:
            cap = h.cell_text(" ".join(re.findall(r"<figcaption\b.*?</figcaption>", f, re.S)))
            out[cap[:80]] = [(re.search(r'<mark( class="[^"]+")?', x.group(0)).group(1) or "", h.cell_text(x.group(1))[:40])
                             for x in MARK.finditer(f)]
    return out
tot = collections.Counter(); rows = []
for f in sorted(root.glob("*/index.html.gz")):
    page = gzip.decompress(f.read_bytes()).decode("utf-8", "replace")
    art = old.extract_article(page)
    a, b = old.mark_shading(art), new.mark_shading(art)
    ma, mb = marks(old, a), marks(new, b)
    tot["papers"] += 1
    tot["marks_old"] += sum(map(len, ma.values())); tot["marks_new"] += sum(map(len, mb.values()))
    tot["floats_old"] += len(ma); tot["floats_new"] += len(mb)
    tot["papers_old"] += bool(ma); tot["papers_new"] += bool(mb)
    tot["algorithms_new"] += sum(1 for k in mb if re.match(r"\s*Algorithm", k))
    words_a = re.sub(r"<[^>]+>", "", a); words_b = re.sub(r"<[^>]+>", "", b)
    tot["text_changed"] += words_a != words_b
    for cap in set(ma) | set(mb):
        if ma.get(cap) != mb.get(cap):
            tot["floats_changed"] += 1
            tot["floats_lost_marks"] += len(mb.get(cap, [])) < len(ma.get(cap, []))
            rows.append({"paper": f.parent.name, "caption": cap, "old": len(ma.get(cap, [])), "new": len(mb.get(cap, [])),
                         "added": [m for m in mb.get(cap, []) if m not in ma.get(cap, [])][:12]})
Path("shading-compare.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
print(dict(tot))
