---
id: pdf-table-as-picture
title: "PDF tables taken for pictures, and figures for tables"
converter: pdf
takes: [engine, reconvert, reread]
status: open
cost: "engine: small to medium; reconvert the papers with such tables; re-read those whose results are in them"
---

# PDF tables taken for pictures, and figures for tables

`engine` `reconvert` `reread` · pdf · open

**Broken.** docling labels a whole table a picture, so the markdown keeps only its image under the "Table N" caption, and an agent reads no numbers at all. When filed, two papers, both with their results tables lost.

**Fix.** When a region labelled a picture carries a "Table N" caption, pass it to the table route instead: the table-structure model where the PDF has a text layer under it, the OCR route of `pdf-table-image-ocr` where it has none.

**Found 19 Oct 2026.** ROUGE's tables (pp. 5–7) have their text in the text layer, so no OCR is needed, but PyMuPDF's own `find_tables` collapses their rows into one cell per column (tried on the random-walk paper's Table 2, p. 7). A good fix runs docling's table-structure model on the picture's region, which docling's pipeline does not offer for one region: a design question, left open.

**Found 20 Oct 2026: the reverse.** docling labels a figure of word lists a table, so its words come out as a table with words in the wrong rows and topic numbers fused into them ("year 6"), after the figure's image or in place of it. The same rule the other way: a region labelled a table under a "Figure N" caption stays a picture.

**What it gives.** Results tables back as text, where the findings rest on them.

**Cost.** Engine: small to medium; reconvert the papers with such tables; re-read those whose results are in them.

**Examples.** ROUGE Tables 1–3 (pp. 5–7); "Unsupervised Random Walk Sentence Embeddings" Table 2 (p. 7). The reverse: "Probabilistic Topic Models" Figures 2 and 3 (pp. 2–6).
