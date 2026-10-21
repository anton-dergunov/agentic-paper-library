---
id: html-row-spans-unreached
title: "Row-spanning labels the span repair does not reach"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small to medium, a fixture per table below; reconvert the papers"
---

# Row-spanning labels the span repair does not reach

`engine` `reconvert` · html · open

**Broken.** Tables left wrong by `html-multirow-lost` (done 21 Oct 2026): a `\multirow` label LaTeXML lost or misplaced still leaves its rows unlabelled or a cell short, so the rest of the row moves one column left. Movie Gen Table 24 has its merged threshold cells blank; ALE's parameter table (p. 23) has its group column flattened; "A Survey of Visual Transformers" Table III has two unlabelled QueryInst R-50-FPN rows (b) and a MaxDeepLab Max-L row that looks shifted (c); in the label-features paper's Table 4, LaTeXML puts an empty `\multirow{2}{*}{}` beside the Decaf row's, so from the second example on the InceptionXML-LF rows are a cell short with an empty cell at the end.

**Fix.** Trace each table through `span_group_labels` and `source_row_spans`: why the group was not ruled off, the source not fetched, or the source's span not matched to the row. An empty `\multirow` in the source spans nothing and should be dropped rather than placed.

**What it gives.** Every row under its group's label, values in their columns.

**Cost.** Engine: small to medium, a fixture per table below; reconvert the papers.

**Examples.** Movie Gen Table 24 (p. 51); "The Arcade Learning Environment" p. 23; "A Survey of Visual Transformers" Table III(b), (c) (p. 13); "Learning label-label correlations in Extreme Multi-label Classification via Label Features" Table 4 (p. 6).
