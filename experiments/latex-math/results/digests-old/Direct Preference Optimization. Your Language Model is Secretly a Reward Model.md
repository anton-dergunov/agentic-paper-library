# Direct Preference Optimization: Your Language Model is Secretly a Reward Model

type: method
family: RLHF alternative; offline direct preference optimization (reward-free policy learning)
evidence: IMDb sentiment (GPT-2-large, ground-truth classifier reward), Reddit TL;DR summarization (GPT-J, GPT-4 win rates plus a human study), Anthropic-HH dialogue (Pythia-2.8B, GPT-4 win rates) vs PPO, PPO-GT, Best of N, Preferred-FT, Unlikelihood, SFT; strength: one paper, no variance or seed reporting for main results, GPT-4 as main judge, dialogue results only in a plot, PPO dialogue baseline is an external checkpoint

## Digest

- Claim: the KL-constrained reward-maximization objective of RLHF (Eq. 3, p. 3) can be optimized with a single binary cross-entropy loss on policy log-ratios, with no separate reward model and no RL loop (p. 1–2, 4, Eq. 7).
- Mechanism: the optimal policy for reward r is π_r ∝ π_ref·exp(r/β) (Eq. 4, p. 4). Inverting gives r = β·log(π_r/π_ref) + β·log Z(x) (Eq. 5, p. 4). Substituting into Bradley-Terry makes Z(x) cancel, so the preference probability depends only on the policy and π_ref (Eq. 6, p. 4). The Eq. 6 rendering is spread across lines in the text layer, so quote it with care.
- Definitions: the implicit reward is r̂_θ(x,y) = β·log(π_θ(y|x)/π_ref(y|x)) (p. 5). β controls the KL constraint. π_ref is the SFT model, or, when no SFT model exists, a model fit by maximum likelihood on the preferred completions (p. 5).
- Gradient (p. 5): raises the likelihood of y_w and lowers that of y_l, weighted by σ(r̂(x,y_l) − r̂(x,y_w)), i.e. how wrongly the implicit reward orders the pair. The paper says an unweighted version degenerates, but that evidence is in Appendix Table 3, which is not in the main text (p. 5).
- Theory: Theorem 1 claims all Bradley-Terry and Plackett-Luce reward classes can be represented in the reparameterization "under mild assumptions" (p. 6). Only a proof sketch is given; the lemma and theorem proofs are in appendices not included here.
- Consistency of the estimator is claimed by reference to [4] (p. 4–5), not shown in this paper.
- Summarization: DPO's win rate is "approximately 61%" at temperature 0.0, against PPO at 57% at its best temperature, also 0.0 (p. 9). Win rate is against reference test summaries, judged by GPT-4 (p. 7, 9). Figure 2 right (p. 7) shows the temperature curves; the text says DPO is more robust to temperature than PPO (p. 9).
- Human study (Table 2, p. 10): DPO at temperature 0.25 vs PPO at temperature 0 gets a human win rate of 58 (N = 272 respondents). SFT gets 43 (N = 122) and PPO-1 gets 17 (N = 199). GPT-4 (C) gets 54 for DPO. Human-human agreement is 65 and GPT-4 (C)-human agreement is 67 for the DPO comparison. Multiple human judgments were collected only for DPO and PPO-1 (p. 10).
- Sentiment (controlled setting): the reward–KL frontier is shown only in Figure 2 left (p. 7). The text gives no numeric values, so the claim that DPO "provides the highest expected reward for all KL values" rests on the plot. The sweep covers PPO target KL {3, 6, 9, 12}, β {0.05, 0.1, 1, 5}, α {0.05, 0.1, 0.5, 1}, and seeds for Preferred-FT (p. 8). The text says the sweep totals 22 runs, but the seed count is not stated, so the total cannot be checked.
- Dialogue (Anthropic-HH, Pythia-2.8B with Preferred-FT as reference): GPT-4 win rates vs chosen completions appear only in Figure 3 left (p. 8). The text says DPO matches or beats Best of 128 and 2-shot Pythia (p. 9), and the paper calls DPO "the only computationally efficient method" that improves over the chosen completions (p. 9).
- The PPO dialogue baseline is an external 6B checkpoint from a third-party repository. The authors could not find a prompt or temperature where it beat base Pythia-2.8B (p. 9). Best of 128 is used as a "rough proxy" for PPO-level performance, which is the authors' own inference (p. 9).
- Out-of-distribution (CNN/DailyMail, Table 1, p. 9), win rate vs ground-truth summaries: DPO 0.36 vs PPO 0.26 at temperature 0; DPO 0.31 vs PPO 0.23 at temperature 0.25. The text calls the margin "significant", but no statistical test is reported.
- β: the text says β was "not meaningfully" tuned for summarization and dialogue (p. 9). The values used for those experiments are not in the main text.
- Headline numbers depend on GPT-4 judgments, and the paper notes that the prompt changes win rates (p. 10). The GPT-4 (C) prompt was chosen for the main results because it tracks humans better (p. 10).
- Not in the text: variance or confidence intervals for main results, seed counts for most runs, full hyperparameters, prompts and training details (these are in appendices not provided). Models are limited to 6B parameters (p. 2, p. 10). Reward over-optimization is listed as future work (p. 10).
- The abstract's claim that DPO "exceeds PPO-based RLHF in ability to control sentiment" rests on a synthetic classifier reward and a plot-only frontier (p. 1, p. 7).
- Training is offline on a fixed preference dataset. The paper says sampling from π_ref is needed only to collect that data, and public datasets are assumed to be reusable (p. 5).
- The paper's own inconsistencies: the Figure 3 caption calls the Anthropic-HH comparison "chosen summaries" although the task is dialogue (p. 8); the sentiment sweep reports 22 runs, but the printed values give 12 (4 PPO targets, 4 β, 4 α), and the Preferred-FT seed count is not stated (p. 8).

## Related in library

## Q&A
