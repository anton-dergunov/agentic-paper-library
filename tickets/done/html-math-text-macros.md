---
id: html-math-text-macros
title: Text-mode TeX inside a formula comes out raw
converter: html
takes: [engine, reconvert]
closed: '2026-10-21'
cost: 'engine: small to medium, a mapping per construct; reconvert the papers'
---

# Text-mode TeX inside a formula comes out raw

`engine` `reconvert` · html · done

**Broken.** A formula whose TeX holds text-mode or box commands arrives as junk: a text macro becomes an operator name (`D\operatorname{textquoteright}` for D′, `\operatorname{textsl}{CTR}`, `\operatorname{adjustlimits}`, `\textrm{textquotedblleft}`, `\text{\textrm{boldmath}\(y\)}`), and symbols an author builds from boxes print as their construction (`\mathrel{\hbox to0.0pt{…\operatorname{hss}}}` for ⊥⊥ and ⟹̸, `\operatorname{vtop}\operatorname{halign}` for "does not subsume", `\operatorname{raise} 0.73193pt\hbox{…}` for "~", `\char 1 111` for an overbar). Split from `html-equation-garbled` on 21 Oct 2026, eleven papers; most stay readable from the prose.

**Fix.** Where the formula's TeX comes from LaTeXML's alttext, map the text macros to their characters (`\textquoteright` → ′, `\textsl` and `\textrm` → `\text`, `\textquotedblleft` → “, `\boldmath` → `\boldsymbol`, `\adjustlimits` dropped), and replace a known box construction by its symbol (the `\hbox to0pt` overlay of two ⊥ → `\perp\!\!\!\perp`, `\not` over an arrow → `\not\Longrightarrow`); or take the formula from the MathML when its alttext holds `\hbox`.

Done 21 Oct 2026 ([experiment](../experiments/references-shades-and-text-macros/README.md)): in `arxiv-html.lua`, text-mode symbols KaTeX lacks are written by mode (`TEXT_SYMBOL`: `\textquoteright` is `'` in math and ’ in text, quotes, dashes, daggers, `\textbackslash`, `\textlangle`…), `\textsl` is `\textit`, `\sl`, `\adjustlimits` and a stray `\boldmath` go, `\text{\boldmath$y$}` is `\boldsymbol{y}`, `\hss`, `\vss`, `\raise` and `\lower` are layout, and `box_symbols` replaces two `\perp` overlaid in a zero-width box by `\perp\!\!\!\perp` and a `\not` laid over an arrow, or stacked above it in a `\vtop`, by `\not\implies`; another zero-width box is a plain `\hbox`. amsmath's nested accent left as internals (`\macc@nested@a 111`) is `\bar`, the only code seen, in two papers (GRF's overbars, p. 20). Fixed on the ticket's ten papers, all of whose formulas parse in KaTeX. 33 more papers hold 229 such leftovers without a record; a full reconversion reaches them.

**What it gives.** Independence, implication and approximation symbols an agent can read without guessing.

**Cost.** Engine: small to medium, a mapping per construct; reconvert the papers.

**Examples.** "Estimating Average Causal Effects Under General Interference" Condition 4 (p. 15); Generalized Random Forests pp. 8, 20; SPADE pp. 9–10; Deep Interest Network p. 8; "Off-policy evaluation for slate recommendation" Eq. 8 (p. 5).
