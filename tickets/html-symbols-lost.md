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

**Fix.** Not known yet: a catch-all. Group by symbol; each group is a mapping in `arxiv-html.lua`. Split on 21 Oct 2026: lost approximation signs are `html-approx-sign-lost`. Split on 23 Oct 2026: "¿" for ">" is `html-ot1-angle-glyphs`, a paper's own macros printed as names `html-own-macros-as-names`, macros LaTeXML left undefined `html-undefined-macros-dropped`, colour-only markers `html-coloured-markers`, TikZ pictures drawn empty `html-empty-pictures`, and characters missing from arXiv's HTML that the PDF prints `html-latexml-dropped-characters`. Of the records checked against the PDF that day, 24 were the papers' own slips (the dropped "k" in "65k tokens", a p-value's lost exponent, a lost ∈ the author never typed) and were deleted. Most of what is left are one-off glyphs (card suits, primes, stray characters, U+ code points).

**What it gives.** Significance markers and intervals an agent can read.

**Cost.** Unknown until its sub-causes are found.

**Examples.** "Neural Ranking Models with Weak Supervision" Tables 2–5 (^œ, ^™); MT3 Table 1 (ranges).
