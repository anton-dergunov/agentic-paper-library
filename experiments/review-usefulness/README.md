# Experiment · do reviews and notes help an agent answer questions?

**Question.** Reviews and notes are written for the reader, and also so that a later agent session starts from them instead of re-reading papers. Does a fresh session find them? Does it answer better, faster or more cheaply with them?

**Status.** Measured twice. 5 Oct 2026: three questions, three copies of the library, one session each. A session finds and uses reviews and notes without being told beyond the library guide; with the guide's first rule ("start from the review") it answered a synthesis question from the review alone, at a third of the tokens and with more wrong statements. 6 Oct 2026, with the rewritten rule ("the review is a map, not evidence"), five questions and three sessions per cell: sessions search the review, then read notes and papers, and **their answers have about as many wrong statements as answers written without reviews**. They are not more complete: level on two questions, and narrower on the question the review covers best. They used a fifth fewer tokens over the three questions a review covers, a saving no larger than the run-to-run differences. A stronger rule (notes and papers first, the review only to find them) raised the cost by half for a gain within those differences, and was not adopted. **The rule stays as it is. Neither reviews nor notes made Opus's answers measurably better than reading the papers directly**; reviews are worth writing for the reader.

**Serves.** [`docs/design.md`](../../docs/design.md), and the "Start from the review" rule in [`guide/library-guide.md`](../../guide/library-guide.md).

## First run (5 Oct 2026)

### Method

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

### Results

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

### Conclusions

1. Notes are the part that helps an agent most. Every paper read for a review should leave one, and the 76 papers of the first two reviews that have none should get one.
2. A review is a map, not evidence. The guide's rule now says: use the review to find the papers and the shape of the answer, then open the note or the paper before stating a number or what a result means, and say when an answer rests on the review alone.
3. Reviews do pay for themselves in tokens (a third of the input on a synthesis question), so the rule keeps them as the starting point.
4. Limits: one session per cell, three questions, one model, and a judge that is the same model. Differences of one or two points or errors are within what a rerun would change; the pattern on questions 1 and 3 (fewer tokens, fewer points, more misreadings with reviews) is the same in both.

## Second run (6 Oct 2026): the rewritten rule

After the first run the guide's rule was rewritten: "Start from the review, then check the paper … The review is a map, not evidence … Before you state a number, or what a result means, read that paper's note or the paper at the cited page … Search a review for the part you need rather than reading it whole." The question for this run, fixed before the grades were seen: with that rule, is the answer from the unchanged copy on a level with the answer written without reviews, and still cheaper? On the questions a review covers (1, 3 and 4), the gap counts as closed when its points made and its wrong statements are within the range of the three sessions without reviews, and it counts as cheaper when its mean input tokens are at most 75% of theirs.

### Method

What changed from the first run:

- **Five questions.** Two were added: 4, "What kinds of agent memory systems are there, and how do they differ?", which the memory review answers by itself; and 5, "What do my papers say about prompt compression?", in a folder with no review and notes for 6 of its 20 papers, to see whether the rule sends a session looking for a review that is not there.
- **Three sessions per cell**, so that a difference can be set against the range of the repeats. The sessions of one question start together.
- **Copies are real and read-only** ([`copies.py`](copies.py)), built from the library at `d7dccd40` (2,200 papers, 5 reviews, 330 notes). In the first run one session wrote to a note through the shell. The copies without reviews or notes keep three passing mentions of "review" in the notes section of the guide.
- **Sonnet 5.5 as a second answerer**, once per question, in the unchanged copy and the copy without reviews.
- **A rule variant**, `asis-v2`: the unchanged copy with the rule replaced by [`rule-v2.md`](rule-v2.md) ("Answer from the notes and the papers; the review tells you which to open"), three sessions each on questions 1, 3 and 4. It was run after the first grades, because the rule under test did not pass.
- **Grading in two stages** ([`judge.py`](judge.py)), in the copy without reviews and notes. One Opus session per question pools up to 30 points from all the answers, the first run's included, and checks each in the paper; then one session per batch of up to five answers, shuffled, marks which points each answer makes and lists its wrong statements. The variant's answers were graded later against the same points. 150 of the 151 pooled points held. Judging took 23 sessions and $29 at API prices.
- **A second judge on question 1**: Gemini 3.1 Pro, without tools, given the pooled points and the full text of the papers the answers name.
- **Per session** ([`summarize.py`](summarize.py)): whether a review was printed whole or in part, the notes and papers named after the first look at a review, and attempts to write. These columns are read from shell commands and miss some idioms; what is said below about the Opus sessions in the unchanged copy and the variant was checked by eye in the event streams.

```bash
python3 copies.py <library> <scratch-dir>
python3 run.py results-2/streams --repeats 3 asis=<copy> noreviews=<copy> nonotes=<copy>
python3 run.py results-2/streams --model claude-sonnet-5-5 asis=<copy> noreviews=<copy>
python3 copies.py <library> <scratch-dir> asis-v2=asis
python3 copies.py --rule rule-v2.md <scratch-dir>/lib-asis-v2
python3 run.py results-2/streams --repeats 3 --questions q1,q3,q4 asis-v2=<scratch-dir>/lib-asis-v2
python3 summarize.py results-2/streams <library> results-2/answers > results-2/sessions.tsv
python3 judge.py results-2/judge <scratch-dir>/lib-nonotes results-2/answers results/answers@run1
python3 judge.py results-2/judge <scratch-dir>/lib-nonotes --judge gemini-3.1-pro-preview --only q1 results-2/answers results/answers@run1
python3 report.py results-2/sessions.tsv results-2/judge
```

Results: [`results-2/sessions.tsv`](results-2/sessions.tsv), the 64 answers in [`results-2/answers/`](results-2/answers/), and the pooled points and grades in [`results-2/judge/`](results-2/judge/). The event streams hold local paths and are not committed.

### Results

Opus 5.5 as answerer; the mean of three sessions, with their range.

| Question | Copy | Input tokens, K | Seconds | Points made | Wrong statements |
|---|---|---|---|---|---|
| 1 synthesis within one review (30 points) | as is | 632 (376–890) | 100 | 17.7 (16–20) | 1.7 (1–2) |
| | as is, rule variant | 992 (898–1,127) | 113 | 18.3 (15–21) | 1.3 (1–2) |
| | no reviews | 1,002 (877–1,229) | 134 | 17.0 (15–20) | 4.0 (4–4) |
| | no reviews, no notes | 1,017 (827–1,205) | 140 | 17.3 (16–19) | 0.7 (0–1) |
| 2 detail of one paper (29 points) | as is | 99 (71–115) | 24 | 22.0 (21–24) | 0.3 (0–1) |
| | no reviews | 112 (112–112) | 22 | 18.7 (18–20) | 0 |
| | no reviews, no notes | 80 (67–106) | 19 | 20.0 (20–20) | 0 |
| 3 across two reviews (31 points) | as is | 631 (543–761) | 122 | 14.3 (12–16) | 2.0 (0–3) |
| | as is, rule variant | 844 (702–974) | 121 | 16.7 (14–18) | 1.0 (0–3) |
| | no reviews | 602 (506–725) | 102 | 16.3 (11–21) | 0.3 (0–1) |
| | no reviews, no notes | 624 (378–930) | 107 | 18.0 (16–20) | 0.7 (0–1) |
| 4 what the review answers (30 points) | as is | 273 (239–317) | 52 | 11.3 (11–12) | 1.0 (0–3) |
| | as is, rule variant | 521 (452–564) | 90 | 13.7 (13–15) | 1.3 (1–2) |
| | no reviews | 370 (318–440) | 73 | 18.7 (17–21) | 2.0 (1–3) |
| | no reviews, no notes | 339 (294–410) | 73 | 15.7 (15–16) | 2.0 (1–3) |
| 5 no review for the area (30 points) | as is | 761 (687–860) | 110 | 21.3 (19–23) | 1.0 (1–1) |
| | no reviews | 1,069 (928–1,313) | 135 | 20.3 (18–24) | 2.0 (1–3) |
| | no reviews, no notes | 1,106 (907–1,208) | 149 | 20.0 (18–23) | 2.0 (2–2) |

Summed over the three questions a review covers (1, 3 and 4; 91 points):

| Copy | Input tokens, K | Points made | Wrong statements |
|---|---|---|---|
| as is | 1,536 | 43.3 | 4.7 |
| as is, rule variant | 2,357 | 48.7 | 3.7 |
| no reviews | 1,974 | 52.0 | 6.3 |
| no reviews, no notes | 1,980 | 51.0 | 3.3 |

- **The rule changed what sessions do.** No session answered from a review alone. On questions 1 and 3 each searched the review, printed 30 to 190 of its 870 lines, then read 5 to 15 notes and searched 5 to 7 papers for the numbers. On question 4 each read the review's prose nearly whole, in two or three ranged reads, and checked its numbers in about ten notes or in the papers. Seven of the nine answers to questions 1, 3 and 4 say which points rest on a review or a note.
- **By the test fixed in advance, the rule passes on question 1 only.** There the answers match those without reviews on points, have fewer wrong statements (1 to 2 against 4 in each of three sessions) and took 63% of the tokens. On question 3 the points are within range, two of three sessions have three wrong statements where the sessions without reviews have at most one, and the cost is the same. On question 4 the cost is 74%, the wrong statements are level, and the answers make 11 to 12 of the pooled points against 17 to 21.
- **What still goes wrong on question 3 is a sentence of the review restated.** The review says of two studies: "Neither has users judge answers to their own questions over time." Two sessions wrote that no paper in the library has users rate answers to their own requests, although one of the two studies, which both answers cite, does exactly that. It is the first run's failure in a smaller dose: right about the numbers, wrong about what the library lacks.
- **On question 4 the answer is the review's selection.** The three answers follow the review's taxonomy and its headline comparisons: they make three pooled points that no answer written without the review makes (store size, the long-history result, write-time loss), and none makes the points on MemoryOS, A-MEM and SeCom, or the finding of a twelve-system comparison that no architecture wins everywhere, which all three sessions with notes and no reviews make. The pool is built from all the answers, eight of eleven written without the review, so some of the gap is that a review-shaped answer is a different one. It is still narrower.
- **The rule variant buys little.** With notes and papers first, sessions read only the matching section of the review, then more notes and papers. Points rose on all three questions and wrong statements stayed level, with ranges that overlap the first rule's except for the points on question 4 (13 to 15), which remain below the answers without reviews. Tokens rose by 53%, to 19% above the copy that has no reviews at all.
- **Token differences of 30% occur without a cause in the library.** On question 5 no review exists, and the unchanged copy and the copy without reviews hold the same notes; the sessions in the first still used 29% fewer tokens, with ranges that do not overlap. The copies differ there only in the guide's review rule. Either its advice to search rather than read whole carries over to papers, or three sessions do not pin the cost down. So the fifth saved on questions 1, 3 and 4 is not evidence that reviews save tokens.
- **Without reviews or notes the answers are as good.** Sessions that could only search and read the papers made 51 of the 91 points with 3.3 wrong statements, level with every other copy, at the same cost as the copy with notes. On question 1 the copy with notes and no reviews had the most wrong statements.
- **No session went looking for a missing review.** On question 5 each session in the unchanged copy listed or searched `reviews/` in one or two calls, found nothing for the folder, and went to the notes and papers.
- **Sessions try to record what they found.** Two of three sessions on question 1 and all three on question 3, under either rule, tried to append a Q&A entry to the review, as the guide asks; the read-only copy refused. None tried on questions 4 and 5.

The first run's answers, graded again in the same pools: on question 1 the review-only answer makes 19 points with 5 wrong statements, the most of any answer to that question; on question 3 it makes 12 points with none wrong. The first run's judge had found 8 and 3 in the same two answers, so one answer's count moves by three between gradings.

**Sonnet 5.5 as the answerer**, one session per cell, beside the Opus means:

| Kind of question | Copy | Sonnet: tokens, K | Points | Wrong | Opus: tokens, K | Points | Wrong |
|---|---|---|---|---|---|---|---|
| Detail of one paper (2) | as is | 99 | 22 | 1 | 99 | 22.0 | 0.3 |
| | no reviews | 98 | 19 | 2 | 112 | 18.7 | 0 |
| Synthesis of an area (1) | as is | 145 | 14 | 3 | 632 | 17.7 | 1.7 |
| | no reviews | 336 | 18 | 2 | 1,002 | 17.0 | 4.0 |
| Synthesis of an area (4) | as is | 136 | 8 | 2 | 273 | 11.3 | 1.0 |
| | no reviews | 104 | 9 | 0 | 370 | 18.7 | 2.0 |
| Synthesis of an area (5) | as is | 249 | 12 | 1 | 761 | 21.3 | 1.0 |
| | no reviews | 218 | 8 | 1 | 1,069 | 20.3 | 2.0 |
| Across areas (3) | as is | 229 | 14 | 0 | 631 | 14.3 | 2.0 |
| | no reviews | 269 | 16 | 2 | 602 | 16.3 | 0.3 |

Sonnet matches Opus on a detail of one paper, with one or two wrong statements where Opus has none, and on the question across areas. On a synthesis of an area it reads a fifth to a half of what Opus reads and makes fewer points: about half as many on questions 4 and 5. On question 1 in the unchanged copy it answered from three searches of the review and opened no note or paper.

**The second judge.** Gemini 3.1 Pro found 1 wrong statement in the 14 answers to question 1 where Opus found 35, and counted somewhat more points for the answers without reviews (20.3 against 17.0). A judge that cannot search the library can say which points an answer makes; it does not find the errors.

### Conclusions

1. **The rule stays as rewritten after the first run.** It ended the failure it was written for: sessions check notes and papers, and wrong statements are level with the other copies. It does not pass the test on questions 3 and 4, and the stronger wording does not either, at half again the cost.
2. **A review does not make an agent's answer better.** With it, answers were as accurate, no more complete, and on the question the review covers best, narrower. Reviews are for the reader. For an agent they are a way in to an area, and the guide's rule already treats them so.
3. **Notes did not help measurably either.** Answers from the papers alone were level on points, wrong statements and tokens. The case for notes is the reading they record once (see [`reading-models`](../reading-models/README.md)), not better answers to these questions.
4. **Opus answers questions about papers.** Sonnet is enough for a detail of one paper and makes about half the points on a synthesis of an area, at a third of the tokens.
5. **Limits.** Three sessions per cell: the range of points in a cell is up to 10, and tokens differed by 30% on a question where the copies hold the same material. Five questions, in three areas of one library. The pooled points favour what most answers say, and most were written without reviews. The judge is the answerer's model, and its count of wrong statements in one answer moved by 3 between two gradings. The rule variant ran a day later than the sessions it is compared with, and alone.
