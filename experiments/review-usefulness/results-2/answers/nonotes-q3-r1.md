**Not on the question that matters most.** A judge can replace raters for checking whether a response honours a preference that has been written down. It cannot yet replace them for deciding whether personalising made the response better for the user: there it scores too high and tracks humans only weakly.

A concrete example of the gap: a response that opens "Given your interest in machine learning…" and then says what it would have said anyway looks personalised to a judge, but reads as robotic or intrusive to a person.

## Where the judge fails: "is this better for the user?"

**Re-Centering Humans in LLM Personalization** (2026) is the one paper here that tests this head-on. Humans and five LLM judges compared a generic and a personalised response on a 1–5 scale, where 3 is neutral.

- **Inflation:** humans average 3.18, the judges 3.41–4.02. Humans rated 54.6% of personalised responses as no better than the generic one ([p. 8, §6.2](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.2&page=8)).
- **Weak tracking:** Spearman correlation with the human mean is 0.11–0.38 across judges ([p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15)).
- **A judge inherits its own generation habits:** models that mention user attributes explicitly when generating also reward such mentions when judging (r = 0.90 across five models). Humans are indifferent to explicit mentions (Δ = 0.03), while Claude Sonnet 4.6 over-penalises them (Δ = −0.39).
- **Training does not fix it:** reward models trained on the human ratings also reach only about 0.3 ([p. 9, §6.3](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.3&page=9)).
- **The same pattern appears one stage earlier:** on which user attributes are relevant to a prompt, LLMs agree with each other (κ = 0.60) more than with humans (κ = 0.30), and mark 40–60% relevant where humans mark about 20% ([p. 6, §5.2](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.5.2&page=6)).

**PRISM-X** (2026) asks the stricter version: can an LLM stand in for the specific user? GPT-4o role-played each of 530 real participants and ranked the same four models.

- **Aggregate ranking is recovered, individuals are not:** Kendall τ with the real person is 0.22 and top-1 accuracy 40.1%, against a human self-consistency ceiling of 0.57 and 68.8% ([p. 17, §4.1](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=subsection.4.1&page=17)).
- **Position bias is amplified:** the simulator ranks the first-shown response best 33.8% of the time and the last 15.0%; humans are near the 25% chance level ([p. 18, §4.2](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=subsection.4.2&page=18)).

## Where the judge works: "does this meet the stated criteria?"

| Paper | What the judge checks | Agreement with humans |
|---|---|---|
| Personalized RewardBench | Which of two responses follows a user-specific rubric | 97.5% directional agreement on 2,830 pairs ([p. 17, §B.4](http://pdf.invalid/llm/post-training/preference-learning/Personalized%20RewardBench.%20Evaluating%20Reward%20Models%20with%20Human%20Aligned%20Personalization.pdf?dest=subsection.B.4&page=17)) |
| LaMP-QA | Whether an answer covers the aspects the user asked for in their own post | 73% with aspect rubrics, 58% with direct scoring ([p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7&search=aspect-based%20evaluation%20method%20selects)) |
| PersonaLens | Dialogue-level scores on a fixed guideline | κ = 0.78 for task completion, but 0.52 for personalisation ([p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=table.5&page=8)) |

Two details in these numbers matter:

- **Personalisation is the weakest dimension even here.** In PersonaLens it has the lowest judge–human agreement of the six metrics, while the annotators agree with each other at 0.75.
- **Judge size changes both agreement and score level.** In LaMP-QA a 0.5B judge agrees with humans 48% of the time and gives a mean score of 0.94; a 32B judge reaches 73% and gives 0.44. Small judges inflate.

## What is weakly supported

- **The headline negative result is small.** Stage 3 of Re-Centering Humans rests on 80 items, 367 ratings and three annotators ([p. 15, Appendix G](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=appendix.G&page=15)).
- **Its raters are third parties, not the users.** They agree with each other at only ρ = 0.33, so a judge at 0.36 against their mean is not clearly worse than one more annotator. The inflation and the explicit-mention bias are the firmer findings.
- **Its text and table disagree.** The text says open-weight judges correlate very poorly, but Table 6 gives the highest correlation to Llama-3.3-70B (0.376), which is also the most inflated judge (4.02).
- **PRISM-X tests a naive simulator.** It is GPT-4o with a persona prompt, and the authors say it is not the ceiling of what simulation can do.
- **The 97.5% is an easy case.** The Personalized RewardBench pairs were constructed to follow or violate the rubric, so the judge only has to detect a built-in difference.

Many personalisation benchmarks in the library use an LLM judge with no human validation of scores at all. Beyond Recall, for example, states that human annotation was feasible but not done (p. 23).

## What this means in practice

- **Use a judge for rubric adherence**, with per-user criteria and a large model.
- **Keep humans, ideally the actual users, for the question of benefit.** Use judges there for ranking systems in aggregate, not for absolute scores or per-user verdicts.
- **Randomise response order** in any pairwise judging.

For mixing a small human sample with many judge labels, the library has Prediction-Powered Inference and Trust or Escalate in `llm/evaluation/methods/`; I did not reread them for this answer.
