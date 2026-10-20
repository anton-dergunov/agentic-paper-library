---
id: html-row-span-heuristics
title: The converter's row-label repairs move a value or stretch a label too far
converter: html
takes: [engine, reconvert]
closed: '2026-10-20'
cost: 'engine: done; reconvert the papers whose spans the repairs change'
---

# The converter's row-label repairs move a value or stretch a label too far

`engine` `reconvert` · html · done

**Broken.** Two repairs for LaTeXML's row labels misfire. `raise_group_labels` takes any lone cell on a group's last row for a `\multirow{-n}` label: in SAM 2's Table 11, the ✓ of the default (third) row moves to the first row and spans all three. `extend_rowspans` stretches a label over the following rows while they start with an empty cell, and those rows can belong to the next group, whose label LaTeXML left on its last row. Phi-4's "simple-evals" grows from 7 to 13 rows, Voicebox's "YT" from 7 to 13 (over the VB-Multi rows), Qwen2.5-Omni's 7-row groups to 8 (MusicCaps loses its label), and the "General" group in "Continual Learning of Large Language Models" Table 3 from 11 to 19.

**Fix.** Done 20 Oct 2026: `extend_rowspans` stops at a row with a rule above its first cell (Phi-4, Voicebox, the CL survey), and does not take a run of several empty first cells that ends at a lone label: those rows are that label's group. `raise_group_labels` raises a label only when it has a letter (not a "✓" or a number) and another group in the body has a label (SAM 2 Table 11). Qwen2.5-Omni's 7-row groups growing to 8 was right: each has eight models under a `\multirow{7}`; its record (MusicCaps' metric names) is a different cause, absent from arXiv's HTML, re-filed as `new`.

**What it gives.** Row groups as the paper sets them, so a result is read under the right setting.

**Cost.** Engine: done; reconvert the papers whose spans the repairs change.

**Examples.** SAM 2 Table 11; Phi-4 Table 1; Voicebox Table 3; Qwen2.5-Omni Table 3; "Continual Learning of Large Language Models. A Comprehensive Survey" Table 3.
