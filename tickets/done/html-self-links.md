---
id: html-self-links
title: Links within an arXiv-HTML paper point to arxiv.org
converter: html
takes: [engine, reconvert]
closed: '2026-10-16'
cost: 'engine: small; reconvert four papers'
---

# Links within an arXiv-HTML paper point to arxiv.org

`engine` `reconvert` · html · done

**Broken.** Some arXiv HTML pages write their table of contents and cross-references as absolute links to the paper's own page (`https://arxiv.org/html/2302.07730v4#S1.SS1`), so they leave the markdown instead of jumping to the section.

**Fix.** Done 16 Oct 2026 (`local_links`): a link to `arxiv.org/html/<the paper's id>[vN]#X` is `#X`, the id taken from the rendering. The four papers in the cache that had them (MegaScale-Infer, Mastering Diverse Domains through World Models, Transformer models, ReTool) were reconverted: 619 links in-page, the papers 8–13% shorter for the hover titles that went with them, no word lost. → [`experiments/colours-marks-and-icons`](../experiments/colours-marks-and-icons/README.md)

**What it gives.** Cross-references that stay in the local copy.

**Cost.** Engine: small; reconvert four papers.

**Examples.** MegaScale-Infer (174 links), "Mastering Diverse Domains through World Models" (118), "Transformer models: an introduction and catalog" (100), ReTool (79).
