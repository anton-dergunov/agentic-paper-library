---
id: html-shared-float-anchor
title: "References to floats that share an anchor print the wrong number"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small; reconvert the HTML papers with such floats (minutes)"
---

# References to floats that share an anchor print the wrong number

`engine` `reconvert` · html · open

**Broken.** arXiv's HTML puts two figures in one float with one anchor, and every reference to either names the second. ViT's Figures 3 and 4 share `S4.F4`, so its references to Figure 3 read "Figure [4]". When filed, at least 17 read papers reported numbers off by one.

**Fix.** In `caption-numbers.py`, for a link to a float that holds several captions, take the number the PDF prints after the same words.

**What it gives.** An agent pointing to a figure names the right one; the claims themselves are unaffected, so no re-read.

**Cost.** Engine: small; reconvert the HTML papers with such floats (minutes).

**Examples.** ViT (Figures 3–4), BERTScore, HuBERT, RMSNorm, mixup, "Delving Deep into Rectifiers", "Stop Regressing", MiniCPM.
