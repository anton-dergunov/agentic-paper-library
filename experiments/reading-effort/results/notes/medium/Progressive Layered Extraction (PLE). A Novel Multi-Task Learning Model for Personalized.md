# Progressive Layered Extraction (PLE): A Novel Multi-Task Learning (MTL) Model for Personalized Recommendations

type: method
family: gated mixture-of-experts multi-task learning for recommendation ranking
evidence: Tencent News video dataset (VTR/VCR, CTR/VCR, 3–4 task groups), a 4-week online A/B test, synthetic data, census-income and Ali-CCP; compared with single-task, hard sharing, asymmetric/customized sharing, cross-stitch, sluice, MMOE and ML-MMOE; strength: vendor-run, single runs, no significance tests or variance, public baselines limited to MMOE

## Digest

- **Claim.** MTL rankers in recommendation show a "seesaw phenomenon": one task improves while another degrades relative to the single-task model. PLE is proposed to remove it and to beat MMOE on every task (p. 1–2).
- **CGC (Customized Gate Control).** CGC has task-specific expert modules and shared expert modules. Each task's softmax gate weights only the shared experts and that task's own experts (Eq. 2–5, p. 5). CGC removes MMOE's links from a task's tower to the other tasks' experts.
- **PLE.** PLE stacks several CGC-like "extraction networks". It adds a gate for the shared experts that mixes all experts of the layer. Higher-level gates take the lower-level gate outputs as their selector, not the raw input (Eq. 6–7, p. 6). The paper calls this "progressive separation routing".
- **Loss.** Each task's loss is masked to its own sample space, for example share/comment only after a click (Eq. 9, p. 7).
- **Dynamic loss weights.** ω_k^(t) = ω_k,0 × γ_k^t per epoch (Eq. 10, p. 7). The values of ω_k,0 and γ_k are not given, and the schedule is not ablated.
- **New baselines.** Asymmetric sharing and customized sharing are introduced as baselines (p. 4). ML-MMOE is a two-level MMOE built for fair depth (p. 7).
- **Industrial data.** 8 days of Tencent News video logs: 46.926 million users, 2.682 million videos, 0.995 billion samples (p. 7). The first 7 days are training and the rest is the test set.
- **Industrial setup.** Towers are three-layer MLPs [256, 128, 64]. Experts are single-layer, and multi-level models have two levels (p. 7). The tuned expert counts are not reported.
- **Metric.** MTL gain is the MTL model's metric minus the single-task metric, with the sign flipped for MSE (Eq. 11, p. 7).
- **VTR/VCR group (complex correlation).**
  - Single-task: VTR AUC 0.6787, VCR MSE 0.1321.
  - PLE: 0.6831 / 0.1307, MTL gain +0.0044 / +0.0013.
  - CGC: 0.6832 / 0.1320.
  - MMOE: 0.6803 / 0.1319.
  - ML-MMOE: 0.6815 / 0.1329.
  - Sluice: 0.6825 / 0.1329 (p. 7, Table 1).
- **Overclaim on VTR/VCR.** The text says CGC and PLE "significantly outperform all baseline models in VTR". The margin over sluice is 0.6832/0.6831 vs 0.6825, and no significance test is reported (p. 8). The paper asserts that a 0.1% AUC/MSE change matters online (p. 4).
- **CTR/VCR group (normal correlation).**
  - Single-task: CTR AUC 0.7379, VCR MSE 0.1179.
  - PLE: 0.7406 / 0.1150.
  - CGC: 0.7398 / 0.1155.
  - MMOE: 0.7382 / 0.1175.
  - Cross-stitch is the only model with a negative gain, −0.0158 on CTR (p. 8, Table 2).
- **Online A/B test.** 4 weeks, VTR+VCR; figures are improvements over the single-task model (p. 8, Table 3).
  - PLE: total view count +4.17%, total watch time +3.57%.
  - CGC: +3.92% / +2.75%.
  - MMOE: +1.94% / +1.73%.
  - ML-MMOE: +1.96% / +1.10%.
  - Hard sharing: −1.65% / −1.79%.
- **Abstract's online figures.** The abstract's "2.23% increase in view-count and 1.84% … watch time compared to SOTA MTL models" (p. 1) does not appear in Table 3. Table 3 reports only improvement over the single-task model.
- **Multi-task groups.** PLE's MTL gain over single-task (p. 8, Table 4):
  - VTR+VCR+SHR+CMR: PLE +0.0128 / +0.0017 / +0.0058 / +0.0080; CGC +0.0097 / +0.0016 / +0.0008 / +0.0012.
  - CGC's SHR gain is −0.0001 in the VTR+VCR+SHR group.
- **Overclaim on multi-task groups.** The text says "PLE outperforms CGC significantly in all cases" (p. 8). Some margins are +0.0000 vs +0.0001 (CMR) and +0.0016 vs +0.0017 (VCR).
- **Public data.** PLE is compared only with MMOE and single-task (p. 10, Table 5).
  - Census task1 AUC: PLE 0.9522 vs single 0.9445 and MMOE 0.9393.
  - Ali-CCP CVR AUC: PLE 0.6097 vs single 0.6040 and MMOE 0.5738.
  - Synthetic data: PLE has "87.2% increase in MTL gain over MMOE on average" (p. 9). The per-correlation results are only in Figure 7 (p. 9).
- **Seesaw plot.** The seesaw evidence for the baselines on VTR/VCR is shown in Figure 3 (p. 4) and repeated in Table 1.
- **Expert utilization.** Here CGC and PLE have one expert per module and MMOE/ML-MMOE have three per layer (p. 9, Figure 8). The paper reads MMOE's non-zero, similar weights as evidence that it cannot converge to CGC/PLE. This is an interpretation, not a test.
- **The paper's own inconsistencies:** Census task1 MMOE AUC 0.9393 is below single-task 0.9445, yet its MTL gain is printed as +0.0048 (p. 10, Table 5). The abstract says "1 billion samples" while the dataset section gives 0.995 billion (p. 1; p. 7).

## Related in library

- Modeling Task Relationships in Multi-task Learning with Multi-gate Mixture-of-Experts: PLE extends MMOE with task-specific experts and multi-level routing, and uses MMOE as its main baseline and synthetic-data protocol.
- Recommending What Video to Watch Next. A Multitask Ranking System: cited as the YouTube application of MMOE to multi-objective video ranking, which PLE positions against.
