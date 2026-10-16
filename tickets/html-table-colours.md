---
id: html-table-colours
title: "Colour marking with more than one colour is dropped"
converter: html
takes: [engine, reconvert, reread]
status: open
cost: "engine: small, measured as in experiments/table-emphasis; reconvert the papers; re-read three"
---

# Colour marking with more than one colour is dropped

`engine` `reconvert` `reread` · html · open

**Broken.** Shading or coloured text is kept only when the caption names it and the table has one colour. Red/blue for best and second best becomes bold for both. When filed, 28 notes reported a lost colour, three as key content.

**Fix.** Keep each colour the caption names, marked with its name.

**What it gives.** Tables whose colours separate conditions (trained on the closed set, invalid values) read correctly.

**Cost.** Engine: small, measured as in experiments/table-emphasis; reconvert the papers; re-read three.

**Examples.** SAM 3 Table 1 (grey: trained on the closed set); "End-to-end Piano Performance-MIDI to Score Conversion" Table 6 (grey: invalid values); "A Survey of Agent Memory in the Second Half" Table 4 (two kinds of ✓); MM-LLMs Table 2.
