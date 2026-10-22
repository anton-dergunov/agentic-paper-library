---
id: html-footnotes-lost
title: "Footnotes missing from arXiv-HTML papers"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small once the form is found; reconvert the papers"
---

# Footnotes missing from arXiv-HTML papers

`engine` `reconvert` · html · open

**Broken.** A footnote's text is missing: in APE (§5.3, p. 9) the mark is a link "[6](#footnote6)" to nothing, and the six tasks it names are lost; in "A Case Study on Sampling Strategies" footnotes 2 and 5 are gone, mark and text, between ^1, ^3, ^4 and ^6. The other footnotes of both papers come through, so a form the converter does not take, such as `\footnotemark` with a separate `\footnotetext`, or a note inside a float or a formula, is the likely cause. In two older papers the footnotes' text is all there but in the wrong place, which points to the same form: graph2vec's three footnotes, and all of "Representation Learning on Graphs"' run together, form one paragraph between the title and the author block, away from their marks.

**Fix.** Find the two footnotes in arXiv's HTML and take that form as the others are taken; if arXiv's HTML lacks them, move the ticket to wont-fix.

**What it gives.** Footnotes that name a paper's tasks or settings.

**Cost.** Engine: small once the form is found; reconvert the papers.

**Examples.** "Large Language Models Are Human-Level Prompt Engineers" p. 9; "A Case Study on Sampling Strategies for Evaluating Neural Sequential Item Recommendation Models" pp. 2–4.
