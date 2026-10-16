---
id: html-dropped-floats
title: "Tables and figures LaTeXML dropped"
converter: html
takes: [engine, reconvert, reread]
status: open
cost: "engine: medium, by the route of html-incomplete; reconvert; re-read the papers whose results are in the missing tables"
---

# Tables and figures LaTeXML dropped

`engine` `reconvert` `reread` · html · open

**Broken.** Tables the text cites are missing, and figures arXiv does not serve still link to arXiv (16 papers when filed, `figure-link` in `paperlib symptoms`).

**Fix.** Take such a table or figure from the PDF, by the route of `html-incomplete`.

**What it gives.** Results tables back where the findings rest on them.

**Cost.** Engine: medium, by the route of html-incomplete; reconvert; re-read the papers whose results are in the missing tables.

**Examples.** "Establishing Best Practices for Building Rigorous Agentic Benchmarks" (a `longtblr` of 17 benchmarks); Qwen3-VL's results tables ("results_flagship"); "A Simple Baseline for Bayesian Uncertainty in Deep Learning" Table 2; "Offline RL for Natural Language Generation with Implicit Language Q Learning" Tables 5–6; "Bad Characters" Table III.
