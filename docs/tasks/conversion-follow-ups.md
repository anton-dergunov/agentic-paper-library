# Task: conversion follow-ups

On 2026-10-02 the author's library of 2,200 papers was reconverted with the rebuilt converters
(see [`../conversion.md`](../conversion.md) and
[`experiments/library-reconversion`](../../experiments/library-reconversion/README.md)), and the
result was validated and merged. 1,904 arXiv-HTML papers (the three hand-edited ones were
skipped) and all 277 PDF-only papers converted; `tests/test_conversion.py` passes; papers
showing a conversion symptom fell from 1,370 to 362, almost all of them tables with no rule under
the header. What is still open, with the papers of that library as examples:

## Papers to convert again

- **Papers whose arXiv HTML is incomplete** (27 in that library, listed in its `catalog/conversion-issues.yaml`).
  arXiv's rendering stops partway or leaves out appendix pages, so the markdown does too: the
  GPT-4 Technical Report has no System Card, "Studying Large Language Model Generalization
  with Influence Functions" ends at §2.1. They were found by comparing each PDF page's text
  with the markdown: a page with 120 or more words of which under a quarter of the three-word
  sequences occur in the markdown is missing; reference pages are not counted. Eighty papers
  have three or more such pages; the catalog lists those missing eight pages or a quarter of
  the paper. The fix is to convert these from the PDF, which `paperlib reconvert` cannot do for a
  `source: html` paper yet: it needs an option for that, or a way to add only the missing
  pages. The page comparison belongs in `paperlib symptoms` so that newly added papers
  are checked too.
- **Figures arXiv does not serve** (16 papers, `figure-link` in `conversion-symptoms.py`).
  They still link to arXiv. The figures are in the PDFs and could be cut from there.
- **International AI Safety Report 2026.** The equation model failed on it, so text blocks
  whose symbols the text layer lost were left as they are. It has no equations. Reconvert it
  alone: `paperlib reconvert --pdf-text <paper.md>`.
- **Inline mathematics for the PDF papers.** The reconversion was the quick one: structure,
  tables, figures, display equations, and text with lost symbols. The thorough conversion,
  which also writes every paragraph's inline mathematics as LaTeX, is what newly added papers
  get (see [`experiments/inline-math-reread`](../../experiments/inline-math-reread/README.md)). For the existing 277
  it is about 11,700 paragraphs at eight seconds each, a day or more:
  ```sh
  caffeinate -i paperlib reconvert --all --pdf-text --inline-math --state ~/.cache/papers/reconvert-pdf-inline.jsonl
  ```
  It resumes where it stopped, so it can run over several nights, or area by area
  (`paperlib reconvert --pdf-text --inline-math library/llm/evaluation ...`) before each
  literature review.
- `Memory in the Age of AI Agents`: its `\Cref` targets could get section numbers the way
  `LABEL:` references now do; the paper is hand-edited, so it needs `--force` and its cropped
  Figure 1 put back.

## arXiv HTML

Left open by the fixes of 2026-10-04 ([`experiments/review-flagged-fixes`](../../experiments/review-flagged-fixes/README.md)):

- **A source file LaTeXML did not include.** "Measuring what Matters" (2511.04703) renders `\input{sections/1_intro}` as the path, so the introduction and Figure 1 are missing and every later section number is two low. `paperlib symptoms` flags it (`input-path`); that paper was repaired by hand from its LaTeX source. The converter could do the same: convert the file with pandoc, splice it in, and renumber the sections that follow.
- **A float LaTeXML dropped.** "Establishing Best Practices for Building Rigorous Agentic Benchmarks" has no table of its 17 benchmarks (a `longtblr`); references to it now show its label ("Table all-benchmarks"). The table could be taken from the PDF.
- **Named destinations are trusted without a check.** When the HTML's section numbers differ from the PDF's (the case above), `page-map.py` places "1 Methods" on the page of the PDF's section 1. The check that now guards bookmarks (the heading must be printed on the page) could guard destinations too; it needs measuring first, since a heading set in mathematics or small capitals would fail it.
- **References that share an anchor.** See "Table and figure numbers" in `conversion.md`.
- **Undefined author macros** leave their names in the author block ("\\multiauthors\\affiliations" in "The Leaderboard Illusion").

## The PDF converter

- **OpenCV is held at 4.12.** Later releases segfault in their Arm resize inside RapidOCR, about one conversion in three of "Canaries in the Coal Mine" ([`experiments/ocr-engines`](../../experiments/ocr-engines/README.md)). Lift the pin, and the numpy override that goes with it, when a release converts that paper ten times without a crash.
- **Equations are right about two times in three.** In the spot check of nine display
  equations against the page image, six were right. The three errors: an exponent written as a
  factor (LambdaLoss, NDCG-Loss2, p. 6), left-hand sides dropped and a subscript swapped
  (DSSM, eq. 16, p. 7), and a figure legend taken for an equation (Adam, p. 6).
- **Tables that are images.** Their numbers come from OCR, and differ a little from run to run, while the note at the top of the
  paper says the numbers are the PDF's own (TabPFN's Extended Data tables, pp. 18–23). The
  converter should say so in the note when a table had no text layer under it.
- **Old PDFs with a broken text layer** ("Long Short-Term Memory", "The power of two random
  choices") lose ligatures and, for LSTM, headings and equations. Replacing the PDF with a
  cleaner copy is the fix.

## Equations KaTeX cannot draw

56 of 444,263 maths spans still fail after the fixes of 2026-10-04 ([`experiments/katex-equation-check`](../../experiments/katex-equation-check/README.md)); `paperlib symptoms --katex` lists them.

- **Pictures and tables inside an equation** (26 spans in 9 arXiv-HTML papers): a TikZ picture, a `NiceArray`, a `tabular` or an image set in maths comes out as its TeX internals. They could be replaced by a placeholder, or by the picture LaTeXML renders for them.
- **PDF-only papers** (17 spans in 11 papers): the model's reading of an equation has unbalanced braces or delimiters. The check could run after each reading, and a reading that does not parse be read again.
- **Mathematics inside an HTML table** is written as `<span class="math inline">$…$</span>`. VS Code's preview does not read markdown inside an HTML block, so it may show these as source; not checked.
