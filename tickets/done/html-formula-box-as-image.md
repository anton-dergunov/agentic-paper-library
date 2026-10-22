---
id: html-formula-box-as-image
title: A box around a formula is kept as an image
converter: html
takes: [engine, reconvert]
closed: '2026-10-22'
cost: 'engine: small; reconvert six papers'
---

# A box around a formula is kept as an image

`engine` `reconvert` · html · done

**Broken.** LaTeXML draws a framed box (tcolorbox, `\fbox` around a display) as an SVG picture, with its content in a `<foreignObject>`. `picture_text` turns a box into a quote when its text has words enough. A box that holds mainly a formula has few words, so it is saved as an image, and an agent reading the markdown sees no formula. Universal Model Routing's Eq. (11), which defines its prediction-error-vector representation Ψ(h), exists only as `fig01.svg`, though its MathML and TeX are inside that file. A scan of the library's SVG figures with MathML and at most four shapes finds 10 such boxes in 6 papers.

**Fix.** In `picture_kind`, count a formula as text, so that a plain frame around a formula becomes a quote holding the formula in `$$…$$`, numbered as the HTML numbers it.

Done 22 Oct 2026 ([experiment](../experiments/cell-lines-and-unreached-spans/README.md)): `picture_kind` counts a block with a display formula as a block of text (twelve words), and `span_equations_to_tables` turns the equation table LaTeXML sets as spans inside the box back into a table, which the Lua filter writes as `$$…\tag{n}$$`. Universal Model Routing's Eq. (11), Central Flows' boxed equation, Laplace Redux's and Nemotron-Cascade 2's boxes are now quotes; two boxes of aligned equations in other papers became display equations. SimCLR's two boxes are drawn crops labelled A–D and stay images; The Prompt Report has none left.

**What it gives.** Boxed definitions and key equations an agent can read.

**Cost.** Engine: small; reconvert six papers.

**Examples.** "Universal Model Routing for Efficient LLM Inference" Eq. (11) (p. 5); Nemotron-Cascade 2 (three boxes); "Understanding Optimization in Deep Learning with Central Flows" (two); SimCLR (two); Laplace Redux; The Prompt Report.
