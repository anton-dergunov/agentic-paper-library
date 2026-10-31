**Short answer:** read pages 4–6 (the pipeline and the dataset) and pages 19–20 (filtering and correctness checks). The rest is mostly results you can skim.

**What to read, in order**

1. **p. 4, Figure 2.** The whole pipeline on one page: sample k responses from a strong model, grade each for correctness, keep only questions with at least one correct and one incorrect response, then pair them.
2. **p. 5, "JudgeBench's pipeline" and the paragraph after it.** The key design choice. Mixing responses from several models gives easy pairs, style differences, and self-preference bias. Sampling k answers from one model fixes all three, at the cost of making the pairs hard mainly for that model.
3. **p. 5–6, "JudgeBench's datasets" and "Data Filtering".** The four sources: MMLU-Pro (Knowledge), LiveBench reasoning and math, and LiveCodeBench (Coding). Also the GPT-4o-mini check that drops responses where the regex grader and the LLM disagree on correctness, because format errors would otherwise create a shortcut.
4. **p. 6, "Evaluating LLM-based judges" protocol.** Each pair is judged twice with the order swapped. Only consistent verdicts count, and ties in both trials count as wrong. Read this before comparing any numbers.
5. **p. 19, A.3–A.5.** The actual counts per split (154/98/56/42 in the GPT-4o split), the augmentation check (the knowledge set grows from 154 to 770 pairs with the same rankings), and the length check (562 vs 561 tokens, so length bias is controlled).

**Most useful overall**

- **p. 9, Table 4.** Judge accuracy tracks solver accuracy closely. This is the main evidence that the benchmark measures the model's ability to solve the problem, not something else.
- **p. 9–10, Figure 4.** The bias check. Claude-3.5-Sonnet drops from 64.3% on GPT-4o pairs to 44.8% on its own pairs, so the generator-model bias is real but bounded. Use it to decide how far to trust per-judge rankings.
- **p. 8, the "Reward models" paragraph.** Reward models do as well as much larger LLM judges, which matters if you use judges as reward models.

**Skip for now:** the related work (pp. 2–4 beyond the pipeline), the reference list, A.1 and A.2 (judge details and fine-tuned judge failure modes, pp. 16–17), and A.6 (prompts, p. 21). Read A.2 only if you want to know why fine-tuned judges score below chance.

**What I did not check:** I read pp. 1–10 and the appendix sections A.3–A.5 but not the other pages. I did not find how the coding responses are executed against tests; the text only says LiveCodeBench provides a verification algorithm. If that matters for you, look at pp. 5 and 21 or the code repository.

No files changed, so there is no commit to suggest.
