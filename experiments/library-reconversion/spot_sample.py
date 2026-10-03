"""Draw the spot-check sample: ten HTML papers, six PDF papers with five or more display
equations, four PDF papers with fewer. Run from the library root. Inline in the session;
saved here unchanged."""
import sys,random,re
sys.path.insert(0,'scripts')
from paperlib import LIBRARY_DIR,paper_files,read_paper
random.seed(20261002)
html=[];pdf=[];pdfeq=[]
for md in paper_files():
    meta,body=read_paper(md)
    if meta.get('source')=='html' and meta.get('arxiv'): html.append(md)
    elif meta.get('source')=='pdf-text':
        (pdfeq if len(re.findall(r"^\$\$",body,flags=re.M))>=5 else pdf).append(md)
print("HTML sample:")
for m in random.sample(html,10): print("  ",m.relative_to(LIBRARY_DIR))
print("PDF sample (with equations):")
for m in random.sample(pdfeq,6): print("  ",m.relative_to(LIBRARY_DIR))
print("PDF sample (few equations):")
for m in random.sample(pdf,4): print("  ",m.relative_to(LIBRARY_DIR))
print(len(html),len(pdfeq),len(pdf))
