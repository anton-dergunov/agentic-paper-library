---
id: html-cell-attachments
title: A footnote or badge inside a cell runs into the value
converter: html
takes: [engine, reconvert, reread]
closed: '2026-10-20'
cost: 'engine: done; reconvert the papers with a badge or a repeated note in a table; re-read EuroBERT'
---

# A footnote or badge inside a cell runs into the value

`engine` `reconvert` `reread` · html · done

**Broken.** Something attached to a value inside a cell joins it with no space. EuroBERT's Table 1 draws each score's significance rank as a small TikZ badge; `picture_text` reads it as "3" and the cell prints "42.03" for 42.0 ranked 3 (key content: every score in the table is one digit off). A footnote set in a cell leaves its mark on the value ("31⁰" in BlazePose Table 1, "66.31" for 66.3 in Phi-4 Table 1) and its text spills into the cells (Nemotron-4 340B Table 5).

**Fix.** Done 20 Oct 2026: a badge set right after a word or number (EuroBERT's significance ranks) is written in brackets after it, "37.5 (6)" (`extract_svgs`, `picture_text`). A note marked in several cells of one table is written once under it (`lift_notes`: Nemotron-4's EvalPlus note had seven copies). Cell footnotes were already set as a mark and a note under the table: Phi-4's "66.3<sup>1</sup>" is that, and BlazePose's "31<sup>0</sup>" is a superscript in the source, as printed. Cells written as HTML also lose the spaces and line breaks around and inside their text (`trim_cell`).

**What it gives.** Values as printed, with the rank or note beside them.

**Cost.** Engine: done; reconvert the papers with a badge or a repeated note in a table; re-read EuroBERT.

**Examples.** EuroBERT Table 1; BlazePose Table 1; Phi-4 Table 1; Nemotron-4 340B Table 5.
