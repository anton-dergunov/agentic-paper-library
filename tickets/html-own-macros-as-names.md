---
id: html-own-macros-as-names
title: "A paper's own macros print as their names"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: medium (macro definitions from the LaTeX source); reconvert about 170 papers"
---

# A paper's own macros print as their names

`engine` `reconvert` · html · open

**Broken.** The formulas come from LaTeXML's alttext, which keeps the author's macros as typed. A macro KaTeX lacks prints as its name (`\operatorname{mme}`, `\operatorname{mmv}`, `\operatorname{mmc}` for expectation, variance and covariance throughout "Multiple Randomization Designs"; `\operatorname{promptcollection}` for a bold P in "Ask Me Anything"; `\bx`, `\pPr`, `\kv`, `\Xsc`, `\sdcp` elsewhere), and one that shadows a standard command prints that command's symbol (FlashAttention-2's `\S` for the matrix **S** comes out as "§"; Knowledge-Based Trust's presence vote `\Pre` was expanded by LaTeXML as REVTeX's journal name, "Phys. Rev. E"). `html-latexml-macros` kept the names by design; for opaque names they hide the meaning. 168 papers show 5,339 such names; many are harmless (`\E`, `\Var`, `\tr`, `\diag`), about a third are opaque. Split from `html-symbols-lost` and `html-equation-garbled` on 23 Oct 2026.

**Fix.** Read the paper's macro definitions from its LaTeX source, which `latex_source` already fetches (`\newcommand`, `\renewcommand`, `\def`, `\DeclareMathOperator`, with arguments), and expand them in the alttext before `rewrite_commands`; a macro still unknown keeps its name. Where the source is missing, take the macro's expansion from the MathML of a formula that holds only it. Leave a macro whose name KaTeX knows (`\E` as an operator) as it is unless the source redefines a standard command (`\S`, `\Pre`). Check on the four papers below, then count the names left with `paperlib symptoms`.

**What it gives.** Formulas whose symbols say what they are: E[·] instead of "mme", **S** instead of §.

**Cost.** Engine: medium (macro definitions from the LaTeX source); reconvert about 170 papers.

**Examples.** "Multiple Randomization Designs" pp. 13–76; "Ask Me Anything" pp. 4–7; FlashAttention-2 §2.2 (p. 3); Knowledge-Based Trust Eqs. 12, 14 (pp. 5–6); "Variational Autoencoders for Collaborative Filtering" (the acronym macro in "Mult-VAE^pr").
