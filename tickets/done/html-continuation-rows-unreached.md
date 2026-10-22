---
id: html-continuation-rows-unreached
title: Cells continued on a new row that the merge does not reach
converter: html
takes: [engine, reconvert]
closed: '2026-10-22'
cost: 'engine: small to medium, a fixture per table below; reconvert the papers'
---

# Cells continued on a new row that the merge does not reach

`engine` `reconvert` · html · done

**Broken.** Some tables are still left wrong after `html-continuation-rows` (done 21 Oct 2026): a cell the author continued on a new row keeps that row of its own.

- In two-column tables, the description column's second line is a row with an empty first cell. In Ray Table 1 that row also joins two API entries under one description: one column of text in two is "text in most columns", so the row is kept.
- Two-line column headers are split over two rows and shifted: Reflexion's "Test execution" lands in the row-label column, and Entropic OOD's Tables I and VI have the same fault.
- A row-spanning cell is split over the rows it spans: Foundation Agents Table 8.1's Definition cells, and the serving survey's "References" and "LLM Applications" cells with their label in pieces.

**Fix.** Trace each table through `merge_continuation_rows`, see which condition keeps the row, and add a fixture for each. In a two-column table, a row whose first cell is empty and whose second continues the sentence above (no capital, no full stop before it) is a continuation.

Done 22 Oct 2026 ([experiment](../experiments/cell-lines-and-unreached-spans/README.md)). Four causes, each with a fixture. A sentence wrapped onto the next row joins in any table: five words or more above, not ended, ending in a word or a comma, and below a word in lower case or a formula (Ray; a fragment with a formula was always kept before). A row most of whose fragments go on from the cells above (an upper ending in a comma, "and" and the like, or a wrapped sentence; not a bracket, which icons read as "[times]" also are) joins though it fills more than half the columns, its label too (the serving survey's "References" and "LLM" / "Applications"). The second line of an entry whose other cells span both rows joins when a fragment goes on (Foundation Agents); a fragment that does not read on is kept as a line with `<br>`. `span_header_rows` takes a header of four rows when the fourth holds no results and now reads tables with a stack in a cell (Entropic Table VI). Not converter faults: Reflexion's second header row puts "Test execution" under "Approach" in the source and the PDF, and Entropic Table I lays each technique over four rows beside two-line values, which read in order. Ray's two API entries under one description are printed that way.

**What it gives.** One row per entry, its text whole.

**Cost.** Engine: small to medium, a fixture per table below; reconvert the papers.

**Examples.** "Ray. A Distributed Framework for Emerging AI Applications" Table 1 (pp. 2–3); Reflexion p. 3; "Entropic Out-of-Distribution Detection" Tables I, VI; "Advances and Challenges in Foundation Agents" Table 8.1 (p. 136); "Towards Efficient Generative Large Language Model Serving" Table 1 (pp. 8–10).
