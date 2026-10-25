---
id: figure-text-lost
title: "Numbers printed inside a vector figure are in the PDF's text layer, not in the markdown"
converter: any
takes: [engine, reconvert]
status: open
cost: "engine: medium (the figure's region on its PDF page, and the text-layer words inside it); reconvert the papers with vector figures"
---

# Numbers printed inside a vector figure are in the PDF's text layer, not in the markdown

`engine` `reconvert` · any · open

**Broken.** A figure drawn as vector graphics in the PDF carries its labels as text: bar labels, heatmap cells, p-values, annotated points. The markdown keeps the figure only as a picture file (arXiv's raster `.webp`, or an `.svg` whose letters are glyph outlines, not `<text>`), so these numbers are nowhere an agent can read them without opening the picture. The PDF's text layer has them. In the reading-formats experiment (tier C2, 25 Oct 2026) the markdown declined both such questions in 3 of 3 runs, while the text layer, the page image and the page PDF answered them in 3 of 3.

**Fix.** For each figure, find its region on its PDF page (the caption's position and the page map give the page; PyMuPDF's drawings or docling's picture box give the region), take the text-layer words inside it, and add them under the figure as one short line ("Text in the figure: …"), in reading order, without the axis ticks if they cost more than they say. Check first how docling's PDF path treats the same figures, and measure the tokens added library-wide against the questions it makes answerable.

**What it gives.** Values a figure prints but the prose does not: online A/B effects and p-values, heatmap cells, labelled points.

**Cost.** Engine: medium (the figure's region on its PDF page, and the text-layer words inside it); reconvert the papers with vector figures.

**Examples.** "GenRec. An LLM-Backed Recommendation Ranker at Netflix" Figure 3 (p. 6: +0.115%, P = 3.1 × 10⁻¹⁰); "SFT Conflicts, RL Coexists" Figure 2 (p. 4: the heatmap's cosines and norms, e.g. −3.92e-04, 8.7e-02).
