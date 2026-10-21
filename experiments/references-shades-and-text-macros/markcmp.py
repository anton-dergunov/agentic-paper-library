"""Compare the table marks of two html-to-markdown.py versions on every cached rendering with coloured tables.

    git show HEAD:scripts/html-to-markdown.py > /tmp/h2m_head.py
    uv run python markcmp.py /tmp/h2m_head.py
"""
import gzip, re, sys, glob, os, collections, importlib.util
ENGINE = __import__("pathlib").Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(ENGINE))
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
old = load("old", sys.argv[1]); new = load("new", str(ENGINE / "html-to-markdown.py"))
changed = 0; total = 0
for f in sorted(glob.glob(os.path.expanduser("~/.cache/papers/arxiv/html/*/index.html.gz"))):
    page = gzip.open(f).read().decode("utf-8", "replace")
    if "--ltx-" not in page or "ltx_table" not in page: continue
    art = old.extract_article(page)
    total += 1
    a = collections.Counter(re.findall(r"<mark[^>]*>", old.mark_shading(art)))
    b = collections.Counter(re.findall(r"<mark[^>]*>", new.mark_shading(art)))
    if a != b:
        changed += 1
        print(f.split("/")[-2], dict(a - b), "->", dict(b - a))
print("papers", total, "changed", changed)
