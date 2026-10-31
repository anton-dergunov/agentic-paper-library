# Direct Preference Optimization: Your Language Model is Secretly a Reward Model

type: method
family: offline preference optimization; RL-free alternative to RLHF
evidence: controlled IMDb sentiment generation (GPT-2-large; reward–KL frontier vs. PPO, PPO-GT, unlikelihood, Preferred-FT), TL;DR summarization (GPT-J; GPT-4 win rates vs. reference summaries, vs. PPO, Best-of-N, SFT), Anthropic-HH dialogue (Pythia-2.8B; GPT-4 win rates vs. chosen responses, vs. Best-of-128 and 2-shot Pythia); strength: three tasks but mostly single runs with no error bars in the main text; GPT-4-judged win rates; human check on one task only; no ablation in the main text

## Digest

- Claim: RLHF's objective (maximize a learned reward under a KL penalty to a reference model) can be optimized directly from pairwise preferences with a binary cross-entropy loss on the policy, with no separate reward model and no RL sampling loop (p. 1; p. 4, Eq. 7).
- Mechanism: the implicit reward is $\hat r_\theta(x,y)=\beta\log\frac{\pi_\theta(y|x)}{\pi_{ref}(y|x)}$. Under Bradley-Terry, the preference probability depends only on reward differences, so the intractable partition function $Z(x)$ cancels (p. 4, Eqs. 5–6).
- Loss (p. 4, Eq. 7): $-\mathbb{E}\big[\log\sigma\big(\beta\log\frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)}-\beta\log\frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}\big)\big]$, where $y_w$ and $y_l$ are the preferred and dispreferred completions and $\sigma$ is the logistic function.
- Definitions: $\pi_{ref}$ is the SFT model when available. Otherwise it is fit by maximum likelihood on the preferred completions (p. 5). $\beta$ controls deviation from the reference (p. 3–4). No default value for $\beta$ appears in the main text.
- Eq. 6 (p. 4) is garbled in the text layer: the fraction and exponent are split across lines. I rewrote the preference probability from Eq. 7's form and did not quote it as exact.
- Gradient (p. 5): each pair is weighted by $\sigma(\hat r_\theta(x,y_l)-\hat r_\theta(x,y_w))$, so pairs the implicit reward misorders get more weight. The authors say a version without this weight degenerates (citing Appendix Table 3). That table is not in the text I read, so this is unverified here.
- Theory (p. 5–6): Lemmas 1–2 (p. 5) and Theorem 1 (p. 6) claim that reward classes consistent with Plackett-Luce/Bradley-Terry "under mild assumptions" have this reparameterization. Full proofs are in appendices not in the text. MLE consistency is cited to [4] and not shown (p. 4–5).
- Stability argument (Sec. 5.2, p. 6): the normalizer in PPO-style objectives can cause high-variance gradients, and DPO needs no baseline. This is analytical; no experiment isolates PPO variance.
- Sentiment (p. 7): GPT-2-large SFT on IMDb. Preference labels come from a pretrained sentiment classifier, so the "preferences" are a ground-truth proxy. The main result is the reward–KL frontier (p. 7, Figure 2 left), where DPO is claimed to dominate PPO and PPO-GT. Frontier values exist only in the plot.
- Sentiment sweep (p. 8): $\beta\in\{0.05,0.1,1,5\}$; PPO target KL $\in\{3,6,9,12\}$; unlikelihood $\alpha\in\{0.05,0.1,0.5,1\}$; seeds for Preferred-FT; "22 runs in total." The seed count is not stated, so the total cannot be reconciled.
- Summarization (p. 7, Figure 2 right; p. 9): GPT-J SFT, GPT-4 judging against reference summaries. DPO has "approximately 61%" at temperature 0.0, vs. PPO "at 57% at its optimal sampling temperature of 0.0." Preference data came from a different, similarly trained SFT model (p. 7), so it is off-policy relative to $\pi_{ref}$. The text says $\beta$ was "not meaningfully tuned" (p. 9).
- Human check (p. 10, Table 2): DPO (temp 0.25) vs. PPO (temp 0). Human win 58, GPT-4 (S) 47, GPT-4 (C) 54. GPT-4 (C)–human agreement 67 vs. human–human 65 for this comparison. Respondents: 272 (DPO), 122 (SFT), 199 (PPO-1). Multiple human judgments were collected only for the DPO and PPO-1 comparisons. The study covers only TL;DR.
- Out-of-distribution (p. 9, Table 1): CNN/DailyMail, GPT-4 win rate vs. ground-truth summaries. DPO 0.36 (temp 0) and 0.31 (temp 0.25); PPO 0.26 and 0.23. The text calls the margin "significant," but no significance test or test-set size is given.
- Dialogue (p. 8, Figure 3 left; p. 9): Pythia-2.8B on Anthropic-HH. GPT-4 win rates vs. chosen responses appear only in the plot. The text says DPO performs "as well or better" than Best-of-128 and 2-shot Pythia-2.8B at their best temperatures. An external PPO checkpoint could not beat the base Pythia-2.8B (p. 9). Best-of-128 is used as a "rough proxy" for PPO-level performance (p. 9), not a PPO run.
- Training curve (p. 8, Figure 3 right): DPO win rates over about 3,300 steps at two temperatures. The text says convergence is "relatively quick" and notes a "slight decrease" (p. 8, p. 10). No numbers in the text.
- Overclaim: the abstract and Sec. 7 claim "almost no tuning" and "stable" training (p. 1, p. 10). The sentiment sweep tunes $\beta$ over four values, and no seed counts, run-to-run variance, or error bars are reported for the headline comparisons.
- Scope: models up to 6B parameters only (p. 2). The authors say GPT-4 win rates depend on the prompt (p. 10). Test-set sizes for the GPT-4 evaluations are not given in the main text.
- Not in the text I read: hyperparameters, learning rates, proofs, the Table 3 weighting ablation, and the prompts are all in appendices that were cited but not provided.
- The paper's own inconsistencies: Figure 3 (left) caption says DPO "improves over chosen summaries" for the dialogue task, while the axis and task say responses (p. 8); Sec. 5.1 cites "Eq. 5" for the optimization objective, which is Eq. 7 (p. 6); Sec. 5.2 cites "Eq. 7" for the optimal policy, which is Eq. 4 (p. 6).

## Related in library

## Q&A
