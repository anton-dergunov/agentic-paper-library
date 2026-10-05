Mostly no. A judge can rank systems against each other, but it can't replace humans for deciding whether personalisation helped.

**What the evidence says**

- **Judges inflate the scores.** In [Re-Centering Humans](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15), human raters gave personalised responses 3.18 on average. LLM judges gave 3.41–4.02, and their Spearman correlation with humans was at most 0.38 ([p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15)).
- **Humans often see no gain.** They judged 54.6% of personalised responses no better than the generic ones ([p. 8, Fig. 5](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=figure.5&page=8)).
- **Judges reward visible personalising.** Across five models, how often a model mentions user attributes when generating correlates at r = 0.90 with how much it rewards such mentions when judging. Humans show almost no gap between responses with and without explicit mentions (Δ 0.03) ([p. 8, Fig. 7](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=figure.7&page=8)). Phrases like "Given your interest in ML…" win over the judge but not over people.
- **Trained reward models don't fix it.** They reach only about 0.3 Spearman with humans (p. 9).
- **The same pattern shows up in other papers.** I took these from the library's review and haven't re-read the papers:
  - A small entailment model beat 8B-class LLM judges, which called generic answers personalised ([Semantic Constraint Verification](http://pdf.invalid/llm/personalization/methods/Evaluating%20LLM%20Personalization%20via%20Semantic%20Constraint%20Verification.pdf?page=7), p. 7).
  - LaMP-QA's pairwise judge flipped 78% of its verdicts when the answer order was swapped (p. 7).
  - PersonaLens's judge agreed with humans at κ 0.78 on task completion but only 0.52 on personalisation.
  - PUMA's judge rated the system above real human counsellors (4.37 vs 3.85).

**Caveats on the human side**

- Re-Centering used three third-party Prolific raters, not the users themselves. They agreed with each other only moderately (Spearman 0.325, weighted κ 0.310). A judge correlation near 0.37 is therefore close to the human-human level, but the two numbers aren't strictly comparable because one is judge-vs-average and the other is rater-vs-rater.
- The Stage 3 sample is small: 80 items and 367 ratings.
- No paper here has users rate answers to their own questions over time, which is the strongest test.

**Where a judge does help**

- **Ranking systems against each other.** [PRISM-X](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?page=16)'s simulated users recover the aggregate model ranking at r ≈ 0.98–0.99. They fall far below human self-consistency on individual judgements: Kendall τ 0.11–0.22 vs 0.57 (p. 16–17).
- **Checks that don't depend on taste.** Constraint or entailment checks, like the Semantic Constraint Verification one above, work here.

**Practical recipe**

- Use the judge for development-time ranking and regression checks.
- Use a rubric or constraint check in place of a holistic "how personalised is this?" score.
- Randomise answer order.
- Don't report an absolute gain from a judge alone.
- Run a human pass, ideally with the users themselves, before claiming personalisation helps.

This is from the [personalisation review](reviews/llm/personalization.md), which has a section on it.

I tried to append this answer to that review's `## Q&A`, but the write failed with permission denied, so nothing was saved. If you make the file writable I'll add it. There's no commit to suggest, since nothing changed.
