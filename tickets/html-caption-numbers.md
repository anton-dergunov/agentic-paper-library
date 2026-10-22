---
id: html-caption-numbers
title: "Captions numbered by LaTeXML's counters, not the PDF's"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: medium; reconvert the papers"
---

# Captions numbered by LaTeXML's counters, not the PDF's

`engine` `reconvert` · html · open

**Broken.** LaTeXML numbers floats with its own counters. Where the author resets or shares a counter, puts a table in a figure environment or sets a listing as a figure, the captions in the markdown differ from the PDF's:

- two tables both "Table 1" (Mamba) or "Table 3" (SAM 3), and two "Table 2"s (graph RAG);
- two figures numbered 21 and two numbered 22, with no Figure 14 (Sleeper Agents);
- a results table captioned "Figure 3" that the text calls Table 4 (DeltaNet);
- code-listing figures with no number, so every later figure is off (Laplace Redux);
- subcaptions all "(a)" (Scaling Laws Beyond Fixed Training Durations, Figs. 8 and 13).

References follow the HTML's numbers, so they point to the wrong caption too.

**Fix.** Number each caption as the PDF prints it, by the route `caption-numbers.py` uses for references: match the caption's first words in the PDF's text and take the label printed before them. Then renumber the references that reach that caption by its anchor.

**What it gives.** Caption numbers that match the PDF, so page citations and "Table N" agree with what the reader sees.

**Cost.** Engine: medium (the caption side of `caption-numbers.py`); reconvert the papers.

**Examples.** Mamba pp. 10–16; SAM 3 pp. 7–8; Sleeper Agents pp. 30–34; "Parallelizing Linear Transformers with the Delta Rule" p. 7; "The GAN is dead" pp. 3, 8–9; "Hypothesis testing with e-values" Table 13.23.
