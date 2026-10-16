---
id: pdf-table-structure
title: "PDF tables with a garbled header or merged columns"
converter: pdf
takes: [engine, reconvert]
status: open
cost: "unknown until its sub-causes are found"
---

# PDF tables with a garbled header or merged columns

`engine` `reconvert` · pdf · open

**Broken.** A table of a PDF paper keeps its rows but loses its header structure: column labels merged, flattened into one cell, or lost; sometimes the whole table becomes loose paragraphs. Unlike `pdf-table-rows-collapsed`, the rows are right.

**Fix.** Not known yet: a catch-all. Compare docling's table model with MinerU's on these papers, together with `pdf-table-rows-collapsed`.

**What it gives.** Which column a number belongs to, without counting; key content in a few results tables.

**Cost.** Unknown until its sub-causes are found.

**Examples.** "Term Frequency Normalisation Tuning for BM25 and DFR Models" Tables 2–9; "Elucidating the Design Space of Diffusion-Based Generative Models" Table 2; GPT-2 Table 1.
