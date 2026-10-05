**Not for the question that matters most.** An LLM judge can check whether a response *followed a stated preference*, but it cannot yet stand in for humans on whether the personalised response is *actually better for the user*. The library has one paper that tests this directly and several that bear on it.

## The direct test

*Re-Centering Humans in LLM Personalization* (June 2026) shows humans and five LLM judges the same pair of responses, one generic and one personalised with human-approved attributes. Both rate their preference from 1 (generic) to 5 (personalised).

| Judge | Mean rating | Spearman ρ with humans |
|---|---|---|
| Human | 3.18 | – |
| Claude Sonnet 4.6 | 3.43 | 0.36 |
| GPT-5.4 | 3.52 | 0.31 |
| Llama-3.3-70B | 4.02 | 0.38 |
| Qwen3.5-27B | 3.49 | 0.18 |
| Gemma-4-31B | 3.41 | 0.11 |

([p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15))

- **Judges inflate the benefit.** Humans found 54.6% of personalised responses no better than the generic one, while every judge rated personalisation higher than humans did ([p. 8, §6.2](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.2&page=8)).
- **Judges reward visible personalisation.** Open-weight judges score a response higher when it names the attribute ("Given your interest in machine learning…"); humans are indifferent (Δ = 0.03). Claude over-corrects the other way (Δ = −0.39).
- **A judge's taste mirrors its own writing.** Models that mention attributes more often as generators also reward mentions more as judges (ρ = 0.90, though with only five models).
- **The same gap appears one step earlier.** On which user attributes are relevant to a prompt, LLMs agree with each other (κ = 0.60) more than with humans (κ = 0.30), and mark 40–60% relevant against the humans' 20% ([p. 6, §5.2](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.5.2&page=6)).
- **Training did not fix it.** Reward models trained on the human ratings also reach only about ρ = 0.3 ([p. 9, §6.3](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.3&page=9)).

## Where judges do agree with humans

Agreement is high when the judge checks a response against a written criterion rather than deciding what the user would like:

| Paper | Task given to the judge | Agreement with humans |
|---|---|---|
| [PrefEval, p. 43, A.17](http://pdf.invalid/llm/personalization/benchmarks/Do%20LLMs%20Recognize%20Your%20Preferences.%20Evaluating%20Personalized%20Preference%20Following%20in%20LLMs.pdf?page=43) | Did the response violate a stated preference? | 86–98% |
| [Personalized RewardBench, p. 17, B.4](http://pdf.invalid/llm/post-training/preference-learning/Personalized%20RewardBench.%20Evaluating%20Reward%20Models%20with%20Human%20Aligned%20Personalization.pdf?dest=subsection.B.4&page=17) | Which of two responses meets the user's rubric? | 97.5% on direction |
| [LaMP-QA, p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7) | Does the response cover the aspects the user asked for? | 73%; direct 0–1 scoring only 58% |
| [PersonaLens, p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=table.5&page=8) | Rate personalisation in a dialogue | κ = 0.52, against 0.78 for task completion |

Personalisation is the weakest dimension in PersonaLens even with a rubric. RewardBench's 97.5% is on pairs built to differ clearly on the rubric, so it is an easy case.

## Aggregate versus individual

*PRISM-X* has GPT-4o simulate each of 497 real participants and rank four models as that person would ([p. 17, §4.1](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=subsubsection.4.1&page=17)).

- **Across the population it works.** The simulated model ranking correlates r = 0.99 with the human one, though one simulation condition swapped the top two models.
- **Per person it does not.** Kendall τ is 0.22 against a human self-consistency ceiling of 0.57, and it picks the person's favourite 40% of the time against 69%.
- **Position bias is much stronger.** One simulator ranked the first-listed model best 34% of the time and the last 15%; humans were near 25% for each ([p. 18](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?page=18)). LaMP-QA saw its pairwise judge flip in 78% of cases when the order was reversed.

So a judge can tell you which system is better on average, but not whether a given user was well served, which is what personalisation is about.

## What is weakly supported

- **The human reference is itself noisy.** In Re-Centering Humans the three annotators agree with each other at only ρ = 0.33, about the same as the best judges' correlation with the human mean. The low correlations may partly reflect a noisy target; the score inflation is the more solid finding.
- **The raters are third parties.** No paper here except PRISM-X asks the actual user, and both Re-Centering Humans and LaMP-QA say the user is the only real authority.
- **The sample is small.** Stage 3 has 80 items and 367 ratings.
- **The text and table disagree.** The paper says open-weight judges correlate very poorly, but Table 6 gives Llama-3.3-70B the highest ρ (0.38) alongside the worst inflation. I have not checked the PDF to see which is right.

## In practice

Use a judge for constraint-style checks with an explicit rubric, and avoid pairwise prompts unless you run both orders. For "is the personalised response better", keep a human-rated sample, ideally from the users themselves, and use it to calibrate the judge. The library has two general methods for that: [Prediction-Powered Inference](http://pdf.invalid/llm/evaluation/methods/Prediction-Powered%20Inference.pdf?page=1), which corrects many judge labels with a few human ones, and [Trust or Escalate](http://pdf.invalid/llm/evaluation/methods/Trust%20or%20Escalate.%20LLM%20Judges%20with%20Provable%20Guarantees%20for%20Human%20Agreement.pdf?page=1), which sends low-confidence cases to humans. I did not re-read either for this answer.
