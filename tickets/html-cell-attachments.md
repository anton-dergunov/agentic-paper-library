---
id: html-cell-attachments
title: "A footnote or badge inside a cell runs into the value"
converter: html
takes: [engine, reconvert, reread]
status: open
cost: "engine: small, fixtures; reconvert the papers with a footnote or picture in a cell; re-read EuroBERT"
---

# A footnote or badge inside a cell runs into the value

`engine` `reconvert` `reread` · html · open

**Broken.** Something attached to a value inside a cell joins it with no space. EuroBERT's Table 1 draws each score's significance rank as a small TikZ badge; `picture_text` reads it as "3" and the cell prints "42.03" for 42.0 ranked 3 (key content: every score in the table is one digit off). A footnote set in a cell leaves its mark on the value ("31⁰" in BlazePose Table 1, "66.31" for 66.3 in Phi-4 Table 1) and its text spills into the cells (Nemotron-4 340B Table 5).

**Fix.** Set a picture's text in a cell apart from the value, as a superscript or in brackets. Give a cell's footnote the mark and the note under the table, as `arxiv-html.lua` does for a paragraph.

**What it gives.** Values as printed, with the rank or note beside them.

**Cost.** Engine: small, fixtures; reconvert the papers with a footnote or picture in a cell; re-read EuroBERT.

**Examples.** EuroBERT Table 1; BlazePose Table 1; Phi-4 Table 1; Nemotron-4 340B Table 5.
