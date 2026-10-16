---
id: html-latexml-macros
title: "LaTeXML's macros left in formulas"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small, fixtures; reconvert 20 papers"
---

# LaTeXML's macros left in formulas

`engine` `reconvert` · html · open

**Broken.** `\operatorname{mathbfcal}`, `displaystyleh`, `textsubscript`, the physics package's `quantity` and `expectationvalue`, and `[1.0]{-}` for a minus sign: 396 in 20 papers when filed. `0pt` appears in 88 papers and may be a length or a lost symbol ("depth $0pt$" where L was meant).

**Fix.** Map them in `arxiv-html.lua`; inspect the `0pt` cases first.

**What it gives.** Formulas that render and read cleanly; a few lost symbols back.

**Cost.** Engine: small, fixtures; reconvert 20 papers.

**Examples.** See `paperlib symptoms` for the papers.
