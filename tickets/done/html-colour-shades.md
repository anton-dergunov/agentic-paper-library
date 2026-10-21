---
id: html-colour-shades
title: Two shades of one colour marked alike; a caption that points to another table's colours
converter: html
takes: [engine, reconvert]
closed: '2026-10-21'
cost: 'engine: small; reconvert the papers with shaded tables'
---

# Two shades of one colour marked alike; a caption that points to another table's colours

`engine` `reconvert` · html · done

**Broken.** Two gaps left by `html-table-colours`. A table that tells best from second best by a dark and a light shade of one hue gets one mark for both, since a colour is marked by its hue name only: AlignScore's #92D050 and #E0F1CB both come out as `<mark class="green">`. And a table whose caption names no colour but refers to another table's ("The color format is the same as in Table 2") loses its marking altogether, and so does one whose legend is in a note under the table rather than its caption (Open Bandit Tables 4–6: red bold for the best and blue bold for the worst both come out as plain bold). Checked with today's converter on AlignScore: the same 14 marks, all in Table 2, against 102 cells of each shade in arXiv's HTML.

**Fix.** Name a shade by its lightness too when a table holds two of one hue ("green", "light green"), as the caption names them. Take the colours a caption refers to from the table it cites when it names none of its own, and read a table's note as part of its caption.

Done 21 Oct 2026 ([experiment](../experiments/references-shades-and-text-macros/README.md)): `shade_names` names the shades of one colour the caption refers to by their luminance ("dark-green", "light-green"; up to five, "darkest" to "lightest") where the caption tells shades apart ("dark green", "darker red", "shade", "intensity") or shows each shade in a legend of its own; else they keep one name, since two greens can mean one thing. A caption beside a plain "green" leaves that shade plain. Over five shades (a heatmap) the values say it and the name stays one. A caption that speaks of colour but names none borrows the caption of the table it links to; a paragraph opening "Note" under the table counts as caption. A colour in every other row under spanning labels no longer counts as a whole column (its header was marked instead of the cells): a column is read from the full-width rows only when they are at least half the table. Over 1,336 cached renderings with coloured tables, 14 papers' marks changed, each read: AlignScore's best and second best, the RAG survey's two oranges, DocRED's head and tail, graded tables, Open Bandit's red and blue, ClashEval's prior-bias cells. Checked on AlignScore Tables 2–4, the RAG survey, Open Bandit Tables 4–6 and ClashEval; Chameleon, Steering Llama 2, When Thinking Fails, Inverse Scaling, Contextualized Privacy, MCP, Rethinking Unlearning and Enabling Citations were already right with the converter of 17 Oct and were reconverted. Inverse Scaling's Natural Zebra row is marked on its label, as every row in one colour is ([conversion](../docs/conversion.md#arxiv-html)). Not reached: FollowBench Table 2, whose group tints are so faint the hue rule reads them as white, re-filed as `new:html-faint-tints`.

**What it gives.** Best and second best told apart in tables that mark them by shade; the ranking can be recovered from the values today, so no re-read.

**Cost.** Engine: small; reconvert the papers with shaded tables.

**Examples.** AlignScore Tables 2–4 (pp. 4–6), and the appendix tables in the same format.
