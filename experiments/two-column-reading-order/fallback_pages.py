"""How often the column regions are rejected and a page falls back to the plain sort.

    python3 fallback_pages.py <scripts dir>

<scripts dir> holds the candidate pdf-to-markdown.py and paperlib.py (for the paper
list, frontmatter and PDF paths). Runs page_text on every page of every
`source: pdf-text` paper's PDF and counts the pages where it returned the plain
position-sorted text. Writes nothing.
"""
import sys, importlib.util
from pathlib import Path
SCRIPTS = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(SCRIPTS))
spec=importlib.util.spec_from_file_location('p2m', SCRIPTS / 'pdf-to-markdown.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from paperlib import paper_files, read_paper, pdf_path_for
import pymupdf
tot_pages=0; papers=0; fb_papers=[]
for p in paper_files():
    if read_paper(p)[0].get('source')!='pdf-text': continue
    papers+=1; fb=0; n=0
    doc=pymupdf.open(pdf_path_for(p))
    for page in doc:
        n+=1
        plain=page.get_text('text',sort=True); t=m.page_text(page)
        if t==plain: fb+=1
    tot_pages+=n
    if fb/n>0.5: fb_papers.append((p.name[:60], fb, n))
print(papers,'papers',tot_pages,'pages; >50% pages fell back:',len(fb_papers))
for x in fb_papers[:15]: print(x)
