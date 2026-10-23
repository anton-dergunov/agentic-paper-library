---
id: html-aligned-cells-split
title: "A gap lands inside a formula split at its alignment points"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small, a fixture; reconvert the papers with aligned equations"
---

# A gap lands inside a formula split at its alignment points

`engine` `reconvert` · html · open

**Broken.** LaTeXML lays out an aligned display as table cells cut at the author's `&`. `equation_rows` in `arxiv-html.lua` rejoins them directly only when the next cell starts with a relation (`continues`), and with `\qquad` otherwise, so a gap lands wherever the author put the `&` elsewhere: inside a word ("di \qquad ag" for diag in AWQ's Eq. 4), inside brackets ("[Q_1;Q_2 \qquad ]=XW^Q", Differential Transformer Eq. 1), between an operator and its argument ("\operatorname{DiffAttn} \qquad (X)"), or splitting one definition over two displays (Reasoning or Reciting, p. 3). 366 papers hold 3,272 such joins; most are right (two equations on one row). Split from `html-equation-garbled` on 23 Oct 2026.

**Fix.** Join by the cells' column alignment: a right-aligned cell and the left-aligned cell after it are one `&` pair and join with nothing; `\qquad` only between pairs. Also join with nothing when the cells so far leave a bracket or `\left` open. Fixtures from the three papers; count the joins that change.

**What it gives.** Formulas that read as one expression.

**Cost.** Engine: small, a fixture; reconvert the papers with aligned equations.

**Examples.** AWQ Eq. 4 (p. 3); Differential Transformer Eqs. 1–2 (p. 2); "Reasoning or Reciting" §2 (p. 3).
