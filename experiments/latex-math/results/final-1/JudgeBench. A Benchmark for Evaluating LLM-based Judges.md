---
title: "JudgeBench: A Benchmark for Evaluating LLM-based Judges"
authors: [Sijun Tan, Siyuan Zhuang, Kyle Montgomery, William Y. Tang, Alejandro Cuadron, et al.]
affiliations: [UC Berkeley, Washington University in St. Louis]
year: 2024
type: benchmark
topic: llm/evaluation/methods
links:
  - https://arxiv.org/abs/2410.12784
concepts: ["[[LLM-as-a-judge]]", "[[Reward model]]", "[[Position bias]]"]
papers: ["[[Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena]]", "[[LLM Evaluators Recognize and Favor Their Own Generations]]", "[[Reliability without Validity]]"]
tags: [gpt-4o, mmlu-pro, livebench, livecodebench, rewardbench, arena-hard]
read: false
analyzed: false
queued: false
revisit: false
reproduce: false
---

> [!abstract]
> A test of whether AI judges can spot a wrong answer that sounds as good as the right one.

## Overview

### Setting

Judging hard questions where one answer is correct and one is wrong, and both read smoothly. Think of a math solution with one bad step, or a clean-looking program that fails on an edge case. Success means picking the correct answer, not the one a reader would like more.

### Construction

**One generator for both answers.** Every pair comes from the same model (GPT-4o), so style and fluency cannot tell the two answers apart. Only correctness is left to decide.

**Keep the questions the model is unsure about.** The authors sample several answers per question and keep only questions where the model is sometimes right and sometimes wrong. A question it always gets right gives no wrong answer to pair; one it always gets wrong gives no right one. The mixed ones are where the model's own sense of right and wrong is shaky.

**Use checkable sources.** Knowledge questions come from MMLU-Pro, reasoning and maths from LiveBench, and coding from LiveCodeBench. A checker decides which answers are right. The result is 350 pairs, mostly knowledge and reasoning.

**Score consistency, not one verdict.** Each pair is judged twice with the two answers swapped. The judge only gets credit if both verdicts point to the correct answer. A judge that flips a coin therefore scores below half, because contradictory verdicts count as wrong.

### Findings

- **Judges are close to chance.** GPT-4o with a plain prompt reaches about 51%. Most fine-tuned judges do worse, and some score far below chance.
- **Reasoning models lead.** o1-class and o3-mini judges reach 73–81%, against about 57% for GPT-4o with its best prompt.
- **Reward models sit in the middle.** The strongest ones reach about 60%, the level of the best prompted model.
- **Judging is about as hard as solving.** A model's accuracy as judge roughly matches its accuracy as solver, so asking it to judge does not get it an easier task.
- **The generator's own judgment drops.** When the pairs are built from Claude's answers, Claude scores much worse as a judge. The questions that survived are the ones Claude itself finds unstable, so the benchmark is hardest for the model that made it.

### Validity

- **No human baseline.** The paper does not say how well people do on these pairs.
- **Small.** Coding has only 42 pairs, so one item moves that score by a few points.
- **Specific to its pairs.** The items are one model's unstable questions, so the numbers do not measure "judging" in general.
- **Other judge benchmarks look easier.** The paper reports that they are less discriminating; the spread across models is wider here.

### Novelty

- **vs [[Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena]]:** judges are scored against a checker, not against human preference. Human voters favour plausible or longer answers, so agreement with them is the wrong target on hard questions.
- **vs [[LLM Evaluators Recognize and Favor Their Own Generations]]:** the same model on both sides removes self-preference from the comparison. The paper's own generator-effect result is a selection effect, not self-favouritism, and the difference matters when reading it.
- **vs RewardBench:** the reward-model reasoning subsets there are close to saturated, while the same kind of model scores about 60% here.

### Concepts

- [[LLM-as-a-judge]]: a language model grades another model's answer, in place of a human.
- [[Reward model]]: a model trained to score responses, used to steer training. Here it is used as a judge.
- [[Position bias]]: a judge's verdict changes when the answers swap places. The paper's double-order scoring is built to catch it (not from the paper for the general term).

## Questions

- Why is agreement with a checker a better target for a judge than agreement with human votes?
- Why does using one generator for both answers help, and what does it cost?
- Why does Claude's judge score drop on pairs Claude generated?
- Where does judging a question split from solving it?

## Follow-ups

**Read**
- [[Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena]]: the human-agreement benchmark this paper argues against.
- [[LLM Evaluators Recognize and Favor Their Own Generations]]: the self-preference effect the single-generator design removes.
- [[Reliability without Validity]]: a later audit; judge rankings do not transfer across judge benchmarks.
- [[RewardBench]]: reward models on a related question, with saturated reasoning subsets.

**Try**
- Pick a few questions with answers you can check, have one model answer each several times, and see where its answers flip. Those flip points are the questions this benchmark keeps.
