# Task: conversion follow-ups

What is open in the converters and in the conversion of the author's library (`~/papers`); the examples are papers of that library. The first section changes what every newly added paper gets. The others repair papers already in the library and can wait until the paper or its area matters.

## 1. For every new paper

- **A check for pages arXiv's HTML lacks.** arXiv's rendering can stop partway or leave out appendix pages, and nothing says so when the paper is added. Put the page comparison in `paperlib symptoms` as `missing-pages`: a PDF page with 120 or more words, of which under a quarter of the three-word sequences occur in the markdown, is missing; reference pages are not counted.
- **A reading of an equation that does not parse.** In a PDF-only paper the model's reading can have unbalanced braces or delimiters (17 formulas in 11 papers, `paperlib symptoms --katex`). Check each reading with KaTeX when it is made, and read again one that fails.
- **Tables that are images.** Their numbers come from OCR and differ a little from run to run, while the note at the top of the paper says the numbers are the PDF's own (TabPFN's Extended Data tables, pp. 18–23). Say so in the note when a table had no text layer under it.
- **OpenCV is held at 4.12** ([`experiments/ocr-engines`](../../experiments/ocr-engines/README.md)). Lift the pin, and the numpy override that goes with it, when a release converts "Canaries in the Coal Mine" ten times without a crash.

## 2. Content arXiv's HTML lacks, taken from the PDF

- **Papers whose arXiv HTML is incomplete**: 27 are in the library's `catalog/conversion-issues.yaml`, those missing eight pages or a quarter of the paper (the GPT-4 Technical Report has no System Card, "Studying Large Language Model Generalization with Influence Functions" ends at §2.1); eighty papers miss three pages or more.
  - `paperlib reconvert` cannot convert a `source: html` paper from its PDF. Add `--from-pdf`, and compare it on five papers with adding only the missing pages to the HTML conversion.
  - Read the converted papers again; estimate the cost of that first.
- **Figures arXiv does not serve** (16 papers, `figure-link` in `paperlib symptoms`) still link to arXiv. Cut them from the PDFs by the same route.
- **A float LaTeXML dropped.** "Establishing Best Practices for Building Rigorous Agentic Benchmarks" has no table of its 17 benchmarks (a `longtblr`), and Qwen3-VL's "Table results_flagship" is a label because its table is not in the HTML. Take such a table from the PDF.

## 3. PDF papers converted the quick way

Run these after the equation check of section 1, so that they get it.

- **The thorough conversion of 30 catalogued papers** (28 of `search-and-ranking`, Command A and "Reinforcement Learning for LLM Post-Training. A Survey"), listed in the library's `docs/tasks/pdf-reconversion-papers.txt`. About 13 minutes a paper, and more than two jobs do not help; expect 6–8 hours.
  ```sh
  cd ~/papers
  tr '\n' '\0' < docs/tasks/pdf-reconversion-papers.txt | xargs -0 caffeinate -i \
    paperlib reconvert --pdf-text --inline-math --jobs 2 --state ~/.cache/papers/reconvert-pdf-2026-10-08.jsonl
  ```
  Then:
  1. A state line saying "equation model failed" or "fell back to the text layer" is worse than before: `git checkout` that paper and its images, delete its line from the state file, and run it again alone.
  2. `paperlib read --redo <paper.md> …` for every converted paper; the Q&A of each note is kept.
  3. `/fix-conversions search-and-ranking` and the two `llm` papers: replace each catalog entry with what the new conversion line reports, or remove it. Check the PDF before marking key content broken. Expect equations and algorithms to improve and a flattened table not to.
  4. `paperlib check`, then delete `pdf-reconversion-papers.txt`.
- **Inline mathematics for the other 277 PDF papers.** They have structure, tables, figures and display equations, and text with lost symbols; newly added papers also get every paragraph's inline mathematics as LaTeX ([`experiments/inline-math-reread`](../../experiments/inline-math-reread/README.md)). About 11,700 paragraphs at eight seconds each, a day or more; the run resumes where it stopped, so it can go over several nights or area by area before a literature review:
  ```sh
  caffeinate -i paperlib reconvert --all --pdf-text --inline-math --state ~/.cache/papers/reconvert-pdf-inline.jsonl
  ```
- **International AI Safety Report 2026.** The equation model failed on it, so text blocks whose symbols the text layer lost were left as they are. Reconvert it alone: `paperlib reconvert --pdf-text <paper.md>`.
- **Old PDFs with a broken text layer** ("Long Short-Term Memory", "The power of two random choices") lose ligatures and, for LSTM, headings and equations. Replace the PDF with a cleaner copy.

## 4. Small

- **A reference to an equation, a theorem or an appendix that LaTeXML lost** shows its label's name ("eq.(exactSol)", "Appendix minibatch"); only sections and floats get their number from the LaTeX source. Nine papers have them, "Real numbers, data science and chaos" in thirteen places. An equation's number could be taken from its place among the numbered equations of the source.
- **`Memory in the Age of AI Agents`** is edited by hand, so it keeps "§ what-memory" for Section 3. A reconversion with `--force` resolves such references from the LaTeX source; its cropped Figure 1 has to be put back after.
- **A `tabular` or an `\includegraphics` inside a formula** stays as its TeX, which an agent reads and KaTeX does not draw (23 formulas in 4 papers). A `NiceArray` arrives empty (5 formulas, one paper).
- **References that share an anchor.** See "Table and figure numbers" in [`conversion.md`](../conversion.md).
