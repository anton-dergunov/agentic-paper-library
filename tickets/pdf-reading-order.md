---
id: pdf-reading-order
title: "Text of a PDF paper out of reading order"
converter: pdf
takes: [engine, reconvert]
status: open
cost: "unknown until its sub-causes are found"
---

# Text of a PDF paper out of reading order

`engine` `reconvert` · pdf · open

**Broken.** docling places text out of order: the introduction before the abstract on a two-column first page, a caption a paragraph away from its float, a figure's labels spilled into the prose.

**Fix.** Not known yet: a catch-all, partly a known limitation of docling (docs/conversion.md). Candidates: move a caption next to its float; drop text that sits inside a figure's box.

**What it gives.** Mostly cosmetic: the agent reads past it. Worth it only where a caption ends up on the wrong table.

**Cost.** Unknown until its sub-causes are found.

**Examples.** ROUGE p. 1; Dropout Table 4 caption (p. 10); "A Simple but Tough-to-Beat Baseline for Sentence Embeddings" Figure 2 (p. 7).
