---
id: html-cell-lines-flattened
title: A cell broken over lines loses its bold, italics, colour and math
converter: html
takes: [engine, reconvert]
closed: '2026-10-18'
cost: 'engine: small, a fixture; reconvert the papers it changes'
---

# A cell broken over lines loses its bold, italics, colour and math

`engine` `reconvert` · html · done

**Broken.** LaTeXML writes a cell broken over lines (`\makecell`, `\shortstack`, `\parbox` with `\\`) as a one-column table inside the cell. `flatten_cell_tables` in `arxiv-html.lua` collapses it to the text of its lines, read with `pandoc.utils.stringify`, which keeps no markup: bold, italics, underlining and the converter's colour marks go, and a formula becomes its bare TeX (`$\bullet$` reads as the word `\bullet`, in "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity"). Counted 17 Oct 2026 over 1,967 arXiv-HTML papers: such cells hold bold in 62 papers (619 cells), math in 24 (264), colour in 15 (160), italics in 13 (47). Found while tracing `html-table-colours`: TRUE's Table 1 sets its red and blue words in these cells.

**Fix.** Done 17 Oct 2026 (`flatten_cell_tables`): the lines are joined from their own inline content, so their bold, italics, marks, formulas and pictures stay; a line that is not text (a list, a table) still gives its text. The 99 library papers with such a cell holding markup were reconverted with the 128 whose colour marks changed (213 in all, all `ok`, 178 changed): no word lost, 0.52% more characters; `macro-name` symptoms 12 → 1, the bare TeX names now formulas again (`\bullet`, `\times 128`, `\sim 1800`); pictures in such cells, dropped without a trace before, are back: 49 in BigGAN's sample grids, 45 in GME's examples, 2 in Knowledge Graphs. → [`experiments/colour-parts-and-cell-lines`](../experiments/colour-parts-and-cell-lines/README.md)

**What it gives.** The emphasis and formulas of multi-line cells, which are often a table's labels and examples.

**Cost.** Engine: small, a fixture; reconvert the papers it changes.

**Examples.** TRUE: Re-evaluating Factual Consistency Evaluation, Table 1 (red and blue spans); Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity (`\bullet`).
