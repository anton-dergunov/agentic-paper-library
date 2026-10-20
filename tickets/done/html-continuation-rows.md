---
id: html-continuation-rows
title: A cell's text continued on extra table rows
converter: html
takes: [engine, reconvert]
closed: '2026-10-21'
cost: 'engine: medium, a heuristic with fixtures; reconvert the papers'
---

# A cell's text continued on extra table rows

`engine` `reconvert` · html · done

**Broken.** An author breaks a long cell by starting a new table row (`\\` and `&` with the other cells empty), so a model's citation, the second line of a header ("PlaNet" over "MobileNet") or a category label in pieces ("self-" / "Model" / "improvement") lands on its own mostly empty row. arXiv's HTML keeps those rows, and the table gains rows that are neither data nor headers, sometimes above the row they belong to (LLMs-as-Judges Table 1).

**Fix.** Merge a row that holds only text fragments, no values and no rule above it, into the row it continues: the one above, or the one below when that row's cells in the same columns are empty. In a header, join the fragments into the header cell above. Keep a row that has values, or text in most columns (a group heading).

Done 21 Oct 2026 ([experiment](../experiments/row-groups-and-continuation-rows/README.md)): `merge_continuation_rows`, after the span passes. In the body a fragment joins only where the two texts read as one (the upper ends going on, or the lower is a whole parenthesis or starts with "&"), and joins the row below when that is how it reads ("Pointwise, Pairwise," over "& Generative"); the spans over a joined row shrink. In the header (the `<thead>`, or the rows above a rule under the first four) short titles join whatever they read like. One-column tables keep their lines. Fixed on Doc2Vec Table 1, LLMs-as-Judges Table 1, GLUE Table 2 and MobileNets Table 11; Orca is reconverted overnight. Not reached, re-filed as `new`: a label's words typed on separate data rows (`html-label-in-pieces`: the data-synthesis survey, MobileNets Table 13), Gemini 2.5 Table 10 and CapSpeech; EASE Table 2 is a header row left in the body (`html-header-row-in-body`).

**What it gives.** One row per item; the citation or second line in its cell.

**Cost.** Engine: medium, a heuristic with fixtures; reconvert the papers.

**Examples.** "Distributed Representations of Sentences and Documents" Table 1; "LLMs-as-Judges" Table 1; GLUE Table 2; MobileNets Tables 11 and 13; "A Survey on Data Synthesis and Augmentation for LLMs" Tables 2–3.
