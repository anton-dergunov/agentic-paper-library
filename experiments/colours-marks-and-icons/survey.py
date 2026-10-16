"""Tables with two or more colours in the cache: does the caption name them, or show them in a legend of its own?"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import gzip, re, collections, colorsys, importlib.util, random
spec = importlib.util.spec_from_file_location("h2m", Path(__file__).resolve().parents[2] / "scripts/html-to-markdown.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
from paperlib import CACHE_DIR; root = CACHE_DIR / "arxiv" / "html"
WORDS = r"\b(red|pink|orange|yellow|green|cyan|teal|blue|purple|violet|magenta|brown|gr[ae]y(?:ed)?|black|white|gold|olive|navy|lime|maroon|turquoise)\b"
def name(hx):
    r, g, b = (int(hx[i:i+2], 16) / 255 for i in (1, 3, 5))
    hue, l, s = colorsys.rgb_to_hls(r, g, b); hue *= 360
    if s < 0.15 or max(r,g,b) - min(r,g,b) < 0.08:
        return "black" if l < 0.12 else "white" if l > 0.97 else "gray"
    if hue < 15 or hue >= 345: return "pink" if l > 0.8 else "red"
    if hue < 45: return "brown" if l < 0.35 else "orange"
    if hue < 70: return "yellow"
    if hue < 165: return "green"
    if hue < 195: return "cyan"
    if hue < 255: return "blue"
    if hue < 290: return "purple"
    return "pink"
out = collections.Counter(); rows = []
files = sorted(root.glob("*/index.html.gz"))
for f in files:
    page = gzip.decompress(f.read_bytes()).decode("utf-8", "replace")
    for m in h.TABLE_FLOAT.finditer(page):
        end = h.balanced_end(page, m.start(), "figure")
        if not end: continue
        body = page[m.start():end]
        if "--ltx-bg-color" not in body and "--ltx-fg-color" not in body: continue
        capsrc = " ".join(re.findall(r"<figcaption\b.*?</figcaption>", body, re.S))
        cap = h.cell_text(capsrc).lower()
        t = h.table_only(body)
        cols = {}
        for kind in ("bg", "fg"):
            for c in re.findall(rf"--ltx-{kind}-color:\s*(#[0-9A-Fa-f]{{6}})", t):
                c = c.lower(); n = name(c)
                if kind == "fg" and n in ("black",): continue
                if kind == "bg" and n == "white": continue
                cols[(kind, c)] = n
        if len(cols) < 2: continue
        words = set(w.replace("grey", "gray").replace("grayed", "gray") for w in re.findall(WORDS, cap))
        capcols = {c.lower() for c in re.findall(r"--ltx-fg-color:\s*(#[0-9A-Fa-f]{6})", capsrc)} - {"#000000"}
        legend = {k for k in cols if k[1] in capcols}
        named = {k for k, n in cols.items() if n in words}
        unmatched = words - set(cols.values()) - {"black", "white"}
        key = ("named" if named else "") + ("+legend" if legend else "") or "none"
        out[key] += 1
        rows.append((f.parent.name, key, sorted(set(cols.values())), sorted(words), sorted(unmatched), cap[:160]))
print(out)
random.seed(1)
for r in random.sample([r for r in rows if r[1] != "none"], 40): print(r)
print("unmatched words:", collections.Counter(w for r in rows for w in r[4]))
