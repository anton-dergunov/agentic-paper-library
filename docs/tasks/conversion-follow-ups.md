# Task: conversion follow-ups

The one list of what is open in the converters and in the conversion of the author's library (`~/papers`). The examples are papers of that library. A problem that does not change what an agent reads from a paper, and is hard to fix, is not here: the last section says which were dropped.

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
- **An `\includegraphics` or a `tabular` inside a formula** stays as its TeX, which an agent reads and KaTeX does not draw (23 formulas in 4 papers). A `NiceArray` arrives empty (5 formulas, one paper).
- **A reference to an equation, a theorem or an appendix that LaTeXML lost** shows its label's name ("eq.(exactSol)", "Appendix minibatch"); only sections and floats get their number from the LaTeX source. Nine papers showed an unrelated float's number there until 2026-10-09, "Real numbers, data science and chaos" in thirteen places. An equation's number could be taken from its place among the numbered equations of the source.
- **A colour mix that ends in a colour's name** (`red!30!blue`) before a cell's text cannot be told from the text; no paper of the library has one.
- **Image file names repeat the paper's title**, so image links are 1.6% of the text of the arXiv-HTML papers. Shorter names would change the layout the VS Code extension and `move-paper.sh` rely on.

## Dropped

Looked at on 2026-10-09 and left, because an agent reads the paper as well without the fix and the fix is hard or serves one paper:

- A source file LaTeXML did not include (`\input{sections/1_intro}` printed as its path): one paper, repaired by hand; `paperlib symptoms` still flags the case (`input-path`). The same paper is the only one where a named destination puts a heading on the wrong page.
- `\hspace` indentation at the start of a table cell, which sets an algorithm's nesting in one paper, repaired by hand.
- Undefined author macros that leave what they held as loose text in the author block.
- Shading in several colours, and heat maps: marking them was not measured, and one colour marked where the caption refers to it changed few answers ([`experiments/table-emphasis`](../../experiments/table-emphasis/README.md)).
- The `±` arXiv's HTML does not have between a value and the deviation printed small after it ("0.34 0.01"), and citations LaTeXML could not resolve whose words are not found once in the source (22 in "Transformer models: an introduction and catalog").
- Mathematics in an HTML table as VS Code's preview shows it: the reader's view, not the agent's.
