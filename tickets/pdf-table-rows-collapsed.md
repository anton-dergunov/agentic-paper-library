---
id: pdf-table-rows-collapsed
title: "Rows of a PDF table without rules collapse into one row"
converter: pdf
takes: [engine, reconvert, reread]
status: open
cost: "engine: medium, with a comparison on the papers; reconvert them; re-read where a results table was involved"
---

# Rows of a PDF table without rules collapse into one row

`engine` `reconvert` `reread` · pdf · open

**Broken.** The values of several rows land in one cell, readable only by order, or in the wrong rows. When filed, 18 of the 103 read PDF papers.

**Fix.** Split a cell holding several values when the text layer puts them on separate lines aligned with the row labels, or try the table model MinerU uses on these papers.

**What it gives.** Results tables an agent can read cell by cell; key content where values land in the wrong rows.

**Cost.** Engine: medium, with a comparison on the papers; reconvert them; re-read where a results table was involved.

**Examples.** "Learning to Rank using Gradient Descent" Table 6; "Accuracy at the Top" Table 1; "Reciprocal rank fusion…" Table 1; "Expected Reciprocal Rank for Graded Relevance" Table 2; CatBoost Table 4 (rewritten by hand on 2026-10-16).
