# The library: design decisions

What goes into `library/`, how it is organised, and how papers are converted, with the reasons.
The reading workflow around it is in [proposal.md](proposal.md); the rules an agent follows are
in `AGENTS.md`.

## What it covers

The library holds the papers for all of Anton's work and interests, weighted by focus:

- **Primary:** LLM evaluation and post-training; search, ranking and recommender systems;
  experimentation and metrics. These folders hold 30–60 papers each.
- **Secondary:** ML systems.
- **The long tail:** NLP, representation learning, vision, generative models, RL, graphs,
  interpretability, foundations, robotics. 5–15 seminal and recent papers per folder.

It started on 2026-09-29 as about 240 LLM papers from a project on LLM memory. On 2026-09-30
and 2026-10-01 it grew to 2,200 papers, in two steps:

- **Everything Anton had referenced:** the 546 PDFs of an older unsorted collection, the
  papers linked or named in the Obsidian vault, and those in the org plans. Every one was
  added, found already in the library, or skipped with a reason.
- **A literature pass**, one reading list per area. Anton struck what he did not want, and the
  papers considered but not proposed were recorded as skips. The `literature-pass` skill runs
  this again for any area.

The working records of that expansion (the inventory of referenced papers, the structure
proposal, the fourteen reading lists) are in git history: see the commit that removed
`docs/tasks/library-expansion/`.

## Structure

- **Twenty areas follow Anton's org study plans**, so a plan section and a library folder
  point at the same thing:

  | Org plan | Library areas |
  |---|---|
  | `Generative_AI.org` | `llm/`, `generative-models/`, `vision-and-multimodal/` |
  | `Ranking.org` | `search-and-ranking/`, `recommender-systems/` |
  | `Experiments.org`, `Statistics.org` | `experimentation-and-metrics/` |
  | `Deep_Learning.org` | `deep-learning/`, `representation-learning/`, `nlp/`, `graphs/`, `interpretability/` |
  | `Foundations.org` | `ml-foundations/`, `data-centric-ml/`, `trustworthy-ml/` |
  | `Systems.org` | `ml-systems/`, `computer-systems/` |
  | `RL.org` | `reinforcement-learning/`, `robotics-and-embodied/` |

  Plus `ai-and-society/`, `research-practice/`, and `curiosities/` for papers kept for fun.
- **Two levels, three where an area has a natural grouping** (`llm/post-training/`,
  `llm/memory/`, `llm/personalization/`, `llm/evaluation/`).
- **General before LLM-specific.** A method that predates LLMs or applies to all of ML lives in
  its general area: knowledge distillation in `deep-learning/`, SHAP in `interpretability/`,
  DP-SGD and federated learning in `trustworthy-ml/`. `llm/` holds what is about language
  models.
- **Interpretability is one area**, `mechanistic/` and `explainability/`, rather than split
  between `llm/` and elsewhere.
- **Bandits go under `reinforcement-learning/`**, as in `RL.org`, not under recommender systems.
- **The tree is declared, not grown.** Every folder is listed with its scope in
  `catalog/topics.yaml` and exists even while empty, so filing means choosing from a fixed
  list with written scopes, not inventing folder names. A new folder is a deliberate catalog
  change.
- **About 20 papers per folder is a heuristic, not a limit.** A folder is split only when a
  natural division exists.

## What gets added, and what is skipped

- **Skipped:** duplicates, things that are not papers (books, slides, talks), off-interest
  items, and papers superseded by a later version.
- **An engineering blog post** that is the only write-up of a system (Netflix's recommendation
  foundation model, Meta's GEM) is added as a web article.
- **Every skip is recorded** in `catalog/skipped.yaml` with its reason, so it is not proposed
  again; `arxiv-lookup.py` reports it, and each folder's README lists its skips under
  "Considered, not added".

## Conversion

The markdown is the agent's copy of a paper, so its quality decides how well the agent reads.

**arXiv's HTML rendering is the source whenever it exists.** A comparison on 2026-09-29 of
three conversions of Zep (simple tables, no display maths), DPO and SimPO (maths-heavy,
multi-level tables):

| | Zep | DPO | SimPO |
|---|---|---|---|
| Display equations in arXiv HTML (exact LaTeX) | 0 | 25 | 10 |
| Numbered equations still present, raw PDF text (PyMuPDF) | – | 21 of 25, flattened | 5 of 10 |
| Numbered equations still present, pymupdf4llm | – | 0 | 1 |

- For prose and simple tables, all three were fine.
- **pymupdf4llm drops display maths silently**: DPO's objective (Eq. 7) is an empty gap with no
  warning. A silent loss is worse than a visible mess, so it is not used for text.
- **Raw PDF text keeps equations but flattens them**, and a formula in a table cell can come
  out as a different formula: SimPO's β/|y| length normalisation, the paper's whole idea, lost
  its numerators.
- **Two-level table headers** lose their column structure in both PDF conversions; the HTML
  keeps it.

What follows from it:

- `add-arxiv-paper.sh` converts arXiv's HTML with pandoc: maths as `$...$`, merged-cell tables
  as HTML, figures saved to `images/`. Plots arXiv embeds as SVG objects are kept, as WebP when
  the SVG is over 300 KB.
- Papers without arXiv HTML fall back to the PDF's text layer (`source: pdf-text`): PyMuPDF's
  raw text in pymupdf4llm's column order. Their prose is reliable; equations, tables and
  numbers are not, and the paper says so at the top. An ML-based converter (MinerU, marker,
  docling) is the thing to test if these papers start to matter.
- Web-only papers (Distill, transformer-circuits.pub, blogs) are converted from the page, and
  the PDF is the page printed by Chrome (`source: web`).
- Headings carry the PDF page they start on, so the agent can cite pages in the PDF Anton is
  reading.

Where arXiv's HTML itself loses content, the converter recovers it (since 2026-10-01; see the
docstring of `html-to-markdown.py`):

- **Boxed text** (definitions, findings, takeaways, prompt templates) is drawn by LaTeXML as an
  SVG frame with the text inside. It becomes a quote, so the agent can read it; only drawings
  with real shapes stay images. Small text badges in tables become their text.
- **Tables in `\resizebox` or `\scalebox`** come out of LaTeXML as inline spans and are rebuilt
  as tables. A header row LaTeXML did not mark is recognised by the rule under it.
- **Taxonomy trees drawn with `forest`**, which LaTeXML cannot render, are taken from the
  paper's LaTeX source on arXiv and written as nested lists.
- **Equation tables** keep their text: `\intertext` prose, a left-hand side set as text, and
  several equations on one row.
- A paper converted from PDF text gets its HTML conversion once arXiv renders it
  (`reconvert.py` tries the HTML first).

`scripts/test_conversion.py` checks each of these on small fixtures.

Known limitations of PDF-text papers: tables and figures are lost; plot and legend text is
sometimes fenced as code; most have no headings, so no page numbers; grids of numbers in old
two-dimensional figures come out jumbled.

## Paper metadata services

As of 2026-09-30, for resolving titles to papers:

- **arXiv title search** (`ti:` word query, 3 s between requests) resolves most titles;
  **Crossref**'s `query.bibliographic` covers papers not on arXiv.
- **Semantic Scholar**: the title search is rate-limited to near zero without an API key, but
  the batch endpoint (`POST /paper/batch` with `ARXIV:`, `DOI:` or `ACL:` ids, up to 400 per
  call) works and gives year, venue and citation count.
- **OpenAlex** (anonymous search paused) and **DBLP** (behind a bot check) were unavailable.
- **Publishers that block scripts:** ACM, Wiley, Springer, SSRN and OpenReview. Those PDFs are
  downloaded by hand in a browser.
