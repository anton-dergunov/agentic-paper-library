---
id: html-boxed-table-as-text
title: A boxed table taken for layout comes out as one line of text
converter: html
takes: [engine, reconvert]
closed: '2026-10-20'
cost: 'engine: done; reconvert the papers with a span tabular'
---

# A boxed table taken for layout comes out as one line of text

`engine` `reconvert` · html · done

**Broken.** A table inside `\resizebox` or another box is built from `<span>`s, and `span_tabulars_to_tables` turns it into a real table unless `is_layout_tabular` takes it for layout: fewer than two cells per row on average. Rows of the tabulars nested in its cells (multi-line cells) count as its own rows, and full-width heading rows count as one cell, so a real table falls under the bar and comes out as one line of text: Qwen3 Table 9 (15 rows, 17 cells), Movie Gen Table 28 (10 rows, 18 cells), Phi-3 Table 6, SummEval Table 1. Phi-3 Table 5 is converted but its header cells, themselves span tabulars, lose their text.

**Fix.** Done 20 Oct 2026: `is_layout_tabular` counts only the outer tabular's own rows (`tabular_widths`), a cell spanning rows counting in each of them, and takes a tabular for a table when most of its rows have two columns or more; one column of lines is still layout. Qwen3 Table 9, Movie Gen Table 28, Phi-3 Table 6 and SummEval Table 1 are tables again. A nested table whose lines are header rows (Phi-3 Table 5's rotated model names) keeps its text: `flatten_cell_tables` reads all of a nested table's rows, head and foot included.

**What it gives.** Tables back as tables: chat templates, metric definitions, benchmark results.

**Cost.** Engine: done; reconvert the papers with a span tabular.

**Examples.** Qwen3 Table 9; Movie Gen Table 28; Phi-3 Tables 5–6; SummEval Table 1.
