---
id: katex-undrawable-tex
title: "TeX that KaTeX does not draw"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small; reconvert 5 papers"
---

# TeX that KaTeX does not draw

`engine` `reconvert` · html · open

**Broken.** A `tabular` or an `\includegraphics` inside a formula stays as its TeX (23 formulas in 4 papers when filed, 20 of them in CheckList). A `NiceArray` arrives empty (5 formulas in "Multiple Randomization Designs").

**Fix.** Write such a formula as a table or an image.

**What it gives.** The few affected formulas readable; mostly cosmetic.

**Cost.** Engine: small; reconvert 5 papers.

**Examples.** CheckList; "Multiple Randomization Designs".
