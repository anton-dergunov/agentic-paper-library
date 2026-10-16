---
id: pdf-table-bold
title: "Bold in PDF tables is dropped"
converter: pdf
takes: [engine, reconvert, reread]
status: open
cost: "engine: small; reconvert the PDF papers with bold in tables overnight; re-read those where the bold carries a claim"
---

# Bold in PDF tables is dropped

`engine` `reconvert` `reread` · pdf · open

**Broken.** docling keeps a table's text but not its weight, so the bold that marks the best or the significant result is gone. Underlining and grey cells go the same way. When filed, 12 of the 103 read PDF papers reported it.

**Fix.** The text layer still has it: each word carries a font name (`-Bold`, `CMBX`, `SFBX`, `-Medi`). Mark a table cell bold when all its characters in the cell's box are set in a bold font. The hand fixes of 2026-10-16 read it that way with PyMuPDF. Underlining and shading are drawings, not fonts: a short rule under a cell, a filled rectangle behind it (PyMuPDF's `get_drawings`).

**What it gives.** Which result is best or significant, without the PDF: key content where the bold is the paper's claim.

**Cost.** Engine: small; reconvert the PDF papers with bold in tables overnight; re-read those where the bold carries a claim.

**Examples.** "Large-scale validation and analysis of interleaved search evaluation" Table II and "Command A" Tables 7, 12, 14 (restored by hand on 2026-10-16); "Predicting Search Satisfaction Metrics with Interleaved Comparisons" Tables 2 and 4; LambdaLoss Tables 3–4; "Are Neural Rankers still Outperformed by Gradient Boosted Decision Trees" Table 2.
