**No, not for the question that matters most: "is this answer better for this person?"** On that question LLM judges agree only weakly with people, and they err in one direction, towards calling an answer personalised. A judge does work for narrower checks, where the user's preference has been written down as a rubric or checklist.

An example of the failure: a reply opens with "Given your interest in machine learning…" and then gives the generic answer. Open-weight judges score that higher; human raters do not, and the paper notes such replies can feel robotic or intrusive to users ([Re-Centering Humans, p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.2&page=8)).

| What the judge is asked | Agreement with people | Human ceiling | Source |
|---|---|---|---|
| Is the personalised answer better than the generic one (1–5)? | Spearman 0.11–0.38 | 0.325 between raters | [Re-Centering Humans, p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15) |
| Rank four models as this user would, given their profile | Kendall τ 0.22 | 0.57 (a person's own consistency) | [PRISM-X, p. 17, Fig. 8](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=figure.8&page=17) |
| Personalisation score of a task dialogue | κ 0.52 (0.78 for task completion) | Fleiss κ 0.75 | [PersonaLens, p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=table.5&page=8) |
| Does the answer cover the asker's own rubric aspects? | picks the human-preferred answer in 73% of cases | κ 0.726 between raters | [LaMP-QA, p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7) |
| Does an inferred preference match the true one (checklist)? | Krippendorff α 0.769 | not given | [CUPID, p. 3](http://pdf.invalid/llm/personalization/benchmarks/CUPID.%20Evaluating%20Personalized%20and%20Contextualized%20Alignment%20of%20LLMs%20from%20Interactions.pdf?page=3) |

What the numbers mean:

- **The error is a bias, not noise.** Every judge in Re-Centering Humans rates personalised answers above the human mean (3.41–4.02 against 3.18 on a 1–5 scale), so averaging over more items does not fix it.
- **Humans often see no gain at all.** In the same study raters judged 54.6% of personalised responses no better than the generic one ([p. 8, Fig. 5](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=figure.5&page=8)). A judge-only evaluation would have reported an improvement.
- **Aggregate rankings can survive while individual verdicts do not.** In PRISM-X, a GPT-4o judge given each participant's profile recovers the overall model ranking (r = 0.98–0.99) but not the individual's choice: it picks their favourite of four models 40.1% of the time, against 68.8% for the person's own consistency ([p. 17](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=figure.8&page=17)).
- **The human ceiling is itself low.** Re-Centering's three raters agree with each other at only Spearman 0.325, so its best judges (0.36–0.38) are about as good as one more third-party rater. That rests on 80 items and 367 ratings.
- **Trained reward models do no better:** about 0.3 Spearman with human ratings ([p. 9](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.3&page=9)).

What raises agreement, on the library's evidence:

- **Make the preference a checkable criterion.** LaMP-QA scores against aspects extracted from the asker's own post and reaches 73% agreement, against 58% for direct scoring of the same answers.
- **Use a large judge.** In LaMP-QA agreement rises from 48% to 73% between a 0.5B and a 32B judge, and the small judge inflates scores (0.94 against 0.44 on average).
- **Avoid uncalibrated pairwise prompts.** LaMP-QA's pairwise judge changes its verdict in 78% of cases when the two answers are swapped.
- **Check that the judge can tell "correct but generic" apart.** In Semantic Constraint Verification, 8B-class judges get 0–19% on that class ([p. 7, Table 3](http://pdf.invalid/llm/personalization/methods/Evaluating%20LLM%20Personalization%20via%20Semantic%20Constraint%20Verification.pdf?dest=table.3&page=7)). That is a synthetic setup with small judges, and the paper concedes the strongest LLM judges still beat its entailment model at identifying the personalised class.

Two gaps in the evidence:

- **No paper here has users rate answers to their own requests.** The human raters are third parties reading a profile, so even the "human" side is a proxy; both Re-Centering and LaMP-QA say the user is the only reliable judge.
- **The most direct paper is not in the library.** "Can LLM be a Personalized Judge?" (Dong et al., 2024) is in `catalog/skipped.yaml` as too narrow. Say if you want the skip reversed and the paper added.

I tried to append this to the Q&A of `reviews/llm/personalization.md`, but the file is read-only in this checkout, so nothing was written and there is nothing to commit.
