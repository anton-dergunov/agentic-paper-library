The construction is on pages 4–6 and the checks on pages 10 and 19. Read those and you can rebuild the pipeline; the results tables are for later.

**Read these, in order (about 8 pages)**

1. **[p. 4, §3 and Figure 2](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=4)**: the whole pipeline. Take a dataset with ground truth and a checker, sample k responses from one strong model, keep questions where the samples disagree, and pair a correct response with an incorrect one.
2. **[p. 5](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=5)**: why one generator and not several (style differences and self-preference), the three source datasets (MMLU-Pro, LiveBench, LiveCodeBench), and the GPT-4o-mini filter that drops responses where it disagrees with the regex checker.
3. **[p. 6](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=6)**: the final counts and the scoring rule. Each pair is judged in both orders, and only a consistent correct verdict counts. Every accuracy number depends on this rule.
4. **[p. 10, §4.4 and Figure 4](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=10)**: the only check on the construction. It regenerates pairs with Claude-3.5-Sonnet and shows the benchmark is hardest for its generator. Table 4 on the same page shows judging tracks solving.

**Read for detail on the construction (p. 19, Appendix A.3–A.5)**

- A.3 gives the sampling: 1,400 MMLU-Pro questions reduced to 154 knowledge pairs, 11 per discipline. It also gives the Claude-generated split sizes and a check that a larger knowledge set ranks models the same way.
- A.4 checks length bias: correct and incorrect responses average 562 and 561 tokens.
- A.5 describes the regex and GPT-4o-mini correctness checks.

**Skip for the construction:** related work (pp. 2–3), the judge descriptions (pp. 6–7), the result tables for judges and reward models (pp. 7–9, unless you want the numbers), and the prompts in the appendix (pp. 21–26).

**Most useful overall**

- p. 4 (the idea), p. 6 (the scoring rule), and Table 4 on p. 10. These three give you the design, how to read a score, and the main finding that judging is about as hard as solving.
- Table 2 on p. 7 for model comparisons.

**One inconsistency to know about.** Page 6 gives 56 math pairs, which sums to the 350 total. Appendix A.3 on p. 19 says 46 math pairs came from GPT-4o. With 46, the total is 340, not 350. I haven't resolved which is right. The paper doesn't say, so check the GitHub repo before you use the per-category counts.
