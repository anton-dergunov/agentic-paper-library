---
id: html-lost-labels
title: "References to an equation, a theorem or an appendix show the label's name"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: medium; reconvert the papers"
---

# References to an equation, a theorem or an appendix show the label's name

`engine` `reconvert` · html · open

**Broken.** References LaTeXML lost show the label's name ("eq.(exactSol)", "Appendix minibatch"), in nine papers when filed. Collapsed numbers ("Assumptions [2.1]-[2.1]", "([2]) follows from ([2])") are the same fault.

**Fix.** Take an equation's number from its place among the numbered equations of the LaTeX source.

**What it gives.** Cross-references an agent can follow.

**Cost.** Engine: medium; reconvert the papers.

**Examples.** "Real numbers, data science and chaos" (thirteen).
