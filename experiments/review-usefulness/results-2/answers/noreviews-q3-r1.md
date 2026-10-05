**No, not for the question that matters most: whether personalising made the response better for the user.** An LLM judge is a usable stand-in only for the narrower check of whether a response met a preference that is already written down, and even there it agrees with humans less than humans agree with each other.

One paper in the library tests this directly, *Re-Centering Humans in LLM Personalization*. Raters saw a generic and a personalised response side by side and scored which they preferred on a 1–5 scale (3 = no preference).

- **Judges inflate:** humans averaged 3.18, while the five LLM judges averaged 3.41–4.02 ([p. 15, Table 6](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=table.6&page=15)).
- **Judges rank differently:** the best Spearman correlation with the human average was 0.376, and two open-weight judges were below 0.2.
- **Why:** several open-weight judges reward a response for visibly naming an attribute ("Given your interest in ML…"), which humans do not; GPT-5.4 showed little of this and Claude Sonnet 4.6 the opposite ([p. 8](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?dest=section.6&page=8)).
- **Same pattern one step earlier:** asked whether a user attribute is relevant to a prompt, LLMs said yes for 40–60% of pairs and humans for about 20%. LLM–human κ was 0.300 against 0.426 between humans (p. 6).

The evidence is thin: 80 items, 367 ratings, and three third-party annotators rather than the users themselves. The annotators agreed with each other at only ρ 0.325, so the low correlation is partly noise in the human data; the inflation is the firmer finding.

Where the judge is given an explicit rubric, it does better:

| Paper | What the judge checks | Agreement with humans |
|---|---|---|
| PersonaLens ([p. 8, Table 5](http://pdf.invalid/llm/personalization/benchmarks/PersonaLens.%20A%20Benchmark%20for%20Personalization%20Evaluation%20in%20Conversational%20AI%20Assistants.pdf?dest=table.5&page=8)) | Personalisation in a dialogue, against the profile | κ 0.520, against 0.750 between humans |
| LaMP-QA ([p. 7](http://pdf.invalid/llm/personalization/benchmarks/LaMP-QA.%20A%20Benchmark%20for%20Personalized%20Long-form%20Question%20Answering.pdf?page=7)) | Aspects the user asked for in their own post | Picks the human-preferred response 73% of the time; 58% without the aspects |
| CUPID ([p. 3](http://pdf.invalid/llm/personalization/benchmarks/CUPID.%20Evaluating%20Personalized%20and%20Contextualized%20Alignment%20of%20LLMs%20from%20Interactions.pdf?page=3)) | Inferred preference against the true one, as a checklist | α 0.769 against the human majority |

These validations are small (about 100 items each for PersonaLens and LaMP-QA), and PersonaLens and CUPID use synthetic users.

Having the LLM play the user instead of judging fails in the same way. In PRISM-X, GPT-4o simulators given a participant's profile reproduced the aggregate model ranking (r 0.98–0.99) but not individual choices: per-trial τ was 0.22 and 0.11 against 0.57 for human self-consistency ([p. 16–17](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?page=16)). So a judge or simulator can rank systems on average while being wrong about each person, which is the thing personalisation is about.

In practice, I would use the judge for rubric checks and keep a human-labelled sample to measure and correct its bias. Two papers in the library cover that: *Prediction-Powered Inference* for correcting the judge's bias from a small labelled set, and *Trust or Escalate* for letting the judge abstain when unsure. The "is it actually better" question should go to the users being personalised for; in the library only PRISM-X does that.

I tried to save this comparison to the Q&A in `notes/Re-Centering Humans in LLM Personalization.md`, but the write was denied, so nothing in the library changed.
