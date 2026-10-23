---
id: html-caption-numbers
title: Captions numbered by LaTeXML's counters, not the PDF's
converter: html
takes: [engine, reconvert]
closed: '2026-10-23'
cost: 'engine: medium; reconvert the papers'
---

# Captions numbered by LaTeXML's counters, not the PDF's

`engine` `reconvert` · html · done

**Broken.** LaTeXML numbers floats with its own counters. Where the author resets or shares a counter, puts a table in a figure environment or sets a listing as a figure, the captions in the markdown differ from the PDF's:

- two tables both "Table 1" (Mamba) or "Table 3" (SAM 3), and two "Table 2"s (graph RAG);
- two figures numbered 21 and two numbered 22, with no Figure 14 (Sleeper Agents);
- a results table captioned "Figure 3" that the text calls Table 4 (DeltaNet);
- code-listing figures with no number, so every later figure is off (Laplace Redux);
- subcaptions all "(a)" (Scaling Laws Beyond Fixed Training Durations, Figs. 8 and 13).

References follow the HTML's numbers, so they point to the wrong caption too.

**Fix.** Done 23 Oct 2026 in `caption-numbers.py`, with `shared_label_titles` in `html-to-markdown.py` and the link filter in `arxiv-html.lua`. Five changes:

- PDF captions with no punctuation after the label ("Table 1 Evaluation …", "Table2 …", Meta's style) count for any label no punctuated caption has.
- Captions that open alike match the same PDF captions best. When as many PDF captions open with their first four words, they are paired in reading order: Mamba's two "Induction Heads" tables, and its Great Apes figure and appendix table.
- A label stays with a caption only when the PDF confirms it. A caption that matched no PDF caption no longer blocks another caption from the number.
- A short caption that matches a table and a figure in full ("FFHQ-64") takes the one of its own kind. Citations are left out of the words compared, and a caption on the line of its picture is read too.
- A link to one of two floats LaTeXML gave one label is titled "Table 3 #2" by the converter, and is renumbered by the caption it reaches. `\cref`'s "Figures 16" link text is renumbered too.

Checked on Mamba, SAM 3, DeltaNet, Sleeper Agents, graph RAG, the GAN baseline, Laplace Redux and BEIR. Their caption labels now equal the PDF's, apart from captions arXiv's HTML lacks and two panel captions in SAM 3. The e-values book prints both "Figure 13.23" and "Table 13.23" itself. Re-filed `new`: subcaptions all "(a)" (Scaling Laws), and algorithm numbering (Thompson Sampling).

**What it gives.** Caption numbers that match the PDF, so page citations and "Table N" agree with what the reader sees.

**Cost.** Engine: medium (the caption side of `caption-numbers.py`); reconvert the papers.

**Examples.** Mamba pp. 10–16; SAM 3 pp. 7–8; Sleeper Agents pp. 30–34; "Parallelizing Linear Transformers with the Delta Rule" p. 7; "The GAN is dead" pp. 3, 8–9; "Hypothesis testing with e-values" Table 13.23.
