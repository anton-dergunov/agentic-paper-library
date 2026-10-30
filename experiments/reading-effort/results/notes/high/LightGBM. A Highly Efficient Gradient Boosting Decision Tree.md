# LightGBM: A Highly Efficient Gradient Boosting Decision Tree

type: method
family: histogram-based gradient boosting decision trees (GBDT) with instance sampling and sparse-feature bundling
evidence: 5 public datasets (Allstate, Flight Delay, LETOR, KDD10, KDD12), compared against XGBoost (pre-sorted and histogram variants), the authors' own LightGBM without GOSS/EFB, and stochastic gradient boosting (SGB); strength: vendor-run (Microsoft authors benchmarking their own system), single machine, ablation of GOSS and EFB in Table 2, GOSS-vs-SGB sampling sweep on LETOR only, parameter settings deferred to the supplement

## Digest

- **Claim.** Histogram building costs O(#data × #feature) and dominates GBDT training. LightGBM cuts both factors with two techniques, Gradient-based One-Side Sampling (GOSS) and Exclusive Feature Bundling (EFB), and keeps "almost the same accuracy". It reports speed-ups of "up to over 20 times" (p. 1, Abstract).
- **GOSS.** The paper treats instances with small |gradient| as already well-trained.
  - It keeps the top a×100% of instances by |gradient| and randomly samples b×100% of the rest.
  - When computing the variance gain, it multiplies the sampled small-gradient instances by (1−a)/b to limit the shift in the data distribution (p. 4, Alg. 2, Eq. 1).
- **Split criterion.** The variance gain is defined as the squared sums of gradients on the left and right of a split, each divided by the child's count, all scaled by 1/n_O (p. 4, Definition 3.1).
- **GOSS theory.**
  - Theorem 3.2 bounds the GOSS approximation error with probability at least 1−δ, using C_{a,b} = (1−a)/√b · max over A^c of |g_i| (p. 4, Eq. 2). The equation's layout is garbled in the text layer, so it is not quoted exactly here.
  - The text says that for balanced splits the error "decreases to 0 in O(√n)" (p. 5). This rate looks garbled or mis-stated.
  - Random sampling is presented as GOSS with a = 0, and GOSS beats it when C_{0,β} > C_{a,β−a} (p. 5).
  - The proof is only in the supplementary material (p. 4).
- **EFB.**
  - Finding the minimum number of exclusive feature bundles is shown NP-hard by reduction from graph colouring (p. 5, Theorem 4.1).
  - Features are bundled with a greedy colouring heuristic: features are vertices, edges are weighted by conflicts, features are ordered by degree, and conflicts are capped (p. 6, Alg. 3).
  - Bundling cost is O(#feature²), run once before training. For millions of features, ordering by nonzero count replaces the graph (p. 6).
- **Merging bundled features.** Features in a bundle are merged by adding bin offsets so each original feature occupies its own bin range (p. 6, Alg. 4).
- **Unsupported assertions.**
  - The greedy bundling is said to have "a constant approximation ratio" (p. 2, p. 6), but the main text gives no proof.
  - Tolerating a conflict rate γ is claimed to affect accuracy by at most O([(1 − γ)n]−2/3). The exponent appears garbled, and the claim is deferred to supplementary Proposition 2.1 (p. 6).
- **Setup.**
  - Hardware: two E5-2670 v3 CPUs (24 cores), 256GB memory, 16 threads (p. 6).
  - xgb_his, lgb_baseline and LightGBM use leaf-wise growth. xgb_exa supports only layer-wise growth and was tuned to grow similar trees (p. 6–7).
  - Settings: a = 0.05, b = 0.05 for Allstate, KDD10 and KDD12; a = 0.1, b = 0.1 for Flight Delay and LETOR; γ = 0 (p. 7).
- **Datasets (p. 7, Table 1).** Allstate: 12 M rows, 4228 features. Flight Delay: 10 M rows, 700 features. LETOR: 2M rows, 136 features, dense. KDD10: 19M rows, 29M features. KDD12: 119M rows, 54M features.
- **Training time per iteration, LightGBM vs lgb_baseline (p. 7, Table 2).**

  | Dataset | LightGBM (s) | lgb_baseline (s) |
  |---|---|---|
  | Allstate | 0.28 | 6.07 |
  | Flight Delay | 0.22 | 1.39 |
  | LETOR | 0.31 | 0.49 |
  | KDD10 | 2.85 | 39.85 |
  | KDD12 | 12.67 | 168.26 |

  The text states speed-ups of 21x, 6x, 1.6x, 14x and 13x respectively (p. 7).
- **Against XGBoost (p. 7, Table 2).**
  - xgb_exa takes 10.85, 5.94, 5.55, 108.27 and 191.99 s per iteration on the same five datasets.
  - xgb_his runs out of memory (OOM) on KDD10 and KDD12. The text claims "up to 9x" over xgb_his, on Allstate (2.63 vs 0.28).
- **How speed-up is measured.** Speed-ups are per-iteration times, justified by the statement that all algorithms "converge after similar number of iterations" (p. 7). Wall-clock curves are shown only for Flight Delay and LETOR (p. 7, Figures 1–2).
- **Accuracy, test AUC or NDCG@10 (p. 7, Table 3).**

  | Dataset | LightGBM | lgb_baseline | xgb_exa | SGB |
  |---|---|---|---|---|
  | Allstate | 0.6093 ± 9e-5 | 0.6093 | 0.6070 | 0.6064 ± 7e-4 |
  | Flight Delay | 0.7846 ± 4e-5 | 0.7847 | 0.7601 | 0.7780 ± 8e-4 |
  | LETOR | 0.5275 ± 5e-4 | 0.5277 | 0.4977 | 0.5239 ± 6e-4 |
  | KDD10 | 0.78732 ± 1e-4 | 0.78735 | 0.7796 | 0.7759 ± 3e-4 |
  | KDD12 | 0.7051 ± 5e-5 | 0.7049 | 0.7029 | 0.6989 ± 8e-4 |

  - The baselines are reported without a spread.
  - Results come "from the iteration with the best score" (p. 7). The text does not say this iteration was chosen on a separate validation set.
- **GOSS alone (EFB_only vs LightGBM, p. 8, Table 2).**
  - The text claims "nearly 2x speed-up" from GOSS using 10%–20% of the data (p. 8).
  - On Flight Delay, Table 2 shows only 0.27 vs 0.22 s, and on LETOR 0.46 vs 0.31 s.
- **EFB alone (lgb_baseline vs EFB_only, p. 7, Table 2).**
  - Allstate: 6.07 → 0.71 s. KDD10: 39.85 → 6.33 s. KDD12: 168.26 → 20.23 s. LETOR (dense): 0.49 → 0.46 s.
  - The γ study is only in the supplement (p. 8).
- **GOSS vs SGB at equal sampling ratio (LETOR, NDCG@10, p. 8, Table 4).**
  - At ratio 0.1: GOSS 0.5224 vs SGB 0.5182. At ratio 0.4: 0.5296 vs 0.5267. GOSS is higher at every ratio from 0.1 to 0.4.
  - The a and b settings are in the supplement. Standard deviations are described as "small" but not printed.
  - This is one dataset only, yet the text generalises that "GOSS is a more effective sampling method" (p. 8).
- **Overclaim on memory.** The conclusion says LightGBM outperforms XGBoost and SGB in "memory consumption" (p. 8). No memory measurements are reported; the only memory evidence is xgb_his going OOM (p. 7, Table 2).
- **Not disclosed in the main text:** full hyperparameters, the number of iterations, the supplement's training curves for the other datasets, and per-run variance for the baselines.
- **The paper's own inconsistencies:**
  - The size of the small-gradient sample B is defined two ways. Alg. 2 uses randN = b × len(I), and the text says b×100% are sampled "from the rest" (p. 3–4). Section 3.2 instead says |B| = b × |A^c| (p. 4). The normaliser (1−a)/b fits only the first definition.
  - Alg. 3 uses a max conflict count K and indexes bundlesConflict[i], while the text controls conflicts by a rate γ (p. 5–6).
  - The merged-bundle example gives range [10, 30) for the shifted feature, then calls the bundle range "[0, 30]" (p. 6).

## Related in library

- XGBoost. A Scalable Tree Boosting System: the main baseline, in pre-sorted (xgb_exa) and histogram (xgb_his) variants, beaten on time per iteration and OOM on KDD10/KDD12.
- Greedy function approximation. A gradient boosting machine.: LightGBM is an implementation of GBDT, the gradient boosting method that paper introduces.
- Scikit-learn. Machine Learning in Python: cited as a GBDT implementation using the pre-sorted split-finding algorithm; it is not benchmarked.

## Q&A
