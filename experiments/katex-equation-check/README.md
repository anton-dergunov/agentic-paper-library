# Experiment · do the converted equations render in KaTeX?

**Question.** The library's markdown is read in VS Code's preview, which draws maths with KaTeX. KaTeX covers most of LaTeX maths but not all of it, and the TeX arXiv keeps for each equation is the author's source, with the paper's own macros and LaTeX layout commands in it. How many of the converted equations does KaTeX refuse to draw, why, and what in the converter fixes them?

**Status.** Measured 29–30 Sep 2026 on the 238-paper library: **the first full check found 830 of 35,486 maths spans failing (2.3%); after three rounds of fixes to the converter, 6 of 35,299 (0.02%), all one construct in one paper.** Before any of this, every equation had been written in a form VS Code's preview does not draw as intended. Re-run 3 Oct 2026 on 2,202 papers: 600 of 444,047 spans fail (0.14%), 583 of them in papers converted from arXiv's HTML; those are not yet fixed.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#equations).

## Method

- **Corpus.** The library as first set up on 29 Sep 2026: 238 papers, 231 converted from arXiv's HTML and 7 from PDF text. Fixes were tried first on small sets: 3 and then 5 freshly converted maths-heavy papers, the 10 papers with the most failures, and 8 papers for the last fix. The re-run on 3 Oct covers the library as it then stood.
- **Apparatus.** [`check.js`](check.js) walks a folder of paper markdown (skipping `README.md`), removes fenced code blocks, takes every `$$…$$` as display maths and every `$…$` within a line as inline maths, and renders each with `katex.renderToString` (`throwOnError: true`, `strict: false`). It groups the errors by message, with the position stripped, and prints each kind's count and its first example. `LIST=1` also prints the files with a failure; that was added during the run to pick the papers to reconvert. [`katex-commands.js`](katex-commands.js) lists the control sequences KaTeX supports (976 of 1,016 candidate names found in KaTeX's source); the converter reads that list as `scripts/katex-commands.txt`. KaTeX is pinned to 0.16.47 by [`package-lock.json`](package-lock.json).

  ```bash
  cd experiments/katex-equation-check && npm ci
  node check.js <folder of paper markdown>   # e.g. the library
  node katex-commands.js katex-commands.txt   # KaTeX's \show also prints a token dump; ignore it
  ```

  `check.js` is as run. `katex-commands.js` was an inline `node -e` snippet that wrote straight into the library's `scripts/`; only its output path became an argument. Re-run on 3 Oct 2026, it produced a list identical to the one committed.
- **The converter measured** is `scripts/arxiv-html.lua` (a pandoc filter) and `scripts/html-to-markdown.py`, at their state in commit `dd908cf` ("Fix math, figures, tables and filenames in paper markdown"), where the fixes below landed.
- **Rendering check.** Beyond the parse check, two papers from the report that started this were rendered with `pandoc --katex` and screenshotted in headless Chrome: the reward-model objective of *Active Preference Learning for Large Language Models* and Section 3.2 of *Is GPT-3 a Good Data Annotator?* with its figure and table. The screenshots show paper pages and are not kept here.
- **Results.** [`results/2026-09-30-runs.txt`](results/2026-09-30-runs.txt) holds the output of every run, copied from the session. [`results/2026-10-03-rerun-saved.txt`](results/2026-10-03-rerun-saved.txt) re-runs `check.js` on the small-set conversions saved that day and reproduces each count exactly. [`results/2026-10-03-library.txt`](results/2026-10-03-library.txt) is the re-run on the current library. Each gives the first 160 characters of one example per failure kind; no converted paper text is committed.

## Results

### Before the check: the delimiters

The library as first set up held 39,764 inline spans written as `` $`…`$ `` and 1,101 display equations as ```` ``` math ```` blocks. That is pandoc's GitHub-markdown output (its `tex_math_gfm` extension), which GitHub renders; VS Code's preview draws only `$…$` and `$$…$$`: inline spans came out with backticks drawn as quote marks (`‘s(P)∈R^M‘` in the report that started this), and display blocks as code. Converting with `-t gfm-tex_math_gfm+tex_math_dollars` writes standard `$…$` and `$$…$$`, which every run below checks.

### The runs

| Run | Papers | Maths spans | Failed |
|---|---|---|---|
| Pilot, after the switch to `$` delimiters | 3 | 336 | 14 |
| Pilot, after `\mathds` → `\mathbb` and merging adjacent inline maths | 5 | 368 | 2 |
| **Whole library, after the first full reconversion** | 238 | 35,486 | **830** |
| Ten papers with the most failures, before → after the normalisation | 10 | 2,022 → 1,964 | 146 → 6 |
| Whole library, after the second full reconversion | 238 | 35,371 | 84 |
| Eight papers, after the mode-aware rewrite | 8 | 1,308 | 6 |
| **Whole library, final** (12 papers reconverted) | 238 | 35,299 | **6** |
| Re-run 3 Oct 2026, whole library | 2,202 | 444,047 | 600 |

The span count falls as fixes land because LaTeXML sometimes splits one expression into adjacent pieces, which are now merged into one span.

### The 830 failures, and what fixed each

| Failure | Spans | Cause | Fix in `arxiv-html.lua` |
|---|---|---|---|
| `Invalid color: '['` | 233 | xcolor's model syntax, `\color[rgb]{1,0,0}` | rewritten as `\color{#FF0000}` |
| `\textsc`, `\mbox` undefined | 216, 37 | text commands KaTeX lacks | → `\text` (small caps are lost) |
| `\mathbbm` (earlier `\mathds`) undefined | 70 | the indicator 1 from the bbm and dsfont packages | → `\mathbb` |
| `Expected EOF, got '}'`, unexpected end of input | about 70 | a `$` inside the TeX (`\text{bo$n$}`) closes the markdown span early | inside a text argument written as `\(…\)`; in maths, dropped |
| `Can't use function '$'` | 37 | a currency `\$` next to maths (`\$$15$`), or adjacent maths pieces read as `$$` | sign moved into the maths; adjacent pieces merged |
| the paper's own macros (`\montraita`, `\degen`, `\defeq`, `\bias`, `\rank`, `\bin`, `\maximize`, …) | about 75 | defined in the paper's preamble, which arXiv's HTML does not carry | shown as their name, upright: `\operatorname{rank}` in maths, `\textrm{rank}` in text |
| `\textless`, `\nicefrac`, `\lx@sectionsign`, `\addcontentsline`, `\begin{array}[]` | about 60 | LaTeX and LaTeXML commands with a close equivalent | `<`, `\tfrac`, `\S`, removed, `\begin{array}` |
| `\vskip`, `\penalty`, `\hfil`, `\indent` | 17 | layout commands that mean nothing in a rendered equation | removed |

A command is "lacking" when it is not on the list `katex-commands.js` generates; the list replaced a growing set of hand-written cases.

The second full run left 84 failures in two kinds. 72 were siunitx numbers in one paper, `0.769$\pm$0.162`, whose inner `$` broke the span; 12 were `\ref` and `\cite` inside `\text{}`, rewritten to `\operatorname`, which KaTeX does not allow in text. Both needed the rewrite to know whether it is in maths or in a text argument, so the last fix is a single scanner over the TeX that tracks the mode at each brace. Cross-references and citations now keep their label as text.

The 6 that remain are one construct in HippoRAG, `\mathrel{\mathchoice{\hbox{\(…\)}…}}`, which KaTeX cannot draw.

### Converting from MathML instead: not tested

LaTeXML's HTML carries each equation twice, as MathML and as the author's TeX. One run tried converting from the MathML by removing the TeX `alttext` attribute (section 4 of the run log). The TeX was still present as a MathML `<annotation encoding="application/x-tex">`, which pandoc read instead, so both outputs are byte-identical and the run says nothing about MathML. The converter stayed on the TeX, which keeps the author's notation; whether pandoc's MathML-to-TeX output would render better is open.

### The 3 Oct re-run

Since 30 Sep the library grew to 2,202 papers, and the converter gained siunitx, boxed-text and table recoveries. 600 spans fail: 583 in 100 of the 1,909 papers converted from arXiv's HTML, and 17 in 11 of the 277 PDF-only papers, whose equations are read from page images by a model. The largest kinds are maths commands inside a text argument, which the mode-blind list of supported commands lets through: `\text{\times}` (115, mostly siunitx output such as `5\text{\times}{10}^{-4}`), `\mathbin` inside `\raisebox` (84) and `\pm` inside `\raisebox{…}{\tiny …}` (56). Next are LaTeXML's citation internals, `\@@bibref` (68). These are open: the fix is to check a command's mode as well as its name.

## Limits

- `check.js` finds maths spans with its own regular expressions, not with the markdown parser VS Code uses, so a span's boundaries can differ from what the preview sees (inside tables and code spans in particular).
- It checks that KaTeX parses an equation, not that the result is right. A paper macro shown as its name renders without error but loses the macro's meaning; `\textsc` loses its small caps.
- Obsidian renders maths with MathJax, not KaTeX, and was not checked.
- Only two papers were checked by rendering them; the rest rests on the parse check.
