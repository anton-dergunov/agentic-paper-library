"""Run html-to-markdown.py on cached pages, with figure downloads cached on disk.

    [SCRIPTS=<scripts dir>] [HTML=<cached pages>] python3 run.py <out-dir> [stem-substring ...]

SCRIPTS defaults to this repository's scripts/; HTML to ./html, filled by fetch_html.py.
"""
import sys, os, hashlib, importlib.util, io, contextlib
from pathlib import Path
S = Path(__file__).parent
SCRIPTS = os.environ.get('SCRIPTS', str(Path(__file__).resolve().parents[2] / 'scripts'))
HTML = Path(os.environ.get('HTML', S / 'html'))
sys.path.insert(0, SCRIPTS)
import paperlib
CACHE = S / 'fetch-cache'; CACHE.mkdir(exist_ok=True)
_fetch = paperlib.fetch
def cached_fetch(url, *a, **k):
    f = CACHE / hashlib.sha1(url.encode()).hexdigest()
    if f.exists():
        d = f.read_bytes(); return d or None
    d = _fetch(url, *a, **k)
    f.write_bytes(d or b'')
    return d
paperlib.fetch = cached_fetch
spec = importlib.util.spec_from_file_location('h2m', SCRIPTS + '/html-to-markdown.py')
h2m = importlib.util.module_from_spec(spec); spec.loader.exec_module(h2m)
if hasattr(h2m, 'fetch'): h2m.fetch = cached_fetch
out = Path(sys.argv[1]); subs = sys.argv[2:]
for page in sorted(HTML.glob('*.html')):
    stem = page.stem
    if subs and not any(s in stem for s in subs): continue
    d = out / stem; d.mkdir(parents=True, exist_ok=True)
    for f in (d / 'images').glob('*') if (d / 'images').exists() else []: f.unlink()
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        try:
            h2m.main(page, d / 'body.md', d / 'images', stem)
            status = 'ok'
        except BaseException as e:
            status = f'FAIL {e!r}'
    w = len((d / 'body.md').read_text().split()) if (d / 'body.md').exists() else 0
    print(f'{status} {w:6d} words  {stem[:60]}  {err.getvalue().strip()[:200]}', flush=True)
