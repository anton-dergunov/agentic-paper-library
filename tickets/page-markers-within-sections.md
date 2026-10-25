---
id: page-markers-within-sections
title: "A page marker gives a section's first page, so a table or figure deeper in the section is cited early"
converter: any
takes: [engine, reconvert]
status: open
cost: "engine: medium (place captions, perhaps paragraphs, on PDF pages in page-map.py); measure the tokens and the citations on real papers; reconvert the library"
---

# A page marker gives a section's first page, so a table or figure deeper in the section is cited early

`engine` `reconvert` · any · open

**Broken.** Only headings carry `(p. N)`, the page the section starts on. A table or figure that LaTeX floats to a later page, or that sits in a long section, has no page of its own, so an agent cites the section's page for it. The library's reviews cite Self-Instruct's Table 2 at p. 4 (printed on p. 5), Memory-R1's Tables 1 and 5 at pp. 5 and 17 (printed on 6 and 18), and OLMo 2's Table 8 at p. 18 (printed on 19); in each the table sits under a heading whose marker is one page earlier (found while checking the golds of the reading-formats experiment, tier D, 25 Oct 2026). A scan of 137 random papers (25 Oct 2026; a caption matched to the one PDF page that prints a line starting "Table N:" or "Figure N."): of 1,861 captions placed, 632 print on their heading's page, 819 one page later, 405 two or more pages later, 5 earlier; 127 of the 137 papers have at least one caption off its heading's page.

**Fix.** In `page-map.py`, place each caption on the PDF page that prints it, and add the page to the caption when it differs from its heading's (`Table 2: … (p. 5)`). Then measure whether paragraph-level markers at page breaks inside long sections are worth their tokens (about six a page): an agent's citations of prose facts suffer the same way, but less visibly than a table's.

**What it gives.** Citations of tables and figures that point to the page the reader must open, in answers, notes and reviews.

**Cost.** Engine: medium; reconvert the library (page maps only, no model requests). Measure on real papers: tokens added, and how often answers' and reviews' page citations become exact.

**Examples.** "Self-Instruct. Aligning Language Models with Self-Generated Instructions" Table 2 (§3.3 p. 4, printed p. 5); "Memory-R1" Table 1 (p. 6) and Table 5 (p. 18); "2 OLMo 2 Furious" Table 8 (§4.1 p. 18, printed p. 19); "The Disagreement Problem in Explainable Machine Learning" Figures 2–3 (§ p. 7, printed p. 9).
