---
id: html-listing-lines-lost
title: "Lines of a code listing missing"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small to medium once the dropped element is found; reconvert the papers"
---

# Lines of a code listing missing

`engine` `reconvert` · html · open

**Broken.** A code listing loses its first line or lines, the `def` or `async def` signature, so it starts mid-signature or mid-function: "A Categorical Archive of ChatGPT Failures" §2.7 (and the `baskets` definition in its second listing), SPADE's Fig. 3 and the listings on pp. 6 and 11. In Sleeper Agents the model's code is missing from the sample boxes altogether (Figures 4, 9, 15), leaving empty Assistant responses; whether that is the same fault, a listing inside a boxed table cell, is not known yet.

**Fix.** Find where arXiv's HTML puts the missing lines (a listing's first `ltx_listingline`, perhaps carrying the line number or a caption) and keep them in the fenced block; for Sleeper Agents, see whether the code is in the HTML at all.

**What it gives.** Listings that say which function they are, and the backdoored model's code, which is what the samples show.

**Cost.** Engine: small to medium once the dropped element is found; reconvert the papers.

**Examples.** "A Categorical Archive of ChatGPT Failures" pp. 16–23; SPADE pp. 4, 6, 11; Sleeper Agents pp. 4, 17, 22.
