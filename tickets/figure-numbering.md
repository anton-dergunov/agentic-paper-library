---
id: figure-numbering
title: "Figures and tables cited or placed wrongly"
converter: any
takes: [engine, reconvert]
status: open
cost: "unknown until its sub-causes are found"
---

# Figures and tables cited or placed wrongly

`engine` `reconvert` · any · open

**Broken.** A figure or table is cited by the wrong number or kind ("Table [4]" for Figure 4), or placed far from where the paper has it; so is a block of text: a function description from KAG's Table 1 sits in §2.3.2, and HackAPrompt opens with the abstract of the third-place report in its Appendix S, its own abstract missing. Overlaps `html-shared-float-anchor`.

**Fix.** Not known yet: a catch-all. Split on 22 Oct 2026: references printing a wrong number or kind are `html-reference-number-unmatched`, captions numbered differently from the PDF are `html-caption-numbers`. What is left are floats and blocks placed away from their text (KAG, HackAPrompt's abstract, the citations paper's Figure 4 table, Cartridges' Figure 8); most of these are marked wont-fix, as an agent finds a float by its number.

**What it gives.** Pointers to figures that land on the right one.

**Cost.** Unknown until its sub-causes are found.

**Examples.** mixup p. 5; "Perceptual Losses for Real-Time Style Transfer" p. 6; Cartridges Figure 8 (p. 20).
