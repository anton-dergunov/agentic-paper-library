---
id: pdf-text-layer-errors
title: "Wrong characters from a PDF's text layer"
converter: pdf
takes: [engine, reconvert]
status: open
cost: "unknown until its sub-causes are found"
---

# Wrong characters from a PDF's text layer

`engine` `reconvert` · pdf · open

**Broken.** The PDF's text layer or its OCR gives wrong characters: lost ligatures, "D" for "=", "=0" for "≠0", doubled glyphs, stray characters in numbers.

**Fix.** Not known yet: a catch-all. Where the page image is clean, read the affected words from it; flag numbers the text layer and the image disagree on. Some records are the paper's own typos.

**What it gives.** Numbers and signs an agent can trust in those papers.

**Cost.** Unknown until its sub-causes are found.

**Examples.** "In Defense of the Triplet Loss for Person Re-Identification" Table 1 ("=0" for "≠0"); "Cumulated Gain-Based Evaluation of IR Techniques" ("D" for "="); MMR Table 1.
