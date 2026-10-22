---
id: html-cell-lines-run-together
title: "Lines stacked in one cell run together with spaces"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small; reconvert the papers with such cells"
---

# Lines stacked in one cell run together with spaces

`engine` `reconvert` · html · open

**Broken.** A cell that lists several items on separate lines (`\makecell`, `\shortstack`, a nested tabular) is joined with spaces when the row is not split. `html-stacked-cell-rows` (done) splits a row only when most of its cells stack to the same height. Otherwise the items read as one phrase, and where items are several words long their boundaries are lost:

- "GSM8K GaoKao MATH-500" (Stop Overthinking Table 1);
- RAGAS's "Context Relevance Faithfulness Answer Relevance" against "\* Cosine Similarity" (RAG survey Table IV), so which metric goes with which aspect is unclear;
- "Top-1 Acc. IoU" over "92.8 85.9" (Transformers in Vision Table II);
- "LDA NVLDA" as one header (Autoencoding VI Table 6).

**Fix.** In `flatten_cell_tables`, join a stack that stays in one cell with `<br>` rather than a space, in pipe and HTML tables alike. Check that the matching of hand corrections and `paperlib symptoms` read `<br>` as a line break.

**What it gives.** Lists in cells whose items can be told apart and matched across columns.

**Cost.** Engine: small; reconvert the papers with such cells (a scan of the cache counts them).

**Examples.** Stop Overthinking Tables 1, 3 (pp. 6–8); "Evaluation of Retrieval-Augmented Generation. A Survey" Table 1 (p. 6); "Retrieval-Augmented Generation for Large Language Models. A Survey" Table IV (p. 14); "Autoencoding Variational Inference For Topic Models" Table 6; "Transformers in Vision" Table II; "Is Stack Overflow Obsolete" Table 3.
