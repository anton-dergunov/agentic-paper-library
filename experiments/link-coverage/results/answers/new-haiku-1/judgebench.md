**Short version:** Read pp. 4–6 for the construction and the scoring rule. Skim the rest, and use the appendix only for the filtering and correctness checks.

**How it's built, in one pass.** Take a hard dataset that has ground truth and an automatic checker. Sample k responses per question from one strong model (GPT-4o). Keep only questions where at least one sample is right and at least one is wrong. Pair a correct response with an incorrect one. Since both come from the same model, style and length are matched, which removes the self-preference confound. Each pair is judged twice with the order swapped, and a judge only scores if both verdicts agree on the correct answer.

**What to read, in order**

1. **p. 2, Figure 1** — the three-principle hierarchy (instruction following, then factual/logical correctness, then style). Its examples show what JudgeBench tests and what it doesn't.
2. **p. 4, Figure 2 and §3** — the pipeline. This is the core idea, and the reason the pairs are hard.
3. **pp. 5–6, §3 "datasets" and "filtering"** — the four sources (MMLU-Pro, LiveBench, LiveCodeBench), and why GPT-4o-mini plus the automatic checker are used to drop format-only failures.
4. **p. 6, §4** — the two-trial aggregation rule. You need this to read any number in the paper. Under it, a coin-flip judge scores well below 50%.
5. **pp. 19–21, Appendix A.3 and A.5** — the exact sampling counts and the correctness check. A.3 also has the knowledge-set augmentation (Table 8), which tests whether 154 pairs is enough.

**Most useful results**

- **Table 1 (p. 7)** — prompted, fine-tuned and multi-agent judges. Most are near chance.
- **Table 2 (p. 7)** — the same prompt with different models. Reasoning models lead, so this is the table that says "judging needs reasoning".
- **Table 4 and Figure 4 (p. 10)** — judging vs. solving, and the Claude-generated ablation. These show the benchmark is hardest for the model that generated it, which is a selection effect, not self-preference.
- **Appendix A.4 (p. 19)** — the length check, showing correct and incorrect responses are the same length (562 vs 561 tokens).

Skip related work, the judge-detail appendix (A.1) and the prompt appendix (A.6) unless you need to reproduce a judge.

**A paper inconsistency to know about.** The main text (p. 6) gives 56 math pairs and a total of 350. Appendix A.3 (p. 19) says 46 math pairs came from GPT-4o. With 154 + 98 + 46 + 42, that sums to 340, not 350. The existing note (`notes/JudgeBench. A Benchmark for Evaluating LLM-based Judges.md`) repeats the p. 6 figure of 56. Treat the math count as unresolved until the source code or a corrected version confirms it.
