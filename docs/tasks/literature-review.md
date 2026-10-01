# Task: a literature review of every area

Write one review per area with the `literature-review` skill (`.claude/skills/literature-review/`),
which also defines the format. A review covers a top-level area, or a subarea of `llm/`.
The order follows Anton's priorities.

Any session can pick up the next scope: `/literature-review <scope>`. Reading is split into
batches whose results are kept in `reviews/.work/<scope>/`, so an area can be read across
several sessions or by several agents; `scripts/review-status.py <scope>` shows how far it
got. After each review, update its line below.

Status: `todo` · `reading` (some batches done) · `written` · `checked` (Anton has read it and
the format corrections are in `format.md`).

When every line is `checked`: delete this file, and in `docs/proposal.md` move the
literature review to "Done".

## Pilot

The first review sets the format. Anton reads it and corrects it before the next one starts.

- [ ] `llm/memory` (70): revised after Anton's first read (kinds-of-systems section added); format corrections are in format.md

## Primary areas

- [ ] `llm/personalization` (71): written
- [ ] `llm/evaluation` (109): todo
- [ ] `llm/post-training` (110): todo
- [ ] `search-and-ranking` (127): todo
- [ ] `recommender-systems` (97): todo
- [ ] `experimentation-and-metrics` (71): todo

## Systems and the rest of `llm/`

- [ ] `ml-systems` (74): todo
- [ ] `llm/context` (20): todo
- [ ] `llm/uncertainty-and-hallucination` (24): todo
- [ ] `llm/safety-and-privacy` (48): todo
- [ ] `llm/behaviour` (24): todo
- [ ] `llm/agents` (48): todo
- [ ] `llm/retrieval-augmented` (28): todo
- [ ] `llm/reasoning` (35): todo
- [ ] `llm/prompting-and-in-context` (28): todo
- [ ] `llm/pretraining` (35): todo
- [ ] `llm/architecture` (62): todo
- [ ] `llm/foundation-models` (39): todo
- [ ] `llm/efficiency` (19): todo
- [ ] `llm/routing` (16): todo
- [ ] `llm/text-analytics` (12): todo

## Other areas

- [ ] `data-centric-ml` (79): todo
- [ ] `deep-learning` (185): todo
- [ ] `representation-learning` (76): todo
- [ ] `nlp` (87): todo
- [ ] `graphs` (57): todo
- [ ] `interpretability` (78): todo
- [ ] `vision-and-multimodal` (112): todo
- [ ] `generative-models` (49): todo
- [ ] `ml-foundations` (77): todo
- [ ] `trustworthy-ml` (62): todo
- [ ] `reinforcement-learning` (74): todo
- [ ] `robotics-and-embodied` (21): todo
- [ ] `computer-systems` (28): todo
- [ ] `ai-and-society` (19): todo
- [ ] `research-practice` (27): todo

`curiosities` (2 papers) gets no review.

## Separately: conversion fixes

Reading flags broken conversions into `catalog/conversion-issues.yaml`. Fix them in their own
pass, not while writing reviews: `scripts/reconvert.py <paper.md>` first, then by hand,
marked `<!-- hand-edited -->`.
