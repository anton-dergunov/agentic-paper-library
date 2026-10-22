---
id: html-incomplete
title: arXiv's HTML is incomplete
converter: html
takes: [engine, reconvert, reread]
status: fixed
cost: 'engine: medium, with a measurement; reconvert the papers at PDF speed; re-read them (about $0.30
  each)'
---

# arXiv's HTML is incomplete

`engine` `reconvert` `reread` · html · fixed

**Broken.** arXiv's rendering lacks pages of the paper: when filed, 27 papers missed eight pages or a quarter of the paper, and `paperlib symptoms --pages` listed 73 missing three pages or more. `paperlib reconvert` cannot convert a `source: html` paper from its PDF. Parts can be missing as well as pages: in "Knowledge Graphs" every inline TikZ drawing of nodes and edges (781 of them, including the RDFS/OWL axioms and examples of Tables 2–6) is an empty `<svg>` in arXiv's HTML, which the markdown links as a blank image.

**Fix.** Convert only the pages the HTML lacks from the PDF and splice them into the HTML conversion, rather than the whole paper (`--from-pdf`): for the pages it has, the HTML holds every equation exactly, where the PDF route reads 71% of them close. The LaTeX source route stays the by-hand one it is ([`experiments/latex-source`](../experiments/latex-source/README.md)).

Fixed 22 Oct 2026 (`scripts/missing-pages.py`; `convert_pages` in `pdf-to-markdown.py`), run after the page and caption passes on every arXiv-HTML conversion. The pages `missing_pages` flags, and a page with little text between two of them, are converted by layout analysis with the model reading equations; a page with under 100 words outside its pictures and captions is left out, since the HTML has the picture. Each run goes before the first heading on a later page, the reference list counting as on its PDF page, between `<!-- pp. N–M from the PDF, not in arXiv's HTML … -->` and `<!-- end of pp. N–M from the PDF -->`; the guide tells agents to treat it as a PDF conversion. Checked on Qwen3-VL, Beyond Memorization, Influence Functions, Absolute Zero, Training Agents and QASC: the five that lacked 2–98 pages lack none, but Influence Functions' six boxes of influential sequences, which docling reads as pictures; 95,000 words added, KaTeX parses all 370 formulas in them; QASC's four flagged pages are screenshots and are left out. Pages left out get a marker, and the missing-page measure skips the pages the splice handled, so `paperlib read --clean` reads a spliced paper. A reference list the HTML has only in part (Sparks lists 27 of the PDF's entries) is found by its heading on the first PDF page after the HTML's last placed heading. Eight new checks, two of them for flaws of the PDF converter found on the way: a caption kept twice, once with the marks and mathematics read from the page, and a running header taken for a heading. → [`experiments/html-missing-pages`](../experiments/html-missing-pages/README.md)

The other records filed here were not missing pages: 12 were the paper's own text as the PDF prints it, or a mistaken record (deleted); BIRD Table 4 and the memory-security survey's Table 3 are in an appendix the reading view leaves out, which it now names; four are wont-fix (a run-in heading, a contents list, colour lost in Confident Learning's hand conversion); Knowledge Graphs' empty inline TikZ drawings are re-filed as new (`html-inline-tikz-empty`). Confident Learning stays converted by hand.

**What it gives.** The whole paper readable; today an agent answering about the missing part must open the PDF.

**Cost.** Engine: medium, with a measurement; reconvert the papers at PDF speed; re-read them (about $0.30 each).

**Examples.** GPT-4 Technical Report (no System Card); "Studying Large Language Model Generalization with Influence Functions" (ends at §2.1); "Sparks of Artificial General Intelligence" (ends at §3.1.2); "Training Agents Inside of Scalable World Models" (ends in §4.2); Absolute Zero (pp. 29–50).
