"""Count the fenced code blocks a candidate converter writes for every pdf-text paper.

    python3 codeblock_census.py <scripts dir> [<out.tsv>]

<scripts dir> holds the candidate pdf-to-markdown.py and paperlib.py. Converts
each `source: pdf-text` paper's PDF in memory (nothing is written to the
library), prints the papers with the most blocks and the start of each one's
first block, and writes "<blocks>\t<paper>" per paper to <out.tsv>. Used to find
false positives by reading the top of the list.
"""
import sys, importlib.util, re
from pathlib import Path
SCRIPTS = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(SCRIPTS))
spec=importlib.util.spec_from_file_location('p2m', SCRIPTS / 'pdf-to-markdown.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from paperlib import paper_files, read_paper, pdf_path_for
rows=[]
for p in paper_files():
    if read_paper(p)[0].get('source')!='pdf-text': continue
    out=m.convert(pdf_path_for(p))
    blocks=re.findall(r'```text\n(.*?)\n```', out, re.S)
    rows.append((len(blocks), p.name[:55], blocks[:1]))
rows.sort(reverse=True)
print('papers with code blocks:', sum(1 for r in rows if r[0]), 'total blocks:', sum(r[0] for r in rows))
for n,name,b in rows[:12]: print(n, name, '|', (b[0][:120].replace('\n',' ⏎ ') if b else ''))
if len(sys.argv) > 2:
    open(sys.argv[2],'w').write('\n'.join(f'{n}\t{name}' for n,name,_ in rows))
