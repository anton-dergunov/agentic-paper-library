#!/usr/bin/env python3
"""Count what each conversion kept: equations and tables.

    python3 count.py <dir>

<dir> holds, for each paper <n> in dpo, simpo, zep, three conversions:
<n>_html.md (arXiv HTML through pandoc), <n>_pdftext.md (PyMuPDF text) and
<n>_p4llm.md (pymupdf4llm). As run on 29 Sep 2026, except that the directory
became an argument (the original ran in the working directory).

- Display equations in the HTML conversion: pandoc's gfm "``` math" blocks.
- Inline math in the HTML conversion: "$`" openers.
- Equation numbers still present in a PDF conversion: distinct "(k)", 0 < k < 40,
  at the end of a line. A proxy: an equation whose number survives is at least
  partly present; one whose number is gone is usually gone entirely.
- Tables: markdown delimiter rows ("|---|---|"), one per table or per header
  row, so the number is a rough count rather than an exact one.
"""
import re
import sys
from pathlib import Path

d = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
for n in ["dpo", "simpo", "zep"]:
    html = (d / f"{n}_html.md").read_text(); pt = (d / f"{n}_pdftext.md").read_text(); p4 = (d / f"{n}_p4llm.md").read_text()
    disp = len(re.findall(r"^``` math", html, re.M))
    inline = len(re.findall(r"\$`", html))
    # numbered equations: "(k)" at end of a line, k up to 40
    def eqnums(t): return sorted({int(m) for m in re.findall(r"\((\d{1,2})\)\s*$", t, re.M) if 0<int(m)<40})
    h_tab = len(re.findall(r"^\|[-| :]+\|\s*$", html, re.M))
    p4_tab = len(re.findall(r"^\|[-| :]+\|\s*$", p4, re.M))
    print(f"{n}: HTML display eqs={disp}, inline math={inline}, tables={h_tab} | "
          f"pdftext eq-numbers found={len(eqnums(pt))} | p4llm eq-numbers found={len(eqnums(p4))}, tables={p4_tab}")
