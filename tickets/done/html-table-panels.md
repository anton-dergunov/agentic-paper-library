---
id: html-table-panels
title: A table set as side-by-side panels loses its row labels or splits
converter: html
takes: [engine, reconvert]
closed: '2026-10-22'
cost: 'engine: medium, beside share_panel_labels; reconvert the papers with table panels'
---

# A table set as side-by-side panels loses its row labels or splits

`engine` `reconvert` · html · done

**Broken.** A table typeset as panels (subtables, minipages, or one long table wrapped into halves) arrives as separate tables. A panel that shares its row labels with the panel beside it has none of its own (DINOv3 Table 9, Word Rotator's Distance Tables 1(b) and 3(b), Movie Gen Table 16(b)), the panels' letters are lost ("(8)" in SAM 3 Table 8), and the halves of one table read as two (mixup Table 4, "Don't Stop Pretraining" Table 6). `share_panel_labels` gives a panel its neighbour's labels only when neither has a span and the row counts match.

**Fix.** Extend `share_panel_labels` to panels with spans in the header and to panels whose rows match the labelled panel after its header; keep each panel's letter before its table; join halves with the same columns into one table.

**Done (2026-10-22).** `share_panel_labels` now classes each panel's rows (header, group heading, values), finds all leading label columns, and matches a label-less panel kind by kind or to the labelled panel's value rows alone (DINOv3 Table 9 gets Method and ViT); spans are allowed, the labels' titles span a taller header, group headings widen, and "-" counts as a missing value (Word Rotator's Distance 1(b), 3(b)); MoCo Table 5 gains its labels too. `join_table_halves` joins tables that follow each other in one float with only layout between, when the second repeats the first's titles over rows of other names (mixup Table 4, Transformers in Vision Table III, and 8 more papers' appendix tables); tables with the same titles over the same rows (one per metric) and wide tables wrapped by columns stay apart, as the measurement showed joining them loses or gains nothing. SAM 3's "(8)" was a reference, not the table: a `\ref` to a label inside a `\subfloat` or subtable now reads "8(b)" (in `unresolved_citations`). Panel letters stay after their tables, like every caption. Not covered: Movie Gen 16(b) (LaTeXML lacked `\subfloat`; the only such paper; `html-subfloat-undefined`), and records with other causes, re-filed as `new`: CLAP Table 1, LeJEPA 1b/1d, MemBench Table 3, Entropic OOD Table I; "Don't Stop Pretraining" Table 6 (a wide table wrapped by columns) marked wont-fix.

**What it gives.** Every value with its row label; one table where the paper has one.

**Cost.** Engine: medium, beside share_panel_labels; reconvert the papers with table panels.

**Examples.** DINOv3 Table 9; Word Rotator's Distance Tables 1(b), 3(b); Movie Gen Table 16(b); SAM 3 Table 8; mixup Table 4.
