# Experiment · do reviews and notes help an agent answer questions?

**Question.** Reviews and notes are written for the reader, and also so that a later agent session starts from them instead of re-reading papers. Does a fresh session find them? Does it answer better, faster or more cheaply with them?

**Status.** Measured 5 Oct 2026: three questions, three copies of the library, one session each. A session finds and uses both without being told beyond the library guide. **Reviews make a synthesis answer two to three times cheaper and faster, and less accurate**: the session answers from the review without opening the papers, and misreads what the review's compressed statements mean. **Notes help without that cost**: the best answer to two of the three questions came from the copy with notes and no reviews. The guide now tells sessions to check a paper's note or text before stating a number or what a result means.

**Serves.** [`docs/design.md`](../../docs/design.md), and the "Start from the review" rule in [`guide/library-guide.md`](../../guide/library-guide.md).

## Method

- **Questions.** [`questions.txt`](questions.txt):
  1. "What does current research say about managing obsolete facts in LLM memory?": a synthesis across the papers of one review.
  2. "How does Zep invalidate outdated facts, and what did it score on LongMemEval against which baseline?": a detail of one paper.
  3. "Can an LLM judge replace human raters when evaluating personalised responses?": a question that spans two reviews.
- **Conditions.** Three copies of the author's library (2,200 papers, without figures): as it is, with 5 reviews and 322 notes; without `reviews/`; without `reviews/` and `notes/`. In the copies without them, the rules and links that mention them were removed from the agent instructions and the folder indexes. [`copies.py`](copies.py) builds the copies (written after the run, from the commands used in it).
- **Sessions.** Each question once per copy with `claude -p` (Opus 5.5), in a fresh session started in the copy. A session could read files and run shell commands, and could not edit files, search the web or start subagents. [`run.py`](run.py).
- **Measures.** From each session's event stream ([`summarize.py`](summarize.py)): seconds, input tokens processed (written to the cache plus read from it), output tokens, tool calls, and whether a review or a note was read. The API price is not used to compare conditions: the nine sessions started together, and the first to start paid to cache the prompt prefix the others then read.
- **Grading.** [`judge.py`](judge.py): a separate Opus session in the full library gets the three answers to a question, labelled A to C in a shuffled order. It pools the distinct points the answers make (at most 20), checks each against the paper's markdown, not against reviews or notes, and lists per answer the points it makes and the statements that are wrong.
- **Results.** [`results/sessions.tsv`](results/sessions.tsv), the nine answers in [`results/answers/`](results/answers/), and the judge's findings in `results/judge-q*.json`. The event streams are not committed.

```bash
python3 copies.py <library> <scratch-dir>
python3 run.py <out-dir> asis=<copy> noreviews=<copy> nonotes=<copy>
python3 summarize.py <out-dir> <library> results/answers > results/sessions.tsv
python3 judge.py results/answers <library> results
```

## Results

All 60 pooled points held when checked against the papers, so the answers differ in how many of them they make and in what else they get wrong.

| Question | Copy | Seconds | Input tokens processed | Tool calls | Points made, of 20 | Wrong statements | Judge's rank |
|---|---|---|---|---|---|---|---|
| 1 synthesis | as is | 53 | 292K | 7 | 17 | 8 | 3 |
| | no reviews | 110 | 932K | 15 | 20 | 3 | 1 |
| | no reviews, no notes | 150 | 1,092K | 21 | 15 | 5 | 2 |
| 2 one paper | as is | 21 | 111K | 2 | 16 | 0 | 2 |
| | no reviews | 21 | 110K | 2 | 19 | 0 | 1 |
| | no reviews, no notes | 17 | 103K | 2 | 15 | 0 | 3 |
| 3 two reviews | as is | 43 | 296K | 8 | 10 | 3 | 3 |
| | no reviews | 101 | 517K | 9 | 16 | 4 | 2 |
| | no reviews, no notes | 107 | 527K | 12 | 17 | 2 | 1 |

- **Sessions find the reviews and notes.** In the unchanged copy, questions 1 and 3 went to the reviews first and question 2 to the paper's note, as the guide's rules say. Nothing more needs to be said in a library's `AGENTS.md`.
- **A review is read whole.** Both sessions that used a review printed the entire file (107KB and 127KB, about 30K tokens each) and then searched it. A quarter to a third of a review is link definitions.
- **With reviews, the answer is cheaper and worse.** On question 1 the session read two reviews and no paper. Its eight wrong statements are not wrong numbers: the numbers are right and what is said about them is not. It headed a paragraph "append-only stores do worst" over a table where they score highest, stated a share of failures the paper does not give, and twice claimed the library has no paper that does something two of its papers do. On question 3 it made 10 of the 20 points, from five papers, where the other two made 16 and 17 from seven and eight.
- **With notes and no reviews, the answer is best or close to it.** On question 1 that session read the notes of the area, then opened the papers it needed: all 20 points, three slips (two pages and a count). It processed three times the tokens of the review-based answer.
- **For a question about one paper nothing differs**: the paper is short enough to read, and all three answers were free of errors. The note added four points.
- **Without either**, sessions grep the papers and read slices: the most tokens, and on question 1 the fewest points.
- One session tried to append its finding to a note's Q&A, as the guide asks, and reported that it had; editing was disabled, and the write, made through the shell, went to the copy.

## Conclusions

1. Notes are the part that helps an agent most. Every paper read for a review should leave one, and the 76 papers of the first two reviews that have none should get one.
2. A review is a map, not evidence. The guide's rule now says: use the review to find the papers and the shape of the answer, then open the note or the paper before stating a number or what a result means, and say when an answer rests on the review alone.
3. Reviews do pay for themselves in tokens (a third of the input on a synthesis question), so the rule keeps them as the starting point.
4. Limits: one session per cell, three questions, one model, and a judge that is the same model. Differences of one or two points or errors are within what a rerun would change; the pattern on questions 1 and 3 (fewer tokens, fewer points, more misreadings with reviews) is the same in both.
