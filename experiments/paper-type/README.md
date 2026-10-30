# Experiment · can a cheap request find a paper's type?

**Question.** A paper's type (`method`, `survey`, `benchmark`, `study`, `system`, `position`, `theory`) was written only by `paperlib read`, which reads the whole paper with Opus, so a paper had no type until it was read. Does one cheap request, from the title, the abstract and (for a paper already in the library) its one-line summary, find the type that the whole-paper reading finds? If it does, every paper gets its type when it is filed, and the readings correct it.

**Status.** Measured 30 Oct 2026 on 105 papers of the author's library, 15 of each type. The filing request with a `type` field added agreed with the reading on **97 of 105** papers (93% at the library's mix of types); a type-only request with the stored summary agreed on **100 of 105** (95%). Of the 11 disagreements, read by hand, the filing request was clearly wrong on 3 and the type-only request on 1; the others are papers on the border between two types, where the reading's call is no better than the candidate's. A type-only request costs $0.0034 and adds nothing to the filing request's cost. **The filing request types a paper when `paperlib add` files it, and the type-only request backfills the library (`paperlib fill-types`).** The experiment cost $0.96.

**Serves.** [`docs/design.md`](../../docs/design.md#decisions-log), `paperlib add`, `paperlib fill-types`, `paperlib read`.

## Method

- **Gold.** The type in each paper's note (`paperlib.note_fields`), written by an Opus reading of the whole paper with [`guide/reading-prompt.md`](../../guide/reading-prompt.md). One model's call, so the disagreements were read by hand before a candidate was blamed.
- **Papers.** 15 of each type, drawn with a fixed seed from the 1,829 papers whose note has a type ([`sample.py`](sample.py), [`papers.txt`](papers.txt)). The stratified sample gives the rare types (theory 37 papers, position 36) as much weight as `method` (989); accuracy is also reported reweighted to the library's mix. 105 papers rather than 210: the decision was coarse (good enough or not, and which of two requests), and 15 a type puts the overall accuracy within about ±8 points.
- **Abstract.** arXiv's for a paper with an id, else the opening of its text layer (`paperlib.paper_abstracts`), as at filing and in the backfill.
- **Candidates.** One request a paper through `claude -p`, Sonnet 5.5 at `FILING_EFFORT` (`high`) ([`run.py`](run.py)):
  - **filing**: the request `paperlib add` sends (the topic tree, three style summaries, the title and the abstract), its JSON now with `"type"` ([`guide/filing-prompt.md`](../../guide/filing-prompt.md)). The summary does not exist yet when a paper is filed, so it is not in the input.
  - **type-only**: [`guide/type-prompt.md`](../../guide/type-prompt.md), the title, the stored summary and the abstract. What the backfill sends for a paper without a note.
  - Both prompts list the seven types, as the reading prompt does, and ask for the closest one when the paper is mixed or unclear. Neither defines them.
- **Not run.** Haiku: on 446 papers it could save about $1 over Sonnet's $1.50. `paperlib info`'s own type, as a baseline: `info` now takes the type from the filing request it already sends.
- **Pilot.** Two papers a type through both candidates first, to check the cost before the rest: $0.17 for 28 requests, all agreeing with the notes.
- **Results.** [`results/`](results/): each candidate's answers with tokens, dollars and seconds (`filing.jsonl`, `type-only.jsonl`), [`scores.md`](results/scores.md) (the tables below, with both confusion matrices) and [`disagreements.tsv`](results/disagreements.tsv). Abstracts are not committed: not every paper is openly licensed.

```bash
PAPER_LIBRARY=<library> python3 sample.py 15 > papers.txt
PAPER_LIBRARY=<library> python3 run.py filing --per-type 2       # the pilot
PAPER_LIBRARY=<library> python3 run.py type-only --per-type 2
PAPER_LIBRARY=<library> python3 run.py filing                    # the rest
PAPER_LIBRARY=<library> python3 run.py type-only
PAPER_LIBRARY=<library> python3 score.py
```

## Results

| | filing | type-only |
|---|--:|--:|
| Agrees with the note | 97 of 105 | **100 of 105** |
| Accuracy, at the library's mix of types | 93.2% | **94.5%** |
| Clearly wrong, read by hand | 3 | **1** |
| Input tokens a paper (of which from the cache) | 6.3K (5.0K) | 1.3K (0) |
| Output tokens a paper | 204 (with the summary) | 13 |
| Dollars a paper, as `claude -p` reports it | $0.0058 (the whole filing request) | $0.0034 |
| Seconds a paper | 3.9 | 3.0 |

Recall by type (of 15):

| | method | study | benchmark | system | survey | theory | position |
|---|--:|--:|--:|--:|--:|--:|--:|
| filing | 14 | 13 | 15 | 14 | 15 | 15 | 11 |
| type-only | 14 | 15 | 14 | 13 | 15 | 15 | 14 |

- **Survey, theory and benchmark are found almost always.** The misses sit where the plan expected and one more: `position` against `study` and `method`, `method` against `system`, `study` against `method` and `benchmark`.
- **The filing request is weakest on position papers** (11 of 15), which it calls a study or a method when the paper measures something or proposes a format to argue its point. Its instructions are mostly about the folder; the type-only request, with the summary, does better there.
- **The type costs the filing request nothing**: a few output tokens in a request that is made anyway.

### The disagreements, read by hand

Each was read from the paper's abstract, its summary, and the head and first lines of its note.

| Paper | Note | filing | type-only | Verdict |
|---|---|---|---|---|
| Bad Characters: Imperceptible NLP Attacks | method | study | method | filing wrong: it introduces a class of attacks |
| DBSCAN Revisited, Revisited | position | study | position | filing wrong: a technical correspondence rebutting a paper |
| Embedding based retrieval for long tail search queries in ecommerce | system | method | method | both wrong: Best Buy's production retrieval and its A/B test |
| Model Cards for Model Reporting | position | method | method | border: proposes a documentation framework, argues for its use |
| A Call for Clarity in Reporting BLEU Scores | position | study | position | border: measures BLEU's variation to argue for one standard |
| Language Model Cascades | position | method | position | border: a formalisation, with no new method measured |
| Deep RL at the Edge of the Statistical Precipice | study | method | study | border: an evaluation study that releases its tools (rliable) |
| Recall Is Not Enough (budget-constrained RAG) | study | method | study | border: a diagnostic metric, with a packing method |
| Eyes Wide Shut (MMVP) | benchmark | benchmark | study | border: a diagnostic benchmark built to study a failure |
| A-MEM: Agentic Memory for LLM Agents | method | method | system | border: "a novel agentic memory system" |
| DSPy | system | system | method | border: a programming framework with an optimiser |

On the border papers a reader could pick either type, and the reading's pick is not better evidence than the candidate's: the type is a coarse label, and these papers are two kinds at once.

## Caveats

- **The gold is the papers already read**, mostly the review scopes read first. The 446 papers without a note are a different mix: 154 (35%) have no arXiv id, against 105 of the 1,829 read (6%) and 7 of the 105 sampled, so their abstract comes from the text layer far more often, and that path was barely tested here. `paperlib read` now logs the type it replaces, so their agreement is measured when they are read.
- **One request per paper.** A second run could move a border paper either way; the gap between the two candidates (3 papers of 105) is within that.
- **Both candidates are Sonnet; the gold is Opus**, from the whole paper. The prompts were not tuned: this is their first wording.

## Decision

- **Filing**: `paperlib add` writes the type its filing request gives. The add-paper skill sets it with `paperlib set-type` beside the summary it writes.
- **Backfill**: `paperlib fill-types` copies the note's type where there is one, and asks the type-only request for the rest. Run on 30 Oct 2026: 1,824 types from notes, 446 asked for $1.57 (about $140 to read those papers instead), none failed. The 446 came out method 172, study 97, survey 48, system 45, position 44, theory 24, benchmark 16. Position is 10% of them against 2% of the papers read. The unread are mostly areas not yet reviewed, where essays are common (trustworthy-ml 10, research-practice 8), and in the sample the type-only request called no other type position; but that was 15 papers, so position is the first type to check as these papers are read.
- **Reading**: `paperlib read` replaces the type when the reading says otherwise, says so, and logs both in `read-papers.jsonl`.
- The frontmatter's `type` is required; the note keeps its `type:` line, as the record of what the reading said ([`docs/design.md`](../../docs/design.md#decisions-log)).
