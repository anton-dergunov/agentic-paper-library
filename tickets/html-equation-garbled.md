---
id: html-equation-garbled
title: "arXiv-HTML formulas garbled"
converter: html
takes: [engine, reconvert]
status: open
cost: "unknown until its sub-causes are found"
---

# arXiv-HTML formulas garbled

`engine` `reconvert` · html · open

**Broken.** A formula from arXiv's HTML is unbalanced, has lost a sign, or is collapsed onto one line with its labels inline.

**Fix.** Not known yet: a catch-all. Check each against the LaTeX source; parts are LaTeXML's own errors (then wont-fix), parts may be `arxiv-html.lua`'s. Split on 21 Oct 2026: text-mode TeX and box constructions inside a formula are `html-math-text-macros`. Split on 23 Oct 2026: a gap inside a formula rejoined from its alignment cells is `html-aligned-cells-split`, an alttext LaTeXML garbled while its MathML is right is `html-alttext-garbled`, and a paper's own macros are `html-own-macros-as-names`. Most of what is left is copied faithfully from the author's TeX (a missing bracket, a lost minus, a wrong index): check each against the PDF, and delete those the PDF prints the same; HuBERT's Eq. 10 and Matching the Blanks' classifier were such slips.

**What it gives.** Formulas an agent can quote; most are explained in the prose already.

**Cost.** Unknown until its sub-causes are found.

**Examples.** Larimar Eq. (1); "Fine-tune BERT for Extractive Summarization" Eqs. (5)–(8).
