# Conversion

The markdown is the agent's copy of a paper, so its quality decides how well the agent reads. This document records how each kind of paper is converted, and why. The measurements behind each decision are in [`experiments/`](../experiments/README.md); this page keeps only the decision.

| Source | `source:` | Converter | Command |
|---|---|---|---|
| arXiv, with an HTML rendering | `html` | arXiv's LaTeXML HTML through pandoc and a Lua filter | `paperlib add-arxiv` |
| arXiv without a rendering, or any other PDF | `pdf-text` | docling's layout analysis, plus marker's equation model | `paperlib add-arxiv` (falls back), `paperlib add-pdf` |
| A paper published as a web page | `web` | the rendered page through pandoc; Chrome prints the PDF | `paperlib add-web` |

Each converter writes figures to `images/` (raster images as WebP, plots as SVG) and adds the PDF page to every heading.

## Why arXiv HTML

**arXiv's HTML rendering is the source whenever it exists.** It is built from the paper's LaTeX, so equations arrive as the author's TeX and tables keep their structure. PDF text extraction either flattens equations into glyphs (raw PyMuPDF) or drops them without a trace (pymupdf4llm left DPO's objective as an empty gap), and both lose two-level table headers. For papers of prose and simple tables, every conversion is fine. → [`experiments/pdf-vs-arxiv-html`](../experiments/pdf-vs-arxiv-html/README.md)

## arXiv HTML

`scripts/html-to-markdown.py` runs pandoc with `scripts/arxiv-html.lua`. Maths becomes `$...$`, tables with merged cells become HTML, and figures are saved locally. Plots arXiv embeds as SVG objects are kept as vectors, except that one over 300 KB is rasterised to WebP: on 10,000 figures that rule was projected to cut 2.24 GB on disk to 0.91 GB, and 435 MB in git to 326 MB. → [`experiments/svg-figures`](../experiments/svg-figures/README.md)

LaTeXML sometimes loses content that the converter recovers. Its docstring has the details, and `tests/test_conversion.py` checks each case on a small fixture:

- **Boxed text** (definitions, findings, takeaways, prompt templates). LaTeXML draws it as an SVG frame with the text inside; it becomes a quote the agent can read. Only drawings with real shapes stay images, and small text badges in tables become their text.
- **Tables in `\resizebox` or `\scalebox`.** LaTeXML emits them as inline spans; they are rebuilt as tables. A header row LaTeXML did not mark is recognised by the rule under it.
- **Taxonomy trees drawn with `forest`.** LaTeXML can't render them, so they are taken from the paper's LaTeX source and written as nested lists. A node's reference to a section (`\S\ref{sec:x}`) shows the section's number, found by the title of the section the label follows; the spaces that centre a node's lines are dropped.
- **Equation tables** keep their text: `\intertext` prose, a left-hand side set as text, several equations on one row.
- **siunitx numbers** arrive unrounded with digit groups. The groups are joined, and raw input is rounded to four decimals.
- **Inline icons**, such as a check mark in a table cell, keep their file's name as alt text.
- **Citations left as BibTeX keys**, when a paper shipped its `.bib` uncompiled, are rebuilt with the reference list by pandoc's citeproc.
- **A paper converted from its PDF** gets the HTML conversion once arXiv renders it: `paperlib reconvert` tries the HTML first.
- **Text set only for its width** is dropped. A `\phantom{5}` that pads a column arrives as a hidden span still holding the "5", which printed as a digit of the number beside it ("53.4" for 3.4); a zero-width `\parbox` arrives holding a TeX length.
- **Inline code** written with `\lstinline` keeps its text.
- **Icon-font glyphs** (Font Awesome) are written as the icon's name, `[lock]`, so a column of icons still says what each cell holds.
- **Several captions in one float** each stay with their own table.
- **Citations showing only a year**, where LaTeXML did not know the bibliography style, get the first author from the reference list.
- **References with nothing in them** ("(Table )") are looked up in the paper's LaTeX source by the words before them. The float's number is used when its caption is in the HTML, its label's name otherwise.
- **The author block** shows a list of affiliations shared by all authors once, not after every name.
- **A title broken over two lines** is one heading.
- **Warnings a style file typesets** when a paper changed its page layout ("marginparsep has been altered. … The page layout violates the ICML style.") arrive as the paper's first paragraphs, above the title. They are dropped.
- **Numbers and symbols LaTeXML left half-expanded:** digit groups joined by "true" (`2true294`), a `\mathchoice` of boxed symbols, `\penalty` before a control space, an accent over nothing (`pass\^{}k`), a tilde set on a digit ("5̃5%").

→ [`experiments/review-flagged-fixes`](../experiments/review-flagged-fixes/README.md), [`experiments/tree-references-and-style-warnings`](../experiments/tree-references-and-style-warnings/README.md)

## Table and figure numbers

arXiv's HTML numbers floats itself, and sometimes differently from the PDF: a plot set beside a table in one float is captioned as a table, a caption written with `\captionof` gets no number, and every later number is then off by one or two. `scripts/caption-numbers.py` matches each caption in the markdown to the PDF caption that starts with the same words, and renames it, with the links that point to it, when the PDF calls it something else. A caption that matches no PDF caption, or two equally well, is left alone. It runs after `page-map.py` on every arXiv-HTML conversion. → [`experiments/review-flagged-fixes`](../experiments/review-flagged-fixes/README.md)

What it cannot repair is a reference whose target LaTeXML got wrong: four tables in one float share one anchor, so every reference to them names the last. Those are corrected by hand.

→ [`experiments/html-converter-pilot`](../experiments/html-converter-pilot/README.md)

## Equations

Maths is written as `$…$` and `$$…$$` for KaTeX, VS Code's renderer, not as pandoc's `` $`…`$ ``. It is normalised for KaTeX during conversion:

- unsupported commands are mapped to an equivalent, or shown upright as their name;
- layout commands and LaTeXML's internals are dropped;
- a `$`, a `_`, or a maths-only command such as `\times` inside a text argument is rewritten for its mode;
- environments KaTeX lacks or restricts (`split` outside a display, `multlined`, `@{}` columns) become ones it draws.

`scripts/katex-commands.txt` is the list of commands KaTeX supports, with those it refuses in a text argument marked; `scripts/katex/katex-commands.js` generates it. In a library of 2,202 papers, 56 of 444,263 equations do not parse: pictures and tables set inside an equation, and equations a model read from a PDF. `paperlib symptoms --katex` lists them.

The equations are converted from the author's TeX, which LaTeXML keeps beside its MathML. Converting from the MathML parses slightly more often but gives machine-written TeX without the author's macros, fonts and alignment, so it is not used. → [`experiments/katex-equation-check`](../experiments/katex-equation-check/README.md)

In papers converted from a PDF, display equations are read from the page image by a model (see the next section). About three in ten differ somewhere from arXiv's LaTeX, so the note at the top of such a paper says to check the PDF before quoting an equation. Inline mathematics is re-read from the page image the same way. → [`experiments/inline-math-reread`](../experiments/inline-math-reread/README.md)

## Page numbers

Every heading ends with the PDF page it starts on, `(p. N)`, so the agent can cite the page of the PDF the reader has open. `scripts/page-map.py` finds the page from three sources, in order: the PDF's named destinations (LaTeX writes one per section), its outline, and a search of the page text for the heading. A bookmark is believed only when its page prints the heading, since hyperref can point appendix "A.7" at section 7. A run-in paragraph heading ("Setup. We evaluate …") is found at the start of a line. → [`experiments/page-number-mapping`](../experiments/page-number-mapping/README.md)

## PDF-only papers

Some papers have no arXiv HTML: older papers, and papers never on arXiv. `scripts/pdf-to-markdown.py` converts them in two steps:

- **docling converts the paper.** It reads the layout (headings, tables, figures, reading order) and takes words and numbers from the PDF's own text layer, so a number can't be misread. Its table model put every table number in its table.
- **marker's equation model reads the mathematics.** docling marks where the equations are; `scripts/pdf-equations.py` crops each one and has the model read it, about two seconds an equation. The model is surya, served by llama.cpp. A paper without equations never loads it.
  - **Text whose symbols the text layer lacks.** A PDF made with Word leaves "a task _ ~ ( )" where the mathematics was. The same model reads such text block by block. Its reading replaces the text layer's only when it keeps the block's words and every number. An equation that docling took for text is caught the same way.
  - **Inline mathematics.** Every paragraph with text in a mathematics font is read by the model under the same guard, so "q ∈ R n" becomes `$q \in \mathbb{R}^n$`. It takes about eight seconds a paragraph. `paperlib add-arxiv` and `paperlib add-pdf` always do it; `paperlib reconvert --pdf-text` does it only with `--inline-math`, so that a bulk reconversion stays a matter of hours.

This pairing won a comparison with docling alone, docling's own formula model, marker, and the text layer, scored against arXiv's HTML on papers that have both. It is the only one that put all table numbers in tables while still reading most equations. MinerU was installed, but its run failed, so it was never compared; it is the one to try next. → [`experiments/pdf-converter-bakeoff`](../experiments/pdf-converter-bakeoff/README.md)

Before that, papers without HTML were converted from the text layer alone, in column order. That kept the prose but lost headings, tables and figures. It remains as the fallback when docling fails. → [`experiments/two-column-reading-order`](../experiments/two-column-reading-order/README.md)

A table or a code listing that is an image in the PDF is read by OCR (RapidOCR), and comes out as a table or a code block; its numbers are then the OCR's, not the text layer's. Apple's OCR was compared and reads logos and chart labels into the text. OpenCV is pinned to 4.12: later releases crash now and then inside the OCR on Apple silicon. → [`experiments/ocr-engines`](../experiments/ocr-engines/README.md)

docling writes a table's caption with the table and yields it again as an item of its own; the second copy is dropped.

Known limitations:

- Headings set as run-in bold text (as in PNAS) are not found.
- A table's caption can appear a paragraph away from the table.
- On a two-column first page the title and authors can land inside the introduction.
- Plots keep their image but not their numbers.

## Web articles

`scripts/add-web-article.py` renders the page in headless Chrome, so that pages built by JavaScript have their content. It converts the rendered DOM with pandoc, maths included, and saves the page printed as a PDF. Interactive figures are missing from both.

## Reconversion

When a converter improves, `paperlib reconvert` regenerates paper bodies and keeps their frontmatter and PDFs:

- arXiv downloads are cached in `~/.cache/papers/`, so a reconversion needs no network.
- `--jobs N --state <file>` runs many papers at once, resumably.
- A paper containing `<!-- hand-edited -->` is skipped, also when the marker carries a note (`<!-- hand-edited: … -->`).

A whole-library run is validated with:

- `paperlib symptoms`, which detects known conversion problems;
- `paperlib symptoms --compare <git-ref>`, which flags papers whose body shrank by more than 5% since that commit;
- `paperlib symptoms --katex`, which lists papers with equations KaTeX cannot parse (it needs Node);
- `tests/test_conversion.py`.

The converters are pinned in `pyproject.toml`, so that a fresh install converts a paper exactly as before. Upgrading docling or PyMuPDF changes papers already in a library, so it is a measured step. → [`experiments/library-reconversion`](../experiments/library-reconversion/README.md)

Open problems are in [`tasks/conversion-follow-ups.md`](tasks/conversion-follow-ups.md).

## Metadata

As of 2026-09-30, for resolving a title to a paper:

- **arXiv title search** (a `ti:` word query, 3 s between requests) resolves most titles. **Crossref**'s `query.bibliographic` covers papers that aren't on arXiv.
- **Semantic Scholar**'s title search is rate-limited to near zero without an API key. Its batch endpoint works: `POST /paper/batch` with `ARXIV:`, `DOI:` or `ACL:` ids, up to 400 per call, returns year, venue and citation count.
- **OpenAlex** (anonymous search paused) and **DBLP** (behind a bot check) were unavailable.
- **Publishers that block scripts:** ACM, Wiley, Springer, SSRN and OpenReview. Their PDFs are downloaded by hand in a browser and added with `paperlib add-pdf`.

→ [`experiments/metadata-sources`](../experiments/metadata-sources/README.md)

## Setup

`paperlib` runs in the engine's own environment. uv creates it from `pyproject.toml` on first use. For equations in PDF-only papers, two more things are needed:

- **marker, in an environment of its own**, because marker and docling pin different versions of the same libraries. `paperlib setup-equations` creates it in `~/.cache/papers/venvs/marker`; set `PAPERS_MARKER_PYTHON` to use another.
- **llama.cpp**, which serves marker's model (`brew install llama.cpp`).

Without marker, equations are written as the PDF's raw text, and the paper's note says so. Web articles need Google Chrome or Chromium; set `chrome:` in `paper-library.yaml` if it isn't found.
