**The construction in one paragraph:** JudgeBench takes hard datasets that have automatic correctness checkers (MMLU-Pro, LiveBench, LiveCodeBench). For each question it samples k answers from GPT-4o and grades them. It keeps only questions where the k answers are mixed, with at least one correct and one wrong, then pairs a correct answer with a wrong one. A judge sees each pair twice, with the order swapped. Labels come from the checker, not from people. Because one model writes both answers, style differences and self-preference are mostly removed. The wrong answers are subtle, so the pairs are hard to judge. (Sec. 3, p. 4–5)

**What to read, in order**

1. **Fig. 2, p. 4.** The pipeline on one page.
2. **Sec. 3, p. 4–5.** Why the pipeline is built this way. The straightforward alternative (mix answers from several LLMs) is rejected for three reasons: wrong answers are too easy to spot, style gives the answer away, and self-enhancement bias. This is the core design argument.
3. **Sec. 3, "Data Filtering and selection", p. 5–6.** The sources (MMLU-Pro, LiveBench, LiveCodeBench) and the GPT-4o-mini check. The regex checker was rejecting correct answers over formatting, so the authors cross-checked it with a second LLM and dropped disagreements. That is the most practical detail for anyone building something similar. Counts are on p. 6.
4. **A.3, p. 19.** How the subsets were sampled (100 questions per discipline, 1,400 in total) and the counts of pairs per category, with Table 8 showing an augmented 770-pair knowledge set keeps the same rankings.
5. **A.5, p. 19–20, and A.4, p. 19.** Correctness checking and length bias. The example of disagreement is short and makes the checker problem concrete.
6. **Sec. 4 intro, p. 6.** Position-bias handling and the aggregation rule. Only A>B-consistent verdicts count as correct. The rule is easy to get wrong when reimplementing.
7. **Sec. 4.4, p. 9–10 (Table 4 and Fig. 4).** The two ablations. Table 4 asks whether judging is as hard as solving. Fig. 4 asks whether the GPT-4o generator biases the results. This is what shows how far the numbers can be trusted.

**Skip for a quick understanding:** the related-work prose, the references, A.6 (prompts, reference only), and most of A.1–A.2 (judge details; A.2 on why fine-tuned judges underperform is useful only if you care about that question).

**Most useful overall:** Sec. 3 with Fig. 2, then the two Sec. 4.4 ablations. Table 1 and Table 2 give the headline numbers (GPT-4o at 56.6% overall, o3-mini high at 80.9%). Read them as results on this one construction.

**Things to check while reading:**

- **Counts disagree.** The main text (p. 6) gives 350 pairs with 56 math. A.3 (p. 19) gives 46 math pairs from GPT-4o, and its figures sum to 340. The text I read doesn't reconcile this.
- **k is never given** in the text I read. The sample count is the one parameter needed to reproduce the filtering.
- **The pairs are conditioned on the generator.** Every question was kept because GPT-4o got it inconsistently, so GPT-4o judges are disadvantaged. Fig. 4 (p. 10) shows the effect: Claude-3.5-Sonnet falls from 64.3% on GPT-4o pairs to 44.8% on its own pairs. The paper reads this as a stronger model producing harder pairs, but that is a reading, not a control.
- **Small set.** 350 pairs, with 42 coding pairs, so per-category differences of a few points are noise.

Source: the text layer of [JudgeBench, p. 1](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=4). I read the text layer, not the PDF pages, and there is no note or review for this paper yet. The rectangles for the figures and tables are not in these links; say if you want them and I'll run `paperlib locate` for the key ones.
