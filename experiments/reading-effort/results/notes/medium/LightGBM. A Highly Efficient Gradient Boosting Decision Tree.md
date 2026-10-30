# LightGBM: A Highly Efficient Gradient Boosting Decision Tree

type: method
family: gradient boosting decision trees (histogram-based), with data subsampling and feature bundling
evidence: 5 public datasets (Allstate, Flight Delay, LETOR, KDD10, KDD12), compared with XGBoost (exact and histogram), LightGBM without GOSS/EFB, and SGB; strength: run by the method's authors on their own implementation, on one server, partial ablation (EFB_only; GOSS vs SGB on LETOR only), test accuracy taken at the best iteration

## Digest

- **Claim.** Histogram-based GBDT costs O(#data × #feature) per histogram build (p. 2). Two techniques cut #data (GOSS) and #feature (EFB) with "almost the same accuracy", for up to "over 20 times" speed-up over conventional GBDT (p. 1).
- **GOSS (Gradient-based One-Side Sampling).**
  - It sorts instances by |gradient| and keeps the top a×100%. It randomly samples b×100% of the rest and multiplies those sampled small-gradient instances by (1−a)/b when computing variance gain (p. 4, Alg. 2, Eq. 1).
  - Rationale: large-gradient ("under-trained") instances contribute more to information gain.
- **GOSS theory.**
  - Theorem 3.2 bounds the gain approximation error with probability 1−δ (p. 4, Eq. 2). Random sampling is the special case a = 0.
  - GOSS beats it when C_{0,β} > C_{a,β−a} (p. 5). The proof is in supplementary material, not included here.
  - The extracted text of Eq. 2, the definitions under it and the stated rate ("decreases to 0 in O(√n)", p. 5) are garbled, so the exact expressions cannot be quoted.
- **EFB (Exclusive Feature Bundling).**
  - It bundles features that rarely take nonzero values at the same time into one feature. Bin offsets keep the original values recoverable (p. 6, Alg. 4).
  - Finding the optimal bundling is shown NP-hard by reduction from graph colouring (p. 5, Theorem 4.1). A greedy colouring-style algorithm orders features by degree and allows a conflict budget γ (p. 6, Alg. 3).
  - Its cost is O(#feature²), run once before training. For very many features, ordering by nonzero count is proposed instead (p. 6).
- **Accuracy cost of conflicts.** Allowing conflicts is said to affect accuracy by at most O([(1 − γ)n]^−2/3) (p. 6). Proposition 2.1 is in the supplement. All experiments use γ = 0 (p. 7); the γ study is in the supplement (p. 8).
- **Sparse optimisation in the baseline.** lgb_baseline already includes a per-feature nonzero table, so histogram cost is O(#non_zero_data) (p. 6).
- **Setup.**
  - Baselines: xgb_exa (pre-sorted), xgb_his and lgb_baseline. All are leaf-wise except xgb_exa, which was tuned to grow similar trees (p. 6–7).
  - GOSS settings: a = 0.05, b = 0.05 on Allstate, KDD10 and KDD12; a = 0.1, b = 0.1 on Flight Delay and LETOR (p. 7).
  - Hardware: 2× E5-2670 v3, 16 threads (p. 6).
  - Parameter details are in the supplement.
- **Datasets** (p. 7, Table 1):
  - Allstate: 12 M rows, 4228 features
  - Flight Delay: 10 M rows, 700 features
  - LETOR: 2M rows, 136 features
  - KDD10: 19M rows, 29M features
  - KDD12: 119M rows, 54M features
- **Time per iteration, LightGBM vs lgb_baseline** (p. 7, Table 2):
  - Allstate: 0.28 vs 6.07 s
  - Flight Delay: 0.22 vs 1.39
  - LETOR: 0.31 vs 0.49
  - KDD10: 2.85 vs 39.85
  - KDD12: 12.67 vs 168.26
  - The text states these as 21x, 6x, 1.6x, 14x and 13x (p. 7).
- **Time vs XGBoost.**
  - xgb_his ran out of memory (OOM) on KDD10 and KDD12.
  - On Allstate, xgb_his took 2.63 s per iteration, and LightGBM is "up to 9x" faster (p. 7).
  - xgb_his is faster than lgb_baseline on Allstate (2.63 vs 6.07) and Flight Delay (1.05 vs 1.39) (p. 7, Table 2). The large speed-ups are therefore relative to the authors' own unoptimised baseline.
- **Speed-ups are per iteration.** They assume "all algorithms converge after similar number of iterations" (p. 7). Wall-clock curves are shown only for Flight Delay and LETOR (p. 7, Figures 1–2); the rest are in the supplement.
- **Accuracy, LightGBM vs lgb_baseline** (p. 7, Table 3):
  - Allstate AUC: 0.6093 vs 0.6093
  - Flight Delay AUC: 0.7846 vs 0.7847
  - LETOR NDCG@10: 0.5275 vs 0.5277
  - KDD10 AUC: 0.78732 vs 0.78735
  - KDD12 AUC: 0.7051 vs 0.7049
- **Accuracy vs xgb_exa.** On LETOR, xgb_exa gets 0.4977, well below LightGBM (p. 7, Table 3).
- **Accuracy vs SGB.** SGB (same sampling ratio as LightGBM) is lower on every dataset, for example Flight Delay 0.7780 ± 8e-4 vs LightGBM 0.7846 ± 4e-5 (p. 7, Table 3).
- **Accuracy selection.** Accuracy is taken from "the iteration with the best score" (p. 7). It is not said whether this was chosen on a validation set or on the test set.
- **GOSS alone.**
  - The text says GOSS gives "nearly 2x speed-up by its own with using 10% - 20% data" (EFB_only vs LightGBM, p. 8, Table 2).
  - The Table 2 ratios differ considerably across datasets, so "nearly 2x" is a loose summary.
  - There is no GOSS-only (without EFB) configuration.
- **GOSS vs SGB on LETOR** (NDCG@10, p. 8, Table 4):
  - At sampling ratio 0.1: GOSS 0.5224 vs SGB 0.5182.
  - At 0.4: GOSS 0.5296 vs SGB 0.5267.
  - Standard deviations are not printed, only described as "small". The a/b settings are in the supplement.
- **EFB alone.** EFB_only vs lgb_baseline shows large gains on sparse sets, for example KDD10 6.33 vs 39.85 s and Allstate 0.71 vs 6.07 s (p. 7, Table 2).
- **Overclaim on memory.** The conclusion claims LightGBM outperforms XGBoost and SGB in "memory consumption" (p. 8). No memory measurements are reported, only xgb_his running out of memory.
- The paper's own inconsistencies:
  - The size of the small-gradient sample disagrees. Alg. 2 sets randN ← b × len(I) (p. 3), but Sec. 3.2 samples B "with size b × |A^c|" (p. 4). The normaliser (1−a)/b matches only the former.
  - Alg. 3 tests bundlesConflict[i] with the feature index instead of the bundle index j, and takes a count K while the text speaks of a rate γ (p. 5–6).
  - The merged bundle range is written "[0, 30]" after the ranges "[0, 10)" and "[10, 30)" (p. 6).

## Related in library

- XGBoost. A Scalable Tree Boosting System: main baseline (exact and histogram versions); LightGBM claims faster training at similar accuracy.
- Greedy function approximation. A gradient boosting machine.: the GBDT framework ([1]) that LightGBM accelerates.
- Scikit-learn. Machine Learning in Python: cited as a pre-sorted GBDT implementation in related work, not benchmarked.
