"""Old against new mark_shading over every cached arXiv rendering: tables marked, marks, named marks."""
import sys; from pathlib import Path
ENGINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ENGINE / "scripts"))
import gzip, re, collections, importlib.util
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
old = load(Path(__file__).parent / "h2m_old.py", "h2m_old")
new = load(ENGINE / "scripts/html-to-markdown.py", "h2m_new")
from paperlib import CACHE_DIR; root = CACHE_DIR / "arxiv" / "html"
tot = collections.Counter(); colours = collections.Counter(); rows = []
for f in sorted(root.glob("*/index.html.gz")):
    page = gzip.decompress(f.read_bytes()).decode("utf-8", "replace")
    art = old.extract_article(page)
    a, b = old.mark_shading(art), new.mark_shading(art)
    ta = sum(1 for m in old.TABLE_FLOAT.finditer(a) if "<mark" in a[m.start():old.balanced_end(a, m.start(), "figure") or m.start()])
    tb = sum(1 for m in new.TABLE_FLOAT.finditer(b) if "<mark" in b[m.start():new.balanced_end(b, m.start(), "figure") or m.start()])
    ma, mb = a.count("<mark"), b.count("<mark")
    named = re.findall(r'<mark class="([^"]+)"', b)
    colours.update(named)
    tot["papers"] += 1; tot["tables_old"] += ta; tot["tables_new"] += tb; tot["marks_old"] += ma; tot["marks_new"] += mb
    tot["named_marks"] += len(named); tot["papers_old"] += ma > 0; tot["papers_new"] += mb > 0; tot["papers_changed"] += a != b
    if a != b: rows.append((f.parent.name, ta, tb, ma, mb, len(named)))
with open("shading-compare.tsv", "w") as out:
    out.write("paper\ttables_old\ttables_new\tmarks_old\tmarks_new\tnamed\n")
    for r in rows: out.write("\t".join(map(str, r)) + "\n")
print(dict(tot)); print(colours.most_common(15))
