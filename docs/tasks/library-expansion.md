# Task: expand the library to the whole field

The library started as about 240 LLM papers copied from a project on LLM memory, all under
`llm/`. This task grows it into a library for all of Anton's work and interests:

- LLM evaluation and post-training, the primary area;
- search, ranking and recommender systems, the secondary area;
- experimentation and metrics;
- ML systems;
- a long tail: NLP, representation learning, vision, generative models, RL, graphs,
  interpretability, foundations and robotics.

It runs over many sessions. This file is the plan and the progress record. Its outputs go in
`docs/tasks/library-expansion/`.

## Status

- [x] 1. Inventory of existing papers: `library-expansion/inventory.tsv`, `inventory.md`
  (2026-09-30). 981 papers: 859 to add, 88 `skip?` for Anton, 6 skipped, 28 already in the library.
- [ ] 2. Structure proposal, approved by Anton: `library-expansion/structure.md`. Proposed
  2026-09-30, waiting for approval together with the `skip?` list in `inventory.md`.
- [ ] 3. Tooling for a declared tree: `catalog/`, scripts, `AGENTS.md`, skills
- [ ] 4. Existing papers moved into the new tree
- [ ] 5. Inventory papers added, one batch per area (list the batches here as they are done)
- [ ] 6. Literature pass, one reading list per area (list the areas here as they are done)
- [ ] 7. Wrap-up

## Decisions

- **Every referenced paper is a candidate:** papers in `Papers_old/`, papers with Obsidian notes,
  papers mentioned in passing in concept notes, and papers in the org plans.
- **Skips:**
  - What gets skipped: duplicates, things that are not papers (books, slides, blog posts),
    off-interest items, and papers superseded by a later version.
  - Low-quality, outdated or out-of-place papers from `Papers_old/` are flagged `skip?` for
    Anton to confirm.
  - Every skip has a reason and is recorded in `catalog/skipped.yaml`, so it is not proposed
    again.
- **Anton reviews exceptions only.** For each batch he sees the proposed skips, unclear title
  matches, and papers that fit no folder. The rest is filed by the approved structure without
  asking.
- **The literature pass is weighted by focus:**
  - primary folders get 30–60 papers each: LLM evaluation, post-training, search and ranking,
    recsys, experimentation;
  - the others get 5–15 seminal and recent papers.
- **The tree is declared, not grown.** All folders are created up front, even empty ones, from
  `catalog/topics.yaml`.
- **Storage is not a constraint.** GitHub allows 10 GB per repo, and Yandex Disk has room for far
  more PDFs than this task will add.
- **Some things are not edited:**
  - The Obsidian vault is not touched. Linking notes to library papers is a separate task.
  - career-system is read for context only; nothing from it goes into this repo.

## Sources

| Source | What is there |
|---|---|
| `~/Yandex.Disk.localized/Papers_old/` | 546 PDFs, flat, some duplicates |
| Obsidian `ML & AI/` | about 333 arXiv ids and 90 PDF links, mostly in `Concepts/`; paper notes in `Papers/`; paper lists in `TOC/Papers on *.md` |
| Org `ML/*.org`, `Inbox.org`, `Work/Prep.org` | about 107 arXiv ids, plus titles |
| career-system `strategy/02-target-roles.md`, CV | interests and priorities (read only) |

## 1. Inventory

Outputs:

- `library-expansion/inventory.tsv`, one row per unique paper:

  `key | title | year | arxiv | url | sources | local_pdf | topic | action | reason | status`

- `library-expansion/inventory.md`: counts per source and per action, and notes on anything odd.

How:

- **`Papers_old/`:** the title comes from the filename. Resolve each with
  `scripts/arxiv-lookup.py --title`, in the background because arXiv rate-limits.
  `local_pdf` is the file name.
- **Obsidian and org:**
  - collect arXiv ids and URLs, other paper URLs (ACL Anthology, OpenReview, NeurIPS/PMLR
    proceedings, ACM DL, Semantic Scholar) and PDF links;
  - add the titles of the Obsidian paper notes;
  - an agent reads the prose paper lists (`TOC/Papers on *.md`, org headings) rather than a
    regex;
  - titles without an id go through the lookup.
- **Already in the library:** mark matches `in-library`.
- **Deduplicate** by arXiv id, then by normalised title.
- **`sources`** lists every origin, as vault- or org-relative paths:
  `papers_old; obsidian:ML & AI/Concepts/Attention.md; org:ML/Ranking.org`.
- **`action`** is one of:
  - `add`
  - `in-library`
  - `move`: a library paper that belongs elsewhere
  - `skip`: needs a reason
  - `skip?`: a weak paper waiting for Anton
- **`status`** starts as `todo` and ends as `added`, `skipped` or `in-library`.

## 2. Structure proposal (Anton approves)

Output: `library-expansion/structure.md`. It holds:

- the full tree, two or three levels deep, with one scope line per folder and the expected
  paper count from the inventory;
- the moves of existing papers, each with a reason. Snorkel leaves `llm/alignment/data/`. Also
  review the rest of `alignment/data/`, and the grouping of `personalization/`,
  `user-modelling/` and `user-intelligence/`;
- open questions, only where two placements are genuinely equal.

The inputs are the target roles, the org `ML/` files, the Obsidian `TOC/`, the inventory, and the
draft top level in `AGENTS.md`.

Starting draft, to be refined against the inventory:

```
llm/
  architecture/  pretraining-and-scaling/  prompting-and-in-context/  reasoning/
  post-training/            SFT, preference learning, reward models, RL for reasoning
                            (absorbs alignment/)
  evaluation/  agents/  memory/  context/  retrieval-augmented/
  personalization/  efficiency/  safety-and-privacy/  behaviour/  routing/
search-and-ranking/
  learning-to-rank/  dense-and-sparse-retrieval/  neural-reranking/  query-understanding/
  click-models-and-unbiased-ltr/  ir-evaluation/  ads-and-ctr/
recommender-systems/
  collaborative-filtering/  deep-recsys/  sequential/  llm-and-generative-recsys/
  bandits-and-exploration/  evaluation/
experimentation-and-metrics/
  ab-testing/  variance-reduction/  causal-inference/  off-policy-evaluation/  metric-design/
data-centric-ml/            weak supervision, annotation, data quality, synthetic data
ml-systems/                 distributed training, inference and serving, GPU kernels
ml-engineering/             production ML, MLOps
nlp/  representation-learning/  graphs/  vision-and-multimodal/  generative-models/
interpretability/  ml-foundations/  reinforcement-learning/  robotics-and-embodied/
research-practice/
```

## 3. Tooling for a declared tree

Start only after other in-flight changes to `scripts/` and `library/` are committed.

- **`catalog/`** holds the library's hand-maintained data files. The scripts read them; nothing
  in it is generated.
- **`catalog/topics.yaml`** lists every topic folder with its scope line. It is the single
  source of truth for the tree.
- **`catalog/skipped.yaml`** lists the papers deliberately not added, each with `title`,
  `arxiv` or `url`, `topic`, `reason` and `date`.
- **`scripts/build-index.py`:**
  - creates every declared folder, in `library/` and under `PDF_ROOT`;
  - writes a README for empty folders too: the scope line, then "No papers yet";
  - shows skipped papers as a "Considered, not added" section in their folder's README;
  - prunes only empty folders that are not declared.
- **`scripts/check-library.py`** also fails on:
  - a paper in an undeclared folder;
  - a declared folder that is missing;
  - a malformed skip record.
- **`scripts/arxiv-lookup.py`** reports "skipped earlier: <reason>", the same way it reports
  "already in library".
- **`scripts/move-paper.sh`:** check that a declared folder emptied by a move is recreated.
- **`AGENTS.md`:**
  - folders are declared in `catalog/topics.yaml`;
  - the intended-top-level list becomes a pointer to that file;
  - the `Papers_old` row points to this task.
- **Skills:**
  - `add-paper` picks topics from `catalog/topics.yaml` and honours `catalog/skipped.yaml`;
  - `reorganize` edits `catalog/topics.yaml` along with the moves.

## 4. Move existing papers

Apply the moves approved in step 2 with `scripts/move-paper.sh`, following the `reorganize`
skill. Then:

1. Fix folder references in `docs/`, for example `literature-review.md`.
2. Rebuild the indexes and run the check.

## 5. Add the inventory, in batches

Each batch is one top-level area or one large subfolder, primary areas first. Per batch:

1. Show Anton the exceptions: `skip?` rows, unclear matches, papers with no folder.
2. Add the papers:
   - arXiv papers with `scripts/add-arxiv-paper.sh`, one at a time;
   - `Papers_old/` papers not on arXiv with `scripts/add-pdf-paper.sh --title … --source …`;
   - web-only papers: download the PDF to a temporary folder first, then use the same script.
3. Write each summary with `scripts/paperlib.py set-summary`, reading the abstract and
   introduction.
4. Record confirmed skips in `catalog/skipped.yaml`.
5. Update `status` in `inventory.tsv`, so the next session can resume.
6. Run `scripts/build-index.py`, then `scripts/check-library.py`.
7. Spot-check two or three conversions, and flag any `pdf-text` papers.
8. Suggest a commit message.

## 6. Literature pass

For each area, write `library-expansion/reading-lists/<area>.md`:

- the seminal papers and the important 2024–2026 work, found with a web search, each with a
  one-line reason;
- nothing already in the library or in `catalog/skipped.yaml`;
- outdated candidates go to `catalog/skipped.yaml` with a reason, not into the list.

Anton strikes items. The rest are added as in step 5. Primary areas go first, at the depth set
in Decisions.

## 7. Wrap-up

- Update "Next" in `docs/proposal.md`.
- Update the description of the tree in `AGENTS.md`.
- Tell Anton when every `Papers_old/` file is resolved. Deleting that folder is his call.

## Notes for later sessions

- **Paper metadata services** (as of 2026-09-30):
  - Semantic Scholar's title search (`/paper/search/match`) is rate-limited to near zero
    without an API key. Its batch endpoint (`POST /paper/batch` with `ARXIV:`, `DOI:` or `ACL:`
    ids, up to 400 per call) works, and gives year, venue and citation count.
  - Titles resolve through arXiv's title search (`ti:` word query, 3 s between requests), then
    Crossref's `query.bibliographic` for papers not on arXiv.
  - OpenAlex's anonymous search and DBLP's API were unavailable (paused, and behind a bot
    check).
- **Structure proposal:** `structure.md` is generated from the inventory. Once it is
  approved, `catalog/topics.yaml` is written from its tables (folder, scope), with Anton's
  changes applied.

## Done when

- `scripts/check-library.py` passes.
- `scripts/build-index.py` leaves no diff when run twice.
- Every folder in `catalog/topics.yaml` exists with a README.
- Every inventory row is `added`, `in-library` or `skipped`, and all 546 `Papers_old/` files
  map to a row.
