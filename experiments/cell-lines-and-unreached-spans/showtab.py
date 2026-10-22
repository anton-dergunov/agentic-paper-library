"""showtab.py <arxiv id/version> <key> [nth] [stage]: the table of a cached rendering holding `key`,
one line per row: each cell's tag, spans (r2, c3), rules (T above, B below), a nested tabular (≡)
and text. stage=raw (default) or the converter step to run up to; the converter is new/eng/."""
import gzip, importlib.util, re, sys
from pathlib import Path
ENG = Path(__file__).parent / "new/eng"
sys.path.insert(0, str(ENG))
spec = importlib.util.spec_from_file_location("h", ENG / "html-to-markdown.py"); h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
d = sorted(Path.home().glob(f".cache/papers/arxiv/html/{sys.argv[1]}*"))[-1]
page = gzip.decompress((d / "index.html.gz").read_bytes()).decode()
a = h.extract_article(page)
STEPS = ["clean_math", "drop_invisible", "close_runaway_floats", "drop_style_warnings", "name_icons", "split_captions", "tidy_authors",
         "convert_listings", "span_tabulars_to_tables", "unresolved_refs", "drop_undefined_macros", "drop_tex_residue", "fix_text_encoding",
         "tidy_cells", "split_stacked_rows", "restore_dropped_cells", "extend_rowspans", "span_group_labels", "source_row_spans", "merge_continuation_rows", "join_wrapped_labels",
         "end_guessed_heads", "span_header_rows", "join_table_halves", "share_panel_labels", "mark_shading", "break_cell_lines"]
stage = sys.argv[4] if len(sys.argv) > 4 else "raw"
if stage != "raw":
    for f in STEPS:
        a = getattr(h, f)(a, page) if f in ("source_row_spans", "restore_dropped_cells") else getattr(h, f)(a)
        if f == stage: break
nth = int(sys.argv[3]) if len(sys.argv) > 3 else 0
hits = [m.start() for m in re.finditer(re.escape(sys.argv[2]), a)]
tables = [(m.start(), h.balanced_end(a, m.start(), "table") or 0) for m in re.finditer(r"<table\b[^>]*ltx_tabular", a)]
outermost = [x for x in tables if not any(y[0] < x[0] < y[1] for y in tables)]
found = [x for x in outermost if any(x[0] < i < x[1] for i in hits)]
t = found[nth][0]
body = a[t:h.balanced_end(a, t, "table")]
outer = h.child_elements(body)[0]
for r, row in enumerate(h.own_rows(body[outer[4]:outer[5]], outer[4])):
    cells = []
    for c in h.child_elements(body[row[4]:row[5]]):
        if c[2] not in ("td", "th"): continue
        attrs = c[3]
        marks = "".join(k for k, pat in (("T", r"ltx_border_tt?\b"), ("B", r"ltx_border_bb?\b")) if re.search(pat, attrs))
        sp = "".join(f"{k[0]}{n}" for k, n in re.findall(r'\b(row|col)span="(\d+)"', attrs))
        inner = body[row[4] + c[4]:row[4] + c[5]]
        txt = h.cell_text(re.sub(r"<math\b.*?</math>", "$", inner, flags=re.S))
        txt = " ".join(txt.split())
        stack = "≡" if h.TABULAR_START.search(inner) else ""
        cells.append(f"{c[2]}{sp}{marks}{stack}:{txt[:40]}")
    print(r, " | ".join(cells))
