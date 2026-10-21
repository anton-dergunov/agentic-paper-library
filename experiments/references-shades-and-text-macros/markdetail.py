"""For one cached rendering, print each table whose marks differ between two html-to-markdown.py versions.

    uv run python markdetail.py /tmp/h2m_head.py <arxiv id with version>
"""
import gzip, re, sys, glob, os, collections, importlib.util
ENGINE = __import__("pathlib").Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(ENGINE))
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
old = load("old", sys.argv[1]); new = load("new", str(ENGINE / "html-to-markdown.py"))
page = gzip.open(glob.glob(os.path.expanduser(f"~/.cache/papers/arxiv/html/{sys.argv[2]}/index.html.gz"))[0]).read().decode()
art = old.extract_article(page)
def floats(a):
    out = {}
    for m in old.TABLE_FLOAT.finditer(a):
        e = old.balanced_end(a, m.start(), "figure"); i = re.search(r'id="([^"]*)"', m.group(0))
        out[i.group(1) if i else m.start()] = a[m.start():e]
    return out
fo, fn = floats(old.mark_shading(art)), floats(new.mark_shading(art))
for k in fn:
    mo = re.findall(r"(<mark[^>]*>)(.*?)</mark>", fo.get(k, ""), re.S); mn = re.findall(r"(<mark[^>]*>)(.*?)</mark>", fn[k], re.S)
    if mo != mn:
        cap = " ".join(old.cell_text(c) for c in re.findall(r"<figcaption\b.*?</figcaption>", fn[k], re.S))
        print("==", k, re.sub(r"\s+", " ", cap)[:400])
        short = lambda ms: collections.Counter((t, re.sub(r"\s+", " ", old.cell_text(x))[:15]) for t, x in ms).most_common(8)
        print("  old:", len(mo), short(mo)); print("  new:", len(mn), short(mn))
