# Experiment · row-group labels and a cell's text continued on new rows

**Question.** Two tickets, `html-multirow-lost` and `html-continuation-rows`: a table row reads as belonging to no group, or a row holds only the rest of another row's cell. What causes each, which fix reaches the ticket papers, and what does it change in the other tables of the library?

**Status.** Run 20–21 Oct 2026 on the 1,951 cached arXiv renderings of the library's HTML papers, against the converter of the commit before. **Three passes shipped: a ruled group's lone label spans its group (368 tables in 207 papers), `\multirow` spans LaTeXML dropped are taken from the LaTeX source (3 more tables among the 52 cached sources of the 406 papers that ask for one), and a cell's text continued on a row of its own is joined to it (801 tables in 434 papers with all three). The changed tables are 6.1% shorter (2,032,367 → 1,908,344 characters), 100 turn from HTML into pipe tables and none the other way.** Of the 19 multirow records, 4 are fixed on their papers, 6 are the authors' layout (wont-fix) and 5 are re-filed as new; of the 9 continuation records, 4 are fixed and 4 re-filed.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html).

## Method

- **Tracing the ticket papers.** For each example the place was read in the markdown, in arXiv's HTML (cached) and in the LaTeX source (fetched and cached by the converter's own `source_files`). The multirow records have five causes:
  1. **A ruled group's label on its middle row**, centred by hand (`\multirow{2}` on the third of five rows in "Large Language Models. A Survey" Table I) or typed there (Cosmos Table 16, `4B` on the second of three rows). The PDF shows it as the group's label because rules mark the group off; the markdown has no rules.
  2. **A `\multirow` counted short of its ruled group** ("Coupling" `\multirow{5}` over seven rows, "Splines" `\multirow{2.5}` over three in "Normalizing Flows" Table I). `extend_rowspans` did not extend it: its guard against heading rows (one filled cell) counted the row under the short nested "Splines" span as a heading.
  3. **A `\multirow` LaTeXML dropped.** Over the 73 papers with a source and a rendering in the cache, every `\multirow{-n}` lost its span (76 of 76) and 15% of the others did (107 of 708), in 17 papers. With rules the group shows where the label belongs; without ("Entity Matching" Table 6: `\multirow{-2}` labels between unruled pairs of rows) only the source does. The dropped cells look like any other in the HTML (`<span class="ltx_text">` around the label, as in 21,826 other cells), so the source cannot be fetched only where a span was dropped ([`multirow_spans.py`](multirow_spans.py)).
  4. **The authors' layout**, the same in the PDF: blank cells meaning "as above" (Emergent Abilities Table 1), no value typed (Adafactor's step sizes for (H)–(J)), a hand-drawn bracket ("Train" in the conversation-disentanglement corpus), rows a cell short in the source (rDPO, DriveDreamer4D), a prompt typed once on the first row of its group (LLaVA-1.5 Table 7). Marked wont-fix.
  5. **Not reached:** Movie Gen Table 24, ALE p. 23, two in "A Survey of Visual Transformers" Table III, and Label-features Table 4 from its second example on (an empty `\multirow{2}{*}{}` beside the Decaf row's makes LaTeXML put the InceptionXML-LF row's empty cell at its end). Re-filed as `new`.

  The continuation records: a citation under a model's name (Doc2Vec Table 1), a column title on two or three rows (Doc2Vec, MobileNets Table 11), a list going on under a row label ("Factivity," then "Symmetry/Collectivity" in GLUE Table 2), and a fragment above its row ("Pointwise, Pairwise," over "& Generative" in LLMs-as-Judges Table 1, where the rest of the row is a `\multirow{-2}`). Not reached: a label's words typed on separate data rows (`\multirow{11}{*}{self-}`, then "Model" and "improvement" on rows 5 and 7 of the data-synthesis survey; "Faster-RCNN" / "300" in MobileNets Table 13), Gemini 2.5 Table 10 and CapSpeech, re-filed as `new`. EASE Table 2 is another cause: a header row LaTeXML left in the body.
- **Apparatus.** [`compare.py`](compare.py) runs every table pass of `html-to-markdown.py` (all before pandoc but the forest trees and citations) on each cached rendering with the converter of a git ref and with the working copy, converts each table that differs with pandoc and the Lua filter, and records it. LaTeX sources are read from the cache only; each paper's first line says whether the working copy asked for its source. `--without` leaves passes out, to measure each. The tables' text is the papers', so only [`tables.tsv`](tables.tsv) is committed: paper, table, the caption's first words, HTML or pipe before and after, characters before and after.

  ```bash
  uv run python compare.py <library> --out f1.jsonl --without source_row_spans,merge_continuation_rows
  uv run python compare.py <library> --out f2.jsonl --without merge_continuation_rows
  uv run python compare.py <library> --out f3.jsonl --summary tables.tsv
  python3 -I multirow_spans.py
  ```

  Each round, changed tables were drawn at random and read as diffs, about 300 in all, and every table that changed from HTML to a pipe table. The ten test papers were reconverted in the library and compared with `paperlib symptoms` and `--compare HEAD`.

## Results

| 1,951 renderings, against the commit before | Tables changed | Papers | Characters in them | HTML → pipe |
|---|---|---|---|---|
| Ruled groups (`span_group_labels`) | 368 | 207 | 1,221,150 → 1,178,164 (−3.5%) | 28 |
| + spans from the source (`source_row_spans`) | 371 | 208 | | 28 |
| + continued cells (`merge_continuation_rows`) | 801 | 434 | 2,032,367 → 1,908,344 (−6.1%) | 100 |

- **Ruled groups.** In each column, a group between two rules whose only filled cell is a word spans the group from its first row: an HTML table gets a rowspan, a pipe table has the label moved to the group's first row, which keeps it a pipe table (the 28 tables that became pipe tables were HTML only because the old `raise_group_labels` gave a pipe table a rowspan). Changes made on the way, from reading the diffs:
  - **No label is repeated down a group.** Repeating a lone entry outside the first column filled Leaderboard Illusion Table 3 with one provider's vision model beside each of its text models, and copied long cells into padding rows (AI Agents That Matter A6). Outside the first column only a misplaced label moves: one below the group's first row, or a span cut short. One on the first row is as the author typed it (LLaVA-1.5's prompt).
  - **A number is not a label outside the first column** ("1e-5" and "20.43 ± .07" passed as words by their "e" and "pm"), but is in it: Cosmos's groups are "4B", "5B", "12B".
  - **A column whose groups mix several filled cells with blanks is left alone** (results left out), but its header is still raised: Binoculars Table 4's body has a label in two pieces, and its "Dataset" header span had been lost with it. A header label that already spans body rows is not raised into the head (LLM Hacking Table 2).
  - What the pass does elsewhere: header labels raised over two- and three-row headers (NeRF, SAM 2 and 3, V-JEPA 2), first-column groups spanned (CLIP Table 15's "Finetune", Big Bird's "Prior Art", Larimar's C1/C2), the shared cells of a benchmark's two rows spanning both (the hallucination survey's Table 4).
- **Spans from the source.** The pass runs after the ruled groups, so it fetches a source only for a table still showing the shape a `\multirow{-n}` leaves: two words in a column each under an empty cell. That is 406 papers of 1,951; counted before the ruled pass, any word beside an empty cell would have been 78% and two words under empty cells 21%: about 2 GB of sources at the cache's 5 MB a paper, downloaded once. A tabular matches a table with the same number of rows whose `\multirow` labels sit at the same row and column; a label whose rows hold anything but empty cells is left. On the 52 cached sources it changed five tables, all rightly: Entity Matching's mean table, the base-model and release columns of the Deep Research Agents survey's Tables 4–5, and two headers.
- **Continued cells.** Changes made on the way:
  - **The header is the `<thead>` or the rows above a rule under the first four**, a rule drawn as a row of its own included. Taking the rows above the first number joined EfficientNet's model rows and the variance paper's CPU and OS rows.
  - **Body rows join only when the two texts read as one**: the upper ends going on (",", "-", "/", "&", "and", "of", "by", …) or the lower is a whole parenthesis or citation, or starts with "&", ")" or ",". A colon was dropped ("Instruction 4: …" / "Instruction 5: …" are items), and so was a bracket or parenthesis opening longer text ("[73] - image classification", "(r) cut text").
  - **A header fragment joins any title above it**, both short (three words and four or five): example texts set as the head of a two-column table are not titles (ReAct Table 10, RECOMP Table 6). In the first column a word joins a title only with that evidence: "CIFAR-10" under "Model" is a sub-heading (Sparse Transformers Table 1).
  - **One-column tables keep their lines**: they are prompts and transcripts.

  What it does elsewhere: two- and three-line column titles become one (Megatron-LM, MTEB, T5, Clio, Nemotron-4, Olmo 3, DeiT), lists broken over rows with commas become one cell (CUPID, ANN-Benchmarks, "A Survey of LLMs" Table XIV, the causal-inference toolboxes), descriptions broken mid-sentence too (the bioinformatics hyperparameters, NeoBERT's and NV-Embed's instructions), and a note in parentheses joins its value (LiRank's "(O/E ratio +1.84%)", UMAP's dataset sizes).
- **On the ten test papers**, reconverted: the four multirow tables and four of the continuation tables are right (LLM survey, Normalizing Flows, Cosmos, Entity Matching; Doc2Vec, LLMs-as-Judges, GLUE, MobileNets Table 11), Label-features Table 4's first example too. No paper shrank and the symptom counts are unchanged.
