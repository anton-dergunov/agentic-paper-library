---
id: html-row-span-heuristics
title: "The converter's row-label repairs move a value or stretch a label too far"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small, fixtures from the papers below; reconvert the papers whose spans the repairs change"
---

# The converter's row-label repairs move a value or stretch a label too far

`engine` `reconvert` · html · open

**Broken.** Two repairs for LaTeXML's row labels misfire. `raise_group_labels` takes any lone cell on a group's last row for a `\multirow{-n}` label: in SAM 2's Table 11, the ✓ of the default (third) row moves to the first row and spans all three. `extend_rowspans` stretches a label over the following rows while they start with an empty cell, and those rows can belong to the next group, whose label LaTeXML left on its last row. Phi-4's "simple-evals" grows from 7 to 13 rows, Voicebox's "YT" from 7 to 13 (over the VB-Multi rows), Qwen2.5-Omni's 7-row groups to 8 (MusicCaps loses its label), and the "General" group in "Continual Learning of Large Language Models" Table 3 from 11 to 19.

**Fix.** Raise only a label that is text, not a mark or a number, in a column whose other groups have labels. Stop extending at a row whose group has its own label further down, before a rule, or where the spanned row count would pass the next labelled row. The spans LaTeXML wrote are better left alone than guessed over.

**What it gives.** Row groups as the paper sets them, so a result is read under the right setting.

**Cost.** Engine: small, fixtures from the papers below; reconvert the papers whose spans the repairs change.

**Examples.** SAM 2 Table 11; Phi-4 Table 1; Voicebox Table 3; Qwen2.5-Omni Table 3; "Continual Learning of Large Language Models. A Comprehensive Survey" Table 3.
