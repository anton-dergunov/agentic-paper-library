---
id: web-conversion
title: "Web articles that lose parts of the page"
converter: web
takes: [engine, reconvert]
status: open
cost: "unknown until its sub-causes are found"
---

# Web articles that lose parts of the page

`engine` `reconvert` · web · open

**Broken.** A web article's markdown lacks something the page shows: footnote text, or a figure's equations split around its captions.

**Fix.** Not known yet: a catch-all. Look at each page's markup; each sub-cause is a rule in `add-web-article.py`.

**What it gives.** Web articles as complete as the page.

**Cost.** Unknown until its sub-causes are found.

**Examples.** "Why Momentum Really Works": footnotes (1)–(11) referenced but their text missing, though `<d-footnote>` is handled, so the 2017 Distill markup differs.
