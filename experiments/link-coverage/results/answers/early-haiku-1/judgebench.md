**How it's built, in one idea:** JudgeBench takes existing hard datasets that have automatic correctness checkers (MMLU-Pro, LiveBench, LiveCodeBench). For each question, GPT-4o samples k responses and grades them. Questions where all k responses are right or all are wrong are dropped. From the rest, each pair is one correct and one incorrect response, so the label is objective. Both responses come from the same model, which keeps style and length similar. Each pair is judged twice with the order swapped, and the verdict is aggregated. The final set is 350 pairs: 154 Knowledge, 98 Reasoning, 56 Math, 42 Coding.

**Read these, in order (about 8 pages):**

1. **Section 3, the pipeline:** [p. 4, Section 3](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=4) through [p. 5](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=5). This is the core. It explains why you sample from one model (style control and no self-enhancement bias) and why you keep only mixed-outcome questions. Figure 2 on p. 4 is the diagram.
2. **Filtering:** [p. 5](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=5) to [p. 6](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=6). A second checker (GPT-4o-mini) rejects responses that fail the regex check only because of formatting.
3. **Two-trial aggregation rule:** [p. 6](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=6), Section 4. Ties and inconsistent verdicts count as wrong.
4. **Appendix A.3 and A.5:** [p. 19](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=19), with the prompt on [p. 20](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=20). The exact subset sizes, the 1400 → 347/233 sampling funnel, and how labels were checked.

**Most useful beyond the build:**

- **Section 4.4 ablations, [p. 9](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=9) to [p. 10](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=10).** Table 4 (judge vs solver) and Figure 4 (GPT-4o pairs vs Claude pairs) show the pipeline's bias. Claude-3.5-Sonnet falls from 64.3% on GPT-4o pairs to 44.8% on its own pairs.
- **Table 1, [p. 7](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=7), and Table 2, same page.** These are the main results: even GPT-4o is near chance with the vanilla prompt (50.86%).
- **Appendix A.4, [p. 19](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=19).** Length bias check: correct and incorrect responses average 562 and 561 tokens.

**Skip or skim:** the related work on [pp. 2–4](http://pdf.invalid/llm/evaluation/methods/JudgeBench.%20A%20Benchmark%20for%20Evaluating%20LLM-based%20Judges.pdf?page=3), the judge details in A.1, the prompts in A.6, and the fine-tuned-judge analysis in A.2.

**Caveats to keep in mind (my reading, not claims the paper makes):**

- **Labels rest on automated checks.** I found no human audit of the response pairs. The only manual inspection mentioned is of checker disagreements, which were format errors (p. 6). The paper's own ~98–99% checker agreement (p. 20) is the main quality evidence.
- **Small samples.** With 350 pairs, the standard error on accuracy is about 2.7 points (my calculation: √(0.5·0.5/350)). Coding has only 42 pairs. Differences of 2–3 points between judges are not meaningful on their own.
- **GPT-4o is disadvantaged.** The pairs come from GPT-4o, which is why its judge scores lowest of the strong models on its own pairs in the ablation.

The library also has a note on this paper at `notes/JudgeBench. A Benchmark for Evaluating LLM-based Judges.md`. I did not read it, and it is the place to check for any Q&A already settled.
