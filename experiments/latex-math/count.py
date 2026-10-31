# Counts formulas in each run: display ($$…$$), inline ($…$, Pandoc's rule), code spans and
# Unicode that look like maths, and body words.   python3 count.py <results dir>…

import re, sys, pathlib
def stats(t):
    t = re.sub(r'```.*?```', '', t, flags=re.S)
    disp = re.findall(r'\$\$(.+?)\$\$', t, flags=re.S)
    t2 = re.sub(r'\$\$.+?\$\$', '', t, flags=re.S)
    inl = re.findall(r'\$(?![\s$])((?:\\.|[^\\$])+?)(?<![\s\\])\$(?!\d)', t2)
    code = [c for c in re.findall(r'`([^`]+)`', t2) if re.search(r'[=·^√∑≈×]|_[A-Za-z{]', c)]
    uni = re.findall(r'[A-Za-zα-ω]·[A-Za-z]|[√∑∏∈≤≥σπβθ]', re.sub(r'\$.+?\$', '', t2))
    words = len(re.sub(r'^---.*?---', '', t, flags=re.S).split())
    return len(disp), len(inl), len(code), len(uni), words
for run in sys.argv[1:]:
    print(f'== {run}: display, inline, code-span maths, Unicode maths, words')
    for f in sorted(pathlib.Path(run).glob('*.md')):
        t = f.read_text()
        if f.parent.name.startswith('digests'):  # only the digest
            t = t.split('## Digest')[-1].split('## Related')[0]
        print('  %-16s' % f.name[:16], stats(t))
