"""Compare two page-map.py versions on copies of Larimar, Memanto and 80 random papers.

    git show d791f1a^:scripts/page-map.py > page-map-old.py
    python3 pm_compare.py page-map-old.py      # run from the library's root

Prints the papers whose heading lines differ, and the totals of headings placed
and numbered headings left unplaced by each version.
"""
import sys, random, re, shutil, subprocess, tempfile
SCRIPTS = str(Path(__file__).resolve().parents[2] / 'scripts')
sys.path.insert(0, SCRIPTS)
from pathlib import Path
from paperlib import paper_files, read_paper, pdf_path_for
OLD = Path(sys.argv[1]).resolve()
S = Path(tempfile.mkdtemp())
papers = [p for p in paper_files() if read_paper(p)[0].get('source') == 'html']
random.seed(3)
sample = [p for p in papers if p.stem.startswith(('Larimar', 'Memanto'))] + random.sample(papers, 80)
tot = {'old': [0, 0], 'new': [0, 0]}
diffs = 0
for md in sample:
    pdf = pdf_path_for(md)
    if not pdf.exists(): continue
    res = {}
    for which, script in (('old', OLD), ('new', Path(SCRIPTS) / 'page-map.py')):
        tmp = S / f'pm-{which}.md'; shutil.copy(md, tmp)
        out = subprocess.run([sys.executable, script, pdf, tmp], capture_output=True, text=True).stdout
        m = re.search(r'(\d+) headings placed, (\d+) numbered headings unplaced', out)
        res[which] = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
        tot[which][0] += res[which][0]; tot[which][1] += res[which][1]
        res[which + '_lines'] = [l for l in tmp.read_text().split('\n') if l.startswith('#')]
    changed = [(a, b) for a, b in zip(res['old_lines'], res['new_lines']) if a != b]
    if changed:
        diffs += 1
        print(f"{md.stem[:50]}: old {res['old']} new {res['new']}")
        for a, b in changed[:4]:
            print(f'    {a[:70]}\n -> {b[:70]}')
print('totals placed/unplaced', tot, 'papers changed', diffs)
