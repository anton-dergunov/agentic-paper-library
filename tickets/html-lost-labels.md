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

**Broken.** References LaTeXML lost show the label's name ("eq.(exactSol)", "Appendix minibatch"), in nine papers when filed. Collapsed numbers ("Assumptions [2.1]-[2.1]", "([2]) follows from ([2])", the switchback paper's "Assumptions [4.1] and [4.1]") are the same fault. Close to it: a reference to a section printing another section's number (the agentic-RL survey's "Section [6]" for Section 4), and theorem counters LaTeXML numbers differently from the PDF, so the prose's "Theorem 4.1" names no printed theorem (Double/Debiased ML, Defs. 3.3–3.4 with no 3.1–3.2).

**Fix.** Take an equation's number from its place among the numbered equations of the LaTeX source; theorem, assumption and section numbers the same way, from the source's counters.

**What it gives.** Cross-references an agent can follow.

**Cost.** Engine: medium; reconvert the papers.

**Examples.** "Real numbers, data science and chaos" (thirteen).
