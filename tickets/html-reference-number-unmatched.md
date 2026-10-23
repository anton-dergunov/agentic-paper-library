---
id: html-reference-number-unmatched
title: References the PDF number check does not reach still print the HTML's number
converter: html
takes: [engine, reconvert]
status: fixed
cost: 'engine: medium; reconvert the papers (minutes)'
---

# References the PDF number check does not reach still print the HTML's number

`engine` `reconvert` · html · fixed

**Broken.** `caption-numbers.py` takes a reference's number from the PDF when the words around it match (`html-shared-float-anchor`, done 21 Oct 2026). The references it leaves still print what arXiv's HTML gives, which is often wrong. The HTML can name the wrong kind ("Figure [1]" for Table 1, "Tab. [2]-(c)" for Fig. 2(c), "[Footnote 18]" or "[Section 4.2]" for a figure or table). It can drop a subfigure letter ("Figures [16] and [16]"), print a row number or a section-numbered label ("Table [5.2.2]", "Assumptions [2.1]–[2.1]"), or be off by one or more ("Table [5]" for Table 4). This ticket holds the 21 records the check of 21 Oct re-filed, plus the reference records moved from `figure-numbering` on 22 Oct 2026. Some of these may be the paper's own slips: the PDF settles each one.

**Fix.** Done 23 Oct 2026 in `caption-numbers.py` (`pdf_references`). The words before the float word are matched, and the kind and the number the PDF prints after them are taken, along with the float word itself: "Figure [1]" becomes "Table [1]", "[Footnote 18]" becomes "[Figure 7]", "[Section 6.4]" becomes "[Table 6]". Only a word of another kind is taken from the PDF. Another spelling of the same kind ("Figs." for "Figures") is not, since the PDF can print a list otherwise ("Figs. 13 and 15 to 18"). A plain number or letter in a formula ("$20\%$", "$b=1$") now counts as words, so a reference just after one is found ("(Table [5]" → "(Table [3]" in Tree of Thoughts). Checked against the PDF on S4, ATLAS, AgentDojo, OpenOOD, AUM, Quantifying, Auditing, Tree of Thoughts, UDA and the GAN baseline. Re-checking the records found Bag of Tricks' "Figure 1" and "Figure 3" printed so in its PDF, and Generating Training Data's places now agree with the PDF.

Not done:
- A subfigure letter the PDF prints after the number: the PDF's word tokens lose the parentheses, so "Figure 2 a model" cannot be told from "Figure 2(a)" without the raw text (MegaScale-Infer, variance reduction).
- Row references (piano transcription) and equation references (vLLM, Hyena), which keep the HTML's numbers by design.
- Switchback, whose tables have no captions in the markdown and whose theorems the HTML numbers by section.

Those records are re-filed `new`. The 56 records left are reconverted overnight.

**What it gives.** References an agent can follow to the right figure, table or assumption. The claims themselves are unaffected, so nothing needs a re-read.

**Cost.** Engine: medium, mostly checking records against the PDF; reconvert the papers (minutes).

**Examples.** Switchback (Tables [5.2.2], Assumptions [2.1]–[2.1]); "Bag of Tricks" p. 3; MegaScale-Infer Figs. 15–16; RMSNorm pp. 6–8; Tree of Thoughts pp. 5, 7; "Auditing language models for hidden objectives" p. 14.
