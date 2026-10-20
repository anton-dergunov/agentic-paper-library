---
id: html-continuation-rows
title: "A cell's text continued on extra table rows"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: medium, a heuristic with fixtures; reconvert the papers"
---

# A cell's text continued on extra table rows

`engine` `reconvert` · html · open

**Broken.** An author breaks a long cell by starting a new table row (`\\` and `&` with the other cells empty), so a model's citation, the second line of a header ("PlaNet" over "MobileNet") or a category label in pieces ("self-" / "Model" / "improvement") lands on its own mostly empty row. arXiv's HTML keeps those rows, and the table gains rows that are neither data nor headers, sometimes above the row they belong to (LLMs-as-Judges Table 1).

**Fix.** Merge a row that holds only text fragments, no values and no rule above it, into the row it continues: the one above, or the one below when that row's cells in the same columns are empty. In a header, join the fragments into the header cell above. Keep a row that has values, or text in most columns (a group heading).

**What it gives.** One row per item; the citation or second line in its cell.

**Cost.** Engine: medium, a heuristic with fixtures; reconvert the papers.

**Examples.** "Distributed Representations of Sentences and Documents" Table 1; "LLMs-as-Judges" Table 1; GLUE Table 2; MobileNets Tables 11 and 13; "A Survey on Data Synthesis and Augmentation for LLMs" Tables 2–3.
