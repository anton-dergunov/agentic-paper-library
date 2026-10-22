---
id: html-row-spans-unreached
title: Row-spanning labels the span repair does not reach
converter: html
takes: [engine, reconvert]
closed: '2026-10-22'
cost: 'engine: small to medium, a fixture per table below; reconvert the papers'
---

# Row-spanning labels the span repair does not reach

`engine` `reconvert` · html · done

**Broken.** Tables left wrong by `html-multirow-lost` (done 21 Oct 2026): a `\multirow` label LaTeXML lost or misplaced still leaves its rows unlabelled or a cell short, so the rest of the row moves one column left. Movie Gen Table 24 has its merged threshold cells blank; ALE's parameter table (p. 23) has its group column flattened; "A Survey of Visual Transformers" Table III has two unlabelled QueryInst R-50-FPN rows (b) and a MaxDeepLab Max-L row that looks shifted (c); in the label-features paper's Table 4, LaTeXML puts an empty `\multirow{2}{*}{}` beside the Decaf row's, so from the second example on the InceptionXML-LF rows are a cell short with an empty cell at the end.

**Fix.** Trace each table through `span_group_labels` and `source_row_spans`: why the group was not ruled off, the source not fetched, or the source's span not matched to the row. An empty `\multirow` in the source spans nothing and should be dropped rather than placed.

Done 22 Oct 2026 ([experiment](../experiments/cell-lines-and-unreached-spans/README.md)). Five causes, each with a fixture. Label-features: LaTeXML drops an empty `\multirow{2}{*}{}` whose column a span already covers, with the cell of the row it reaches into; `restore_dropped_cells` gives that cell back where a row is short by the spans ending above it and the source has an empty `\multirow` there, and `span_group_labels` then spans the label. Movie Gen: thresholds centred by hand on the middle row of three are labels when the column does so for two groups or more and fills its other groups (a coefficient alone on a middle row is not). ALE: a group label wrapped onto the group's next row beside its values joins its cell (`join_wrapped_labels`). Griffin: `plain_words` read the colour of `\color{tableemphcolor}\textbf{Hawk}` as a word, so the source table never matched. GNN survey: `span_group_labels` skipped tables with a stack in a cell; `hide_nested_tables` sets the stacks aside. Already right with the converter of 21 Oct: Knowledge-Based Trust Table 7, node2vec Table 4, Graph Embedding Table 1. Not converter faults: "A Survey of Visual Transformers" Table III(b) has two QueryInst rows both "R-50-FPN" and III(c) prints Max-L's PQ values in that order, in the PDF too.

**What it gives.** Every row under its group's label, values in their columns.

**Cost.** Engine: small to medium, a fixture per table below; reconvert the papers.

**Examples.** Movie Gen Table 24 (p. 51); "The Arcade Learning Environment" p. 23; "A Survey of Visual Transformers" Table III(b), (c) (p. 13); "Learning label-label correlations in Extreme Multi-label Classification via Label Features" Table 4 (p. 6).
