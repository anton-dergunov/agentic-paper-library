---
id: html-formula-box-as-image
title: "A box around a formula is kept as an image"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small; reconvert six papers"
---

# A box around a formula is kept as an image

`engine` `reconvert` · html · open

**Broken.** LaTeXML draws a framed box (tcolorbox, `\fbox` around a display) as an SVG picture, with its content in a `<foreignObject>`. `picture_text` turns a box into a quote when its text has words enough. A box that holds mainly a formula has few words, so it is saved as an image, and an agent reading the markdown sees no formula. Universal Model Routing's Eq. (11), which defines its prediction-error-vector representation Ψ(h), exists only as `fig01.svg`, though its MathML and TeX are inside that file. A scan of the library's SVG figures with MathML and at most four shapes finds 10 such boxes in 6 papers.

**Fix.** In `picture_kind`, count a formula as text, so that a plain frame around a formula becomes a quote holding the formula in `$$…$$`, numbered as the HTML numbers it.

**What it gives.** Boxed definitions and key equations an agent can read.

**Cost.** Engine: small; reconvert six papers.

**Examples.** "Universal Model Routing for Efficient LLM Inference" Eq. (11) (p. 5); Nemotron-Cascade 2 (three boxes); "Understanding Optimization in Deep Learning with Central Flows" (two); SimCLR (two); Laplace Redux; The Prompt Report.
