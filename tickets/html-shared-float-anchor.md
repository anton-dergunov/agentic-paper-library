---
id: html-shared-float-anchor
title: References to floats that share an anchor print the wrong number
converter: html
takes: [engine, reconvert]
status: fixed
cost: 'engine: small; reconvert the HTML papers with such floats (minutes)'
---

# References to floats that share an anchor print the wrong number

`engine` `reconvert` · html · fixed

**Broken.** arXiv's HTML puts two figures in one float with one anchor, and every reference to either names the second. ViT's Figures 3 and 4 share `S4.F4`, so its references to Figure 3 read "Figure [4]". When filed, at least 17 read papers reported numbers off by one.

**Fix.** In `caption-numbers.py`, for a link to a float that holds several captions, take the number the PDF prints after the same words.

Fixed 21 Oct 2026 ([experiment](../experiments/references-shades-and-text-macros/README.md)): `caption-numbers.py` now gives every link to a place in the paper the number the PDF prints there, not only links to shared floats, since the same step fixes a `\label` the HTML attached to a section, a footnote or a line. The five to eight words before the reference are looked up in the PDF's text (where a paragraph or a formula leaves fewer, the words after it), and the number next to them is taken when they occur once or always with that number; a formula is a gap no PDF word matches. The number must label a place of that kind in the markdown (a caption, a heading), and a section, theorem or equation the link reaches by its own anchor keeps the HTML's number, since its heading or tag in the markdown does too. On the ticket's 66 papers and 60 at random, 125 references changed in 48 papers, every one checked against its record or the PDF; four false matches found on the way (a sentence repeated without its formula, two references the HTML printed in the other order, chapter-numbered sections, an equation after the word "assumption") each became a rule above. Fixed on ViT, SWE-agent, Sycophancy, the corruption benchmark, OneRec and BERTScore (27 references). Not reached, re-filed as `new:html-reference-number-unmatched` (21 records in 20 papers): the HTML printing the wrong kind ("Figure [1]" for Table 1, "[Footnote 18]"), lost subfigure letters, row numbers, Switchback's theorems and assumptions (numbered by section in the HTML and globally in the PDF, with the markdown's labels following the HTML), and e-values' Table 13.23, a caption problem. LiRank's "Table 5" and KAG's "Algorithm 17" are printed so in the PDF and were closed. The fix reaches papers no record names: 10 of the 60 random papers changed (27 references).

**What it gives.** An agent pointing to a figure names the right one; the claims themselves are unaffected, so no re-read.

**Cost.** Engine: small; reconvert the HTML papers with such floats (minutes).

**Examples.** ViT (Figures 3–4), BERTScore, HuBERT, RMSNorm, mixup, "Delving Deep into Rectifiers", "Stop Regressing", MiniCPM.
