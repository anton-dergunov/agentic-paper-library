**Short answer:** read pages 4–6 (how the pairs are built and scored) and the ablation on pages 9–10. Everything else is either motivation or a results table you can look up when needed.

**Reading order**

1. **p. 4, Figure 2, and §3 "JudgeBench's pipeline."** This is the core idea: sample k answers per question from one strong model (GPT-4o), keep questions where the model is inconsistent (at least one right and one wrong answer), then pair a correct answer with an incorrect one. Using one generator for both sides removes style differences and self-preference across models.
2. **p. 5–6, "JudgeBench's datasets" and "Data Filtering and selection."** These give the four sources (MMLU-Pro for knowledge, LiveBench for reasoning and math, LiveCodeBench for coding) and the rule that drops responses where GPT-4o-mini and the automatic checker disagree on format. The final split is 154 / 98 / 56 / 42 (p. 6).
3. **p. 6, the start of §4: the scoring rule.** Each pair is judged twice with the order swapped, and a verdict counts only if the two trials agree on the right answer. Inconsistent or double-tie verdicts count as wrong, so a coin-flip judge scores below 50%. You need this to read any number in the paper correctly.
4. **p. 9–10, §4.4 ablation.** This is the main threat to validity. With Claude-3.5-Sonnet pairs, Claude's judge drops from 64.3% to 44.8%. The effect is a selection effect: the questions were kept because that model is unstable on them. Read it before you cite the 64.3→44.8 drop as evidence of self-preference, because the paper's own argument goes the other way.
5. **Appendix A.3 (p. 19) and A.5 (p. 19–20).** Read these if you care about the construction details: the balancing step and an example where the format checker and the LLM grader disagree.

**Skim or skip**

- **pp. 1–3** (abstract, intro, related work) give the motivation: crowd preference rewards plausible or longer answers, and the three-level hierarchy (instruction following, correctness, style). Read the abstract and the p. 2 figure if you want the framing.
- **Tables 1–3 (pp. 7–9)** hold the judge, model and reward-model numbers. Read them as needed.
- **Table 4 (p. 10)** is worth a look: judging roughly matches solving overall (GPT-4o 56.6% judge vs 54.6% solver). It is better than solving on math and worse on coding.
- **Appendix A.1 and A.2** (judge details and fine-tuned judge analysis) only matter if you want to reproduce a specific judge. **A.6** holds the prompts.

**Most useful overall:** the construction logic (p. 4–5), the scoring rule (p. 6), and the generator-bias ablation (p. 9–10). Together they tell you what JudgeBench measures and where its numbers can mislead. The existing agent note at `notes/JudgeBench. A Benchmark for Evaluating LLM-based Judges.md` already has a digest with these page references, so you can check my summary against it.
