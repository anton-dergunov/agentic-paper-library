---
id: html-math-text-macros
title: "Text-mode TeX inside a formula comes out raw"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small to medium, a mapping per construct; reconvert the papers"
---

# Text-mode TeX inside a formula comes out raw

`engine` `reconvert` · html · open

**Broken.** A formula whose TeX holds text-mode or box commands arrives as junk: a text macro becomes an operator name (`D\operatorname{textquoteright}` for D′, `\operatorname{textsl}{CTR}`, `\operatorname{adjustlimits}`, `\textrm{textquotedblleft}`, `\text{\textrm{boldmath}\(y\)}`), and symbols an author builds from boxes print as their construction (`\mathrel{\hbox to0.0pt{…\operatorname{hss}}}` for ⊥⊥ and ⟹̸, `\operatorname{vtop}\operatorname{halign}` for "does not subsume", `\operatorname{raise} 0.73193pt\hbox{…}` for "~", `\char 1 111` for an overbar). Split from `html-equation-garbled` on 21 Oct 2026, eleven papers; most stay readable from the prose.

**Fix.** Where the formula's TeX comes from LaTeXML's alttext, map the text macros to their characters (`\textquoteright` → ′, `\textsl` and `\textrm` → `\text`, `\textquotedblleft` → “, `\boldmath` → `\boldsymbol`, `\adjustlimits` dropped), and replace a known box construction by its symbol (the `\hbox to0pt` overlay of two ⊥ → `\perp\!\!\!\perp`, `\not` over an arrow → `\not\Longrightarrow`); or take the formula from the MathML when its alttext holds `\hbox`.

**What it gives.** Independence, implication and approximation symbols an agent can read without guessing.

**Cost.** Engine: small to medium, a mapping per construct; reconvert the papers.

**Examples.** "Estimating Average Causal Effects Under General Interference" Condition 4 (p. 15); Generalized Random Forests pp. 8, 20; SPADE pp. 9–10; Deep Interest Network p. 8; "Off-policy evaluation for slate recommendation" Eq. 8 (p. 5).
