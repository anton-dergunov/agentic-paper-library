# Experiment · what is left in a converted paper that an agent pays for and cannot read?

**Question.** After the reconversion of 8 Oct 2026 the library still showed macro names in 68 papers. Reading the arXiv HTML behind them turned up text of a different kind: titles on every cross-reference, formulas rendered into tags inside HTML tables, and the drawing commands of pictures set in formulas. How much of a paper is it, and is anything lost by dropping it?

**Status.** Measured 9 Oct 2026 on the 1,920 cached renderings of the author's library and on 40 papers drawn at random. **The titles of cross-references are 8.4% of the text of the arXiv-HTML papers; without them and with table formulas written as TeX, the 40 papers are 13.1% shorter, and 22 of them differ in nothing else.** Nine papers carried 611,000 characters of TikZ drawing commands inside formulas, and one paper's main table had lost all 189 of its numbers. All of it is fixed in the converter. **The reconversion of the whole library was started on 9 Oct and its totals are not in this write-up yet** (see "Still to add").

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html).

## Method

- **Where it comes from.** For each macro name `paperlib symptoms` still flagged, the cached arXiv HTML was read beside the library's markdown.
- **The cache.** [`cache_survey.py`](cache_survey.py) counts in every cached rendering what each fix acts on → [`cache-survey.tsv`](cache-survey.tsv).
- **The sample.** 40 arXiv-HTML papers not edited by hand, drawn with seed 20261009 ([`papers.txt`](papers.txt)), converted from the cache with the changed converter and compared line by line with the library's copy, link titles aside. Paper text is not committed.
- **The library.** `paperlib reconvert --all --jobs 3`, then [`compare.py`](compare.py) against the library's last commit: size, title characters, formulas rendered into tags, picture characters, captions, paged headings, and the words the new body lacks.

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

### Checks that were wrong

- `double-mark` flagged two notes sharing a sign ("††"); it now looks for a doubled number.
- `macro-name` flagged a prompt's printed "\nAnswer:".
- `year-citation` flagged "Kang & Schafer (2007)" with the year alone linked, which is the paper's own style.
- `pt-residue` flagged "(3pts)".

## Still to add

After the library's reconversion: its totals from `compare.py` (characters, words lost), the symptom counts before and after, `symptoms --compare HEAD` and `symptoms --katex` (80 formulas in 28 papers failed before; about 45 of them were pictures and tables in formulas), and a look at ten papers.

## What the numbers do not say

No reading test was run: a hover title repeats the reference it sits on and the section it points into, and nothing an agent is asked turns on it. The picture labels were checked by eye in four papers; a picture with no text in it becomes "[picture]". The digits taken from the MathML of "Attention is not Explanation" are rounded to four decimals, where the PDF prints fewer.

## Findings

- Link titles are dropped; `caption-numbers.py` removes the float names it needed.
- Mathematics in an HTML table is its TeX.
- A formula holding a picture or a block is rebuilt from its TeX, the picture replaced by what it shows.
- `paperlib reconvert --all` on a library that holds a PDF-converted paper with an arXiv rendering converts it from the HTML; in the example library that is Larimar, which is kept as the PDF example.
