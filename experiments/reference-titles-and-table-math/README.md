# Experiment · what is left in a converted paper that an agent pays for and cannot read?

**Question.** After the reconversion of 8 Oct 2026 the library still showed macro names in 68 papers. Reading the arXiv HTML behind them turned up text of a different kind: titles on every cross-reference, formulas rendered into tags inside HTML tables, and the drawing commands of pictures set in formulas. How much of a paper is it, and is anything lost by dropping it?

**Status.** Measured 9 Oct 2026 on the 1,920 cached renderings of the author's library and on 40 papers drawn at random. **The titles of cross-references are 8.4% of the text of the arXiv-HTML papers; without them and with table formulas written as TeX, the 40 papers are 13.1% shorter, and 22 of them differ in nothing else.** Nine papers carried 611,000 characters of TikZ drawing commands inside formulas, and one paper's main table had lost all 189 of its numbers. All of it is fixed in the converter. The library was reconverted on 9 Oct: 1,889 papers in 2 h 31 min, none failed, **9.6% fewer characters in 1,890 papers**, and the look at the result found four more converter bugs, fixed the same day (see "The library").

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html).

## Method

- **Where it comes from.** For each macro name `paperlib symptoms` still flagged, the cached arXiv HTML was read beside the library's markdown.
- **The cache.** [`cache_survey.py`](cache_survey.py) counts in every cached rendering what each fix acts on → [`cache-survey.tsv`](cache-survey.tsv).
- **The sample.** 40 arXiv-HTML papers not edited by hand, drawn with seed 20261009 ([`papers.txt`](papers.txt)), converted from the cache with the changed converter and compared line by line with the library's copy, link titles aside. Paper text is not committed.
- **The library.** `paperlib reconvert --all --jobs 3`, then [`compare.py`](compare.py) against the library's last commit: size, title characters, formulas rendered into tags, picture characters, captions, paged headings, and the words the new body lacks → [`compare.tsv`](compare.tsv). Then `paperlib symptoms --counts`, `--compare HEAD` and `--katex`, a count of the numbers each paper lost, and a reading of eleven papers.

  ```bash
  python3 cache_survey.py ~/.cache/papers/arxiv/html > cache-survey.tsv
  paperlib reconvert --all --jobs 3 --state <file>       # in the library, from a clean tree
  python3 compare.py <library> > compare.tsv
  ```

## Results

### In the 1,920 cached renderings

| What | Count | Renderings |
|---|---|---|
| Characters of link titles | 18,908,006 | 1,896 |
| Formulas holding a `<div>` or an `<svg>` | 75 | 12 |
| of them with a TikZ picture's commands as their TeX | 54 (611,118 characters) | 9 |
| Numbers whose TeX is `\par` | 189 | 1 |
| `\par` set as text | 106 | 2 |
| Undefined-macro marks carrying a second class | 4,132 | 178 |
| Undefined colour macros with the colour's name as text | 898 | 2 |
| `\citeauthoryear`, `\cite[citep]{…}`, `\diaghead` as text | 103, 28, 5 | 1, 1, 2 |

In the library's markdown before the change: 60,453 formulas written as `<span class="math inline">` in the HTML tables of 876 papers, 0.9% of the text for the tags alone.

### Each change

| What was there | Cause | Now | Example |
|---|---|---|---|
| `[8](#S4.T8 "Table 8 ‣ 4.2 Results ‣ 4 Experiments ‣ <paper title>")` | LaTeXML's hover title on every reference | `[8](#S4.T8)`; the float's name is kept until `caption-numbers.py` has used it | every paper |
| `<span class="math inline">×10<sup>3</sup></span>`, and "0.26" then loose TeX for 0.26 ± 0.0020 | pandoc renders a formula itself in a table it writes as HTML, and gives up on some | the formula's TeX, `$\times 10^{3}$`; a plain number bare | "How Do Large Language Models Acquire Factual Knowledge During Pretraining", Table 2 |
| `\hbox to46.43pt{\vbox to13.69pt{\pgfpicture…` for thousands of characters | a TikZ picture inside a formula | what the picture shows: `\{\text{Critique},\text{Retrieve}\}`, `c_{t}` | xLSTM 859,318 → 214,786 characters; Self-RAG's reflection tokens |
| "par" in every cell of a table | siunitx numbers whose TeX arrives as `\par`, the digits only in the MathML | the digits, rounded as other siunitx numbers | "Attention is not Explanation", Table 2: "0.3954 $\pm$ 0.2096" |
| "4 \parExperiments", `\cellcolor c3-item-bkg`, `\citeauthoryearBengio et al.2003` | TeX that LaTeXML set as text | dropped or read | 835 colour names in "Perception Encoder" |
| `\llmchip` in a table header | the undefined-macro mark had a second class | dropped like the others | 178 renderings |
| "Section gen_inst" | a reference to a section left as its label | the section's number, from the LaTeX source | LLM.int8(), BetterBench, Sparks of AGI |
| An empty "Table 1:" under an algorithm, beside the real Table 1 | LaTeXML numbers a float with no caption | dropped when a captioned float has the label | DAPO |
| A caption the PDF pass could not find | it follows a sub-table's "(b) …" in one block | found | ColBERTv2, Table 5 |
| A line of "†††" under the abstract | notes with no place in the text | the notes alone | "Transformers without Normalization" |

### The 40 papers

4,879,990 characters before, 4,240,328 after (−13.1%), measured with the link titles and table formulas changed and before the smaller fixes. 22 papers are the same line for line once titles are set aside. In the other 18 the changed lines are formulas in HTML tables, and three headings in one paper that now carry a page: with the titles gone the page search finds them.

### The library

`paperlib reconvert --all --jobs 3` ran from 12:21 to 14:52: 1,889 papers converted, 16 more with figures arXiv does not serve, 299 skipped (276 converted from the PDF, 16 not from arXiv's HTML, 7 edited by hand), none failed. The seven edited by hand had their link titles removed with `LINK_TITLE` alone.

| In 1,890 papers | Before | After |
|---|---|---|
| Characters | 228,311,604 | 206,343,833 (−9.6%) |
| Characters of link titles | 19,092,186 | 0 |
| Formulas rendered into tags in HTML tables | 60,511 | 17, in two papers edited by hand |
| Characters of formulas holding a picture's commands | 816,968 | 0 |
| Captions | 30,756 | 30,755 (DAPO's empty "Table 1:") |
| Headings with a page | 80,715 | 80,883 (in 46 papers) |

| `paperlib symptoms` | Before | After |
|---|---|---|
| Papers with a symptom | 417 | 397 |
| `macro-name` | 56 | 42 |
| `tex-box` | 9 | 5 |
| `empty-ref` | 9 | 1 |
| `double-mark` | 3 | 2 |
| `empty-header` | 335 | 335 |
| Formulas KaTeX cannot parse | 80 in 28 papers | 66 in 25 papers, of 488,925 |

Of the 66 formulas, 28 in five papers hold a `tabular`, a `NiceArray` or an `\includegraphics`, and 17 in eleven papers are a model's reading of a PDF.

- **Size.** `symptoms --compare HEAD` lists 1,323 papers as 5% shorter, because it counts a link's title as words. With the titles taken out of the old text, 17 papers are 5% shorter and one is longer. Each was read: picture commands (xLSTM −34%, "Scaling Laws for Generative Mixed-Modal Language Models", "Attention Heads of Large Language Models", Self-RAG, "The Platonic Representation Hypothesis", "Real numbers, data science and chaos"), colour names (Perception Encoder), titles with a quotation mark in them, which the pattern for titles does not match (H₂O, "Asynchronous Methods…", "Cross-validation…", π0.5, YaRN), and table formulas that count as fewer words once they are TeX ("1.000 ± 0.000" is three words, `$1.000\!\pm\!0.000$` one).
- **Words.** `compare.py` counts 10,565 words of three letters or more that the new bodies lack, in 203 papers. About 5,300 of them are in a formula now ("BERT", "Large", "TabM" in a table header) and are not lost. The rest are colour names ("item", "bkg", "avg", "cellcolor": 3,100 in Perception Encoder), words of titles with a quotation mark, "par" (306 in "Attention is not Explanation"), citation commands and macro names.
- **Numbers.** The words say nothing of digits, so the numbers of each paper were counted too. 147 papers lack a number they had. In the 45 that lack most, all but two lost a picture's coordinates or a `\scalebox` factor, or lost nothing: the count splits a number at a thousands separator and takes a "<" for a tag. The two are the first bug below.

### Four bugs the look found

| What was there | Cause | Now |
|---|---|---|
| 375 empty cells in Perception Encoder's tables, and 15 benchmark names missing in "When AI Benchmarks Plateau" | the name of an undefined colour runs into the cell's text ("c3-avg-bkg72.6", "gray!10ANLI"), and a cell of one word was taken whole for the name | a mix (`gray!10`) ends by its syntax; a one-word cell that begins with a known name keeps the rest |
| "shown in Figure ." in DeepWalk, after the fix for empty references | its source has an `appendix.tex` with its own `\documentclass`, taken for the paper | the longest document of the source is the paper (5 of the 155 sources the library needed) |
| "Table 2" for DeepWalk's Tables 3 and 4; "Table 3" for Table 5 in "Bad Students Make Great Teachers" | captions that open with the same words, the first of them taken | paired with the HTML's captions in order |
| A float's number on a reference to something else: "Eq. 4" for three equations of one paper, "Appendix 2", "Algorithm 7" for Algorithm 1 | the caption looked for was the first of the float before the label, though the label is an equation's or a section's, or follows the float's main caption after its sub-figures' | the caption before the label, inside the label's float (a table, figure or algorithm); a label outside one shows its name. 9 of the 78 papers with such references changed; the three numbers checked against the PDF are now right |

`paperlib check` took "Table\![1](#S5.T1)" for an image once the link had no title; it skips an escaped "!".

### The eleven papers

Title, authors, citations, one table with formulas and one equation were read in "Attention is not Explanation" (Table 2 agrees with the PDF: 0.3954 ± 0.2096 where it prints 0.40 ± 0.21), xLSTM (equations 1–3 are clean), DeepWalk, Self-RAG (its reflection tokens are `\{\text{Critique},\text{Retrieve}\}`), "The Platonic Representation Hypothesis", "How Do Large Language Models Acquire Factual Knowledge During Pretraining" (`$0.26{\pm}\text{\scriptsize 0.0020}$`), TabM, "Large-scale Validation of Counterfactual Learning Methods", DAPO, ColBERTv2 and "Transformers without Normalization". Nothing wrong beyond the bugs above.

### Checks that were wrong

- `double-mark` flagged two notes sharing a sign ("††"); it now looks for a doubled number.
- `macro-name` flagged a prompt's printed "\nAnswer:".
- `year-citation` flagged "Kang & Schafer (2007)" with the year alone linked, which is the paper's own style.
- `pt-residue` flagged "(3pts)".

## What the numbers do not say

No reading test was run: a hover title repeats the reference it sits on and the section it points into, and nothing an agent is asked turns on it. The numbers each paper lost were read for the 45 papers that lost most, not for all 147. The picture labels were checked by eye in four papers; a picture with no text in it becomes "[picture]". The digits taken from the MathML of "Attention is not Explanation" are rounded to four decimals, where the PDF prints fewer.

## Findings

- Link titles are dropped; `caption-numbers.py` removes the float names it needed.
- Mathematics in an HTML table is its TeX.
- A formula holding a picture or a block is rebuilt from its TeX, the picture replaced by what it shows.
- A reference LaTeXML lost gets a float's number only when its label is inside that float; captions that open alike are paired in order; the paper is the longest document of its source.
- After an undefined colour macro the colour's name goes and the cell's text stays.
- A comparison of sizes or words does not see a lost number: count the numbers too after a reconversion.
- `paperlib reconvert --all` on a library that holds a PDF-converted paper with an arXiv rendering converts it from the HTML; in the example library that is Larimar, which is kept as the PDF example.
