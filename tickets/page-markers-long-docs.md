---
id: page-markers-long-docs
title: "Page markers in long documents are sparse or out of order"
converter: any
takes: [engine, reconvert]
status: open
cost: "engine: medium, measured on the 8 papers; reconvert them"
---

# Page markers in long documents are sparse or out of order

`engine` `reconvert` · any · open

**Broken.** Books and tutorials have sparse or out-of-order page markers, so notes cite wrong pages.

**Fix.** In `page-map.py`, search the page text for every heading without a marker, and drop a marker that goes backwards.

**What it gives.** Page citations an agent gives in long documents point to the right place.

**Cost.** Engine: medium, measured on the 8 papers; reconvert them.

**Examples.** "A Tutorial on Thompson Sampling" and "An Introduction to Conditional Random Fields" (none from Chapter 3 on); "Deep Reinforcement Learning, a textbook"; "Introduction to Multi-Armed Bandits"; "Understanding Diffusion Models"; "Mastering Chess and Shogi by Self-Play" (all on p. 1); MMMU; "The Implicit Bias of Gradient Descent on Separable Data".
