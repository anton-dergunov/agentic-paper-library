---
id: html-stacked-cell-rows
title: Rows stacked inside cells come out as one row
converter: html
takes: [engine, reconvert]
closed: '2026-10-22'
cost: 'engine: medium, fixtures from the papers below; reconvert the papers'
---

# Rows stacked inside cells come out as one row

`engine` `reconvert` · html · done

**Broken.** Some authors set several rows as one, each cell a one-column `tabular` (or `\makecell`) with one line per sub-row: PaLM 2 Table 1 has the four model sizes stacked in each cell of a FLOPs row, the GRU paper's Table 2 has train over test. `flatten_cell_tables` joins each cell's lines with spaces, so a row reads "2.488 2.404 2.400 2.406" and the reader has to count positions to match values across columns.

**Fix.** Where all or most cells of a row are stacked lines and the stacks have the same height, split the row into that many rows, line by line. Cells with a single line (a shared label) span the new rows. A stack in a single cell stays a multi-line cell, as now.

**Done (2026-10-22).** `split_stacked_rows` in html-to-markdown.py splits a row when at least two cells, and at least half of the filled ones, are pure stacks (a one-column tabular and nothing but its wrappers) of the same height, one of them all numbers; a one-line cell, a cell spanning the row from above, and a stack that reads as one wrapped text (a value over its "(+0.0)" gain, a label over "(DDPG)", a list going on after a comma) span the new rows. Header rows (the first, the `<thead>`, column titles) keep their lines. Measured on all 1,954 cached library papers: 5 change, all correctly (PaLM 2 Table 1, GRU Table 2, "State of What Art" Table 2, Stack Overflow Table 2, Deep RL that Matters); the digit-only and wrapped-text guards removed false splits in CutMix, Swin V2, Inverse Scaling, AgentInstruct and "Stop Overthinking". Not covered, re-filed as `new` for triage: stacks of unequal height (Stack Overflow Table 3, `html-stacked-rows-uneven`), a lone stack whose lines run together (AVITM, the RAG surveys, "Stop Overthinking", Transformers in Vision Table II, `html-cell-lines-run-together`), and a cell's text split over extra rows, the opposite fault (Foundation Agents, Reflexion, Ray, LiRank, LLM serving survey, `html-cell-split-over-rows`).

**What it gives.** One value per cell, readable by column.

**Cost.** Engine: medium, fixtures from the papers below; reconvert the papers.

**Examples.** PaLM 2 Table 1; "Is Stack Overflow Obsolete?" Tables 2–3; "State of What Art?" Table 2; "Empirical Evaluation of Gated Recurrent Neural Networks" Table 2; "Autoencoding Variational Inference For Topic Models" Table 6.
