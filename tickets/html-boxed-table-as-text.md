---
id: html-boxed-table-as-text
title: "A boxed table taken for layout comes out as one line of text"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small, a fixture; reconvert the papers with a span tabular"
---

# A boxed table taken for layout comes out as one line of text

`engine` `reconvert` · html · open

**Broken.** A table inside `\resizebox` or another box is built from `<span>`s, and `span_tabulars_to_tables` turns it into a real table unless `is_layout_tabular` takes it for layout: fewer than two cells per row on average. Rows of the tabulars nested in its cells (multi-line cells) count as its own rows, and full-width heading rows count as one cell, so a real table falls under the bar and comes out as one line of text: Qwen3 Table 9 (15 rows, 17 cells), Movie Gen Table 28 (10 rows, 18 cells), Phi-3 Table 6, SummEval Table 1. Phi-3 Table 5 is converted but its header cells, themselves span tabulars, lose their text.

**Fix.** Count only the outer tabular's own rows and cells, and let a table with at least two columns in most rows pass. Convert a nested span tabular in a cell the way `flatten_cell_tables` treats a nested table.

**What it gives.** Tables back as tables: chat templates, metric definitions, benchmark results.

**Cost.** Engine: small, a fixture; reconvert the papers with a span tabular.

**Examples.** Qwen3 Table 9; Movie Gen Table 28; Phi-3 Tables 5–6; SummEval Table 1.
