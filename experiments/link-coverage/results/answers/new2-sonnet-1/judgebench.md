I've read the paper's structure and the library note, so here is the reading order.

## To understand how it's built (about 10 minutes)

1. **Intro argument, pp. 1–2.** This explains why correctness labels replace crowd preference. Read only the first page and a half.
2. **[Figure 2, p. 4](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=4&rect=107,83,505,325).** The whole pipeline in one picture. Read it first.
3. **Section 3, "JudgeBench", pp. 4–6.** This is the construction, and it is the core of the paper:
   - Take hard questions that have an automatic checker (MMLU-Pro, LiveBench, LiveCodeBench).
   - Sample k answers per question from one model (GPT-4o).
   - Keep only questions where at least one sample is right and one is wrong, then pair a right answer with a wrong one.
   - Using one generator removes style differences and cross-model self-preference.
   - The result is 350 pairs: 154 knowledge, 98 reasoning, 56 math, 42 coding.
4. **Scoring rule, start of Section 4, p. 6.** Each pair is judged twice with the order swapped. Inconsistent verdicts and double ties count as wrong, so a coin-flip judge scores *below* 50%. Skim this, but keep it in mind when reading any number.
5. **Appendix A.3 (dataset filtering, p. 19)** is optional. It covers the format-error filtering that was dropped from the main text.

## Most useful overall

- **[Table 1, p. 7](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=7&rect=114,86,498,335) and [Table 2, p. 7](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=7&rect=120,395,492,618)** are the main results.
  - Fine-tuned judges mostly land at 13–40%, below a coin flip under this scoring.
  - Reasoning models lead: o3-mini (high) 80.9%, o1-preview 75.4%.
  - GPT-4o with the vanilla prompt gets 50.9%.
- **[Table 4, p. 10](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=10&rect=127,86,485,227)** shows that judging ability is roughly solving ability. It is the most transferable insight.
- **[Figure 4, p. 10](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=10&rect=108,342,505,517)** shows the generator dependence: Claude-3.5-Sonnet's judge accuracy falls from 64.3% to 44.8% on pairs Claude generated. This is a selection effect, since the questions were kept because the generator is unstable on them. It is not "judges favour their own outputs".
- **[Figure 3, p. 9](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=9&rect=105,79,516,203)** compares JudgeBench with other judge benchmarks. The best of the five models scores 64% here, which is lower than on the others.

## Skip

- Related work (p. 3) and the references.
- Appendix A.1–A.2 (judge details and fine-tuned judge analysis), unless you want to know why PandaLM and JudgeLM fail.
- Appendix A.6 (prompts), unless you plan to reproduce the evaluation.

## Caveats

- There is no human baseline.
- Coding has only 42 pairs, so one item is worth about 2.4 points.
- These are the generator's unstable questions, so the numbers are not "judge accuracy in general".

The library note `notes/JudgeBench. A Benchmark for Evaluating LLM-based Judges.md` has the full digest, with related papers (MT-Bench, RewardBench, Arena-Hard).
