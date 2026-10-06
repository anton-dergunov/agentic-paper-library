**No, not as a replacement for the question that matters: "is this answer better for this person?"** On that, LLM judges agree with people only weakly, and they err in one direction. They are a workable stand-in for narrower checks against a written criterion, and for ranking systems in aggregate.

I checked these numbers in the papers themselves; the pattern is that agreement rises as the judge has less to guess about what the person wants.

| What the judge decides | Paper | Agreement with people |
|---|---|---|
| Personalised vs generic answer, which is better (1–5) | Re-Centering Humans | Spearman 0.11–0.38; judges average 3.41–4.02 against 3.18 from humans ([p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15)) |
| Which of four models this participant prefers | PRISM-X | Kendall τ 0.22, top-1 40.1%; the participant's own consistency is 0.57 and 68.8% ([p. 16–17, Fig. 8](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=figure.8&page=16)) |
| Degree of personalisation in a dialogue (1–4) | PersonaLens | κ 0.520, against 0.780 for task completion and 0.750 between annotators ([p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=table.5&page=8)) |
| Over-personalisation score (0–1) | OP-Bench | Spearman 0.61–0.74 across eleven judges on 200 responses ([p. 14, Table 5](http://pdf.invalid/llm/personalization/benchmarks/OP-Bench.%20Benchmarking%20Over-Personalization%20for%20Memory-Augmented%20Personalized%20Conversational%20Agents.pdf?dest=table.5&page=14)) |
| Which answer better meets the asker's own rubric | LaMP-QA | 73% of pairs with a 32B judge, 48% with a 0.5B one; 58% when scoring without the rubric ([p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7)) |
| Whether an inferred preference matches the true one | CUPID | Krippendorff α 0.769 on 230 items ([p. 3](http://pdf.invalid/llm/personalization/benchmarks/CUPID.%20Evaluating%20Personalized%20and%20Contextualized%20Alignment%20of%20LLMs%20from%20Interactions.pdf?page=3)) |

**Why the holistic judgement fails**

- **Judges reward visible personalisation.** A reply that says "Given your interest in machine learning…" without adapting the content looks personalised to several judges; human raters show little sensitivity to such mentions ([Re-Centering, p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?page=8&search=mechanical%20attribute%20invocation)).
- **The error is inflation.** Humans rated 54.6% of personalised responses no better than the generic one, while every LLM judge scored them higher than humans did (same page and Table 6).
- **Judges mistake correct for personalised.** In Semantic Constraint Verification, four LLM judges score 0–19% on answers that are correct but generic ([p. 7, Table 3](http://pdf.invalid/llm/personalization/methods/Evaluating%20LLM%20Personalization%20via%20Semantic%20Constraint%20Verification.pdf?dest=table.3&page=7)). The labels there are constructed, not human, and the judges are small models.
- **Pairwise judging is order-dependent.** LaMP-QA's 32B judge changed its preferred response in 78% of cases when the order was swapped (p. 7, link above). PRISM-X's simulated raters put the first-listed model on top 33.8% of the time against 15.0% for the last ([p. 18](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?page=18)).
- **Training a judge does not fix it yet.** Reward models trained on the human ratings reach only about 0.3 Spearman ([Re-Centering, p. 9](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?page=9)).

**Where a judge is usable**

- **Aggregate ranking of systems.** PRISM-X's simulated raters recover model worth at r = 0.98–0.99, although the judgement-only variant swapped the top two models (p. 16–17, link above). That is fine for coarse comparisons, not for close ones.
- **Checking against an explicit criterion.** The asker's own rubric (LaMP-QA) or a preference checklist (CUPID) gives much higher agreement than asking for a holistic score.
- **A large judge.** In LaMP-QA, smaller judges both agree less and score higher (0.94 average at 0.5B against 0.44 at 32B).

**Caveats on the evidence**

- **The human reference is itself noisy.** Re-Centering uses three third-party raters, not the users themselves, on 80 items; they agree with each other at Spearman 0.325 and weighted κ 0.310 (p. 8). A judge at 0.38 is therefore not far below the raters' own agreement, but its inflation is still a real bias.
- **Only PRISM-X has the person being personalised for do the judging** (530 participants). Nothing in the library has users judge answers to their own requests over time, or tests a judge given that user's past ratings.
- **PersonaMem-v3 audits its data with LLM judges only**; its note records no human study of judge accuracy.

I tried to add this to the Q&A of `reviews/llm/personalization.md`, as the library conventions ask, but the file is read-only here, so nothing was changed. `paperlib check` also reports a large number of existing problems unrelated to this question.
