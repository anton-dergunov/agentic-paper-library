**Not for the question that matters most.** A judge can replace raters for checking whether a response *obeyed a known preference*, but not for deciding whether a personalised response is actually *better for the user*. Six papers in the library bear on this; only one tests the second question directly.

## Where the judge fails: "is the personalised response better?"

[Re-Centering Humans in LLM Personalization](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=section.6&page=7) (2026) is the direct test. Humans and five LLM judges compared a generic and a personalised response side by side on a 1–5 scale, where 3 means no preference.

- **Inflation:** humans average 3.18, while every LLM judge scores higher, from 3.41 to 4.02 ([p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15)). Humans rated 54.6% of personalised responses as no better than generic ([p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.2&page=8)).
- **Weak item-level agreement:** Spearman correlation with human ratings is 0.11–0.38 (Table 6).
- **A mechanism:** several open-weight judges reward explicit mentions of a user attribute ("Given your interest in machine learning…"), which humans do not (Δ = 0.03). Models that produce such mentions more often as generators also reward them more as judges (ρ = 0.90, but across only five models, p = 0.04). Claude Sonnet 4.6 errs the other way and penalises mentions (Δ = −0.39) ([p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.2&page=8)).
- **Training does not fix it:** reward models trained on the human ratings reach only about 0.3 Spearman ([p. 9](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.3&page=9)).
- **Upstream too:** on which user attributes are relevant to a prompt, LLMs agree with each other (κ = 0.60) more than with humans (κ = 0.30), and mark 40–60% relevant where humans mark about 20% ([p. 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.5.2&page=6)).

Three weaknesses of this evidence:

- **Low human ceiling:** the three annotators agree with each other at only Spearman 0.325 ([p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.1&page=8)). So a judge at 0.36 is about as close to the humans as they are to each other; my reading is that the inflation and the mention bias are the solid findings, not the low correlation.
- **Third-party raters:** the annotators are Prolific workers reading someone else's profile, not the users being personalised for. The sample is 80 items and 367 ratings.
- **Text and table disagree:** the text says open-weight judges correlate very poorly, but in Table 6 Llama-3.3-70B has the highest correlation (0.376) alongside the worst inflation.

[PRISM-X](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?page=1) (p. 1) uses the right raters: 530 real users judging models personalised to themselves. It tests GPT-4o simulations of those users rather than a judge, but the result is related: simulators recover the aggregate ranking of models, yet fall far below human self-consistency on individual judgements. I read only its abstract for this answer.

## Where the judge holds up: "did it follow the stated preference?"

When the preference is given and the judge only checks compliance, the benchmarks report good agreement with humans:

| Benchmark | What the judge checks | Agreement with humans |
|---|---|---|
| [PrefEval, p. 43, Table 18](http://pdf.invalid/llm/personalization/benchmarks/Do%20LLMs%20Recognize%20Your%20Preferences.%20Evaluating%20Personalized%20Preference%20Following%20in%20LLMs.pdf?dest=table.18&page=43) | Binary checks: violated, acknowledged or hallucinated the preference | 86–98% |
| [CUPID, p. 3](http://pdf.invalid/llm/personalization/benchmarks/CUPID.%20Evaluating%20Personalized%20and%20Contextualized%20Alignment%20of%20LLMs%20from%20Interactions.pdf?page=3) | Whether an inferred preference matches a checklist | Krippendorff α = 0.77 |
| [AlpsBench, p. 4](http://pdf.invalid/llm/personalization/benchmarks/AlpsBench.%20An%20LLM%20Personalization%20Benchmark%20for%20Real-Dialogue%20Memorization%20and%20Preference%20Alignment.pdf?page=4) | Four memory and preference tasks | 73–96% by task |
| [OP-Bench, p. 14, Table 5](http://pdf.invalid/llm/personalization/benchmarks/OP-Bench.%20Benchmarking%20Over-Personalization%20for%20Memory-Augmented%20Personalized%20Conversational%20Agents.pdf?dest=table.5&page=14) | Over-personalisation (irrelevance, sycophancy) | Spearman 0.60–0.74 |
| [LaMP-QA, p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7) | Which of two answers better meets the user's own stated needs | 73% with rubric aspects, 58% with direct scoring |
| [PersonaLens, p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=table.5&page=8) | Personalisation quality of a dialogue | κ = 0.52, against 0.78 for task completion |

Two patterns stand out. Agreement drops as the judgement gets more subjective: within PersonaLens, personalisation is the weakest metric. And in LaMP-QA, small judges both agree less with humans and score higher: a 0.5B judge agrees 48% of the time with a mean score of 0.94, a 32B judge 73% with 0.44. That is the same inflation pattern as in Re-Centering Humans.

These validations are also thin: mostly about 100 samples, third-party annotators, and synthetic personas where the "right" preference was written down in advance.

## What this means in practice

- **Use a judge for compliance checks** against an explicit preference or rubric, with binary or per-aspect questions rather than a holistic "how personalised is this" score.
- **Do not use a judge to claim personalisation helps.** The generic-versus-personalised comparison is exactly where judges are biased upward.
- **Aggregate rankings of systems are safer than per-item scores**, by analogy with PRISM-X's simulator result.

The library's general judge-evaluation papers (for example Prediction-Powered Inference and Trust or Escalate) describe ways to combine a judge with a small human-labelled sample; I checked only their summaries, not the papers.
