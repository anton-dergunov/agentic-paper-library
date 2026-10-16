---
id: html-self-links
title: "Links within an arXiv-HTML paper point to arxiv.org"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small; reconvert four papers"
---

# Links within an arXiv-HTML paper point to arxiv.org

`engine` `reconvert` · html · open

**Broken.** Some arXiv HTML pages write their table of contents and cross-references as absolute links to the paper's own page (`https://arxiv.org/html/2302.07730v4#S1.SS1`), so they leave the markdown instead of jumping to the section.

**Fix.** In `html-to-markdown.py`, rewrite a link to `arxiv.org/html/<the paper's own id>[vN]#X` as `#X`.

**What it gives.** Cross-references that stay in the local copy.

**Cost.** Engine: small; reconvert four papers.

**Examples.** MegaScale-Infer (174 links), "Mastering Diverse Domains through World Models" (118), "Transformer models: an introduction and catalog" (100), ReTool (79).
