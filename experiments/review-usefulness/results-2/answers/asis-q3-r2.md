Not as a replacement. On the papers in the library, an LLM judge can rank personalisation systems on average and can check criteria the user wrote down, but it does not reproduce what an individual person prefers, and it errs in a consistent direction: it scores personalised answers higher than people do.

**Example of the failure.** A response opens with "Given your interest in machine learning…" and is otherwise the generic answer. Open-weight judges score it higher for naming the attribute; human raters and GPT-5.4 show little sensitivity to the mention, and Claude Sonnet 4.6 scores it lower ([Re-Centering Humans, p. 8, Fig. 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=figure.6&page=8)).

| What the judge decides | Agreement with people | Source |
|---|---|---|
| Is the personalised answer better than the generic one (1–5 scale) | Spearman 0.11–0.38 with the human average; judges average 3.41–4.02 against 3.18 from humans | [Re-Centering Humans, p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15) |
| Which answer this particular person would choose, given their profile | Kendall τ 0.22 and 0.11 per trial, against 0.57 for the person's own consistency; aggregate model ranking r = 0.98–0.99 | [PRISM-X, p. 16–17, Fig. 8](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?dest=figure.8&page=16) |
| How personalised a task dialogue is | κ 0.52 with annotators, who agree among themselves at 0.75; on task completion 0.78 against 0.865 | [PersonaLens, p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=table.5&page=8) |
| Which of two answers meets the needs the asker wrote down | 73% with a rubric taken from the asker's own post, 58% scoring directly; annotators agree at κ 0.726 | [LaMP-QA, p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7) |

What follows from these:

- **Ranking systems works; predicting the person doesn't.** PRISM-X is the closest test of "the judge as the user": 530 real participants choose, and GPT-4o given each person's profile tries to match them. It recovers which model wins overall and misses the individual choices.
- **The judge can pick a different winner.** In Personalized Soups, GPT-4 puts P-Soups first and human judges put P-MORL first ([p. 7, Tables 3–4](http://pdf.invalid/llm/personalization/methods/Personalized%20Soups.%20Personalized%20Large%20Language%20Model%20Alignment%20via%20Post-hoc%20Parameter%20Merging.pdf?dest=table.4&page=7)).
- **The more of the preference is written down, the better the judge.** A rubric built from the user's own words (LaMP-QA) beats a holistic score. LaMP-QA's pairwise judge, by contrast, changed its verdict in 78% of cases when the two answers were swapped (p. 7).
- **Training a judge on human ratings did not fix it.** Re-Centering's trained reward models reach about 0.3 Spearman with humans, no better than the stronger LLM judges ([p. 9](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.3&page=9)).

**How strong the evidence is.** Weaker on ranking than the headline suggests, and this reading is mine, not the paper's:

- Re-Centering's Stage 3 is 80 items and 367 ratings from three third-party raters, not the users themselves.
- Those raters agree with each other at only Spearman 0.325 (weighted κ 0.310) ([p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?page=8)).
- The best judges (0.31–0.38) are therefore about at the human–human level. The study shows score inflation and the taste for explicit mentions more firmly than it shows poor ranking.
- PersonaLens is the cleaner case of a judge below the human ceiling (0.52 against 0.75), on 100 dialogues.

No paper here has users rate answers to their own questions over time and compares an LLM judge against that.

**In practice.** Use the judge for system-level comparisons and for checks against explicit criteria, and calibrate it on a human-labelled sample first; the evaluation review's section "Calibrating the judge against people" (`reviews/llm/evaluation.md`) covers how. Keep people for the question "did personalising make this answer better for this user".

**Not in the library.** "Can LLM be a Personalized Judge?" (arXiv 2406.11657) is on exactly this question. It was skipped on 2026-10-01 as narrow; if you want it, the entry in `catalog/skipped.yaml` has to be removed first.

I tried to append this to the Q&A in `reviews/llm/personalization.md`, but the file is not writable in this session, so the review is unchanged and there is nothing to commit.
