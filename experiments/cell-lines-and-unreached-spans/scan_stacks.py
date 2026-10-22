"""Scan cached arXiv HTML for one-column stacks left in a table cell after split_stacked_rows."""
import gzip, importlib.util, json, re, sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
ENG = Path(sys.argv[1]); CACHE = Path.home() / ".cache/papers/arxiv/html"
sys.path.insert(0, str(ENG))
spec = importlib.util.spec_from_file_location("h", ENG / "html-to-markdown.py"); h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
GOES_ON, CARRIES_ON = h.GOES_ON, h.CARRIES_ON

def one(d):
    try:
        a = h.extract_article(gzip.decompress((d / "index.html.gz").read_bytes()).decode("utf-8", "replace"))
        for f in ("clean_math", "drop_invisible", "close_runaway_floats", "span_tabulars_to_tables", "tidy_cells", "split_stacked_rows"):
            a = getattr(h, f)(a)
    except Exception as e:
        return []
    out = []
    for t in re.finditer(r"<table\b", a):
        end = h.balanced_end(a, t.start(), "table")
        if end is None: continue
        body = a[t.start():end]
        outer = h.child_elements(body)[0]
        if outer[2] != "table": continue
        rows = h.own_rows(body[outer[4]:outer[5]], outer[4])
        head = re.search(r"<thead\b.*?</thead\s*>", body, re.S)
        for r, row in enumerate(rows):
            for c in h.child_elements(body[row[4]:row[5]]):
                if c[2] not in ("td", "th"): continue
                lines = h.stack_lines(body[row[4] + c[4]:row[4] + c[5]])
                if not lines or len(lines) < 2: continue
                texts = [h.cell_text(re.sub(r"<math\b.*?</math>", " M ", l, flags=re.S)) for l in lines]
                inhead = r == 0 or bool(head and row[0] < head.end()) or "ltx_th_column" in c[3]
                out.append({"id": d.name, "head": inhead, "th": c[2] == "th", "lines": texts})
    return out

if __name__ == "__main__":
  dirs = [d for d in sorted(CACHE.iterdir()) if (d / "index.html.gz").exists()]
  with ProcessPoolExecutor(8) as ex, open(sys.argv[2], "w") as f:
    for res in ex.map(one, dirs, chunksize=4):
        for x in res: f.write(json.dumps(x, ensure_ascii=False) + "\n")
