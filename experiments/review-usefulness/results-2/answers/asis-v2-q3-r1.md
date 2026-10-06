Not for the open question "is this response better for this person"; yes, with a human-labelled check, for narrow criteria written down in advance. I checked every number below in the papers themselves.

## How closely judges match people

| What the judge decides | Judge vs humans | Humans vs each other | Source |
|---|---|---|---|
| Personalised vs generic response, 1–5 preference | Spearman 0.11–0.38; mean rating 3.41–4.02 vs 3.18 | Spearman 0.325, weighted κ 0.310 | [Re-Centering Humans, p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15), [p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.2&page=8) |
| Whether a user attribute is relevant to the prompt | κ 0.300 | κ 0.426 (LLMs among themselves 0.597) | [Re-Centering Humans, p. 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.5.2&page=6) |
| Personalisation score (1–4) for a dialogue | κ 0.520 | Fleiss κ 0.750 | [PersonaLens, p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=table.5&page=8) |
| Task completion, same dialogues | κ 0.780 | Fleiss κ 0.865 | same table |
| Which of two answers meets the asker's stated needs | 73% with per-aspect rubrics, 58% with direct scoring | κ 0.726 | [LaMP-QA, p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7) |
| Irrelevant use of memory, and sycophancy | Spearman 0.60–0.68 for the five judges I read in the table | not reported | [OP-Bench, p. 14, Table 5](http://pdf.invalid/llm/personalization/benchmarks/OP-Bench.%20Benchmarking%20Over-Personalization%20for%20Memory-Augmented%20Personalized%20Conversational%20Agents.pdf?dest=table.5&page=14) |
| Ranking four models for one participant (LLM "twin" given their profile) | Kendall τ 0.22, top-1 40.1% | self-consistency τ 0.57, top-1 68.8% | [PRISM-X, p. 16–17](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=figure.8&page=16) |

## What this shows

- **The judge does best where the criterion is explicit.** Task completion, a rubric taken from the asker's own post, or a named failure all score well. Holistic preference scores worst.
- **The errors are biased, not only noisy.** More judge calls will not average them out:
  - Judges rate personalised responses higher than humans do, and mark 40–60% of attributes relevant where humans mark about 20% (Re-Centering Humans, p. 6 and p. 15).
  - Several open-weight judges reward explicit mentions such as "Given your interest in machine learning…"; humans and GPT-5.4 do not, and Claude Sonnet 4.6 penalises them (p. 8).
  - LaMP-QA's pairwise judge changed its choice in 78% of cases when the two responses were swapped (p. 7).
- **A judge can rank systems and still be wrong per user.** In PRISM-X the simulated twins recover the aggregate model ranking (r = 0.98–0.99) while missing the individual (p. 16–17).
- **Judges call generic answers personalised.** In [Semantic Constraint Verification, p. 7, Table 3](http://pdf.invalid/llm/personalization/methods/Evaluating%20LLM%20Personalization%20via%20Semantic%20Constraint%20Verification.pdf?dest=table.3&page=7), 8B-class judges get 0–19% on correct-but-generic answers. This is weak evidence: the "users" are MMLU topic clusters, and the paper concedes the best LLM judges still beat its method at spotting personalised answers (p. 9).

## Where the evidence is thin

- **The human reference is itself shaky.** Re-Centering Humans uses three third-party raters on 80 items. Their agreement with each other (0.325) is below the best judge's correlation with their average (0.376); that comparison is mine and not like for like. In [HorizonBench, p. 7](http://pdf.invalid/llm/personalization/benchmarks/HorizonBench.%20Long-Horizon%20Personalization%20with%20Evolving%20Preferences.pdf?dest=subsection.5.3&page=7), annotators reach only 56–64% majority accuracy on which response fits the user's current preference.
- **Nobody tests against the actual user.** No paper here compares a judge with the user's own rating of answers to their own questions. Re-Centering Humans (p. 9) and LaMP-QA (p. 10) both name the user as the proper rater.
- **The paper that asks this directly is not in the library.** "Can LLM be a Personalized Judge?" (Dong et al., 2024, arXiv 2406.11657) is in `catalog/skipped.yaml` as "narrow". I'd reconsider that skip if this question matters to you.

## In practice

Use the judge for per-criterion checks against the user's stated needs, score each response on its own rather than pairwise, and calibrate on a few hundred human labels. Keep real users for the headline claim that personalisation helps. The calibration advice comes from the evaluation review's "Calibrating the judge against people" section; I did not re-read its source papers.

## Not saved

I tried to append this to the Q&A of `reviews/llm/personalization.md`, but `reviews/` is read-only in this copy, so nothing was written and there is no change to commit.
