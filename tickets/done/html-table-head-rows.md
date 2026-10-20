---
id: html-table-head-rows
title: A table's header loses a span into the body, or keeps a row of results
converter: html
takes: [engine, reconvert]
closed: '2026-10-20'
cost: 'engine: done; reconvert the papers with a rowspan in the header'
---

# A table's header loses a span into the body, or keeps a row of results

`engine` `reconvert` · html · done

**Broken.** pandoc ends a span at the end of the table's head. When a header cell spans down into the body, the span is cut and the cells below it move one column left. Two things put such a span there. LaTeXML guesses the header (`ltx_guessed_headers`) and takes in a body row that holds a label spanning the rows under it: Fixup's Table 1, where "CIFAR-10" spans three rows and the Xavier and Fixup rows come out a column short. And `raise_group_labels` lifts a header label ("Section", "Model", "↓ codec") from the second header row into the first and spans both, but the second row is not in the head: Harvard USPTO Table 5, V-JEPA Table 3, Gemma 3 Table 2, Moshi Table 16. A row of results LaTeXML guessed as a header ("DNN | 2000-2000 + dropout | ~10M | 4k | 57.8%") also stays in the head, since `is_data_row` reads "4k" and "57.8%" as text.

**Fix.** Done 20 Oct 2026: a header label `raise_group_labels` raises takes the header's rows into the head with it (`head_through` moves the `</thead>` below them or opens a head), for a header of up to five rows that a rule ends; under an explicit head, `<th>` rows opening the body (a group title, results LaTeXML guessed as a header) go back to the body (`promote_header`). In a table with guessed headers, leading `<th>` rows from a ruled-off row with a cell spanning past them become body rows (`end_guessed_heads`: Fixup Table 1). A double rule under a row ends the header too ("Do Deep Nets" Table 2). Gemma 3 Table 2 was already right (a two-level header). "4k" and "~10M" are still read as text by `is_data_row`; the rule made that unnecessary here.

**What it gives.** Header and first rows in their own columns; values under the right header.

**Cost.** Engine: done; reconvert the papers with a rowspan in the header.

**Examples.** Fixup Table 1; "The Harvard USPTO Patent Dataset" Table 5; "Revisiting Feature Prediction for Learning Visual Representations from Video" Table 3; Gemma 3 Table 2; "Do Deep Nets Really Need to be Deep" Table 2.
