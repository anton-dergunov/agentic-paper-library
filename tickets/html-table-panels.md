---
id: html-table-panels
title: "A table set as side-by-side panels loses its row labels or splits"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: medium, beside share_panel_labels; reconvert the papers with table panels"
---

# A table set as side-by-side panels loses its row labels or splits

`engine` `reconvert` · html · open

**Broken.** A table typeset as panels (subtables, minipages, or one long table wrapped into halves) arrives as separate tables. A panel that shares its row labels with the panel beside it has none of its own (DINOv3 Table 9, Word Rotator's Distance Tables 1(b) and 3(b), Movie Gen Table 16(b)), the panels' letters are lost ("(8)" in SAM 3 Table 8), and the halves of one table read as two (mixup Table 4, "Don't Stop Pretraining" Table 6). `share_panel_labels` gives a panel its neighbour's labels only when neither has a span and the row counts match.

**Fix.** Extend `share_panel_labels` to panels with spans in the header and to panels whose rows match the labelled panel after its header; keep each panel's letter before its table; join halves with the same columns into one table.

**What it gives.** Every value with its row label; one table where the paper has one.

**Cost.** Engine: medium, beside share_panel_labels; reconvert the papers with table panels.

**Examples.** DINOv3 Table 9; Word Rotator's Distance Tables 1(b), 3(b); Movie Gen Table 16(b); SAM 3 Table 8; mixup Table 4.
