---
id: html-cell-lines-run-together
title: Lines stacked in one cell run together with spaces
converter: html
takes: [engine, reconvert]
closed: '2026-10-22'
cost: 'engine: small; reconvert the papers with such cells'
---

# Lines stacked in one cell run together with spaces

`engine` `reconvert` · html · done

**Broken.** A cell that lists several items on separate lines (`\makecell`, `\shortstack`, a nested tabular) is joined with spaces when the row is not split. `html-stacked-cell-rows` (done) splits a row only when most of its cells stack to the same height. Otherwise the items read as one phrase, and where items are several words long their boundaries are lost:

- "GSM8K GaoKao MATH-500" (Stop Overthinking Table 1);
- RAGAS's "Context Relevance Faithfulness Answer Relevance" against "\* Cosine Similarity" (RAG survey Table IV), so which metric goes with which aspect is unclear;
- "Top-1 Acc. IoU" over "92.8 85.9" (Transformers in Vision Table II);
- "LDA NVLDA" as one header (Autoencoding VI Table 6).

**Fix.** In `flatten_cell_tables`, join a stack that stays in one cell with `<br>` rather than a space, in pipe and HTML tables alike. Check that the matching of hand corrections and `paperlib symptoms` read `<br>` as a line break.

Done 22 Oct 2026 ([experiment](../experiments/cell-lines-and-unreached-spans/README.md)), not in `flatten_cell_tables`: most stacks are one-column span tabulars, which `is_layout_tabular` leaves as spans, so the Lua filter never sees a table. A new pass, `break_cell_lines`, after `mark_shading`, marks the breaks between a body cell's lines (a stack left whole, a parbox's `ltx_p` lines, a `\\`), and the Lua filter writes each as a raw `<br>`, which keeps a pipe table one; a `\\` that pandoc read as a line break had written the table as HTML. Lines that read as one text (`reads_as_one`, shared with `split_stacked_rows`, or a lower line opening "for", "of", "or"…) join with a space, as do a header's (the rows the Lua filter makes the head); in a one-column table every line stays. In a framed box `spans_to_blocks` no longer turns a cell's lines into paragraphs. Hand corrections read `<br>` as a space (`_norm_line`); `symptoms` already did. Checked on Stop Overthinking, the RAG survey, Transformers in Vision and Autoencoding VI; the RAG survey's "\* Cosine Similarity" now reads "\*<br>Cosine Similarity", as the PDF prints it.

**What it gives.** Lists in cells whose items can be told apart and matched across columns.

**Cost.** Engine: small; reconvert the papers with such cells (a scan of the cache counts them).

**Examples.** Stop Overthinking Tables 1, 3 (pp. 6–8); "Evaluation of Retrieval-Augmented Generation. A Survey" Table 1 (p. 6); "Retrieval-Augmented Generation for Large Language Models. A Survey" Table IV (p. 14); "Autoencoding Variational Inference For Topic Models" Table 6; "Transformers in Vision" Table II; "Is Stack Overflow Obsolete" Table 3.
