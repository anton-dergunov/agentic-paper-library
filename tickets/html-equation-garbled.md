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

**Fix.** Not known yet: a catch-all. Check each against the LaTeX source; parts are LaTeXML's own errors (then wont-fix), parts may be `arxiv-html.lua`'s.

**What it gives.** Formulas an agent can quote; most are explained in the prose already.

**Cost.** Unknown until its sub-causes are found.

**Examples.** HuBERT Eq. (10); Larimar Eq. (1); "Fine-tune BERT for Extractive Summarization" Eqs. (5)–(8).
