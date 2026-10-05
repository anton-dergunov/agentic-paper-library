# Task: does the adjusted review rule fix answers written from reviews?

A follow-up to [`experiments/review-usefulness`](../../experiments/review-usefulness/README.md).
Run it in a fresh session; everything needed is below and in that folder.

## State on 5 Oct 2026, 20:15: paused on the weekly usage limit

Stopped at 97% of the seven-day allowance (resets Sat 10 Oct, 23:00). Resume after that.

Done, all in `experiments/review-usefulness/`:

- The apparatus has every change listed under Method: `questions.txt` (q4, q5), `copies.py`
  (real read-only copies, `--rule` for a variant), `run.py` (`--repeats`, `--questions`, one
  question at a time, resumable), `summarize.py` (review whole/part, notes and papers after
  the review, write attempts), `judge.py` (pool, then batches of five; `--judge` for a
  second model), `report.py` (the table).
- All 55 answer sessions: Opus, three copies, five questions, three repeats; Sonnet, `asis`
  and `noreviews`, once per question. Built from the library at `d7dccd40`.
  `results-2/sessions.tsv`, `results-2/answers/`, event streams in `results-2/streams/`
  (ignored by git).
- Judged with Opus: q1 and q2, pooled with the first run's answers (`results-2/judge/`).
  Gemini 3.1 Pro as second judge on q1 (`judge-q1-gemini-3.1-pro-preview.json`).

Left to do:

1. Rebuild the judge's copy (the scratch copies are gone):
   `python3 copies.py ~/papers <scratch> nonotes`.
2. Judge q3, q4, q5 (about 3 points of the weekly allowance and 20 of the five-hour one
   per question): `python3 judge.py results-2/judge <scratch>/lib-nonotes results-2/answers results/answers@run1`.
   It skips q1 and q2.
3. `python3 report.py results-2/sessions.tsv results-2/judge`, then apply the decision rule:
   on q1, q3, q4 the gap is closed if `asis` is within the repeat-to-repeat range of
   `noreviews` on points made and on wrong statements; cheaper if its mean input tokens
   are at most 75% of `noreviews`. If not closed, try a wording below in a copy built with
   `copies.py ... asis-v2=asis` and `--rule`, three repeats on q1, q3, q4.
4. Everything under "When it is done".

What q1 and q2 show so far (Opus judge; mean and range of three sessions):

| Question | Copy | Input tokens, K | Points made, of 30 | Wrong statements |
|---|---|---|---|---|
| 1 synthesis | as is | 632 (376–890) | 17.7 (16–20) | 1.7 (1–2) |
| | no reviews | 1,002 (877–1,229) | 17.0 (15–20) | 4.0 (4–4) |
| | no reviews, no notes | 1,017 (827–1,205) | 17.3 (16–19) | 0.7 (0–1) |
| 2 one paper | as is | 99 (71–115) | 22.0 (21–24) | 0.3 (0–1) |
| | no reviews | 112 (112–112) | 18.7 (18–20) | 0 |
| | no reviews, no notes | 80 (67–106) | 20.0 (20–20) | 0 |

- With the new rule no "as is" session read a review whole: each searched it, then read
  notes and papers (on q1, 8 to 15 notes and 5 to 7 papers). On q1 it made as many points
  as the copy without reviews, with fewer wrong statements and 63% of the tokens.
- The first run's "as is" answer to q1, regraded in the same pool: 19 points, 5 wrong
  statements.
- Sonnet on q1: 14 points and 3 wrong statements as is (145K tokens), 18 and 2 without
  reviews (336K).
- Gemini without tools found one wrong statement in the 14 answers to q1 where Opus found
  35: a judge that cannot search the library agrees on points and misses errors.
- Two of three "as is" sessions on q1, and all three on q3, tried to append a Q&A entry to
  the review, as the guide asks; the read-only copy refused.
- On q5 (no review for the area) each "as is" session touched `reviews/` in one call.

## What the first run found (5 Oct 2026)

Three questions were each asked once in three copies of the author's library: as it is
(reviews and notes), without reviews, and without reviews or notes. An Opus judge checked
the answers against the papers.

| Question | Copy | Input tokens | Points made, of 20 | Wrong statements | Rank |
|---|---|---|---|---|---|
| 1 synthesis within one review | as is | 292K | 17 | 8 | 3 |
| | no reviews | 932K | 20 | 3 | 1 |
| | no reviews, no notes | 1,092K | 15 | 5 | 2 |
| 2 detail of one paper | as is | 111K | 16 | 0 | 2 |
| | no reviews | 110K | 19 | 0 | 1 |
| | no reviews, no notes | 103K | 15 | 0 | 3 |
| 3 across two reviews | as is | 296K | 10 | 3 | 3 |
| | no reviews | 517K | 16 | 4 | 2 |
| | no reviews, no notes | 527K | 17 | 2 | 1 |

With reviews, the session read the review whole, opened no paper, and answered: a third of
the tokens, right numbers, wrong statements about what they mean, and fewer papers covered.
The copy with notes and no reviews gave the best answer to questions 1 and 2.

That run used the old rule in the library guide: "Start from the review … Open papers only
for what the review doesn't settle." The rule was rewritten the same day, after the run, and
has not been tested:

> **Start from the review, then check the paper.** … The review is a map, not evidence. Use
> it to find the papers and the shape of the answer. Before you state a number, or what a
> result means, read that paper's note or the paper at the cited page … Search a review for
> the part you need rather than reading it whole.

It is in [`guide/library-guide.md`](../../guide/library-guide.md), and `paperlib build-index`
renders it into a library's `.claude/library-guide.md`.

## The question

With the new rule, is the "as is" answer at least as accurate and complete as the
notes-only answer, while still cheaper? Whatever wins becomes the rule that ships. Three
outcomes are possible:

- **The new rule closes the gap** (errors and points on a level with notes-only, fewer
  tokens): keep it.
- **It closes the gap and costs as much as notes-only**: the review adds nothing for an
  agent. Then say so in the guide: reviews are for the reader, and an agent starts from
  the notes of the area (the folder index lists the papers) and uses the review only to
  find which papers matter.
- **It does not close the gap**: the session still answers from the review. Try a stronger
  wording (candidates below) and run again.

## Method

Reuse the apparatus in `experiments/review-usefulness/`:

1. **Copies.** `python3 copies.py <library> <scratch-dir>` builds `lib-asis`,
   `lib-noreviews` and `lib-nonotes` from the library as it is now, so `lib-asis` carries
   the new rule. Check its output line: a copy without reviews or notes should not mention
   them in its instructions. The paper files in a copy are hard links to the library's:
   delete the copies when done, and check `git status` in the library afterwards.
2. **Sessions.** `python3 run.py <out-dir> asis=<copy> noreviews=<copy> nonotes=<copy>`
   asks every question in `questions.txt` once per copy with `claude -p` (read and shell
   only). For a rule variant, build another `lib-asis`, edit the rule in its
   `.claude/library-guide.md`, and add it as a fourth condition (`asis-v2=<copy>`).
3. **Measure and grade.** `summarize.py` then `judge.py`, as in the README. Keep the first
   run's results: write the new ones to `results-2/`, and add a section to the README
   rather than replacing the old numbers.

Changes to make to the method, each a weakness of the first run:

- **Repeat each cell three times.** One session per cell cannot separate a real difference
  from run-to-run variation; differences of one or two points or errors meant nothing.
  `run.py` skips a run whose output exists, so it needs a repeat number in the file name.
- **Add two questions**, so the result does not rest on three. For example one where the
  review should be enough ("what kinds of agent memory systems are there, and how do they
  differ?") and one outside any review ("what do my papers say about prompt compression?",
  in `llm/context`, which has notes for 6 of 20 papers and no review): the second checks
  that the rule does not send a session looking for a review that is not there.
- **Start the sessions of one question together, not all conditions in order.** In the
  first run the sessions launched first paid to cache the shared prompt prefix that the
  others read, so API price was not comparable. Compare input tokens processed and seconds.
- **Judge with pooled points from all answers of a question, including the first run's**,
  so that scores are comparable between the two runs. The judge is Opus, the same model as
  the answerer; a second judge (Sonnet, or a Gemini model, see the reading-models
  experiment for how to call one) on one question would show whether the ranking depends
  on the judge.
- **Add Sonnet as an answerer, in two conditions.** Which model should answer questions
  about papers is not measured. Run `python3 run.py <out-dir> --model claude-sonnet-5-5
  asis=<copy> noreviews=<copy>` once per question (about 3M tokens), and judge its answers
  in the same pool as the Opus ones. Report it by kind of question: a detail of one paper,
  a synthesis of an area, a question across areas. The result goes in the "Which model"
  table of the engine's `README.md`, where questions are marked as not measured.
- **Disable writes fully.** One session appended to a note through the shell although
  `Edit` and `Write` were disallowed. Allow only read-only shell commands, or make the
  copies' notes and reviews read-only.

Also record, per "as is" session, what the rule is meant to change: whether it read the
review whole or searched it, how many notes and papers it opened after the review, and
whether the answer says which points rest on the review alone.

## Rule wordings to try if the first does not work

- Put the check first: "Answer from the notes and the papers. The review tells you which
  papers to open."
- Make it a procedure: "1. Search the review for the question's terms. 2. List the papers
  it names. 3. Read each one's note. 4. Open the paper for every number you will quote."
- Name the failure: "A review compresses each finding into a sentence. Do not restate
  that sentence as the paper's result without reading the paper's own."

## When it is done

- Add the results to `experiments/review-usefulness/README.md` (a second section, with the
  status line updated) and its row in `experiments/README.md`.
- Put the winning wording in `guide/library-guide.md`, run `paperlib build-index` in the
  library, and update the "A review is a map, not evidence" entry in `docs/design.md`.
- If reviews turn out to add nothing for an agent, also change the `literature-review`
  skill's description ("for agents to start from") and the first paragraph of its
  `SKILL.md`.
- Delete this file.

Budget: the first run cost about 4M tokens of input across nine sessions and about $3 of
judging at API prices. Five questions, three or four conditions and three repeats is
roughly six times that, so spread it over two usage windows; every session is independent.
