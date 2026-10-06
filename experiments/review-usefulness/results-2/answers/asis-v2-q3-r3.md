**No, not for the question that matters ("is this answer better for this person"), but yes for narrow checks against a criterion written down in advance.** The library's evidence is consistent on this; every number below was checked in the paper itself.

Agreement with humans falls as the judgement moves from "was this explicit criterion met" to "would this person prefer it":

| What the judge decides | Judge vs humans | Human vs human | Source |
|---|---|---|---|
| Whether a stated preference was followed (binary checks) | 0.92–0.97 agreement | not reported | [PrefEval, p. 43, Table 18](http://pdf.invalid/llm/personalization/benchmarks/Do%20LLMs%20Recognize%20Your%20Preferences.%20Evaluating%20Personalized%20Preference%20Following%20in%20LLMs.pdf?dest=table.18&page=43) |
| Which of two answers better covers the asker's own stated needs, aspect by aspect | 73% (direct scoring: 58%) | κ 0.726 | [LaMP-QA, p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7&search=Auto-Rater) |
| Over-personalisation score, 0–1 | ρ 0.68 (GPT-4o-mini), 0.74 for the best judge | not reported | [OP-Bench, p. 13–14, Table 5](http://pdf.invalid/llm/personalization/benchmarks/OP-Bench.%20Benchmarking%20Over-Personalization%20for%20Memory-Augmented%20Personalized%20Conversational%20Agents.pdf?dest=table.5&page=14) |
| "Personalisation" rating of a task dialogue | κ 0.52 (task completion: 0.78) | Fleiss κ 0.75 | [PersonaLens, p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=table.5&page=8) |
| Personalised vs generic answer, 1–5 preference | ρ 0.11–0.38 | ρ 0.325, κ 0.310 | [Re-Centering Humans, p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15) |
| A specific person's ranking of four models (GPT-4o given their profile) | τ 0.22, top-1 40.1% | self-consistency τ 0.57, top-1 68.8% | [PRISM-X, p. 16–17, Fig. 8](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=figure.8&page=16) |

A concrete example of the two ends: "the user said they are vegetarian; does the recipe contain meat?" is a rubric check, and judges do it well. "Would this user prefer the answer that mentions their ML background?" requires the judge to stand in for the user, and it cannot.

- **Judges inflate.** In Re-Centering Humans, every LLM judge rates personalised answers higher than humans do (3.41–4.02 against 3.18), and humans find 54.6% of personalised answers no better than generic ones ([p. 8, Fig. 5](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=figure.5&page=8)).
- **Judges reward visible personalisation.** Several open-weight judges score answers higher for phrases like "Given your interest in machine learning…", while humans are indifferent to them (rating gap 0.03). Claude Sonnet 4.6 errs the other way and penalises such mentions (gap −0.39) ([p. 8, Figs 6–7](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=figure.6&page=8)).
- **Small judges inflate more.** In LaMP-QA a 0.5B judge gives a mean score of 0.94 at 48% agreement with humans; the 32B judge gives 0.44 at 73% (p. 7, Fig. 4).
- **Pairwise judging is fragile.** LaMP-QA's pairwise judge changes its verdict in 78% of cases when the two answers are swapped (p. 7). PRISM-X's simulator ranks the first-shown model best 44.9% of the time against 7.2% for the last (p. 18).
- **Aggregate is fine, individual is not.** PRISM-X's simulated users recover the population ranking of models (r = 0.98–0.99) while missing individuals (p. 16–17). So a judge can answer "which system is better on average" and still fail at "was this right for this user".

**Human raters are not the gold standard either.**
- Re-Centering's three raters are third parties, not the users, and agree with each other at only κ 0.310 on 80 items and 367 ratings (p. 8, p. 15). The best judge's ρ of 0.376 is therefore close to the human ceiling in that study, so it shows the task is noisy as much as that judges are bad.
- Trained reward models reach only about 0.3 Spearman on the same data (p. 9).
- LaMP-QA (p. 10) and Re-Centering (p. 9) both say the right evaluator is the user themself. Only PRISM-X has that, with 530 participants rating answers to their own conversations.

**What this means in practice:** use a judge when the user's need can be written as explicit, hidden-from-the-generator criteria (the LaMP-QA and PrefEval designs), use a large judge, and score per criterion rather than pairwise. For any claim that personalisation improved the experience, you still need the users themselves, and the library has no study where users judge answers to their own questions over time.

One correction to the review: its line that LLM judges call generic answers personalised (Semantic Constraint Verification) rests on 8B-class judges. The paper's own limitations concede its entailment model is slightly below the best LLM judges at identifying personalised answers (p. 9). I did not re-read its Table 3.

I tried to append this to the `## Q&A` of `reviews/llm/personalization.md`, as the conventions ask, but the file is write-protected in this copy, so nothing was changed and there is nothing to commit.
