I'll read the paper's text layer and any existing agent note on it.

The note covers the main text. The construction details that matter most are likely in the appendix, so I'll locate those sections.

**Short answer:** read §3 (pp. 4–6) closely, then the appendix bits on filtering and the correctness check (A.3, A.5, pp. 19–20). For results, the single most useful table is Table 4 (p. 10), which shows judging tracks solving. Skip most of the rest on a first pass.

**How it is built, in order:**

1. **Principle (pp. 1–2).** Judges should apply a hierarchy: follow the instruction, then be factually and logically correct, then match style. JudgeBench tests only the second level, because on hard questions crowd annotators can't reliably check correctness and drift toward plausible or longer answers.
2. **Pipeline (pp. 4–5, Fig. 2 on p. 4).** Take a hard dataset with ground-truth answers and an automatic checker. Sample *k* responses per question from one strong model (GPT-4o). Keep only questions where at least one response is correct and at least one is wrong. Pair a correct response with an incorrect one. The core idea: a question the model answers inconsistently is one it also can't reliably tell right from wrong.
3. **Sources and sizes (p. 5–6).** MMLU-Pro for knowledge, LiveBench for reasoning and math, LiveCodeBench for coding. The result is 350 pairs: 154 knowledge, 98 reasoning, 56 math, 42 coding.
4. **Filtering (p. 5–6, A.3 on p. 19, A.5 on pp. 19–20).** A GPT-4o-mini grader and the regex checker must agree, or the response is dropped. The paper shows the disagreements are formatting errors, not wrong answers. Random subsampling balances the subsets.
5. **Scoring (p. 6).** Each pair is judged twice with the order swapped. A judge gets credit only if the two verdicts agree on the correct answer. Inconsistent verdicts or double ties count as wrong, so a coin-flip judge scores below 50%.

**Most useful parts, in order:**

- **Generator-bias ablation (p. 10, Fig. 4; counts in A.3, p. 19).** Claude-3.5-Sonnet drops from 64.3% on GPT-4o pairs to 44.8% on its own pairs. The paper reads this as Claude producing harder pairs, not as self-preference. Use it to judge how much the benchmark depends on its generator.
- **Judge-versus-solver ablation (Table 4, p. 10).** Judge accuracy closely tracks solver accuracy overall. It diverges sharply by category: judges beat solvers on math and lose on coding. The coding gap is the clearest sign that verifying code is harder than the math case.
- **Scoring rule (p. 6).** Needed to read any number in the paper, because it sets the chance level.
- **Length check (A.4, p. 19).** Correct and incorrect responses are about the same length (562 vs 561 tokens), so length bias is controlled.
- **Results (Tables 1–3, pp. 7–8).** Read these for the findings: prompted, fine-tuned and reward models sit mostly between 35% and 65%. Reasoning models lead, with o3-mini at 80.86% at high effort. Skim them unless you need specific numbers.

**Optional, if you plan to rerun it:** A.2 (pp. 17–18) explains why fine-tuned judges underperform, and A.6 (from p. 21) has the prompts.

**Caveats to keep in mind:**

- All 350 pairs come from one generator, GPT-4o, so absolute numbers are not "judge accuracy in general". The paper's own evidence is the Claude ablation above.
- There is no human baseline.
- Sample sizes are small. One coding item is about 2.4 points; the 270-pair Claude ablation has only 31 coding pairs.
- The paper's authors say the numbers are not the same as crowd-agreement benchmarks. The paper's argument is that the single-generator design removes style and self-preference bias for every judge other than the generator.

I checked these points against the text layer. The existing note at `notes/JudgeBench. A Benchmark for Evaluating LLM-based Judges.md` matches the paper on the key numbers. Nothing in it needed correcting.
