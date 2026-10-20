---
id: html-colour-shades
title: "Two shades of one colour marked alike; a caption that points to another table's colours"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small; reconvert the papers with shaded tables"
---

# Two shades of one colour marked alike; a caption that points to another table's colours

`engine` `reconvert` · html · open

**Broken.** Two gaps left by `html-table-colours`. A table that tells best from second best by a dark and a light shade of one hue gets one mark for both, since a colour is marked by its hue name only: AlignScore's #92D050 and #E0F1CB both come out as `<mark class="green">`. And a table whose caption names no colour but refers to another table's ("The color format is the same as in Table 2") loses its marking altogether. Checked with today's converter on AlignScore: the same 14 marks, all in Table 2, against 102 cells of each shade in arXiv's HTML.

**Fix.** Name a shade by its lightness too when a table holds two of one hue ("green", "light green"), as the caption names them. Take the colours a caption refers to from the table it cites when it names none of its own.

**What it gives.** Best and second best told apart in tables that mark them by shade; the ranking can be recovered from the values today, so no re-read.

**Cost.** Engine: small; reconvert the papers with shaded tables.

**Examples.** AlignScore Tables 2–4 (pp. 4–6), and the appendix tables in the same format.
