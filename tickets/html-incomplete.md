---
id: html-incomplete
title: "arXiv's HTML is incomplete"
converter: html
takes: [engine, reconvert, reread]
status: open
cost: "engine: medium, with a measurement; reconvert the papers at PDF speed; re-read them (about $0.30 each)"
---

# arXiv's HTML is incomplete

`engine` `reconvert` `reread` · html · open

**Broken.** arXiv's rendering lacks pages of the paper: when filed, 27 papers missed eight pages or a quarter of the paper, and `paperlib symptoms --pages` listed 73 missing three pages or more. `paperlib reconvert` cannot convert a `source: html` paper from its PDF.

**Fix.** Add `--from-pdf` to `paperlib reconvert`, and compare it on five papers with adding only the missing pages to the HTML conversion.

**What it gives.** The whole paper readable; today an agent answering about the missing part must open the PDF.

**Cost.** Engine: medium, with a measurement; reconvert the papers at PDF speed; re-read them (about $0.30 each).

**Examples.** GPT-4 Technical Report (no System Card); "Studying Large Language Model Generalization with Influence Functions" (ends at §2.1); "Sparks of Artificial General Intelligence" (ends at §3.1.2); "Training Agents Inside of Scalable World Models" (ends in §4.2); Absolute Zero (pp. 29–50).
