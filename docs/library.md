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
- Papers without arXiv HTML are converted from the PDF (`source: pdf-text`) by layout
  analysis: see "PDF-only papers" below.
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
- **siunitx numbers** arrive unrounded with digit groups; the groups are joined and raw
  input is rounded to four decimals.
- **Inline icons** (a check mark in a table cell) keep their file's name as alt text.
- **Citations arXiv left as BibTeX keys**, when a paper shipped its `.bib` uncompiled, are
  rebuilt with the reference list by pandoc's citeproc.
- A paper converted from PDF text gets its HTML conversion once arXiv renders it
  (`reconvert.py` tries the HTML first).

`scripts/test_conversion.py` checks each of these on small fixtures.

### PDF-only papers

About 280 papers have no arXiv HTML (older papers, and papers never on arXiv). Until
2026-10-01 they were converted from the PDF's text layer alone, which kept the prose but
lost headings, tables and figures. A comparison on 2026-10-01 against arXiv's HTML, on papers
that have both (DPO, SimPO, Zep, Larimar, Memory Layers, HippoRAG):

| | Table numbers in a table | Display equations close to arXiv's LaTeX | Headings found | Prose recovered | Time per paper |
|---|---|---|---|---|---|
| Text layer (the old conversion) | 0% | none | 0% | 91% | seconds |
| docling | 100% | none (not decoded) | 75% | 93% | 15–70 s |
| docling with its formula model | 100% | 1 of 2, one misread (`\sinu` for silu) | 74% | 96% | 5 min |
| marker | 83% | 68% | 69% | 90% | 1–5 min |
| **docling + marker's equation model** (in use) | **100%** | **71%** | 68% | 93% | 0.5–2 min |

- **docling** takes words and numbers from the PDF's own text layer, so a number cannot be
  misread, and its table model put every table number in its table.
- **marker** reads equations well but re-reads whole pages with a vision model, and in
  HippoRAG's tables it split every decimal across two cells ("34 | 8" for 34.8).
- **So each does what it is best at.** docling converts the paper and marks where the
  equations are; `scripts/pdf-equations.py` crops each one and has marker's model (surya)
  read it, about two seconds an equation. A paper without equations never loads that model.
- An equation read by a model can be wrong in a symbol or an index (about three in ten differ
  from arXiv's LaTeX somewhere), so the note at the top of such a paper says to check the PDF
  before quoting one. That is still far better than the text layer, where an equation is
  scattered glyphs.
- **Text whose symbols the text layer lacks** (a PDF made with Word leaves "a task _ ~ ( )"
  where the mathematics was) is read by the same model, block by block, and replaces the
  text layer's text only when it keeps the block's words and every number. An equation
  docling took for text is caught the same way.
- MinerU was installed but not evaluated: its command line changed and the run did not
  complete. It is the one to try if this needs improving.

Setup, once per machine: docling in the Python the scripts run with (`pip install docling`);
marker in its own environment, because the two pin different versions of the same libraries
(`uv venv --python 3.12 ~/.cache/papers/venvs/marker && uv pip install --python
~/.cache/papers/venvs/marker/bin/python marker-pdf`, or set `PAPERS_MARKER_PYTHON`); and
`brew install llama.cpp`, which serves marker's model. Without marker, equations are written
as the PDF's raw text and marked so.

Known limitations: headings set as run-in bold text (PNAS) are not found; a table's caption
can appear a paragraph away from it; plots keep their image but not their numbers.

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
