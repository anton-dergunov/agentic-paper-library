"""Sort the library's SVG figures that hold text: box, badge, diagram with text, image.

    python3 classify.py      # run from the library's root; prints counts and samples
"""
import sys, re, glob, random, collections, importlib.util
from pathlib import Path
SCRIPTS = str(Path(__file__).resolve().parents[2] / 'scripts')
sys.path.insert(0, SCRIPTS)
spec = importlib.util.spec_from_file_location('h', SCRIPTS + '/html-to-markdown.py')
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
def classify(svg):
    blocks = h.foreign_objects(svg)
    counts = [h.words(b) for b in blocks]
    total = sum(counts)
    paths = len(re.findall(r"<path\b", svg))
    m = re.match(r"<svg\b[^>]*?\bheight=\"([\d.]+)", svg.lstrip()[svg.lstrip().find('<svg'):] if '<svg' in svg else svg)
    height = float(m.group(1)) if m else 1000
    if total and total < 8 and len(blocks) <= 2 and paths <= 4 and height < 25: return 'badge'
    if not ((paths <= 6 and len(blocks) <= 4 and total >= 6) or (counts and max(counts) >= 12 and max(counts) >= 0.6 * total)): return 'image'
    return 'diagram+text' if paths > 15 else 'box'
def text(svg):
    t = re.sub(r'<annotation\b.*?</annotation>', ' ', svg, flags=re.S)
    return ' '.join(re.sub(r'<[^>]+>', ' ', t).split())
def _report():
    rows = []
    for f in glob.glob('library/**/images/*.svg', recursive=True):
        s = Path(f).read_text(errors='replace')
        if 'foreignobject' not in s.lower(): continue
        s = s[s.find('<svg'):]
        rows.append((classify(s), f, s))
    c = collections.Counter(r[0] for r in rows); print(c)
    random.seed(7)
    for cls in ('box', 'diagram+text', 'badge'):
        print('=====', cls)
        for k, f, s in random.sample([r for r in rows if r[0] == cls], 12):
            print(f'  [{Path(f).name[:45]}] {text(s)[:110]}')
    print('===== image with text')
    cand = []
    for k, f, s in rows:
        if k != 'image': continue
        counts = [h.words(b) for b in h.foreign_objects(s)]
        if counts and max(counts) >= 6: cand.append((max(counts), sum(counts), len(counts), len(re.findall(r'<path\b', s)), f, s))
    print(len(cand))
    for mx, tot, n, paths, f, s in random.sample(cand, 15):
        print(f'  max={mx} tot={tot} fos={n} paths={paths} [{Path(f).name[:40]}] {text(s)[:90]}')

if __name__ == "__main__":
    _report()
