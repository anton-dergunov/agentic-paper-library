# Experiment · should a paper be converted from its arXiv LaTeX source?

**Question.** arXiv serves the LaTeX source of most papers (`arxiv.org/src/<id>`). The engine reads it only to repair what arXiv's HTML lost: taxonomy trees, empty references, unknown citations. Should it be the input instead, converted to markdown here or stored as TeX? And for how many papers of a library is it there when the HTML is not?

**Status.** Measured 13 Oct 2026 on the author's library of 2,208 papers. **The source adds little.** arXiv's HTML is itself made from the source, so the 1,915 papers converted from HTML already have it; of the 46 arXiv papers converted from the PDF, 24 serve a source and 17 of those are the paper's LaTeX (five wrap a PDF, two are PostScript). LaTeXML run here (Homebrew's 0.8.8) converted 7 of those 17 whole and timed out on 8; on 13 papers that do have HTML it converted 7, the same text as arXiv's, and recovered 29 pages arXiv's HTML lacks in one. pandoc converted 16 of 30 sources whole and a model reading its output answered 71% of 42 questions, the tables and the citations being gone. The stripped TeX answered 47.5 of 48 against 48 of 48 for the library's markdown, with 27% more tokens and no figures, page numbers or float numbers. **Nothing shipped: the source stays a repair input.** Open: a newer LaTeXML for the papers that timed out.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#why-arxiv-html).

## Method

- **Coverage.** [`coverage.py`](coverage.py) groups the library's papers by how they were converted and asks arXiv, by a header-only request to `arxiv.org/e-print/<id>`, what it holds for each arXiv paper converted from the PDF: `application/gzip` is a source, `application/pdf` a submission that was a PDF.
- **Corpus.** Two sets.
  - [`papers-no-html.tsv`](papers-no-html.tsv): the 24 papers with a source and no HTML rendering. The library's copy of each is the PDF conversion (docling, equations read from the page image by a model).
  - [`papers-control.tsv`](papers-control.tsv): 13 papers that have HTML, so a conversion from the source can be compared with arXiv's: nine at random and four at random from those the library's catalog lists as "arXiv's HTML is incomplete" ([`sample.py`](sample.py), seeded; papers over 150,000 characters left out).
- **Conversions compared** ([`convert.py`](convert.py)), each from the source at the version of the library's PDF:
  - **library**: what the library holds, the baseline.
  - **latexml**: `latexmlc` 0.8.8 with arXiv's preloads less its own `ar5iv` bindings, then the engine's `html-to-markdown.py` unchanged. **latexml2** is the same with LaTeXML's limit of 100 errors lifted ([`noerrorlimit.sty.ltxml`](noerrorlimit.sty.ltxml)), run for a paper the first run gave up on.
  - **pandoc**: `pandoc -f latex` 3.10.2 on the root file.
  - **tex**: the source as it is. `\input` files spliced in, comments removed, the preamble cut to its macro definitions, the `.bbl` in place of `\bibliography`.

  One conversion at a time at `nice 15`, each step stopped after five minutes. Files of a source that LaTeXML would run as code (`.ltxml`, `.pl`) are not unpacked.
- **Measures** ([`measure.py`](measure.py)), each against the paper's PDF: pages whose text the conversion lacks (the measure of `paperlib symptoms --pages`), display equations, formulas KaTeX cannot parse, and references left as a label or a key. Its count of the PDF's decimal numbers found in the conversion is in the tables and not used below: it is low wherever the PDF's decimals are section numbers.
- **Reading test** ([`qa.py`](qa.py)) on [`papers-qa.tsv`](papers-qa.tsv), the seven control papers pandoc converted and "Kernel and Rich Regimes in Overparametrized Models" (225 display equations; pandoc timed out). Opus 5.5 set six questions a paper, three reading the library's markdown and three reading the stripped TeX, so that neither form is favoured by who set them: one on a display equation, one on a number in a results table, one on a statement that points to a table, a section or a cited work. Sonnet 5.5 answered each paper's six in one request over each form, with no tools, as `paperlib read` reads a paper. Opus graded each answer against the expected one without seeing which form it came from.

```bash
export PAPER_LIBRARY=<library>
uv run python coverage.py > results/coverage.txt
uv run python coverage.py --list > papers-no-html.tsv
uv run python sample.py > papers-control.tsv
uv run python convert.py papers-no-html.tsv >> results/convert-no-html.jsonl    # and papers-control.tsv
uv run python measure.py papers-no-html.tsv > results/measure-no-html.tsv       # and papers-control.tsv
python3 summary.py no-html > results/summary-no-html.txt                        # and control
uv run python qa.py questions papers-qa.tsv > results/questions.jsonl
uv run python qa.py answer results/questions.jsonl > results/answers.jsonl
uv run python qa.py grade results/questions.jsonl results/answers.jsonl > results/grades.jsonl
uv run python qa.py table results/grades.jsonl results/answers.jsonl > results/qa.txt
```

The conversions are paper text and stay in `$PAPERS_CACHE/experiments/latex-source/`; the records, scores, questions and answers are in [`results/`](results/). A first run with six conversions at once shared the machine with another job that filled its memory; its timings were discarded and everything was converted again.

## Results

### Coverage

| Papers | | How the library converted them |
|---|---|---|
| 1,915 | 86.7% | from arXiv's HTML, which is made from the source |
| 231 | 10.5% | from the PDF; not on arXiv |
| 24 | 1.1% | from the PDF; arXiv serves a source |
| 22 | 1.0% | from the PDF; submitted to arXiv as a PDF |
| 16 | 0.7% | web articles |

Of the 24, **17 are the paper's LaTeX**. Five are a file of one line that includes a PDF typeset elsewhere (Adam, PPO, "Understanding deep learning requires rethinking generalization", "Network Embedding as Matrix Factorization", SemAxis), and two are PostScript from before arXiv took sources (SMOTE, LexRank). One root file is not named `.tex` (SQuAD's `main.flt`).

### What converts

| | 17 sources without HTML | 13 controls with HTML |
|---|---|---|
| LaTeXML: whole paper | 5 | 7 |
| LaTeXML: whole paper once the error limit is lifted | 2 | (1 of the 7) |
| LaTeXML: timed out at 5 minutes | 8 | 6 |
| LaTeXML: failed, or lost pages | 2 | 0 |
| pandoc: whole paper | 10 | 6 |
| pandoc: lost pages | 4 | 1 |
| pandoc: failed or timed out | 3 | 6 |

- **Where LaTeXML converts, the result is arXiv's.** On the six controls other than "Confident Learning" its markdown is within 4% of the library's in length, with the same display equations (225 of 225 in the most mathematical) and no reference left as a label. A run that ends takes a median 14–20 s and at most two minutes.
- **The timeouts have two causes.** Either the release interprets the `expl3` programming layer of the local TeX Live, which a paper loads through `siunitx`, `xparse` and the like, or it evaluates the arithmetic of plots drawn with `pgfplots`. arXiv runs a development build newer than 0.8.8; six of the fourteen papers that timed out here have HTML on arXiv.
- **The limit of 100 errors ends a conversion early** when an undefined macro is used throughout. With it lifted, two of the three such papers without HTML converted whole (181 display equations in "Anytime-Valid Linear Models", where the PDF conversion has 175 read from page images), and the third timed out.
- **One incomplete rendering was completed.** arXiv's HTML of "Confident Learning" lacks 29 of the PDF's 37 pages; the run with the limit lifted has all 37. The other three incomplete papers lack the same pages in every conversion from the source (9, 8 and 6 pages): what is missing is not in the root document.
- **What a local LaTeXML conversion still lacks.** Its figures link to nothing (the converter fetches them from arXiv), the repairs that read the source by arXiv id do not run, and the page and caption passes were not applied.

### What the other two forms hold

Medians over the papers each form exists for, both sets together ([`results/summary-no-html.txt`](results/summary-no-html.txt), [`results/summary-control.txt`](results/summary-control.txt)):

| | pandoc | stripped TeX |
|---|---|---|
| Length against the library's markdown | 1.01 and 0.80 | 1.19 and 1.11 |
| Formulas KaTeX cannot parse, a paper | 25 and 0 | not checked |
| References left as a label or a key, a paper | 58 and 35 | 151 and 133 |

- **pandoc keeps an author's macros unexpanded** where they are defined with `\def` or in a loop: 624 formulas of one paper do not parse. It writes a `\ref` as its label and drops what it cannot set, tables among them.
- **The TeX is two to six times the markdown where a paper draws its plots in TeX** (GraphSAINT 441,000 characters against 72,000; "Elucidating the Design Space" 512,000 against 178,000).
- **Results read from data files at compile time are in neither.** The tables of "In Defense of the Triplet Loss" come from CSV files through `csvsimple`.

### Reading test

| Questions | library | pandoc | stripped TeX |
|---|---|---|---|
| All | 48 of 48 | 27 right, 6 partly of 42 (0.71) | 47 right, 1 partly of 48 (0.99) |
| On an equation | 16 of 16 | 14 of 14 | 16 of 16 |
| On a table | 16 of 16 | 6 of 14 | 16 of 16 |
| On a reference or citation | 16 of 16 | 7 right, 6 partly of 14 | 15 right, 1 partly of 16 |
| Input tokens, 8 papers | 312,000 | 175,000 (7 papers) | 397,000 |

- **The TeX reads as well as the markdown, for 27% more tokens.** Its one imperfect answer named a second cited work beside the expected one. The scores are the same whichever form the questions were set from.
- **pandoc's output fails where it dropped content.** All eight wrong table answers and the seven imperfect reference answers say the table or the citation is not in the text.
- **The questions are easy.** Both the markdown and the TeX are at the ceiling, so the test shows that TeX is not worse on single facts, not that the two are equal on harder reading. It does not test what only the markdown has: figures, the page each heading starts on, and the PDF's table and figure numbers.

The reading test cost $5.93 for the questions and $3.62 for the answers; the grading's cost was not recorded (eight short requests). That is near a third of a five-hour window, where a fifth was planned: setting the questions with Opus over two forms of each paper was the larger part.

## Decision

- **arXiv's HTML stays the input.** The stripped TeX answers the same questions for a quarter more tokens and cannot carry figures, page numbers or float numbers; pandoc loses tables and citations.
- **The source stays a repair input**, as in `html-to-markdown.py` now.
- **A local LaTeXML step is not added yet.** With the release Homebrew ships it would convert 7 of the library's 2,208 papers better than the PDF route and complete one incomplete rendering, and it needs figure handling and the page passes first.

## Open

- **A development build of LaTeXML** (`brew install --HEAD latexml`, or arXiv's `ar5iv` image) on the fourteen papers that timed out. If it converts most of them, a local step would cover about 15 papers without HTML and part of the 73 with an incomplete rendering.
- **The source as a check on a PDF conversion.** For the 17 papers the display equations of the source could replace the ones a model read from the page image, three in ten of which differ somewhere ([`pdf-converter-bakeoff`](../pdf-converter-bakeoff/README.md)).
