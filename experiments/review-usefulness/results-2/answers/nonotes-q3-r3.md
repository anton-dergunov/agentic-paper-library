**Not as a replacement, on the library's evidence.** An LLM judge can check whether a response obeys a preference that is written down, and can rank systems in aggregate. It cannot yet stand in for a person's judgement of whether a personalised response is actually better for them.

The papers split by what the judge is asked to do:

| Judge's task | Agreement with humans | Source |
|---|---|---|
| Binary checks against an explicit preference (violated it? acknowledged it?) | 86–98% | [PrefEval, p. 43, Table 18](http://pdf.invalid/llm/personalization/benchmarks/Do%20LLMs%20Recognize%20Your%20Preferences.%20Evaluating%20Personalized%20Preference%20Following%20in%20LLMs.pdf?dest=subsection.A.17&page=43) |
| Pick the better of two responses, given the user's rubric aspects | 97.5% direction agreement | [Personalized RewardBench, p. 17, Table 11](http://pdf.invalid/llm/post-training/preference-learning/Personalized%20RewardBench.%20Evaluating%20Reward%20Models%20with%20Human%20Aligned%20Personalization.pdf?dest=subsection.B.4&page=17) |
| Same pairs, but inferring the needs from the user's history | best model about 76% | [Personalized RewardBench, p. 6](http://pdf.invalid/llm/post-training/preference-learning/Personalized%20RewardBench.%20Evaluating%20Reward%20Models%20with%20Human%20Aligned%20Personalization.pdf?dest=subsection.4.2&page=6) |
| Score a response against aspects taken from the user's own question narrative | 73% (direct scoring: 58%) | [LaMP-QA, p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?dest=subsection.5.2&page=7) |
| Rate "personalisation" of a dialogue | κ = 0.52 (task completion: 0.78) | [PersonaLens, p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=subsection.4.7&page=8) |
| Rate whether the personalised response is better than the generic one | Spearman 0.11–0.38 | [Re-Centering Humans, p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15) |
| Predict one real user's ranking of four models from their profile | Kendall τ = 0.22 (human self-consistency: 0.57) | [PRISM-X, p. 17](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=subsection.4.1&page=17) |

The pattern: agreement is high when the criterion is handed to the judge, and falls as the judge has to infer what this person wants.

**How the judges fail**

- **They inflate the benefit of personalisation.** In Re-Centering Humans, people rated 54.6% of personalised responses as no better than the generic one (mean 3.18 on a scale where 3 is neutral). Every LLM judge scored higher, from 3.41 to 4.02 ([p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.2&page=8)).
- **They reward visible personalisation.** A response that says "Given your interest in machine learning…" without adapting its content looks personalised to open-weight judges. Human ratings barely move with explicit mentions (gap 0.03), while Claude Sonnet 4.6 over-penalises them (−0.39).
- **Position bias is far stronger than in people.** In PRISM-X the simulated user ranked the first-shown model best 44.9% of the time and the last 7.2%; humans were near 25% for each ([p. 18](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=subsection.4.2&page=18)). In LaMP-QA a pairwise judge changed its choice in 78% of cases when the order was swapped.
- **Aggregate rankings survive, individual ones do not.** PRISM-X's simulated users reproduce the human ordering of methods (r = 0.98–0.99) but pick a given participant's favourite model only 40% of the time, against 68.8% for the participant's own consistency.

**Caveats on the evidence**

- **Re-Centering Humans is small and uses third-party raters.** Stage 3 has 80 items and three annotators, whose agreement with each other is itself only Spearman 0.325. So a judge correlation of 0.36 is close to what one human gets with another; the inflation and the explicit-mention bias are the stronger findings.
- **Its text and table disagree.** The text says open-weight judges correlate very weakly, but Table 6 gives Llama-3.3-70B the highest correlation (0.376). I have not checked this against the PDF.
- **Most "human validation" is not by the user.** Only PRISM-X compares against the person being personalised for. The others use annotators reading a profile or rubric.
- **PRISM-X tests a naive simulator.** It is GPT-4o conditioned on a text persona, and the authors say this is not the ceiling.

**What this means in practice**

Use the judge for the parts with a written criterion: preference-following checks, or aspect-based scoring against needs the user stated, as in LaMP-QA. Avoid pairwise prompts without order randomisation, and avoid asking for a holistic "how personalised is this" score. Keep real users for the question of whether personalisation helped, and calibrate the judge's absolute scores against a human sample, since they run high.
