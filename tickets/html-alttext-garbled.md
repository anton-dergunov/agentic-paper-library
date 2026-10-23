---
id: html-alttext-garbled
title: "LaTeXML's TeX for a formula is garbled; its MathML is not"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: medium (MathML to TeX for the formulas that fail a check); reconvert the papers"
---

# LaTeXML's TeX for a formula is garbled; its MathML is not

`engine` `reconvert` · html · open

**Broken.** The converter takes each formula's TeX from LaTeXML's alttext. For some constructs that alttext is itself broken while the MathML beside it holds the formula: continuation lines that start with "}{\displaystyle" (Doubly Robust, Eq. 2), an environment's name fused into the formula ("\rightarrow_{p}0.equation", ML for Variance Reduction Eq. B.1), a sentence set in math with its spaces gone ("Ismodelcollapseinevitable…", Strong Model Collapse Q1/Q2), a `\text` holding a nested tooltip's markup (Muon's Eq. 1 ends in "\textbackslash{}displaystyle=\textbackslash{}text\{N…"). Split from `html-equation-garbled` on 23 Oct 2026.

**Fix.** Check each formula's alttext (balanced braces, KaTeX parses it, no LaTeXML internals such as a leading "}{", a fused environment name, `\textbackslash{}` inside math); for one that fails, write the formula from its MathML (pandoc's texmath reads MathML) instead. Compare the two on the papers below, and count how many formulas library-wide would switch.

**What it gives.** Derivations an agent can follow without rebuilding them from the prose.

**Cost.** Engine: medium (MathML to TeX for the formulas that fail a check); reconvert the papers.

**Examples.** "Doubly Robust Policy Evaluation and Learning" Eq. 2 (p. 3); "Machine Learning for Variance Reduction in Online Experiments" Eq. B.1 (p. 17); Strong Model Collapse (p. 2); "Muon is Scalable for LLM Training" Eq. 1 (p. 2).
