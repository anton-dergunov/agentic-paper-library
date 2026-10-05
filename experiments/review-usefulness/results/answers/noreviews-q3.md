Not for the question that matters most, "is this response better for this user?". On that, the library's evidence says judges track humans weakly and rate personalisation too generously. They do hold up on narrower, checkable questions, such as whether a response violated a stated preference.

## Where judges fail: subjective quality of a personalised response

**Re-Centering Humans in LLM Personalization** is the most direct test in the library. Humans and LLM judges each see a generic and a personalised response and rate which they prefer on a 1–5 scale.

- **Weak agreement:** judge–human Spearman is 0.11–0.38 ([p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15)).
- **Inflation:** every judge rates personalisation higher than humans do, 3.41–4.02 against a human mean of 3.18, where 3 is neutral. Humans found 54.6% of personalised responses no better than the generic one ([p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=subsection.6.2&page=8)).
- **Mechanism:** several open-weight judges reward explicit attribute mentions ("Given your interest in machine learning…") that humans do not reward. Models that mention attributes more as generators also reward mentions more as judges (r = 0.90, five models). Claude Sonnet 4.6 errs the other way and penalises mentions (p. 8, Figs 6–7).
- **Training does not fix it:** reward models trained on the human ratings reach only about 0.3 Spearman (p. 9).

Two caveats on that paper. The sample is small: 80 items and 367 ratings. And the three annotators agree with each other only at Spearman 0.325 (p. 8), so the best judges match the human average about as well as one annotator matches another. My reading is that the measurable problem is the bias, not the rank agreement.

The same pattern shows up one stage earlier in that paper, when deciding which user attributes are relevant to a prompt: humans mark about 20% of pairs relevant, LLMs 40–60%, with LLM–human κ of 0.300 against human–human 0.426 (p. 6).

**PRISM-X** tests the stronger version: an LLM given the user's profile, standing in for that user as rater. GPT-4o reproduces the aggregate model ranking (r = 0.98–0.99) but not individual choices: per-trial τ is 0.22 and 0.11, against 0.57 for human self-consistency ([pp. 16–17](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?page=16)). It also has a strong position bias, picking the first option 44.9% of the time and the fourth 7.2% (p. 18).

## Where judges hold up: checkable sub-questions

| Paper | What the judge decides | Agreement with humans |
|---|---|---|
| PrefEval | Did the response violate a stated preference? | 0.92–0.97 (p. 43, Table 18) |
| CUPID | Does the inferred preference match the ground truth, by checklist? | α = 0.769 (p. 8) |
| AlpsBench | Four memory and preference tasks | 73–96% alignment (p. 4) |
| OP-Bench | Is the response over-personalised or sycophantic? | ρ ≈ 0.68, best judge 0.74 (pp. 13–14, Table 5) |
| PersonaLens | Personalisation in a dialogue | κ = 0.52, against 0.78 for task completion (p. 8, Table 5) |

Agreement falls as the question moves from "was the known preference respected?" to "how well personalised is this?". Most of these benchmarks also use synthetic users with planted preferences, which Re-Centering Humans shows are easier than real ones (p. 4).

## What this means in practice

- **Use a judge** for rubric or checklist questions with a known ground-truth preference, and for ranking systems in aggregate.
- **Keep humans** for whether personalisation improved the response, and for any per-user claim. Ideally the rater is the user: Re-Centering Humans used third-party annotators, and PRISM-X is the only study here where users rate their own responses.
- **Watch the judge's taste:** check whether it rewards explicit mentions of user attributes, and avoid judging a model with itself.

I added this comparison to the Q&A in `notes/Re-Centering Humans in LLM Personalization.md`. Suggested commit message:

```
Note judge-vs-human evidence for personalised responses

- Add a Q&A entry to the Re-Centering Humans note: judges are biased upward and track humans weakly on subjective personalisation quality, but match the annotators' own agreement level and hold up on checkable sub-questions (PrefEval, CUPID, PersonaLens, OP-Bench).
```
