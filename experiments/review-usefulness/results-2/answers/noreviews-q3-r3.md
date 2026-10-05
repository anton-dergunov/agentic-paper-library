**Not as a general replacement.** On the library's evidence, a judge can stand in for humans when the user's criteria are written down and the judge only checks a response against them. It cannot yet answer the open question "is this personalised response better for this person?".

**Intuition.** A judge asked whether a response is well personalised looks for visible signs of personalisation, such as "Given your interest in ML…". People tend to find that mechanical or intrusive, so the judge rewards something users do not value.

**Where judges fail: open-ended preference**

The direct test is Re-Centering Humans in LLM Personalization, which compares five LLM judges with three Prolific annotators at each stage:

- **Which user attributes are relevant to a prompt:** humans mark about 20% relevant, LLMs 40–60%. LLM–human κ is 0.300, against 0.426 human–human and 0.597 LLM–LLM ([p. 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.5.2&page=6)).
- **Personalised vs generic response:** humans average 3.18 on a 1–5 scale where 3 is neutral, and rate 54.6% of personalised responses no better than generic. Judges average 3.41–4.02, with Spearman 0.11–0.38 against the human average ([p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.2&page=8); [p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15)).
- **Mechanism:** open-weight judges score explicit attribute mentions higher; humans and GPT-5.4 do not, and Claude Sonnet 4.6 penalises them. Models that mention attributes more as generators also reward mentions more as judges (r = 0.90, five models) ([p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?page=8&search=mechanical%20attribute%20invocation)).

My reading, not the paper's: the low correlation is weaker evidence than it looks, because the annotators only agree with each other at Spearman 0.325 (p. 8). The best judges are near that noise ceiling. The firmer finding is the systematic bias (score inflation and mention reward), which averaging more judge runs will not remove. The sample is also small: 80 items, 367 ratings.

**The raters are not the users either.** Those annotators are third parties guessing what someone else would prefer. The one study here with the actual users is PRISM-X (530 participants), which tests GPT-4o simulating each user from their profile:

- **Aggregate:** simulated and real users rank the systems almost identically (r = 0.98–0.99).
- **Per person:** agreement is τ 0.22 and 0.11, against human self-consistency of 0.57; top-1 match is 40.1% and 32.3% against 68.8% ([p. 16–17](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?page=16)).
- **Bias:** the simulators pick position A 44.9% of the time and D 7.2% (p. 18).

So a simulated rater can tell you which system wins on average, but not what an individual prefers, which is the thing personalisation is about.

**Where judges work: checking against stated criteria**

| Paper | Judge's task | Agreement with humans |
|---|---|---|
| LaMP-QA ([p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7&search=Effect%20of%20Evaluation%20Method)) | Score against aspects extracted from the user's own question narrative | 73%, vs 58% for direct scoring; the pairwise judge flips 78% of verdicts when order is reversed |
| Personalized RewardBench ([p. 6, Table 2](http://pdf.invalid/llm/post-training/preference-learning/Personalized%20RewardBench.%20Evaluating%20Reward%20Models%20with%20Human%20Aligned%20Personalization.pdf?dest=table.2&page=6)) | Pick the response that meets the user's rubric | 97.8–99.1% given the true rubric (p. 15); at most 75.9% when it must be inferred |
| CUPID ([p. 8](http://pdf.invalid/llm/personalization/benchmarks/CUPID.%20Evaluating%20Personalized%20and%20Contextualized%20Alignment%20of%20LLMs%20from%20Interactions.pdf?page=8)) | Match inferred preference to ground truth via checklists | α = 0.769 vs human majority |
| OP-Bench (p. 13–14, Table 5) | Flag irrelevant memory use and sycophancy | ρ ≈ 0.68 (GPT-4o-mini), 0.74 best |

The pattern is that the judge is good at verification and poor at inferring what the user wants. These validations are small, though: LaMP-QA's is 100 examples and two annotators, and I took the Personalized RewardBench figures from a skim-level digest.

**What I'd do**

- Use rubric- or checklist-based scoring with a strong judge, not a holistic "which is better personalised" prompt.
- Use judges to rank systems in aggregate, not to label individual responses.
- Keep a small first-person human set (the users themselves, not annotators) to measure the judge's bias.
- Send low-confidence items to humans. Trust or Escalate does this with a guarantee on agreement, and the items it abstains on are the subjective ones (p. 7, Table 4).
