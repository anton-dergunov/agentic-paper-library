---
id: html-reference-number-unmatched
title: "References the PDF number check does not reach still print the HTML's number"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: medium; reconvert the papers (minutes)"
---

# References the PDF number check does not reach still print the HTML's number

`engine` `reconvert` · html · open

**Broken.** `caption-numbers.py` takes a reference's number from the PDF when the words around it match (`html-shared-float-anchor`, done 21 Oct 2026). The references it leaves still print what arXiv's HTML gives, which is often wrong. The HTML can name the wrong kind ("Figure [1]" for Table 1, "Tab. [2]-(c)" for Fig. 2(c), "[Footnote 18]" or "[Section 4.2]" for a figure or table). It can drop a subfigure letter ("Figures [16] and [16]"), print a row number or a section-numbered label ("Table [5.2.2]", "Assumptions [2.1]–[2.1]"), or be off by one or more ("Table [5]" for Table 4). This ticket holds the 21 records the check of 21 Oct re-filed, plus the reference records moved from `figure-numbering` on 22 Oct 2026. Some of these may be the paper's own slips: the PDF settles each one.

**Fix.** First re-check every record against the current markdown. The full reconversion of 22 Oct 2026 renumbered references in 27 of the moved papers, so close each record whose place now matches the PDF, and delete those where the PDF prints the same number. For what is left: take the kind as well as the number from the PDF ("Table 3" where the HTML says "Figure [3]"); keep a subfigure letter the PDF prints after the number; and where the words before a reference repeat, use the words after it too. A reference the PDF prints differently from every caption is the paper's own.

**What it gives.** References an agent can follow to the right figure, table or assumption. The claims themselves are unaffected, so nothing needs a re-read.

**Cost.** Engine: medium, mostly checking records against the PDF; reconvert the papers (minutes).

**Examples.** Switchback (Tables [5.2.2], Assumptions [2.1]–[2.1]); "Bag of Tricks" p. 3; MegaScale-Infer Figs. 15–16; RMSNorm pp. 6–8; Tree of Thoughts pp. 5, 7; "Auditing language models for hidden objectives" p. 14.
