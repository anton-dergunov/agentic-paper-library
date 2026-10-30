# Progressive Layered Extraction (PLE): A Novel Multi-Task Learning (MTL) Model for Personalized Recommendations

type: method
family: gated mixture-of-experts multi-task learning for ranking
evidence: Tencent News video dataset (offline: 2-task and 3–4-task groups) plus a 4-week online A/B test, against single-task, hard sharing, cross-stitch, sluice, asymmetric/customized sharing, MMOE and ML-MMOE. Also synthetic data, census-income and Ali-CCP (single-task and MMOE only); strength: single runs with no variance or significance tests, vendor-run online test, partial ablation (CGC vs PLE, expert utilization)

## Digest

- **Seesaw phenomenon.** The paper names and defines it: an MTL model improves one task by hurting another, so it cannot beat single-task models on all tasks at once. The authors observe it under complex, sample-dependent task correlations, such as VCR (regression) and VTR (classification) at Tencent (p. 1, p. 3–4).
- **Fig. 3 bubble plot (p. 4, Figure 3).** On VCR/VTR, no baseline MTL model improves both tasks clearly. MMOE improves VCR by only +0.0001 over single-task (p. 4).
- **"Significant" threshold.** The authors claim a 0.1% change in AUC or MSE is significant for online metrics in their system (p. 4). The paper reports no statistical tests.
- **CGC (Customized Gate Control).**
  - Each task has its own experts, and there are shared experts.
  - Task k's gate is a softmax over a linear map of the input. It weights only the shared experts plus task k's own experts (Eq. 2–5, p. 5).
  - Unlike MMOE, a task's tower cannot reach other tasks' specific experts.
- **PLE.**
  - PLE stacks several CGC-like extraction layers.
  - It adds a gate for the shared experts that covers all experts in the layer.
  - Higher-level gates take the lower-level gate outputs as selector instead of the raw input. This gives "progressive separation" routing (Eq. 6–7, p. 6).
- **Loss.**
  - Each task's loss is averaged only over samples inside that task's sample space. For example, share and comment exist only after a click (Eq. 9, p. 7).
  - Loss weights decay by epoch as ω_k,0 × γ_k^t (Eq. 10, p. 7). The values of ω_k,0 and γ_k are not reported, and this loss scheme is not ablated.
- **MTL gain.** Defined as the MTL model's metric minus the single-task metric, with the sign flipped for negative metrics such as MSE (Eq. 11, p. 7).
- **Industrial data and setup.**
  - 46.926 million users, 2.682 million videos and 0.995 billion samples, collected over 8 days. The first 7 days are used for training (p. 7).
  - Towers are MLPs of size [256, 128, 64]. Experts are single-layer networks.
  - All multi-level models are two-level (p. 7).
  - Expert counts after tuning are not disclosed.
- **VTR/VCR results** (p. 7, Table 1):
  - Single-task: AUC 0.6787, MSE 0.1321.
  - MMOE: 0.6803 / 0.1319.
  - CGC: 0.6832 / 0.1320.
  - PLE: 0.6831 / 0.1307, the best VCR MSE.
  - On VTR AUC, CGC is marginally above PLE.
- **CTR/VCR results** (p. 8, Table 2):
  - Single-task: 0.7379 / 0.1179.
  - MMOE: 0.7382 / 0.1175.
  - PLE: 0.7406 / 0.1150.
  - In this group every model except cross-stitch has positive gain on both tasks.
- **Online A/B, 4 weeks, VTR+VCR** (p. 8, Table 3). Gains over the single-task model:

  | Model | View count | Watch time |
  |---|---|---|
  | PLE | +4.17% | +3.57% |
  | CGC | +3.92% | +2.75% |
  | MMOE | +1.94% | +1.73% |
  | Hard sharing | −1.65% | −1.79% |

  The abstract's "2.23% view-count, 1.84% watch time vs SOTA MTL" (p. 1) is not printed in the table. Its baseline is only implied.
- **3–4-task groups** (p. 8, Table 4):
  - With VTR+VCR+SHR+CMR, PLE's gains are +0.0128, +0.0017, +0.0058 and +0.0080. CGC's are +0.0097, +0.0016, +0.0008 and +0.0012.
  - CGC has −0.0001 on SHR in the 3-task group.
- **Public data.**
  - Synthetic data: PLE achieves an "87.2% increase in MTL gain over MMOE on average" (p. 9). The per-task results are shown only in Figure 7.
  - Census-income, PLE: 0.9522 on task 1 and 0.9945 on task 2, against single-task 0.9445 and 0.9923 (p. 10, Table 5).
  - Ali-CCP CVR: PLE 0.6097, single-task 0.6040, MMOE 0.5738 (p. 10, Table 5).
  - Only single-task and MMOE are compared on public data.
- **Expert utilization** (p. 9, Figure 8):
  - Per-task gates in MMOE weight the experts similarly and give no expert zero weight. The authors take this as evidence that MMOE cannot converge to the CGC/PLE structure.
  - This argument is qualitative and rests on one task group.
- **Where the text claims more than the tables show.** The text repeatedly says "significantly outperform", but many differences are around 1E-4 to 1E-3, with no error bars.
- **Synthetic-data reproducibility.** The synthetic-data hyperparameters are set by the authors (c=1, m=10, d=512, 1.4 million samples), because MMOE's paper did not give them (p. 8).
- The paper's own inconsistencies:
  - Census-income Task1 lists MMOE at AUC 0.9393, below single-task 0.9445, yet prints an MTL gain of +0.0048 (p. 10, Table 5).
  - The PLE VCR gain is printed as +0.0013, but its MSE of 0.1307 against 0.1321 does not match that figure exactly (p. 7, Table 1).
  - The abstract cites "1 billion samples" (p. 1), while the dataset section gives 0.995 billion (p. 7).

## Related in library

- Modeling Task Relationships in Multi-task Learning with Multi-gate Mixture-of-Experts: this is the main baseline. PLE removes MMOE's full expert sharing and reuses MMOE's synthetic data and census setup.
- Recommending What Video to Watch Next. A Multitask Ranking System: cited as the YouTube use of MMOE in industrial MTL ranking, which PLE contrasts with.
- Progressive Layered Extraction (PLE). A Novel Multi-Task Learning Model for Personalized: this paper itself.
