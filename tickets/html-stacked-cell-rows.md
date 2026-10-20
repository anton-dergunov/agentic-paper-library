---
id: html-stacked-cell-rows
title: "Rows stacked inside cells come out as one row"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: medium, fixtures from the papers below; reconvert the papers"
---

# Rows stacked inside cells come out as one row

`engine` `reconvert` · html · open

**Broken.** Some authors set several rows as one, each cell a one-column `tabular` (or `\makecell`) with one line per sub-row: PaLM 2 Table 1 has the four model sizes stacked in each cell of a FLOPs row, the GRU paper's Table 2 has train over test. `flatten_cell_tables` joins each cell's lines with spaces, so a row reads "2.488 2.404 2.400 2.406" and the reader has to count positions to match values across columns.

**Fix.** Where all or most cells of a row are stacked lines and the stacks have the same height, split the row into that many rows, line by line. Cells with a single line (a shared label) span the new rows. A stack in a single cell stays a multi-line cell, as now.

**What it gives.** One value per cell, readable by column.

**Cost.** Engine: medium, fixtures from the papers below; reconvert the papers.

**Examples.** PaLM 2 Table 1; "Is Stack Overflow Obsolete?" Tables 2–3; "State of What Art?" Table 2; "Empirical Evaluation of Gated Recurrent Neural Networks" Table 2; "Autoencoding Variational Inference For Topic Models" Table 6.
