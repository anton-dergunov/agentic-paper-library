---
id: html-table-colours
title: Colour marking with more than one colour is dropped
converter: html
takes: [engine, reconvert, reread]
status: fixed
cost: 'engine: small, measured as in experiments/table-emphasis; reconvert the papers; re-read three'
---

# Colour marking with more than one colour is dropped

`engine` `reconvert` `reread` · html · fixed

**Broken.** Shading or coloured text is kept only when the caption names it and the table has one colour. Red/blue for best and second best becomes bold for both. When filed, 28 notes reported a lost colour, three as key content.

**Fix.** Done 16 Oct 2026 (`mark_named_colours`): a table's background and text colours are each marked where the caption names them (its own word, neighbouring hues allowed: a light red is "red") or sets text of its own in them (a legend's coloured ✓, an empty box as "■"), as `<mark class="red">` when the table has several colours, `<mark>` when one; "gray numbers" and "grayed out" pick the text over a shading of the same name. Over the cache, tables with marks 160 → 327 in 173 papers. Checked on SAM 3, Piano-MIDI, the agent-memory survey, MM-LLMs and Checklists. Not marked: colour of text inside a cell (case-study prose, TRUE Table 1), heat maps. → [`experiments/colours-marks-and-icons`](../experiments/colours-marks-and-icons/README.md)

**What it gives.** Tables whose colours separate conditions (trained on the closed set, invalid values) read correctly.

**Cost.** Engine: small, measured as in experiments/table-emphasis; reconvert the papers; re-read three.

**Examples.** SAM 3 Table 1 (grey: trained on the closed set); "End-to-end Piano Performance-MIDI to Score Conversion" Table 6 (grey: invalid values); "A Survey of Agent Memory in the Second Half" Table 4 (two kinds of ✓); MM-LLMs Table 2.
