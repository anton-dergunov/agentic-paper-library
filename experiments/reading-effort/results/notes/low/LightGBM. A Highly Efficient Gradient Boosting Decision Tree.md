# LightGBM: A Highly Efficient Gradient Boosting Decision Tree

type: method
family: gradient boosting decision trees (histogram-based), data and feature reduction
evidence: 5 public datasets (Allstate, Flight Delay, LETOR, KDD10, KDD12), compared with XGBoost (pre-sorted xgb_exa and histogram xgb_his), its own lgb_baseline, and SGB; strength: one run setup on one 16-thread server, by the authors; ablation of EFB vs GOSS in Table 2; GOSS vs SGB only on LETOR; parameter details and γ study are in the supplementary material

## Digest

- **Claim.** Histogram GBDT spends most of its time building histograms, at a cost of O(#data × #feature) (p. 2). LightGBM cuts #data with GOSS and #feature with EFB, and the abstract says this gives "up to over 20 times" speed-up at "almost the same accuracy" (p. 1).
- **GOSS (Gradient-based One-Side Sampling).**
  - It keeps the top a×100% of instances by absolute gradient.
  - From the rest it randomly samples b×100%.
  - The sampled small-gradient instances are up-weighted by (1−a)/b when the variance gain is computed (p. 4, Alg. 2, Eq. 1).
  - Random sampling is the special case a = 0 (p. 5).
- **GOSS theory.** Theorem 3.2 bounds the gain-estimation error. If the split is not too unbalanced, the error vanishes as n grows (pp. 4–5). The proof is in the supplementary material.
  - The bound (Eq. 2) and its √n terms are garbled in the text layer, so exact forms are not quoted here.
  - The condition for GOSS to beat random sampling (C0,β > Ca,β−a) is stated, not tested empirically (p. 5).
- **EFB (Exclusive Feature Bundling).**
  - It bundles features that rarely take nonzero values at the same time into one feature. Each feature's bins get an offset, so the original histograms can be recovered (p. 6, Alg. 4).
  - Optimal bundling is NP-hard, shown by reduction from graph coloring (p. 5, Thm 4.1).
  - A greedy coloring heuristic is used: order features by degree, or by nonzero count when there are millions of features. It costs O(#feature²) and runs once before training (p. 6, Alg. 3).
  - Allowing a conflict rate γ affects accuracy by at most O([(1−γ)n]^−2/3) (p. 6, from the supplementary material). All experiments use γ = 0 (p. 7).
- **Other design choices.** Leaf-wise tree growth is used for xgb_his, lgb_baseline and LightGBM. xgb_exa is layer-wise only and was tuned to grow similar trees (pp. 6–7). GOSS settings were a = b = 0.05 on Allstate and the KDDs, and a = b = 0.1 on Flight Delay and LETOR (p. 7).
- **Time per iteration (p. 7, Table 2), xgb_exa / xgb_his / lgb_baseline / EFB_only / LightGBM, in seconds.**
  - Allstate: 10.85 / 2.63 / 6.07 / 0.71 / 0.28.
  - Flight Delay: 5.94 / 1.05 / 1.39 / 0.27 / 0.22.
  - LETOR: 5.55 / 0.63 / 0.49 / 0.46 / 0.31.
  - KDD10: 108.27 / OOM / 39.85 / 6.33 / 2.85.
  - KDD12: 191.99 / OOM / 168.26 / 20.23 / 12.67.
- **Stated speed-ups (p. 7).**
  - Versus lgb_baseline: 21x on Allstate, 6x on Flight Delay, 1.6x on LETOR, 14x on KDD10 and 13x on KDD12.
  - Versus xgb_his: up to 9x, on Allstate.
  - The speed-up is per iteration, justified by "similar number of iterations" to converge.
  - Wall-clock curves are shown only for Flight Delay and LETOR (p. 7, Figs. 1–2).
- **Test accuracy (p. 7, Table 3), LightGBM vs lgb_baseline.**
  - Allstate AUC: 0.6093 ± 9e-5 vs 0.6093.
  - Flight Delay AUC: 0.7846 vs 0.7847.
  - LETOR NDCG@10: 0.5275 vs 0.5277.
  - KDD10 AUC: 0.78732 vs 0.78735.
  - KDD12 AUC: 0.7051 vs 0.7049.
  - SGB at the same sampling ratio is lower everywhere, for example 0.7759 on KDD10.
  - xgb_exa is lower on LETOR (0.4977).
- **GOSS vs SGB on LETOR (p. 8, Table 4).** GOSS beats SGB at every sampling ratio from 0.1 to 0.4. At 0.1 it scores 0.5224 vs 0.5182; at 0.4 it scores 0.5296 vs 0.5267. The a and b values per ratio are only in the supplementary material.
- **Speed-up from GOSS alone.** The paper says GOSS gives "nearly 2x speed-up" with 10%–20% of the data, from EFB_only vs LightGBM (p. 8). The per-dataset Table 2 pairs vary noticeably around that figure, for example Flight Delay 0.27 vs 0.22.
- **Claims beyond the evidence.**
  - The conclusion says LightGBM outperforms XGBoost and SGB in "memory consumption" (p. 8). The only memory evidence is xgb_his running out of memory (OOM) on KDD10 and KDD12; memory is never measured.
  - Accuracy is reported from the best iteration on the test set (p. 7).
- **Out of scope.** GPU and parallel training are excluded (p. 2).
- The paper's own inconsistencies:
  - Alg. 3 checks `bundlesConflict[i]` (the feature index) where the bundle index j appears meant, and its input is "K: max conflict count" while the text controls conflicts by the rate γ (p. 5, Alg. 3; p. 6).
  - The bundle example gives feature B the range [10, 30) but the merged bundle range as [0, 30] (p. 6).
  - Alg. 2 labels its loop bound "d: iterations", while Alg. 1 uses d for max depth (p. 3).

## Related in library

- XGBoost. A Scalable Tree Boosting System: the main baseline (xgb_exa and xgb_his), beaten on speed per iteration at similar accuracy.
- Greedy function approximation. A gradient boosting machine.: the GBDT framework (cited as [1]) that LightGBM accelerates.
- Scikit-learn. Machine Learning in Python: cited as a pre-sorted GBDT implementation; not benchmarked.
