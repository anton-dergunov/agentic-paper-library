# Task: conversion follow-ups

The one list of what is open in the converters and in the conversion of the author's library (`~/papers`). The examples are papers of that library. A problem that does not change what an agent reads from a paper, and is hard to fix, is not here: the last section says which were dropped.

## 0. Finish the fixes of 2026-10-09 (start here)

The converter was changed on 2026-10-09 ([`experiments/reference-titles-and-table-math`](../../experiments/reference-titles-and-table-math/README.md)): link titles dropped, mathematics in HTML tables written as TeX, pictures in formulas replaced by what they show, TeX set as text removed. `paperlib test` passes. The library is being reconverted with it:

```sh
cd ~/papers
caffeinate -i sh -c 'paperlib reconvert --all --jobs 3 --state ~/.cache/papers/reconvert-2026-10-09.jsonl; paperlib reconvert --all --jobs 3 --state ~/.cache/papers/reconvert-2026-10-09.jsonl'
```

It began at 12:21 and resumes from the state file if it is run again. It is done when the state file has a line for each of the 2,204 papers and no `reconvert.py` process is left. **Do not edit `scripts/` while it runs:** it converts with the working tree.

State of the two repositories when it began:
- Engine: the converter changes, ten new fixtures, both experiment write-ups, `docs/conversion.md` and this file, uncommitted or committed as "Drop link titles…" (see `git log`).
- Library: clean at `1d812178` apart from the run's output, two corrected table numbers (the Spider 2.0 note and `reviews/llm/evaluation.md`) and two deleted task files.

When the run has ended, in `~/papers`:

1. **Outcome.** Count the statuses in the state file; expect about 1,889 ok, 16 partial (figures arXiv does not serve), 299 skipped, none failed. Look at anything else.
2. **Validate.** `paperlib symptoms --counts` (before the run, with today's checks: 417 papers; `macro-name` 56, `tex-box` 9, `empty-ref` 9, `double-mark` 3, `empty-header` 335). `paperlib symptoms --compare HEAD`: no paper should shrink by 5% except those that lost picture commands (xLSTM, "Scaling Laws for Generative Mixed-Modal Language Models", "Attention Heads of Large Language Models", Self-RAG, "The Platonic Representation Hypothesis") and long tables of rendered formulas; check each one listed. `paperlib symptoms --katex`: 80 formulas in 28 papers before; fewer now.
3. **Measure.** `python3 experiments/reference-titles-and-table-math/compare.py ~/papers > experiments/reference-titles-and-table-math/compare.tsv` (in the engine); read the lost words it prints. They should be picture commands ("pgfpicture", "hbox", "stroke"), macro names and "par".
4. **Look at ten papers** of the diff outside `llm/evaluation`: title, authors, citations, one HTML table with formulas, one equation. Among them "Attention is not Explanation" (Table 2 against the PDF), xLSTM (equations 1–3), DeepWalk (still "shown in Figure ."? then see why the source lookup fails).
5. **The seven papers edited by hand** are skipped by the run and keep their link titles. Remove them with `LINK_TITLE` of `scripts/caption-numbers.py` alone, not by running the script, which would renumber captions.
6. **"Continual Learning via Sparse Memory Finetuning", Table 1** (a heat map, key content broken in the catalog): `python3 experiments/reference-titles-and-table-math/heatmap.py ~/.cache/papers/arxiv/html/<id>v<n>/index.html.gz <paper.md> --write` marks the tokens shaded at a quarter or more of the darkest shade, from the HTML's colours. Then add `<!-- hand-edited: Table 1's shaded tokens marked from arXiv's HTML -->` and a sentence under the caption saying what `<mark>` means, and remove the catalog entry.
7. **Catalog.** In `catalog/conversion-issues.yaml` remove the entries the run fixed: check at least "Attention is not Explanation", Self-RAG, xLSTM, DAPO, and any entry about "par", macro names or garbled formulas in tables. `paperlib read --redo` "Attention is not Explanation" if it has a note: its Table 2 had no numbers.
8. **Indexes.** `paperlib build-index`, `paperlib check`.
9. **Write up.** Fill "Still to add" in the experiment's README and its row in `experiments/README.md`, and the count of formulas KaTeX cannot draw in `docs/conversion.md` ("Equations") and in the sections below. Delete this section.
10. **Two commit messages**, one per repository.

## 1. Content arXiv's HTML lacks, taken from the PDF

The largest gain for an agent: these papers are missing pages of text.

- **Papers whose arXiv HTML is incomplete** (27 in that library, listed in its `catalog/conversion-issues.yaml`, several with key content broken). arXiv's rendering stops partway or leaves out appendix pages, so the markdown does too: the GPT-4 Technical Report has no System Card, "Studying Large Language Model Generalization with Influence Functions" ends at §2.1. They were found by comparing each PDF page's text with the markdown: a page with 120 or more words of which under a quarter of the three-word sequences occur in the markdown is missing; reference pages are not counted. Eighty papers have three or more such pages; the catalog lists those missing eight pages or a quarter of the paper.
  - `paperlib reconvert` cannot convert a `source: html` paper from its PDF. Add `--from-pdf`, and compare it on five papers with adding only the missing pages to the HTML conversion.
  - Put the page comparison in `paperlib symptoms` (`missing-pages`), so that newly added papers are checked.
  - Read the converted papers again; estimate the cost of that first.
- **Figures arXiv does not serve** (16 papers, `figure-link` in `conversion-symptoms.py`). They still link to arXiv. The figures are in the PDFs and can be cut from there by the same route.
- **A float LaTeXML dropped.** "Establishing Best Practices for Building Rigorous Agentic Benchmarks" has no table of its 17 benchmarks (a `longtblr`), and Qwen3-VL's "Table results_flagship" is a label because its table is not in the HTML. Take such a table from the PDF.

## 2. The PDF converter

Before the overnight runs below, so that they get these fixes.

- **A reading of an equation that does not parse.** The model's reading has unbalanced braces or delimiters in 17 formulas of 11 PDF-only papers (`paperlib symptoms --katex`). Check each reading with KaTeX when it is made, and read again one that fails.
- **Tables that are images.** Their numbers come from OCR and differ a little from run to run, while the note at the top of the paper says the numbers are the PDF's own (TabPFN's Extended Data tables, pp. 18–23). Say so in the note when a table had no text layer under it.
- **International AI Safety Report 2026.** The equation model failed on it, so text blocks whose symbols the text layer lost were left as they are. Reconvert it alone: `paperlib reconvert --pdf-text <paper.md>`.
- **Old PDFs with a broken text layer** ("Long Short-Term Memory", "The power of two random choices") lose ligatures and, for LSTM, headings and equations. Replace the PDF with a cleaner copy.
- **OpenCV is held at 4.12** ([`experiments/ocr-engines`](../../experiments/ocr-engines/README.md)). Lift the pin, and the numpy override that goes with it, when a release converts "Canaries in the Coal Mine" ten times without a crash.

## 3. Overnight runs

- **The thorough conversion of 30 catalogued PDF papers** (28 of `search-and-ranking`, Command A and "Reinforcement Learning for LLM Post-Training. A Survey"), listed in the library's `docs/tasks/pdf-reconversion-papers.txt`. Their catalog entries and notes describe the quick conversion. Measured on 2026-10-08: about 13 minutes a paper, and more than two jobs do not help, since the equation model answers one request at a time; expect 6–8 hours.
  ```sh
  cd ~/papers
  tr '\n' '\0' < docs/tasks/pdf-reconversion-papers.txt | xargs -0 caffeinate -i \
    paperlib reconvert --pdf-text --inline-math --jobs 2 --state ~/.cache/papers/reconvert-pdf-2026-10-08.jsonl
  ```
  Then:
  1. A state line saying "equation model failed" or "fell back to the text layer" is worse than before: `git checkout` that paper and its images, delete its line from the state file, and run it again alone.
  2. `paperlib read --redo <paper.md> …` for every converted paper; the Q&A of each note is kept.
  3. `/fix-conversions search-and-ranking` and the two `llm` papers: replace each catalog entry with what the new conversion line reports, or remove it. Check the PDF before marking key content broken. Suspects: CatBoost (Table 4), "The Use of MMR" (Tables 1–4), "Reciprocal rank fusion" (Table 1), "Search Snippet Evaluation at Yandex" (Table 1, §3.2), "Predicting Search Satisfaction Metrics" (Table 1), "The Probabilistic Relevance Framework" (derivation 2.1–2.15), WAND and the two click-model papers (main equations), the survey (appendix tables 2–15). GPT-1, GPT-2 and "Learning Optimal Personalised Reservation Prices" were converted this way on 2026-10-08 and kept an empty equation, ticks read as "3" and "7", and a flattened table: expect equations and algorithms to improve and a flattened table not to.
  4. `paperlib check`, then delete `pdf-reconversion-papers.txt`.
- **Inline mathematics for the other PDF papers.** They have the quick conversion: structure, tables, figures, display equations, and text with lost symbols. The thorough one, which also writes every paragraph's inline mathematics as LaTeX, is what newly added papers get ([`experiments/inline-math-reread`](../../experiments/inline-math-reread/README.md)). For the existing 277 it is about 11,700 paragraphs at eight seconds each, a day or more:
  ```sh
  caffeinate -i paperlib reconvert --all --pdf-text --inline-math --state ~/.cache/papers/reconvert-pdf-inline.jsonl
  ```
  It resumes where it stopped, so it can run over several nights, or area by area (`paperlib reconvert --pdf-text --inline-math library/llm/evaluation ...`) before each literature review.

## Small, for whenever the paper matters

- **`Memory in the Age of AI Agents`** is edited by hand, so it keeps "§ what-memory" for Section 3. A reconversion with `--force` now resolves such references from the LaTeX source; its cropped Figure 1 has to be put back after.
- **References that share an anchor.** See "Table and figure numbers" in [`conversion.md`](../conversion.md).
- **An `\includegraphics` or a `tabular` inside a formula** stays as its TeX, which an agent reads and KaTeX does not draw (about 30 formulas in 6 papers). A `NiceArray` arrives empty (5 formulas, one paper).
- **Image file names repeat the paper's title**, so image links are 1.6% of the text of the arXiv-HTML papers. Shorter names would change the layout the VS Code extension and `move-paper.sh` rely on.

## Dropped

Looked at on 2026-10-09 and left, because an agent reads the paper as well without the fix and the fix is hard or serves one paper:

- A source file LaTeXML did not include (`\input{sections/1_intro}` printed as its path): one paper, repaired by hand; `paperlib symptoms` still flags the case (`input-path`). The same paper is the only one where a named destination puts a heading on the wrong page.
- `\hspace` indentation at the start of a table cell, which sets an algorithm's nesting in one paper, repaired by hand.
- Undefined author macros that leave what they held as loose text in the author block.
- Shading in several colours, and heat maps: marking them was not measured, and one colour marked where the caption refers to it changed few answers ([`experiments/table-emphasis`](../../experiments/table-emphasis/README.md)).
- The `±` arXiv's HTML does not have between a value and the deviation printed small after it ("0.34 0.01"), and citations LaTeXML could not resolve whose words are not found once in the source (22 in "Transformer models: an introduction and catalog").
- Mathematics in an HTML table as VS Code's preview shows it: the reader's view, not the agent's.
