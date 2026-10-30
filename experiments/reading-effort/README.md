# Experiment · does a lower effort level read a paper as well?

**Question.** After the switch to text layers, an Opus read spends about 5.7K output tokens a paper, a third of its cost, and about half of that is thinking. Claude Code's `--effort` sets how much the model thinks. Does `medium` or `low` write notes as good as `high`, for less?

**Status.** Measured 30 Oct 2026 on six papers. **Reads stay at `high`, now set by `paperlib read` itself.** The blind judge preferred the `high` note on all six papers. Over six notes `high` made 2 errors, `medium` 5 and `low` 8; `low` also missed one point. `medium` would save about 28% a read, and `low` 37%. The experiment cost $3.17.

**Serves.** [`docs/design.md`](../../docs/design.md#decisions-log), `paperlib read`.

## Method

- **Papers.** Six of the author's library that Opus had read on 30 Oct 2026, with the current reading prompt and text layers: DBSCAN Revisited, Revisited; LightGBM; The BellKor Solution to the Netflix Grand Prize; Deep Neural Networks for YouTube Recommendations; Progressive Layered Extraction (PLE); Are We Really Making Much Progress? They range from 15K to 26K input tokens ([`papers.txt`](papers.txt)).
- **Conditions.**
  - `high`: the notes already in the library, copied, not read again. `paperlib read` passed no `--effort` then, so `claude -p` took the author's Claude Code setting, `effortLevel: high`. That is why `paperlib read` now passes `--effort high` itself: the measured level no longer depends on whoever runs it.
  - `medium` and `low`: read again with `--effort`. Each request is the one `paperlib read` sends, with the paper's folder as the related list ([`run.py`](run.py)).
- **Judge** ([`judge.py`](judge.py), adapted from [`../prompt-trim`](../prompt-trim/README.md)). Opus, at the same `high` setting, saw the reading view and the three notes, with the letters shuffled per paper. It listed 10 points a note needs, then each note's errors and missed points, and named the note it would keep.
- **Noise floor.** None was run here. In prompt-trim, two runs under the same condition differed by one error over six notes (5 against 4).
- **Results.** [`results/`](results/): the 18 notes, [`reads.jsonl`](results/reads.jsonl) (usage per request), the judge's findings in `judge/` and its choice per paper in [`best.json`](results/best.json). The papers' text is not committed. The `high` condition was called `default` when it ran and was renamed afterwards; the judge's letters and findings are unchanged.

```bash
PAPER_LIBRARY=<library> python3 run.py library medium low
PAPER_LIBRARY=<library> python3 judge.py
```

## Results

| | high | medium | low |
|---|--:|--:|--:|
| Errors (6 notes) | **2** | 5 | 8 |
| Points missed, of 60 | 0 | 0 | 1 |
| Note the judge would keep | **6 of 6** | 0 | 0 |
| Output tokens a paper | 5,746 | 3,943 | 2,791 |
| of which thinking | ~2,670 (estimated) | 1,277 | 441 |
| Note length a paper (characters) | 7,173 | 6,166 | 5,528 |
| Cost a paper, at five-minute cache writes | $0.258 | $0.186 | $0.163 |

- **Costs.** All three are priced as a read of one paper on its own: $5 a million input tokens (written to the five-minute cache) and $20 a million output tokens. The `usd` logged for `low` is lower still, because the parallel `medium` run had just cached the same papers. The thinking of `high` is estimated from its note length, at the characters per visible token of the other two.
- **The errors at lower effort** are of the kinds a careful reading avoids:
  - a claim taken from the text that the paper's own table contradicts (PLE, `low`);
  - "decay" read into an update rule that the paper leaves unspecified (PLE, `low`);
  - a result attributed to the wrong blending method (BellKor, `medium`);
  - one bias term's parts mixed with a separate scaling feature (BellKor, `medium`);
  - "unoptimised baseline", where the paper says that baseline was optimised (LightGBM, `medium`).
- **What `high` adds.** The judge's reasons were completeness and checks of the paper against itself: the `high` notes caught a table contradicting the text in two papers (SpectralCF's recall above TopPopular's; ML-MMOE's −0.0001 gain), which the cheaper notes missed or repeated.
- **The cache fix.** These six `high` reads cost $0.320 each with one-hour cache writes; at five-minute writes the same requests come to $0.258 ([design log](../../docs/design.md#decisions-log)).

## Conclusions

1. Read at `high`, and set it in `paperlib read` (`--effort high`) rather than leave it to the user's Claude Code setting. `medium` saves about $0.07 a paper, but it more than doubles the errors and never wrote the preferred note. The reads are what the reviews rest on.
2. No library note was replaced: the judge preferred the existing note for every paper.
3. **Limits.**
   - Six papers, one run per condition, and an Opus judge.
   - `xhigh` and `max` were not tried.
   - The `high` notes were written a day earlier and not read again. A note's quality varies between runs by about one error in six notes, smaller than the gaps found here.
