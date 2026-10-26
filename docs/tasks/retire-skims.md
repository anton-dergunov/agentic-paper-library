# Task: retire the last "(skimmed)" marks

The first literature reviews read most papers as skims (abstract, introduction, conclusion and headline results), because their reading agents paid again for every paper already in their context. Since `paperlib read` reads every paper in full, one request each, no new skim is written, and on 13 Oct 2026 the concept was removed from the engine: the guide, the reading prompt and the note format have no `read:` line, `paperlib read` has no `--skims`, `review-status` counts no skims, and the literature-review skill and its format have no "(skimmed)" mark.

## Done

- The 152 skim notes of the author's library (llm/evaluation 70, llm/post-training 61, llm/foundation-models 21) were read in full, and no note says `read: skim`.
- Those three reviews were updated on 13 Oct 2026. Every sentence that cites a formerly skimmed paper was checked against the full note, and against the paper where the note did not hold the number. Most claims held. Fifteen were narrowed or qualified, two of them also in an "In practice" section; each review's `## Updates` lists its own.

## Left

The llm/memory and llm/personalization reviews still carry 76 "(skimmed)" marks (41 and 35). Their papers have no note at all: the marks were inferred on 4 Oct 2026 from the missing notes, because the reading batches of those two reviews were not kept. The 152 above did not count them.

1. `paperlib read llm/memory llm/personalization` writes the missing notes (`paperlib review-status <scope>` lists them: 42 and 35 papers). At about $0.36 a paper with Opus that is about $28.
2. For each of the two reviews, check what it says about each marked paper against the new note, correct what does not hold, and remove the marks. The skill no longer knows the mark, so say this when asking for `/literature-review update <scope>`. The same update adds what these reviews lack under the current format.
3. `grep -c '(skimmed):' reviews/llm/*.md` gives 0 for every review. The two reviews' `## Updates` lines of 4 Oct 2026 keep the word, as history.

Done when no review marks a paper as skimmed; then delete this file.

## How the check was done

For a review of 60–70 formerly skimmed papers, reading every note in full next to the review is about 100K tokens. Cheaper and as thorough: a script that prints, for each such paper, the review's sentences that cite it, each followed by the note's lines for the pages that sentence cites, and flags the numbers that the note does not hold. The flagged numbers are then looked up in the paper's text. What this found was mostly of three kinds: a margin quoted from the best case only, a comparison whose two sides also differed in something else, and a claim taken from a paper's prose that its own table does not support.
