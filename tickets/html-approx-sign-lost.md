---
id: html-approx-sign-lost
title: "The \"~\" or \"≈\" before a number is lost"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small, once the TeX form is found; reconvert the papers"
---

# The "~" or "≈" before a number is lost

`engine` `reconvert` · html · open

**Broken.** An approximation sign before a number vanishes and leaves a double space: "reduced by  50%", "with  1 TB/s memory bandwidth" (printed "~1 TB/s" elsewhere in the paper), "ASR of  60%". The reader takes an estimate for an exact figure. Split from `html-symbols-lost` on 21 Oct 2026, eight papers.

**Fix.** Find the form in arXiv's HTML (most likely `$\sim$`, `\approx` or a `\textasciitilde` set as an empty `ltx_Math` or a span the Lua filter drops) and write it as "~" or "≈".

**What it gives.** Approximate figures read as approximate.

**Cost.** Engine: small, once the TeX form is found; reconvert the papers.

**Examples.** LiRank §4.2–4.3 (p. 7); "Understanding Training Efficiency of Deep Learning Recommendation Models" §IV-B1 (p. 6); "Do Vision Transformers See Like Convolutional Neural Networks?" pp. 3–7; Voxtral p. 8.
