---
id: html-multirow-lost
title: Row-group labels LaTeXML lost, cut short or set on another row
converter: html
takes: [engine, reconvert]
status: fixed
cost: 'engine: large, the tabular matched in the LaTeX source; reconvert the papers'
---

# Row-group labels LaTeXML lost, cut short or set on another row

`engine` `reconvert` · html · fixed

**Broken.** In arXiv's HTML itself, a label meant to span a group of rows does not: it sits on the group's middle row ("Encoder-Only" in "Large Language Models. A Survey" Table I, the model sizes in Cosmos Table 16) or on its last row with no rule to mark the group ("Fewshot-related" in "Entity Matching using LLMs" Table 6), or covers fewer rows than the group ("Coupling" in "Normalizing Flows" Table I, five rows of seven), or is missing from rows that share it (Emergent Abilities Table 1, Adafactor Table 2, LLaVA-1.5 Table 7). The rows it should cover read as belonging to no group, and a cell missing under a lost span moves the rest of its row one column left. Some of these are the author's own layout (a label typed on the middle row by hand), which looks the same in the PDF.

**Fix.** Find the float's tabular in the LaTeX source, which the converter already fetches for figures and forest trees, and take each `\multirow`'s row, count and direction from it. Where the source has no `\multirow` (a hand-placed label), a ruled group with exactly one label spans the group from its first row; `raise_group_labels` does this today only for a label on the last row.

Done 21 Oct 2026 ([experiment](../experiments/row-groups-and-continuation-rows/README.md)): `span_group_labels` replaces `raise_group_labels` and works on every column of a table's grid. A ruled group whose only filled cell is a word gets it on its first row, spanning the group: typed on the last row, centred on a middle row (the LLM survey's Table I, Cosmos Table 16), or a span counted short (Normalizing Flows' "Coupling" 5 → 7, "Splines" 2 → 3, nested). A table without spans keeps its pipe form, the label moved up. `source_row_spans` takes the spans LaTeXML dropped (all of `\multirow{-n}`, 15% of the others) from the source, for tables rules do not mark off (Entity Matching's mean table); it fetches the source where a column has two words each under an empty cell, 406 of 1,951 papers. Six records are the authors' layout (wont-fix); Movie Gen Table 24, ALE p. 23, "A Survey of Visual Transformers" Table III and Label-features Table 4 past its first example were not reached and are re-filed as `new`. The four records left (OSWorld, Instruction Tuning survey, I-Con, CLIP Table 5) change with the fix and are reconverted overnight.

**What it gives.** Every row under its group's label: the model, dataset or setting a result belongs to.

**Cost.** Engine: large, the tabular matched in the LaTeX source; reconvert the papers.

**Examples.** "Large Language Models. A Survey" Table I; Cosmos Table 16; "Entity Matching using Large Language Models" Table 6; "Normalizing Flows. An Introduction and Review" Table I; "Emergent Abilities of Large Language Models" Table 1; "Improved Baselines with Visual Instruction Tuning" Table 7.
