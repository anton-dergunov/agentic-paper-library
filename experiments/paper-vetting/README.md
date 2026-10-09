# Experiment · does a first opinion on a paper agree with what the reader decided?

**Question.** `paperlib vet`, the first design of the quick look at a paper, gave a verdict on a paper before it is added: `add`, `skip` or `read first`, from the abstract, citation data, the library's own mentions of the title, the folder's papers and the reader's interests. Does that verdict agree with the decisions already in a library, what does it cost, and which model should write it?

**Status.** Measured 9 Oct 2026 on 72 papers of the author's library. **The verdict does not separate the papers the reader skipped from those kept**: Sonnet 5.5 said `add` for 22 of 30 skipped papers and for 28 of 42 kept ones; Haiku 4.5 for 13 of 30 and 21 of 42. It follows uptake instead: the papers Sonnet would add are named by a median 5.5 library papers, those it would skip by 0.5. The labels are weak (below), so this does not show the verdicts are wrong, only that these labels cannot validate them. A Sonnet verdict costs 11.3K tokens in, 700 out, $0.029; Haiku's cost more ($0.050, 7.3K output tokens) and were slower. Not measured: one request against two.

**Decision.** The recommendation was dropped. The reader's reason for wanting a paper is not written anywhere a script can read, so the command that shipped, `paperlib info`, reports the same signals and a description and recommends nothing.

**Serves.** [`docs/design.md`](../../docs/design.md#decisions-log), `paperlib info`.

## Method

- **Labels**, three classes of uneven strength. An agent proposed both the papers to add and the papers to skip when the library was built; the reader reviewed only the skips.
  - `skipped` (30, drawn from 678 with an arXiv id): in `catalog/skipped.yaml`. The reader looked at each and left it skipped.
  - `kept-reviewed` (27): the two papers that were once in `skipped.yaml` and are now in the library (the file's git history has three commits, so earlier unskips are lost), and 25 papers the reader wrote an overview note of.
  - `kept-unreviewed` (15, drawn from the rest): proposed by an agent and taken on trust.
- **Hiding the answer.** A paper in the library is left out of its folder's list and of the search for its own title. Notes and reviews are not searched, since they name a paper because it is in the library. The skip list is not shown.
- **Input and models.** The command as it was that day, kept here as [`vet.py`](vet.py): the filing request, then the verdict request ([`prompt.md`](prompt.md)) with the reader's interests file as it was on the day (four lists, 30 lines, drafted the same day and not yet corrected by the reader). Sonnet 5.5 and Haiku 4.5 through `claude -p`, no tools, default thinking, four requests at a time.
- **Scoring.** `add` agrees with a kept paper, `skip` with a skipped one; `read first` agrees with neither. [`score.py`](score.py).
- **Results.** [`results/`](results/): the sample with its labels, and each model's verdicts with signals, folder and usage.

```bash
PAPER_LIBRARY=<library> uv run python experiments/paper-vetting/run.py sample
PAPER_LIBRARY=<library> uv run python experiments/paper-vetting/run.py vet claude-sonnet-5-5
python3 experiments/paper-vetting/score.py --disagreements
```

## Results

| Label | Papers | Sonnet: add / read first / skip | Agrees | Haiku: add / read first / skip | Agrees |
|---|---|---|---|---|---|
| skipped | 30 | 22 / 1 / 7 | 7 | 13 / 3 / 14 | 14 |
| kept-reviewed | 27 | 15 / 0 / 12 | 15 | 13 / 0 / 14 | 13 |
| kept-unreviewed | 15 | 13 / 1 / 1 | 13 | 8 / 0 / 7 | 8 |

| | Sonnet 5.5 | Haiku 4.5 |
|---|---|---|
| Tokens in / out per paper (both requests) | 11,345 / 699 | 8,061 / 7,301 |
| Cost per paper | $0.029 | $0.050 |
| Run of 72 | $2.09 | $3.63 |
| Verdict length, median (170 words asked) | 225 words | 189 words |

The two models gave the same recommendation for 49 of 72 papers and the same folder for 54.

**Sonnet's `add` rate is the same for skipped and kept papers** (73% and 67%); Haiku's too (43% and 50%). Neither verdict carries the reader's decision.

**What the verdict follows.** Median citations and library papers naming the title, by Sonnet's recommendation: `add` 536 and 5.5, `skip` 241 and 0.5. By label: skipped 165 and 2, kept-reviewed 585 and 4, kept-unreviewed 442 and 4. The skipped papers are well-cited papers too: they were candidates on reading lists, not a random draw of arXiv.

**Why the skipped papers were skipped**, for the 22 Sonnet would add: 16 reasons are relative to the list they were on ("overlaps UMBRELA and the Bing study", "incremental over StyleGAN2", "superseded by tau-bench, WebArena and OSWorld", "A Cookbook of SSL is in library; surveys cut"), three are scope ("role-play focus rather than user modelling") and three are "too recent to show uptake". The verdict sees the folder's papers and still finds a gap for each: AgentBench (1,459 citations, named by 39 library papers) and Glow (3,721, named by 15) read as papers a library should hold. The reader's bar was how deep a folder should go, which nothing in the request states.

**Why kept papers got `skip`.** All 12 of Sonnet's are papers with an overview note: mostly 2017–2021 work outside today's focus (graph embeddings, concept whitening, GLOM, dalex). The note says the reader studied the paper once, not that they would add it now.

**Cost.** Haiku wrote ten times the output tokens of Sonnet for a shorter verdict (its thinking), so it cost more per paper and its run took about four times as long.

## Reading

- These labels answer "which of these good candidates does a folder need", and the verdict answers "is this paper good and relevant". Agreement between them cannot settle whether the verdict is right. The verdict was written for papers met one at a time, of any quality, and that population is not in the library's history.
- Sonnet leans to `add` for any well-cited paper the library's papers name. For a reader whose long-tail folders hold only the seminal papers, that is too generous.
- Haiku is not cheaper here, and disagrees with Sonnet on a third of the papers.

## Not done

- **One request against two** was in the plan and was not run.
- Giving the verdict the folder's own skipped papers as precedents, and how deep the folder is meant to go, might have raised agreement. It was not tried: the decision above does not rest on the score.
