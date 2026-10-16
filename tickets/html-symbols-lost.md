---
id: html-symbols-lost
title: "Symbols lost or replaced in arXiv-HTML text and tables"
converter: html
takes: [engine, reconvert]
status: open
cost: "unknown until its sub-causes are found"
---

# Symbols lost or replaced in arXiv-HTML text and tables

`engine` `reconvert` · html · open

**Broken.** A symbol in a table or the text is lost or replaced by a stray glyph: ± between a value and its interval, a range's dash, significance markers. Symbols set as images are `html-image-symbols`.

**Fix.** Not known yet: a catch-all. Group by symbol; each group is a mapping in `arxiv-html.lua`.

**What it gives.** Significance markers and intervals an agent can read.

**Cost.** Unknown until its sub-causes are found.

**Examples.** "Neural Ranking Models with Weak Supervision" Tables 2–5 (^œ, ^™); MT3 Table 1 (ranges).
