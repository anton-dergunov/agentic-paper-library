**No as a replacement, yes as a narrower instrument.** A judge can check whether an answer met a criterion someone wrote down, but it cannot tell you whether a real person finds the personalised answer better, and it errs in the flattering direction.

## The intuition

Take a user profile that says "interested in machine learning" and a request for a sourdough recipe. One answer opens with "Given your interest in ML, think of fermentation as gradient descent…", the other just gives the recipe. A judge asked "which is more personalised?" sees the profile being used and prefers the first. A person often finds it presumptuous. The judge is measuring whether personalisation is visible, not whether it helped.

## The one direct test

*Re-Centering Humans* shows generic and personalised answers side by side to three human raters and five LLM judges, on a 1–5 scale where 3 means no preference.

- **Judges inflate.** Humans average 3.18; every judge is higher, from 3.41 to 4.02 ([p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15)).
- **Humans mostly see no gain.** They rate 54.6% of personalised answers no better than the generic one ([p. 8, Fig. 5](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=figure.5&page=8)).
- **Correlation with humans is low.** Spearman with the human average is 0.11–0.38.
- **Correlation does not pick a safe judge.** The best-correlated judge (Llama-3.3-70B, 0.376) is also the most inflated (4.02).
- **The bias is the explicit mention.** Open-weight judges reward answers that name the attribute. Humans are indifferent (gap 0.03), GPT-5.4 nearly so (−0.07), and Claude Sonnet 4.6 over-penalises it (−0.39) ([p. 8, Figs. 6–7](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=figure.6&page=8)).
- **Training on the human ratings doesn't fix it.** Reward models trained on them reach only about 0.3 ([p. 9](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.3&page=9)).

## Weakly supported: the low correlation

The three human raters agree with each other only at Spearman 0.325 ([p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?page=8&search=inter-annotator%20agreement)). By my calculation (not the paper's), a fourth human would then correlate with the average of the others at about 0.40. The best judges, at 0.36–0.38, are close to that.

So on 80 items and 367 ratings, correlation cannot separate a good judge from one more human. The firm evidence is the inflation and the mention bias. The raters are also third parties reading a profile, not the users themselves.

## Where judges do hold up

Agreement is much higher when the judge checks an answer against something stated:

| Paper | What the judge checks | Agreement with humans |
|---|---|---|
| LaMP-QA ([p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7)) | the asker's own rubric, aspect by aspect | picks the human-preferred answer in 73% of pairs; 58% when scoring directly |
| PersonaLens ([p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=table.5&page=8)) | task completion; personalisation | κ 0.78; κ 0.52 (humans among themselves 0.75) |
| OP-Bench ([p. 14, Table 5](http://pdf.invalid/llm/personalization/benchmarks/OP-Bench.%20Benchmarking%20Over-Personalization%20for%20Memory-Augmented%20Personalized%20Conversational%20Agents.pdf?dest=table.5&page=14)) | irrelevant use of memory, sycophancy | ρ about 0.62–0.71 across judge models |

Two warnings from LaMP-QA (same page):

- **Pairwise judging is order-dependent.** Its pairwise judge changes its verdict in 78% of cases when the two answers are swapped.
- **Small judges inflate.** A 0.5B judge agrees with humans 48% of the time while scoring answers 0.94 on average; the 32B judge scores them 0.44.

## Ranking systems is easier than judging items

PRISM-X uses simulated users rather than judges, but shows the same split. Simulated twins of 530 real participants recover the aggregate ranking of four models (r = 0.98–0.99). On individual choices they reach Kendall τ 0.22 and 0.11, against 0.57 for a person's own consistency ([p. 16–17, Fig. 8](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=figure.8&page=16)). This figure is from the library's note on the paper; I did not reopen the paper.

## In practice

- **Use a judge** to order systems that differ clearly, or to check a written rubric or a stated preference, with a large model and absolute rather than pairwise scoring.
- **Keep humans** for the claim "personalisation improved the answer", and for the size of any gain.
- **Validate on inflation and mention bias**, not only on correlation.

No paper in the library has users rate answers to their own questions, so the real target is untested.

I tried to add this to the Q&A of `reviews/llm/personalization.md`, but the file is read-only in this copy of the library, so nothing was changed and there is nothing to commit.
