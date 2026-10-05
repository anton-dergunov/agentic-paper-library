Mostly no, not for the question that matters most. I read the library's notes on this, not the full papers, so page numbers come from those notes.

**Short answer.** An LLM judge can stand in for humans when the response can be checked against an explicit criterion. It can't when the question is whether this particular person would actually prefer the response.

**Where it holds up: checking against a stated preference**
- PrefEval uses a Claude judge with four binary checks, such as preference-unaware or hallucinated preference. It reports 0.92–0.97 human agreement on final accuracy ([PrefEval, p. 43, Table 18](http://pdf.invalid/llm/personalization/benchmarks/Do%20LLMs%20Recognize%20Your%20Preferences.%20Evaluating%20Personalized%20Preference%20Following%20in%20LLMs.pdf?page=43)).
- CUPID matches inferred preferences to ground truth through atomic checklists. It gets α = 0.769 against the human majority, and a distilled 7B matcher gets 0.748 ([CUPID, p. 3, p. 8](http://pdf.invalid/llm/personalization/benchmarks/CUPID.%20Evaluating%20Personalized%20and%20Contextualized%20Alignment%20of%20LLMs%20from%20Interactions.pdf?page=8)).
- These tasks reduce to "does the response honour this stated fact?" That is close to instruction-following verification, which is where LLM judges are strongest.

**Where it breaks: "does this person like it?"**
- The strongest evidence is [Re-Centering Humans in LLM Personalization, p. 8 and p. 15](http://pdf.invalid/llm/personalization/methods/Re-Centering%20Humans%20in%20LLM%20Personalization.pdf?page=8).
  - Humans rate 54.6% of personalised responses no better than generic ones. LLM judges score higher, averaging 3.41–4.02 against 3.18 for humans.
  - Judge–human Spearman is at most 0.38, and trained reward models reach only about 0.3.
  - Judges reward explicit mentions of the profile ("Given your interest in ML…"). The correlation between a generator's mention rate and the judge's reward is r = 0.90. That rewards the most visible personalisation, not the most useful.
  - The sample is small (80 items, 367 ratings), and the raters were third-party annotators, not the users themselves.
- The relevance step has the same gap. Humans call about 20% of attribute–prompt pairs relevant and LLMs 40–60%, with LLM–human κ of 0.30 (p. 6). An LLM judge therefore over-credits using attributes that shouldn't be used. This is the over-personalisation failure that OP-Bench targets.
- [PRISM-X, p. 16–22](http://pdf.invalid/llm/personalization/benchmarks/PRISM-X.%20Experiments%20on%20Personalised%20Fine-Tuning%20with%20Human%20and%20Simulated%20Users.pdf?page=16) tests GPT-4o simulated users that have the profile, against 530 real users.
  - The aggregate ranking of methods matches humans (r = 0.98–0.99).
  - Per-trial agreement is poor: Kendall τ is 0.22 and 0.11, against 0.57 for humans' own self-consistency. Top-1 agreement is about 40% and 32%, against 69%.
  - Simulators show strong primacy bias, are more sycophantic, and are far less diverse across users.
  - Simulated users can rank systems on average, but they can't predict an individual's choice. That is the personalisation question.

**Generic judge problems apply on top**
- [Reliability without Validity](http://pdf.invalid/llm/evaluation/methods/Reliability%20without%20Validity.%20A%20Systematic%2C%20Large-Scale%20Evaluation%20of%20LLM-as-a-Judge%20Models%20Across.pdf?page=4) tested 21 judges. On MT-Bench the best has κ 0.51 even though exact-match is 0.85 (p. 4). Rankings of judges shift between benchmarks (p. 5), and a judge can be highly repeatable and still position-biased (p. 6).
- [The Coin Flip Judge](http://pdf.invalid/llm/evaluation/methods/The%20Coin%20Flip%20Judge.%20Reliability%20and%20Bias%20in%20LLM-as-a-Judge%20Evaluation.pdf?page=7) finds a 13% mean flip rate on near-tied pairs. Near-ties are common in personalisation comparisons.
- Two caveats on these notes: the Reliability paper's κ-deflation gap is partly a denominator mismatch, and the Coin Flip paper has no human ground truth. Neither involves personalisation, so treat them as background.

**Practical setup for your own evals**
1. Use LLM judges for verifiable sub-questions: was the stated preference applied, was a wrong-context preference applied, was an unrelated attribute mentioned. Report agreement as κ or α against a human sample, not raw match.
2. Don't use a single holistic "how personalised or good is this" score as the headline. The judge's bias toward visible personalisation inflates it.
3. Keep humans for the preference verdict, ideally the users themselves or raters close to them. If you can't, calibrate the judge on a human-labelled set and escalate uncertain items, as in [Trust or Escalate](http://pdf.invalid/llm/evaluation/methods/Trust%20or%20Escalate.%20LLM%20Judges%20with%20Provable%20Guarantees%20for%20Human%20Agreement.pdf?page=3). Its guarantee covers only the easier items the judge keeps. Abstained items had lower human agreement, 0.815 against 0.902 (p. 7), and personalisation items likely skew subjective.
4. Control for length and explicit mentions. PRISM-X finds length alone drives much of the preference: 100 extra characters gives 1.57× odds of being chosen (p. 13).
5. Judge each change on an A/B with real users where possible. Judge-based sign and magnitude may differ from human results.

**Gaps.** The library has no paper measuring an LLM judge against the actual user's own ratings of personalised responses. Re-Centering and PRISM-X come closest. The Re-Centering evidence is small, and the other studies use synthetic personas. I haven't saved this synthesis to `notes/`; say if you want it appended to the Q&A of the Re-Centering note.
