I'm fetching the exact page links for the sections I'm about to recommend.

The paper is 10 pages of body text plus appendices. To see how the benchmark is built, you only need about 3 pages. These are based on the library note for the paper. I checked the figure and table locations in the PDF, but I didn't re-read the prose itself.

## To see how it's built (about 3 pages)

1. **Pipeline figure** ([p. 4, Figure 2](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=4&rect=107,83,505,325)). Read this first. It shows the whole construction in one picture.
   - Start with hard questions that have ground truth and an automatic checker.
   - Sample several answers per question from one model, GPT-4o.
   - Keep only questions where at least one answer is right and one is wrong.
   - Pair a right answer with a wrong one.
2. **The construction text, pp. 4–6**. This covers three things:
   - **Why one generator:** using one model for both sides of a pair removes style differences and self-preference.
   - **Sources and filtering:** the questions come from MMLU-Pro, LiveBench and LiveCodeBench. Pairs where the automatic checker and GPT-4o-mini disagree are dropped.
   - **Final size and scoring (p. 6):** 350 pairs (154 knowledge, 98 reasoning, 56 math, 42 coding). Each pair is judged twice with the order swapped. A pair counts as correct only if both verdicts are right, or one is right and one is a tie. A coin-flip judge therefore scores below 50%.
3. **Motivation, pp. 1–2** (skim, about 5 minutes). It argues that agreement with crowd preference is the wrong target for hard questions. [Figure 1, p. 2](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=2&rect=108,83,505,310) compares JudgeBench with earlier judge benchmarks.

Skip the related-work section and the appendix at first. The appendix mostly holds prompts and per-category breakdowns.

## Most useful overall

- **[Table 2, p. 7](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=7&rect=120,395,492,618).** Models used as judges with the Arena-Hard prompt. Reasoning models lead by 10–25 points: o3-mini (high) scores 80.9% and GPT-4o 56.6%. This is the main practical finding.
- **[Table 1, p. 7](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=7&rect=114,86,498,335).** Most fine-tuned judges (PandaLM, JudgeLM, Auto-J, Prometheus 2) score 13–40%, below the random-guess figure the paper uses. Only the Skywork critics reach the mid-50s. If you use or build fine-tuned judges, this table matters most.
- **[Table 3, p. 8](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=8&rect=125,86,487,179).** Reward models score 59–64%, about the same as Claude-3.5-Sonnet as a judge.
- **[Figure 3, p. 9](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=9&rect=105,79,516,203).** JudgeBench is harder than MT-Bench, LLMEval, FairEval and LLMBar, and it separates models more widely.
- **[Table 4, p. 10](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=10&rect=127,86,485,227).** Judging a pair is about as hard as solving the problem. The exception is coding, where judging is much worse than solving.
- **[Figure 4, p. 10](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=10&rect=108,342,505,517).** This is the main caveat. Claude's judge accuracy drops from 64.3% to 44.8% on pairs Claude generated itself. The pairs are hardest for the model that produced them, because questions were kept for being unstable for that generator. This is a selection effect, not the usual self-preference bias.

## Limits to keep in mind

- **No human baseline:** the paper reports none.
- **Small coding set:** with 42 coding pairs, one item is about 2.4 points.
- **Not a general accuracy:** the pairs are the generator's unstable questions, so the scores aren't "judge accuracy in general".

If you want one rule: read the pipeline figure, then pp. 5–6, then Table 2 and Figure 4. That covers how it's built, the headline result and the main caveat.
