# Experiment · what does an agent lose when a table's bold, footnotes and shading are dropped, and which of them are worth their tokens?

**Question.** The fix pass of 8 Oct 2026 over the whole catalog left ten converter bugs in [`docs/tasks/conversion-follow-ups.md`](../../docs/tasks/conversion-follow-ups.md), the commonest being that the bold, underline, italics and cell colour marking a table's best or significant result were gone. Where does each come from, what does fixing it change in real papers, and for cell colour, which markdown cannot express: does keeping it help an agent answer questions about the table?

**Status.** Run 8 Oct 2026 on 91 arXiv-HTML papers of the author's library (the 31 the task file names and 60 at random) and, for the counts, on all 1,917 cached renderings. **Bold went from 244 marks to 9,930 in the 91 papers, underline from 0 to 774, footnote marks printed twice from 649 to 10, macro names left as text from 166 to 16; no word of any paper was lost; the papers grew 0.58%.** Shading: a model answered 11 of 15 shading-dependent questions without it and 15 of 15 with it marked, but three of the four gains were "which method is the paper's own", which a reader of the whole paper knows. Shading is kept only where the caption refers to it and the table uses one colour: 813 marks in 110 tables of 62 papers. The reading test cost $1.08. The full reconversion has not been run.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html), and the rule "the markdown is for the agent" at the top of that page.

## Method

- **Where each bug comes from.** The raw arXiv HTML behind each example was read beside the library's markdown. Three were not where the list put them:
  - Bold was lost everywhere, not only in tables: the pandoc filter unwrapped every `<span>`, and LaTeXML writes `\textbf`, `\textit` and `\underline` as spans (`\emph` is an `<em>` and survived). 82,758 bold table cells in 1,455 of 1,917 renderings, 34,701 uses in running text in 1,575.
  - Superscripts were right in the markdown (`10<sup>4</sup>`). `read_view`, the text `paperlib read` gives a model, deleted the tags, so $10^4$ read "104" and a footnote mark became a digit of the word before it.
  - "Comment lines inside a code listing become headings" could not be reproduced: the lines are inside a correct code fence, and `page-map.py` skips fences. A `grep '^#'` shows them.
- **Corpus.** [`papers.tsv`](papers.tsv), drawn by [`sample.py`](sample.py): the papers the task file names that are arXiv-HTML and not hand-edited (31), and 60 others at random (seed 20261008). Paper text is not committed.
- **Apparatus.**
  - The 91 papers were reconverted in a git worktree of the library, and [`compare.py`](compare.py) diffed each against the library's last commit → [`compare.tsv`](compare.tsv).
  - [`page_markers.py`](page_markers.py) ran the old and the new `page-map.py` over every arXiv-HTML paper (1,911 with a PDF) → [`page-markers.tsv`](page-markers.tsv).
  - [`shading.py`](shading.py) classified every shaded table float in the cache with the converter's own functions → [`shading.tsv`](shading.tsv).
  - [`reading_test.py`](reading_test.py) picked sixteen shaded tables ([`tables.tsv`](tables.tsv)), four for each of rows or cells shaded and the caption referring to the shading or not; one had no cell to mark and was dropped. Each table, its caption and the two paragraphs citing it were converted with the shading dropped and with it as `<mark>`. Opus answered one question that depends on the shading and one plain lookup over each ([`questions.tsv`](questions.tsv), 60 requests, [`answers.jsonl`](answers.jsonl)); the answers were graded by hand against the expected answer.

  ```bash
  PAPER_LIBRARY=<library> uv run python sample.py > papers.tsv
  paperlib reconvert --jobs 3 $(cut -f2 papers.tsv)      # in a worktree of the library
  python3 compare.py <worktree> papers.tsv > compare.tsv
  PAPER_LIBRARY=<library> uv run python page_markers.py <old page-map.py> ../../scripts/page-map.py > page-markers.tsv
  uv run python shading.py > shading.tsv
  uv run python reading_test.py pick shading.tsv > tables.tsv
  uv run python reading_test.py excerpts tables.tsv <dir> && uv run python reading_test.py ask questions.tsv <dir> > answers.jsonl
  ```

## Results

### The sample, before and after

| In 91 papers | Before | After |
|---|---|---|
| Characters | 12,118,274 | 12,188,228 (+0.58%, about 770 a paper) |
| Bold marks | 244 | 9,930 |
| Italic marks | 7,666 | 11,787 |
| Underlines | 0 | 774 |
| A footnote mark printed twice | 649 | 10 |
| Macro names left as text | 166 | 16 |
| Captions "Table N:" / "Figure N:" | 1,766 | 1,766 |
| Headings with a page | 4,171 | 4,158 |
| Papers showing a symptom | 82 | 28 |

- **No word was lost.** The 328 words the new bodies lack are macro names ("sans", "authorFour", "rotate"), the labels LaTeXML puts in a note ("thanks", "footnotemark"), and words that were two words glued together ("FlashGemini", "rotateLlama").
- **The ten doubled marks left are two notes that share a mark** (an author with two `\thanks`, both "†"). The sixteen macro names left are text the paper prints (a prompt's "\n", `<\think>`).
- **Bold in an HTML table costs 7 characters, not 17.** Tables with merged cells are written as HTML, where pandoc writes `<strong>`; the first run grew the papers 0.9%, and 69,000 of the 110,000 characters were that tag. It is written as `<b>`.
- **No new symptom, no paper shrank by 5%, and KaTeX fails on the same equations**: 80 spans in 28 papers of the library before, and the same 80 with the 91 papers reconverted. The 13 headings without a page had a wrong one (below).

### Each bug

| Bug | Cause | Fix | Result |
|---|---|---|---|
| Bold, underline, italics lost | every span unwrapped | kept as `**`, `*`, `<u>`; not in headings, column titles or a caption's label | "Which Tricks…" Table 2 has YetiRank's row in bold again; ANN-Benchmarks Table 2 its italics |
| Superscripts flattened | `read_view` deleted `<sup>`, `<sub>` | written `^x`, `_x` | "N = 10^4", "21.9_{0.4}"; no reconversion needed |
| A value and its deviation glued | a smaller or coloured span with no space | a space | "70.9 +2.3" (Qwen3), "0.34 0.01" (the `±` is not in arXiv's HTML) |
| Footnotes spliced in | mark, mark, number and text inline | one mark; the text after the paragraph or table | 649 → 10 |
| ColBERTv2's Table 5 named Table 7 | the PDF caption of Table 5 is not found (it follows a sub-table's "(b)"), and four shared opening words gave it Table 7's number | a PDF label goes to one caption, the best match, and never to a second | Table 5 again |
| Stacked column titles reversed | the upper line comes second, raised with CSS | a raised span goes first | "Gemini 2.5 Pro"; 80 cells, one paper |
| "( ?)" citations | no key left in the HTML | the `\cite` after the same words in the LaTeX source, labelled from the `.bib` | 69 of 91 in "Transformer models: an introduction and catalog"; 3 in a second paper not found |
| "¿" for ">" | text-font encoding | a lone "¿" or "¡" is ">" or "<" | 47 places in 16 renderings |
| Macro names as text | LaTeXML prints an unknown macro's name | the name is dropped, its arguments stay | 3,138 uses of 199 macros in the cache; `\order{n}` is $\mathcal{O}(n)$ |
| Page markers restart in an appendix | "#### 1. Basic properties" took section 1's destination | a numbered heading is a section only at the level sections sit at | below |
| A panel loses its row labels | the paper prints them in the left panel only | the right panel gets the left one's first column | "Decoding billions…" Tables 4–6; one paper in the cache |
| A row shifted by an empty cell | a `\multirow` counted one row short | the spanning cell takes the row | "Dense Text Retrieval…" Tables I, IV; 339 rows in 117 papers before a guard for heading rows |

- **Page markers.** Over 1,911 papers and 87,312 headings, 90 markers changed in 16 papers. Headings paged before an earlier heading fell from 114 to 31. The 22 that lost their page all had a wrong one and hold mathematics, which the text search cannot match. A first version, refusing any destination that runs backwards, was worse: one wrong destination early in a paper (a numbered run-in heading in the introduction) then refused every right one after it, and 65 headings lost a page.
- **The panel fix needed its guard.** Without requiring names in the labelled column and numbers in the other panel's first column, it also fired in five papers whose panels have label columns of their own.

### Shading

Of 14,452 table floats, 1,390 (9.6%) in 320 papers shade a cell. 607 of them use more than one colour.

| What the shading picks out | Tables | Papers | Caption refers to a colour or shading |
|---|---|---|---|
| Some rows | 588 | 193 | 73 |
| Some cells, a third or fewer | 333 | 127 | 79 |
| Whole columns | 205 | 83 | 17 |
| Some cells, over a third | 132 | 72 | 22 |
| Alternate rows | 61 | 27 | 2 |
| Header row | 42 | 18 | 1 |
| Whole table | 29 | 8 | 1 |

Reading test, 15 tables, each question over the plain and the marked excerpt:

| | Plain | Marked |
|---|---|---|
| Shading-dependent question right | 11 | 15 |
| Lookup question right | 15 | 15 |

- **The four gains.** One is real: a caption says "Gray indicates non-representation steering methods", and without the shading the model answered that the excerpt does not say which they are. The other three asked which method is the paper's own, of a table whose shaded row is that method; the model declined to say from an excerpt, and would know from the paper's title and abstract.
- **No harm was observed**, including where it was looked for: marks on a decorative label column, on a header's logo, on the paper's own row under a caption about gray *text*, and one `<mark>` standing for two colours ("best in blue, second-best in green"), where the model answered from the numbers.
- **What each rule would write** in the 1,917 renderings: marking all shading that picks out rows or cells, 14,384 marks in 1,027 tables of 286 papers; only where the caption refers to it, 2,720 marks in 190 tables of 112 papers; that and one colour only, 813 marks in 110 tables of 62 papers.

## What the numbers do not say

The reading test is fifteen tables, one question each, one model, one run, graded by the author of the questions. It shows that a mark can carry a caption's meaning and that marks did not mislead in these fifteen; it does not measure how often an agent reading a whole paper is asked something that turns on shading. The "caption refers to it" check is a word list ("gray", "shaded", "highlight", colour names) and also fires on captions about coloured text. Shading in several colours, 44% of shaded tables, is not kept at all, and neither is a heat map ("Continual Learning via Sparse Memory Finetuning", Table 1, 83 shades). The sample's named papers were chosen for their bugs, so its before-and-after counts overstate a typical paper; the random 60 are in the same table. The fixes were checked in each named paper at the table or passage the task file cites, not across each paper.

## Findings

- Bold, italics and underlining are kept everywhere but in headings, column titles and caption labels: 0.58% more characters for the marking a table's claim rests on.
- A footnote follows the paragraph or table it annotates, its mark printed once.
- Shading is kept as `<mark>` only where the caption refers to it and the table has one shading colour. Marking more costs five to eighteen times the marks for answers a reader of the whole paper already has.
- `paperlib symptoms` gained `double-mark` and `macro-name`; before the reconversion they flag 1,687 and 132 of the library's papers.
- Still open, in the task file: shading in several colours and heat maps, 22 unresolved citations of one paper, the `±` arXiv's HTML does not have, and the reconversion of the whole library.
