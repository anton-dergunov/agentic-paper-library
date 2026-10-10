# Experiment · what did one fix-conversions pass over two areas change across the library?

**Question.** Reading `search-and-ranking` and `llm/uncertainty-and-hallucination` into notes flagged conversion problems in some sixty papers. Six causes were converter bugs: characters cut in half, text colour a caption refers to dropped, a table that swallowed the rest of its paper, and three ways a table's header came out wrong. How many papers does each fix touch, and does the reconversion that follows lose or break anything?

**Status.** Run 10 Oct 2026 on the author's library: 1,904 arXiv-HTML papers reconverted, 459 of them changed. **Replacement characters fell from 1,826 in 128 papers to 6 in 3; 30 cached papers gain 314 marks for coloured text in 43 tables; six papers get a caption back beside its table; no paper shrank and no word was lost.** The header changes put a row of results in the head of three tables in two papers; the rule that repairs it was chosen on the 44 papers it could touch, after a first version broke five of them.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html).

## Method

- **The bugs** come from the catalog entries of the two areas, each read in the markdown beside the PDF page and the cached arXiv HTML.
- **The cache.** [`text_colour.py`](text_colour.py) lists every table float in the cached renderings that has no shading and now gets a mark → [`text-colour.tsv`](text-colour.tsv). [`runaway_floats.py`](runaway_floats.py) lists the papers with a float closed early → [`runaway-floats.tsv`](runaway-floats.tsv).
- **The library.** `paperlib reconvert --all --jobs 6`, then against the library's last commit: `paperlib symptoms --counts` and `--compare HEAD`, [`compare.py`](../reference-titles-and-table-math/compare.py) of an earlier experiment for the words each new body lacks, a count of "�" in the arXiv-HTML papers, the diffs of the six papers of `runaway-floats.tsv` and of the four largest, and a count over the changed papers of pipe tables, HTML tables and header rows that are mostly numbers.
- **Results rows.** Every paper whose table head holds, after its first row, a label followed only by numbers (44 papers) was reconverted with each version of the rule, and each changed table read → [`results-rows.tsv`](results-rows.tsv).

  ```bash
  uv run python text_colour.py > text-colour.tsv
  uv run python runaway_floats.py > runaway-floats.tsv
  paperlib reconvert --all --jobs 6 --state <file>       # in the library, from a clean tree
  paperlib symptoms --counts && paperlib symptoms --compare HEAD
  python3 ../reference-titles-and-table-math/compare.py <library> > compare.tsv
  ```

## Results

### Each change

| What was there | Cause | Now | Example |
|---|---|---|---|
| "��" for "†" or "±" in italics or bold; "�" for a no-break space in an equation's text | Lua's `%s` and a byte class cut a multi-byte character in two | the character | "SelfCheckGPT", "End-to-End Neural Ad-hoc Ranking with Kernel Pooling" |
| Text the caption refers to by its colour ("excluded topics are in gray"), unmarked | only cell shading was marked | `<mark>`, in a table with no shading and one text colour | "Overview of the TREC 2019 deep learning track", Table 5 |
| The rest of the paper inside a table, and the table's caption at the paper's end | a table LaTeXML could not close | the float closed where the table ends | "SIMD Compression and the Intersection of Sorted Integers", Table 7 |
| A two-row header split in two or its rows swapped; "Method" over the first sub-column | LaTeXML marks only the first row as a header | the spanned rows are header rows; leading header rows of a body move to the head | "SelfCheckGPT", Table 3; "WRENCH" |
| A row of results in the head | LaTeXML marks it as a header | it opens the body | "PLAID", Table 6 |
| A group's name on its last row, naming one row | `\multirow{-2}` | the name spans the group from its first row | "A Survey on Hallucination in Large Language Models", Table 4 |

### The cache

314 marks for coloured text in 43 tables of 30 papers. Six papers have a float closed early, one each.

### The library

1,887 papers converted, 16 more with figures arXiv does not serve, 300 skipped (converted from the PDF or the web, or edited by hand). One paper ran past the ten-minute limit beside five other jobs and converted alone in six minutes, nearly all of it re-encoding its images.

| | Before | After |
|---|---|---|
| "�" in arXiv-HTML papers | 1,826 in 128 papers | 6 in 3 papers, as arXiv's HTML has them |
| Papers showing a symptom | 397 | 395 (empty header 335 → 333; the rest unchanged) |
| Papers more than 5% shorter | | 0 |
| Words the new body lacks | | 0 (32 counted are an image's alt text, now in an HTML table) |
| Captions, headings with a page, in the 459 changed papers | 9,254 and 22,591 | the same |
| Pipe tables / HTML tables in the changed papers | 4,160 / 2,916 | 4,109 / 2,943 |
| Header rows that are mostly numbers, in the changed papers | 260 | 215 |

The 51 pipe tables that became HTML tables are those whose group names now span their rows; in the four papers with the largest diffs every one of them was a table with such names. In the six papers of `runaway-floats.tsv` only the captions moved, each to its table.

### Results rows in a head

With header rows moved into the head, three tables in two papers showed a row of results there that the rule of the day (a label, then only decimal numbers and dashes) did not catch: "GPT-4o-mini | 62% | 100% | 6.67% | 26.67%", and a row with a word among its numbers.

| Rule | Tables repaired | Tables broken |
|---|---|---|
| A row ruled off from the header counts with whole numbers and percentages too | 9 in 7 papers | 6 in 5 papers: column titles moved to the body ("Epochs \| 200 \| 400 \| 800"), and one row moved from under a cell that spans it |
| The same, only when the row mixes whole and decimal numbers or the row under it holds the same kind of values; a spanned row stays (shipped) | 7 in 5 papers | 0 |

The rule that a line above the row is enough fails because column titles that are numbers are ruled off as well. What separates them is the row underneath: titles sit over values of another kind. Left as it was: a row of "Can AI-Generated Text be Reliably Detected" under a spanning cell, the per-column dataset counts of the two VLM2Vec papers, and a row with "None" among its numbers in "An Empirical Study of Mamba-based Language Models".

## What the numbers do not say

- The header rules were read on the tables they changed, not on a sample of the tables they left alone.
- The counts of header rows that are mostly numbers include real headers (sequence lengths, shot counts); the fall from 260 to 215 says rows moved, not that 215 are wrong.
- "Text colour" marks a table only when it has one colour; a table that uses two is left unmarked.

## Findings

- A character class written for bytes cuts any character of more than one byte; the damage showed only where the character met italics, bold or an equation's text, which is why 128 papers had it and nobody had flagged it as one bug.
- LaTeXML's header marks are a guess (`ltx_guessed_headers`), wrong in both directions: a header's second row unmarked, a row of results marked. Each rule that corrects one direction has to be read on the tables it changes for the other.
- Whether a row of numbers is column titles or results cannot be told from the row and the rule above it; the row underneath tells.
