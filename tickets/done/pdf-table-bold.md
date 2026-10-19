---
id: pdf-table-bold
title: Bold in PDF tables is dropped
converter: pdf
takes: [engine, reconvert, reread]
closed: '2026-10-19'
cost: 'engine: small; reconvert the PDF papers with bold in tables overnight; re-read those where the
  bold carries a claim'
---

# Bold in PDF tables is dropped

`engine` `reconvert` `reread` · pdf · done

**Broken.** docling keeps a table's text but not its weight, so the bold that marks the best or the significant result is gone. Underlining and grey cells go the same way. When filed, 12 of the 103 read PDF papers reported it.

**Fix.** Done 19 Oct 2026: a docling table cell is bold or italic when every letter and digit under its box is set in such a font (`-Bold`, `-Medi`, `CMBX`, `SFBX`, or the span's bold flag), and underlined when a drawn rule lies just under its text and ends within 4 pt of its ends (table rules, `\cmidrule`s and Word's per-cell borders run past them); header cells and a mark every body cell has stay plain. Checked on Glorot & Bengio Table 1, LambdaLoss Tables 3–4, Interleaved Comparisons Tables 2 and 4, GPT-1 and DSSM. Left: grey shading (filled rectangles behind cells), and a header row docling does not flag comes out bold. → [`experiments/pdf-equation-retry-and-table-marks`](../experiments/pdf-equation-retry-and-table-marks/README.md)

**What it gives.** Which result is best or significant, without the PDF: key content where the bold is the paper's claim.

**Cost.** Engine: small; reconvert the PDF papers with bold in tables overnight; re-read those where the bold carries a claim.

**Examples.** "Large-scale validation and analysis of interleaved search evaluation" Table II and "Command A" Tables 7, 12, 14 (restored by hand on 2026-10-16); "Predicting Search Satisfaction Metrics with Interleaved Comparisons" Tables 2 and 4; LambdaLoss Tables 3–4; "Are Neural Rankers still Outperformed by Gradient Boosted Decision Trees" Table 2.
