---
id: pdf-equation-unparsable
title: "A model's reading of a PDF equation does not parse"
converter: pdf
takes: [engine, reconvert]
status: open
cost: "engine: small; reaches the PDF papers with their next reconversion"
---

# A model's reading of a PDF equation does not parse

`engine` `reconvert` · pdf · open

**Broken.** The equation model's reading can have unbalanced braces or delimiters. `paperlib symptoms --katex` found 66 equations in 28 papers when filed; 28 of them are the TeX of `katex-undrawable-tex`, and 13 of the 28 papers are PDF ones.

**Fix.** Check each reading with KaTeX when it is made, and read again one that fails.

**What it gives.** Equations that render; fewer garbled formulas for the agent to see through.

**Cost.** Engine: small; reaches the PDF papers with their next reconversion.

**Examples.** See `paperlib symptoms --katex`.
