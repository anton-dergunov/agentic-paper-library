**Not on its own.** On the evidence in the library, an LLM judge inflates personalisation scores and tracks individual human judgements only weakly, though it does recover aggregate system rankings. This comes from the [personalisation review](reviews/llm/personalization.md) and the notes on the two real-user studies; I did not reopen the papers.

**Why it fails here in particular.** Whether an answer suits a person is something only that person knows, so the judge is guessing at a private preference. In practice it rewards visible signs of personalisation: an answer that opens "Given your interest in ML…" scores well whether or not the mention helped.

**What the papers measured**

- **Inflated scores, weak correlation.** In Re-Centering Humans, human raters found 54.6% of personalised responses no better than generic ones ([p. 8, Fig. 5](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=figure.5&page=8)). LLM judges scored the same responses 3.41–4.02 against 3.18 from humans, with Spearman correlation at most 0.38 ([p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15)).
- **Judges reward mentions.** In the same paper, how often a generator mentions user attributes correlates at r = 0.90 with how much judges reward mentions ([p. 8, Figs 6–7](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=figure.6&page=8)).
- **Right ranking, wrong person.** In PRISM-X, GPT-4o "twins" of 530 real participants recover the aggregate model ranking (r = 0.98–0.99). Per trial they reach Kendall τ 0.22 and 0.11, against 0.57 for human self-consistency ([p. 16–17, Fig. 8](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=figure.8&page=16)).
- **Generic passes as personalised.** Semantic Constraint Verification finds 8B-class judges score 0–19% on correct-but-generic answers ([p. 7, Table 3](http://pdf.invalid/llm/personalization/methods/Evaluating%20LLM%20Personalization%20via%20Semantic%20Constraint%20Verification.pdf?dest=table.3&page=7)).
- **Order dependence.** LaMP-QA's pairwise judge flips 78% of its verdicts when the order is swapped ([p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7)).
- **Personalisation is the weak criterion.** PersonaLens's judge agrees with humans at κ 0.78 on task completion but 0.52 on personalisation (from a skim-level digest, no page).

**Caveats on the evidence**

- Re-Centering's human raters are three third-party annotators, not the users themselves, with κ 0.31–0.43 between them. The Stage 3 sample is small: 80 items and 367 ratings (p. 15).
- With human agreement that low, part of the judge's low correlation is a low ceiling, not only judge error.
- No paper in the library has users judge answers to their own questions over time.

**What a judge is still good for**

- **Comparing systems in aggregate**, where PRISM-X shows the ranking holds.
- **Objective sub-criteria**, such as whether a stated preference was followed or the task was completed.
- **Triage with humans kept in the loop.** The [evaluation review](reviews/llm/evaluation.md) describes calibrating on a few hundred human labels and sending low-confidence items to people. None of the papers there tests this on personalisation.
