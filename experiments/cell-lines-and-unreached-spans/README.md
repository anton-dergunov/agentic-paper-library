# Experiment · lines in a cell, continued cells, spans and formula boxes the earlier passes missed

**Question.** Four tickets from the 22 Oct triage: `html-cell-lines-run-together` (lines listed in one cell read as one phrase), `html-continuation-rows-unreached` and `html-row-spans-unreached` (tables `merge_continuation_rows` and the span passes of 21 Oct left wrong), and `html-formula-box-as-image` (a framed formula saved as a picture). What causes each on the ticket papers, which change fixes them, and what does it change in other papers?

**Status.** Run 22 Oct 2026 on the ticket papers, the 1,979 cached arXiv renderings (a scan of the cells) and a sample of 201 of them converted with the converter before (git HEAD) and after. **Shipped. In the sample 136 of 201 papers change, 0.10% fewer characters (25,416,634 → 25,391,401), 61 tables turn from HTML into pipe tables (1,109 → 1,048) and none the other way, and no word is lost; line breaks in cells 767 → 3,231.** Of the 22 records of the four tickets in 21 papers, 13 are fixed on the 20 papers reconverted (17 ticket papers and three more with formula boxes), 5 wait for the overnight reconversion (all five checked fixed in a scratch conversion) and 4 are the authors' tables, the same in the PDF (wont-fix).

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html).

## Method

- **Tracing the ticket papers.** Each place was read in the markdown, in arXiv's HTML at each converter step ([`showtab.py`](showtab.py) prints a table's rows with their spans, rules and nested tabulars after any step), in the LaTeX source where spans were in question, and in the PDF's text layer where the table looked wrong in the source too.
- **The causes.**
  1. *Lines in a cell* come three ways, and pandoc joins each with spaces: a one-column tabular nested in the cell (`\makecell`, `\shortstack`), which `is_layout_tabular` keeps as spans, so `flatten_cell_tables` in the Lua filter, where the ticket put the fix, never sees it (Stop Overthinking Table 1, the RAG survey's Table IV, Autoencoding VI's topic lists); a parbox's lines, each its own `ltx_p` (Transformers in Vision Table II); and a `\\`, which pandoc reads as a line break and so writes the whole table as HTML (Autoencoding VI Table 6). In a framed box `spans_to_blocks` also made a cell's lines paragraphs, which writes the table as HTML.
  2. *Continued cells* the merge did not reach: a sentence wrapped onto the next row with no comma or "and" to show it (Ray Table 1, "…as soon as either" over "$k$ have completed"); an entry all of whose cells go on in the next row, more than half the columns (the serving survey's "LLM" over "Applications"); the second line of an entry whose other cells span both its rows (Foundation Agents Table 8.1); and a header of four rows, which `span_header_rows` capped at three and skipped whenever a header cell held a nested tabular (Entropic OOD Table VI).
  3. *Spans* not reached: an empty `\multirow{2}{*}{}` beside a filled one is dropped by LaTeXML together with the cell of the row it reaches into, so that row is a cell short (label-features Table 4); values centred by hand on the middle of three rows, a number and so not a label to `span_group_labels` (Movie Gen Table 24); a group label wrapped onto the group's next row, whose other cells hold values ("Reinforcement" over "learning" in ALE's parameter table); a `\multirow{-3}{*}{\color{…}\textbf{Hawk}}` whose colour name `plain_words` counted as a word, so the source table did not match (Griffin Table 1); a table with a stack in one cell, which `span_group_labels` skipped (the GNN survey's Table II).
  4. *Formula boxes*: `picture_kind` counts a formula as one word, so a frame around a display formula and its number holds two and is saved as an image (Universal Model Routing Eq. (11)). Inside the box the numbered equation is LaTeXML's equation table set as spans.
  5. *The authors' tables*, the same in the PDF: Reflexion's second header row puts "Test execution" under "Approach"; "A Survey of Visual Transformers" Table III(b) has two QueryInst rows both "R-50-FPN" and III(c) prints Max-L's three PQ values in that order; Entropic OOD Table I sets each technique, its two side effects and its consequence on four rows beside two-line values, which read in order. SimCLR's two "formula boxes" in the ticket are drawn crops labelled A–D, rightly images.
- **Measuring the rules.** [`scan_stacks.py`](scan_stacks.py) lists every stack left in a cell after `split_stacked_rows` in the cache: 7,708 in 429 renderings, 2,602 in header rows (679 of them read as one text by the existing cues, most of the rest titles over two lines, "Number" over "of tasks") and 5,106 in the body (2,539 read as one text). Body stacks mix item lists ("Context Relevance ¦ Faithfulness ¦ Answer Relevance", topic word lists) with wrapped labels ("Holistic ¦ Capability"). A wrapped label broken by `<br>` costs one token and loses nothing; a list joined by spaces loses its items' bounds, so the body breaks unless the lines read as one, and the header joins.
- **The sample.** 151 renderings with a body stack and 50 at random, converted by [`runeng.sh`](runeng.sh) with the engine at git HEAD and with the working copy; [`cmp.py`](cmp.py) counts characters, HTML tables and line breaks, and every changed table of the continuation and span passes was read. Reading them found ten wrong results, each fixed and the sample run again:
  - the sentence cue took "word2vec" for a word in lower case and "(Ethayarajh, 2018)" for an unfinished sentence: the lower word must be letters only and the upper end in a letter or a comma;
  - "continued" voted on whole brackets, so a table of icons read as "[times]" merged into one row: only an upper left unfinished counts, with words of three letters both sides;
  - the substitute characters "o, [, l, ;" over "q" merged on their ";";
  - two datasets under one spanning task merged as "paired": paired needs a fragment that goes on;
  - "CLIP Score Fusion" over "BLIP Feat. Fusion" lost its bound: a fragment that does not read on joins with `<br>`;
  - group label joins took "uniform" over "uniform", "relation classification" over "abstract sent. roles" and "Human" over "xl": the lower case cue needs an upper case word above, the group's empty cells below, and nothing in the next column;
  - a one-column table's lines were joined: such a table is skipped;
  - a regression coefficient alone on its middle row spread over three: a centred value counts only in a column with two such groups or more whose other values fill their groups;
  - a prompt's lines ("&lt;story&gt;" ending in the entity's ";") joined: a line's text is read unescaped, and a one-column table keeps every line;
  - "Adaptation-" over "Specific" joined with a space: a hyphen joins without one.
- **Results.** [`papers.tsv`](papers.tsv): the 136 changed papers of the sample with characters, HTML tables and line breaks before and after. The papers' text is not committed.

```bash
# old/eng and new/eng: copies of scripts/ at the two refs
python3 -I scan_stacks.py new/eng stacks.jsonl
cat sample.txt | xargs -P 8 -I{} ./runeng.sh old ~/.cache/papers/arxiv/html/{} oldout
cat sample.txt | xargs -P 8 -I{} ./runeng.sh new ~/.cache/papers/arxiv/html/{} newout
python3 -I cmp.py oldout newout
python3 -I showtab.py 2405.04545 "InceptionXML-LF" 1 merge_continuation_rows
```

## Results

| | Before | After |
| --- | --- | --- |
| Characters, 201 papers | 25,416,634 | 25,391,401 (−0.10%) |
| HTML tables | 1,109 | 1,048 |
| Line breaks in cells | 767 | 3,231 |
| Papers changed | | 136 |
| Words lost | | none (the differences are the same words written for a pipe table: links, `&` for `&amp;`, `\<tag\>`) |

By ticket, measured in turn on the sample: breaking a cell's lines changed 131 papers and 59 tables became pipe tables; the continuation rules changed 7 more after the fixes above (sentences in 1409.3215 and 2305.14763, the PaLM 2 language lists, the serving survey, Cosmos's split model name); the span rules and the formula boxes changed 19 (group labels in tables with a stack, header labels raised into a two-row head, two boxes of aligned equations now display equations).

On the ticket papers: all six cell-line examples list their items apart; Ray, the serving survey, Foundation Agents and Entropic Table VI read one row per entry; Movie Gen, ALE, label-features, Griffin and the GNN survey give each group its label, and Knowledge-Based Trust, node2vec and Graph Embedding already did; Universal Model Routing's Eq. (11), Central Flows', Laplace Redux's and Nemotron-Cascade 2's boxes are quotes with their formulas.

## Not done

- A ruled group laid out as one logical row over several (Entropic OOD Table I) stays rows: joining whole groups would merge real rows elsewhere.
- A label typed one word per row beside values ("MQA" / "Transformer" / "(Baseline)" in Griffin) stays as typed.
- `merge_continuation_rows`, `source_row_spans` and `join_wrapped_labels` still skip tables with a stack in a cell; only `span_group_labels` and `span_header_rows` see past them.
