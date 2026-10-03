"""Numeric pipe-table cells of the sampled PDF papers that occur in the PDF's text layer.

    python3 spot_tables.py <dir holding spot-pdf.txt>

Inline in the session; saved here without its last part, which printed one table and
rendered the PDF page holding it for a look by eye."""
import sys,re
sys.path.insert(0,'scripts')
from paperlib import LIBRARY_DIR,read_paper,pdf_path_for
import pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
S=sys.argv[1]
tot=found=0
for rel in [l.strip() for l in open(f"{S}/spot-pdf.txt") if l.strip()]:
    md=LIBRARY_DIR/rel; meta,body=read_paper(md); doc=pymupdf.open(pdf_path_for(md))
    text=re.sub(r"\s+","","".join(p.get_text() for p in doc)).replace("−","-")
    cells=[c.strip() for row in re.findall(r"^\|.*\|$",body,flags=re.M) for c in row.strip("|").split("|")]
    nums=[c for c in cells if re.fullmatch(r"[-+]?\d[\d.,]*%?",c) and len(c)>=3]
    ok=sum(c.replace(" ","") in text for c in nums)
    tot+=len(nums); found+=ok
    print(f"{ok:4d}/{len(nums):4d} numeric table cells found in the PDF text | {md.stem[:60]}")
print("total",found,"/",tot)
