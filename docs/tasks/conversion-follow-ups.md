# Task: conversion follow-ups

On 2026-10-02 the whole library was reconverted with the rebuilt converters (see "Conversion"
in `docs/library.md`) and the result was validated and merged. 1,904 arXiv-HTML papers (the
three hand-edited ones were skipped) and all 277 PDF-only papers converted;
`scripts/test_conversion.py` passes; papers showing a
conversion symptom fell from 1,370 to 362, almost all of them tables with no rule under the
header. What is still open:

## Papers to convert again

- **Papers whose arXiv HTML is incomplete** (27, listed in `catalog/conversion-issues.yaml`).
  arXiv's rendering stops partway or leaves out appendix pages, so the markdown does too: the
  GPT-4 Technical Report has no System Card, "Studying Large Language Model Generalization
  with Influence Functions" ends at §2.1. They were found by comparing each PDF page's text
  with the markdown: a page with 120 or more words of which under a quarter of the three-word
  sequences occur in the markdown is missing; reference pages are not counted. Eighty papers
  have three or more such pages; the catalog lists those missing eight pages or a quarter of
  the paper. The fix is to convert these from the PDF, which `reconvert.py` cannot do for a
  `source: html` paper yet: it needs an option for that, or a way to add only the missing
  pages. The page comparison belongs in `conversion-symptoms.py` so that newly added papers
  are checked too.
- **Figures arXiv does not serve** (16 papers, `figure-link` in `conversion-symptoms.py`).
  They still link to arXiv. The figures are in the PDFs and could be cut from there.
- **International AI Safety Report 2026.** The equation model failed on it, so text blocks
  whose symbols the text layer lost were left as they are. It has no equations. Reconvert it
  alone: `scripts/reconvert.py --pdf-text <paper.md>`.
- **Inline mathematics for the PDF papers.** The reconversion was the quick one: structure,
  tables, figures, display equations, and text with lost symbols. The thorough conversion,
  which also writes every paragraph's inline mathematics as LaTeX, is what newly added papers
  get (see "PDF-only papers" in `docs/library.md` for the measurements). For the existing 277
  it is about 11,700 paragraphs at eight seconds each, a day or more:
  ```sh
  caffeinate -i python3 scripts/reconvert.py --all --pdf-text --inline-math --state ~/.cache/papers/reconvert-pdf-inline.jsonl
  ```
  It resumes where it stopped, so it can run over several nights, or area by area
  (`scripts/reconvert.py --pdf-text --inline-math library/llm/evaluation ...`) before each
  literature review.
- `Memory in the Age of AI Agents`: its `\Cref` targets could get section numbers the way
  `LABEL:` references now do; the paper is hand-edited, so it needs `--force` and its cropped
  Figure 1 put back.

## The PDF converter

- **OCR crashes now and then.** docling runs OCR (RapidOCR) on bitmap figures, and OpenCV
  5.0.0's resize segfaults there on some PDFs, on some attempts ("Canaries in the Coal Mine"
  crashed three times in four). `reconvert.py` then reports `RuntimeError: pdf-to-markdown:
  ['  warnings.warn(']`; running it again gets through. 5.0.0 is the newest OpenCV, so there is
  no upgrade to take. Options to compare on real papers: docling's `ocrmac` engine (Apple's
  OCR, no OpenCV), an earlier OpenCV, or no OCR for PDFs that have a text layer.
- **Equations are right about two times in three.** In the spot check of nine display
  equations against the page image, six were right. The three errors: an exponent written as a
  factor (LambdaLoss, NDCG-Loss2, p. 6), left-hand sides dropped and a subscript swapped
  (DSSM, eq. 16, p. 7), and a figure legend taken for an equation (Adam, p. 6).
- **Tables that are images.** Their numbers come from OCR, while the note at the top of the
  paper says the numbers are the PDF's own (TabPFN's Extended Data tables, pp. 18–23). The
  converter should say so in the note when a table had no text layer under it.
- **Old PDFs with a broken text layer** ("Long Short-Term Memory", "The power of two random
  choices") lose ligatures and, for LSTM, headings and equations. Replacing the PDF with a
  cleaner copy is the fix.

## Environment

- A repo `.venv` with the scripts' dependencies declared (docling, pymupdf, tqdm, pyyaml,
  lxml, pillow); marker stays in its own environment. Today the scripts run on the system
  Python, and marker lives in `~/.cache/papers/venvs/marker`.
