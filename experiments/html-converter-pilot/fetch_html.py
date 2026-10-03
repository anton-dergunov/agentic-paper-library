"""Cache arXiv HTML (at the PDF's version) for papers listed in a TSV: id, source, md path."""
import sys, time, importlib.util
from pathlib import Path
SCRIPTS = str(Path(__file__).resolve().parents[2] / 'scripts')
sys.path.insert(0, SCRIPTS)
spec = importlib.util.spec_from_file_location('reconvert', SCRIPTS + '/reconvert.py')
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
from paperlib import pdf_path_for
out = Path(sys.argv[2])
for line in open(sys.argv[1]):
    aid, src, md = line.rstrip('\n').split('\t')
    md = Path(md).resolve()
    dest = out / (md.stem + '.html')
    if dest.exists() or not aid: continue
    v = rc.pdf_version(pdf_path_for(md), aid)
    page = rc.fetch_page(f'https://arxiv.org/html/{aid}{v}')
    if v and (not page or 'ltx_page_content' not in page):
        page = rc.fetch_page(f'https://arxiv.org/html/{aid}')
    if page and 'ltx_page_content' in page:
        dest.write_text(page, encoding='utf-8'); print('ok', aid, v, flush=True)
    else:
        print('none', aid, v, flush=True)
    time.sleep(1)
