---
id: html-table-colours
title: Colour marking with more than one colour is dropped
converter: html
takes: [engine, reconvert, reread]
status: open
cost: 'engine: small, measured as in experiments/table-emphasis; reconvert the papers; re-read three'
---

# Colour marking with more than one colour is dropped

`engine` `reconvert` `reread` · html · open

**Broken.** Shading or coloured text is kept only when the caption names it and the table has one colour. Red/blue for best and second best becomes bold for both. When filed, 28 notes reported a lost colour, three as key content.

**Fix.** Done 16 Oct 2026 (`mark_named_colours`): a table's background and text colours are each marked where the caption names them (its own word, neighbouring hues allowed: a light red is "red") or sets text of its own in them (a legend's coloured ✓, an empty box as "■"), as `<mark class="red">` when the table has several colours, `<mark>` when one; "gray numbers" and "grayed out" pick the text over a shading of the same name. Over the cache, tables with marks 160 → 327 in 173 papers. Checked on SAM 3, Piano-MIDI, the agent-memory survey, MM-LLMs and Checklists. Not marked: colour of text inside a cell (case-study prose, TRUE Table 1), heat maps. → [`experiments/colours-marks-and-icons`](../experiments/colours-marks-and-icons/README.md) **After the full reconversion of 16 Oct 2026**, 9 of the 22 papers with records gained their marks and were closed. Memory Decoder is half done: a colour on a table's header row gets no mark. 12 came out unchanged and stay open. Traced on 17 Oct 2026, the causes are: (1) colour on part of a cell is never marked, since a cell counts only when 80% of its text is in the colour: TRUE's red and blue words, MATH's gray "+x%", xCOMET's coloured bullet before each row name; (2) colour set inside math (`--ltx-fg-color` on `<mi>`, `<mn>`, `<mo>`) is not seen, as `coloured_spans` reads only `<span>`s: MATH, few-sample BERT (whole cells in blue math), xCOMET, and Infini-gram's ■ legend; (3) a legend whose box is coloured text does not match cells shaded in that colour, as `caption_colours` matches a legend within one layer only: LLaVA-1.5's ◼ (text #D9F2FF, cells shaded #D9F2FF), Infini-gram's ■; (4) a header row is skipped even when the caption names its colour: Memory Decoder; (5) the marks TRUE does get are lost in `flatten_cell_tables` (arxiv-html.lua), which reduces a `\makecell` cell to plain text and so also drops bold (62 papers), italics (13) and math (24: `$\bullet$` comes out as the word `\bullet`), a cause outside colour that needs a ticket of its own; (6) Decoupled Weight Decay's algorithms have the legend in the caption (shaded text) and the shading on lines, but only table floats are marked. Not fixable from the HTML: the continual-learning survey's boxes and underlines are TikZ overlays LaTeXML draws as empty 1×1 pictures, and Table XII's red is absent; Batch Normalization Explained's second curve sample is an empty span. By design: Entropic OOD, the continual-learning LLM survey and Swap-guided name no colour in the caption, so the rule does not apply (the last two say the groups can be rebuilt).

**What it gives.** Tables whose colours separate conditions (trained on the closed set, invalid values) read correctly.

**Cost.** Engine: small, measured as in experiments/table-emphasis; reconvert the papers; re-read three.

**Examples.** SAM 3 Table 1 (grey: trained on the closed set); "End-to-end Piano Performance-MIDI to Score Conversion" Table 6 (grey: invalid values); "A Survey of Agent Memory in the Second Half" Table 4 (two kinds of ✓); MM-LLMs Table 2.
