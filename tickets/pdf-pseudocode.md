---
id: pdf-pseudocode
title: "Pseudocode in PDF papers runs together"
converter: pdf
takes: [engine, reconvert]
status: open
cost: "engine: medium, a fixture; reconvert the papers"
---

# Pseudocode in PDF papers runs together

`engine` `reconvert` · pdf · open

**Broken.** An algorithm box becomes one paragraph, with its loops and conditions lost and lines sometimes duplicated or out of order. When filed, 10 of the 103 read PDF papers. The prose or the equations next to it usually give the steps.

**Fix.** Write a box docling labels as code or as an algorithm as a fenced block, one PDF line per line, with the indentation from the words' x positions, and keep its mathematics inline.

**What it gives.** Algorithms an agent can follow step by step.

**Cost.** Engine: medium, a fixture; reconvert the papers.

**Examples.** Ad Click Prediction; DiskANN; HNSW; "Efficient set intersection for inverted indexing"; CatBoost; "From RankNet to LambdaRank to LambdaMART"; "Detecting hallucinations in large language models using semantic entropy"; "Reinforcement Learning for LLM Post-Training. A Survey".
