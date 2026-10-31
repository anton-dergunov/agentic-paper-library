---
title: "JudgeBench: A Benchmark for Evaluating LLM-based Judges"
authors: [Sijun Tan, Siyuan Zhuang, Kyle Montgomery, William Y. Tang, Alejandro Cuadron, et al.]
affiliations: [UC Berkeley, Washington University in St. Louis]
year: 2024
type: benchmark
topic: llm/evaluation/methods
links:
  - https://arxiv.org/abs/2410.12784
  - https://github.com/ScalerLab/JudgeBench
concepts: ["[[LLM-as-a-judge]]", "[[Reward model]]", "[[Position bias]]"]
papers: ["[[Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena]]", "[[RewardBench]]", "[[LiveBench]]", "[[LLM Evaluators Recognize and Favor Their Own Generations]]"]
tags: [gpt-4o, o3-mini, mmlu-pro, livebench, livecodebench, reward-models, math, coding]
read: false
analyzed: false
queued: false
revisit: false
reproduce: false
---
> [!abstract]
> A test of whether an LLM judge can tell a right answer from a wrong one when both are equally fluent, which human-preference agreement cannot measure.

## Overview

### Setting

Judging answers to hard questions, where what counts is whether the answer is correct. Checking a proof or a code snippet takes real expertise, so a crowd worker under time pressure falls back on what is easy to see: the answer that reads more plausibly, or the longer one. The paper's point is that human preference is then the wrong target for a judge. Its example pair has the same confident prose, and only one answer is right.

### Construction

- **Start from hard datasets with an automatic checker.** Knowledge questions, reasoning and math, and coding, each with a ground-truth answer that a program can check.
- **Sample one strong model many times.** Keep only the questions where it is right in some samples and wrong in others.
- **Pair a correct with an incorrect answer from that same model.** Both are equally fluent and equally styled, so style cannot decide the pair.
- **Judge each pair twice, with the order swapped.** A judge only scores if both verdicts agree on the right answer, so a judge that guesses scores below half.

The idea behind the selection step: a question the model answers inconsistently is one it probably cannot judge either.

### Findings

- **Most judges are near chance.** Prompted GPT-4o is barely above a coin flip. Most fine-tuned judges do worse, and some do far worse.
- **Reasoning models lead.** They are clearly ahead of the non-reasoning models, by 10 to 25 points on the paper's table.
- **Judging is about as hard as solving.** A model's accuracy as a judge tracks its accuracy at answering the same questions.
- **Reward models sit in between.** The best ones match the best prompted judges, and a small reward model clearly beats its own base model used as a judge.

### Validity

- **No human baseline.** Nothing shows how well people do on these pairs.
- **Small.** 350 pairs, and the coding part has only 42, so each item moves the coding score a lot.
- **One generator per dataset.** The pairs are hardest for the model that generated them, so the absolute numbers are not "judge accuracy in general".

### Novelty

- **vs [[Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena]]:** those measure agreement with crowd preference; this measures agreement with ground truth.
- **vs [[RewardBench]]:** its reasoning subsets are close to saturated. Here, the same kind of model scores far lower.
- **vs [[LLM Evaluators Recognize and Favor Their Own Generations]]:** self-preference is what the single-generator design is meant to remove from the other judges' scores.
- **Broader trend (not from the paper):** judge audits are moving from "does it agree with people" to "is it right".

### Concepts

- [[LLM-as-a-judge]]: a model that scores other models' answers in place of human raters.
- [[Reward model]]: a judge trained to score responses, used to steer training.
- [[Position bias]]: a judge's verdict changes when the two answers swap places. The paper's double-order scoring is built to catch it.

## Questions

- Why does one generator remove self-preference for the other judges, yet make the pairs hardest for that generator?
- If judging is about as hard as solving, what can a judge check that a solver cannot?
- Does the selection step measure hard correctness, or just unstable questions?
- How much would a reference answer change the picture, and what does that imply for judges without one?

## Follow-ups

**Read**:
- [[Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena]]: the human-agreement standard this paper argues against.
- [[LLM Evaluators Recognize and Favor Their Own Generations]]: the self-preference effect the design is meant to isolate.
- [[Reliability without Validity]]: a later audit; judge rankings do not transfer between judge benchmarks.
- [[LiveBench]]: the source of the reasoning and math items.

**Try**:
- Take five questions you know the answer to. Write one right and one wrong answer, then ask a judge about each pair in both orders and count how often its verdicts agree.
