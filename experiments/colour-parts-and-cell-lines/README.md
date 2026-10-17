# Experiment · colour inside cells, formulas and algorithms, and cells broken over lines

**Question.** After the fix of 16 Oct ([`colours-marks-and-icons`](../colours-marks-and-icons/README.md)), 12 of the 22 papers with an `html-table-colours` record came out unchanged, and Memory Decoder half fixed. Why, and what does fixing each cause change across the library?

**Status.** Run 17 Oct 2026 on the 1,975 cached arXiv renderings and the 213 library papers the changes can touch. **Floats with colour marks went from 326 in 173 papers to 495 in 248; in 20 changed floats read at random, no wrong mark. Fixing how cells broken over lines are flattened gave back the bold, italics, formulas and pictures of such cells: 178 papers changed, 0.52% more characters, no word lost, `macro-name` symptoms 12 → 1, 96 pictures back in 3 papers.** All 8 fixable ticket papers now carry their marks; 5 records are wont-fix.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html).

## Method

- **Tracing the 13 papers.** Each table was run through `cell_colours`, `caption_colours` and `mark_named_colours` on the cached HTML, then through the whole converter, with the marks counted after each step. Six causes:
  1. Colour on part of a cell (TRUE's red words, MATH's gray "+x%", xCOMET's coloured bullet before each row name) is never marked: a cell counts only when 80% of its text is in the colour.
  2. Colour set inside a formula (LaTeXML colours each symbol: `<mn style="--ltx-fg-color:#308CE8;">`) is not seen: only `<span>`s were read (MATH, few-sample BERT, xCOMET, Infini-gram's ■ legend).
  3. A legend's box in a text colour (LLaVA-1.5's ◼ in `#D9F2FF` text) did not match cells shaded in the same colour: legends were matched within one layer.
  4. A header row was skipped even when the caption names its colour (Memory Decoder: "Orange section: …").
  5. The marks TRUE does get were lost after `mark_shading`: TRUE writes each multi-line text as a one-column table inside the cell (`\makecell`), and `flatten_cell_tables` in `arxiv-html.lua` reduced it to `pandoc.utils.stringify` of each line, which drops all markup. Counted over 1,967 library renderings, such cells hold bold in 62 papers, formulas in 24, colour in 15, italics in 13. This became its own ticket, `html-cell-lines-flattened`.
  6. Decoupled Weight Decay's algorithms show their legend in the caption (shaded text) and the shading on lines; only table floats were read.

  Five papers were left: the continual-learning survey (TikZ overlays drawn as empty 1×1 pictures; Table XII's red absent) and Batch Normalization Explained (an empty span) lack the colour in arXiv's HTML; Entropic OOD, the continual-learning LLM survey and Swap-guided name no colour in the caption, which the rule requires by design.
- **Apparatus.**
  - [`shading_compare.py`](shading_compare.py) runs the old `mark_shading` (`h2m_old.py`, the converter of the commit before this one: `git show <commit>^:scripts/html-to-markdown.py > h2m_old.py`) and the new one over every cached rendering, and writes each float whose marks changed, with the marks added → [`shading-compare.jsonl`](shading-compare.jsonl). Every float that lost marks was read, and 20 changed floats drawn at random (seed 20261017).
  - The library papers either change can touch (those in `shading-compare.jsonl`, and those with a one-column table in a cell holding markup) were reconverted in the library, 213 papers with 3 jobs in 13 min; [`words.py`](words.py) compared each paper's words with the last commit, marks and link targets aside → [`words.tsv`](words.tsv). `paperlib symptoms --counts` was run on the changed papers before and after, in scratch libraries holding only them.

  ```bash
  uv run python shading_compare.py
  paperlib reconvert --jobs 3 --state run.jsonl <the 213 papers>     # in the library
  git diff --name-only -- library | grep '\.md$' | tr '\n' '\0' | xargs -0 python3 words.py > words.tsv
  ```

## Results

### Colour marks

| In 1,975 renderings | Before | After |
|---|---|---|
| Floats with marks | 326 | 495 |
| of them algorithms | 0 | 7 |
| Papers with marks | 173 | 248 |
| Marks | 5,618 | 10,131 |

- **Changes made on the way, from reading the floats that lost marks:**
  - A caption's colour word is matched to whole cells' colours first, and to colour inside cells only when it fits none of them. Matching all at once made "red" in Chameleon's Table 3 ("highlighted in blue and red") the brand red its name is set in, ahead of the light red of the best cells, which only matches "red" as a neighbouring hue; 8 marks moved from the numbers to the name.
  - A formula counts as coloured when half its visible symbols are in the colour, not 80%: MATH sets "+15%" with the "%" back in black.
  - A `\phantom` in a text colour is not colour (MATH aligns its column with a gray invisible "5", which was marked three times); in a background colour it is a legend's box (`\colorbox{…}{\phantom{x}}` in the Moshi technical report's Table 18) and prints as "■" rather than its hidden "x".
- **Floats that still have fewer marks, rightly:** the MoR paper's Table 4 (a gray formula cell now counts, so both gray rows are shaded end to end and marked once, on their first cell, as the rule is); 2309.01219's Table 10 (the old marks were two red "User Input" headers, the new one the "captivating drama film" the caption says is highlighted in red).
- **In the sample of 20**, all right: ROME's green and red numbers (Tables 4 and 5), case studies' red and green spans (2407.02485, 2606.02245), chat templates' blue `{x}`, MT-bench's "bottom gray value is #votes", T5's "greyed-out word apple", 2405.04545's gray mispredicted labels (its caption's legend: "Labels" in gray). Tülu 3's caption gains two marks on its own pink words ("color-coded"), harmless.
- **In the ticket papers:** TRUE's 16 red and blue spans; Memory Decoder's orange header row; MATH's 7 gray gains; few-sample BERT's 36 blue results; xCOMET's 17 coloured bullets with the caption's legend; LLaVA-1.5's and Infini-gram's legend rows; Decoupled Weight Decay's lines 6 and 9 of Algorithm 1 and line 6 of Algorithm 2. Line 12 of Algorithm 2 is a raw `\hbox{…pagecolor{SpringGreen}…}` in arXiv's HTML, so that algorithm has one colour and plain marks.

### Cells broken over lines

| 178 changed papers | Before | After |
|---|---|---|
| Characters | 23,678,822 | 23,801,774 (+0.52%) |
| Papers with a symptom | 63 | 57 |
| `macro-name` | 12 | 1 |
| Words lost | | none |

- **What the word counts show:** the 13 papers that "lost" words lost tokens like `times128`, `sim1800` and `langleBOS_TOKEN`: bare TeX that is now a formula again (`$\times 128$`). The bullet paper's `&gt;` is `$>$`.
- **Pictures in such cells** were dropped without a trace before: 49 in BigGAN's sample grids, 45 in GME's examples, 2 in Knowledge Graphs. Their later figure files are renumbered.
- **Tülu 3** lost one picture file: its red legend square is read as "[red ■]" now, like the blue, orange and green squares beside it.
