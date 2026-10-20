---
id: html-table-structure
title: "arXiv-HTML tables flattened, shifted or split"
converter: html
takes: [engine, reconvert]
status: open
cost: "unknown until its sub-causes are found"
---

# arXiv-HTML tables flattened, shifted or split

`engine` `reconvert` · html · open

**Broken.** A table from arXiv's HTML arrives with its header spans shifted, rows split or merged, cells out of place, or a stray character in a cell; most stay readable by order.

**Fix.** Not known yet. Split on 2026-10-20 into `html-table-head-rows`, `html-row-span-heuristics`, `html-multirow-lost`, `html-stacked-cell-rows`, `html-continuation-rows`, `html-boxed-table-as-text`, `html-table-panels` and `html-cell-attachments`; what is left here are single records with no second paper of the same cause yet (a garbled header in a book chapter, a legend set as a table, a header group flattened in a wide minipage table) and doubts about values the HTML may or may not share. File a new table record under one of those tickets first.

**What it gives.** Tables an agent can read cell by cell instead of by order.

**Cost.** Unknown until its sub-causes are found.

**Examples.** "Introduction to Multi-Armed Bandits" Table 4.1 (header garbled); T5 Table 16 (group headers misaligned); Cambrian-1 Fig. 9 (a legend set as a table).
