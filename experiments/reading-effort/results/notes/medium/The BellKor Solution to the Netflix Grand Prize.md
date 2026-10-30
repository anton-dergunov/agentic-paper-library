# The BellKor Solution to the Netflix Grand Prize

type: system
family: temporal baseline biases + timeSVD++ factorization + time-aware item-item neighborhood + conditional RBMs, blended with GBDT
evidence: Netflix Prize Quiz-set RMSE for individual predictors and blends, compared against Netflix Cinematch, earlier BellKor models and its own variants; strength: one dataset, single runs, constants tuned by hand on Probe, Test scores never disclosed, few controlled ablations

## Digest

- **Scope.** This is a partial report. It covers only the predictors added since the 2008 Progress Prize report (p. 1):
  - improved time-aware baseline predictors;
  - timeSVD++ with those baselines;
  - a time-decayed neighborhood model;
  - RBMs with conditional visible units;
  - GBDT blending.
- **Not disclosed here.**
  - The final ensemble blend was handled by the BigChaos team and is not described (p. 8).
  - Reported RMSEs are on the Quiz set. Test scores were never disclosed by Netflix (p. 1).
- **Data.** Over 100 million dated ratings from m = 480,189 users on n = 17,770 movies (p. 1). The Hold-out set holds the last nine ratings per user and is split into Probe, Quiz and Test (p. 1).
- **Tuning.** Constants were tuned by a manual greedy search on Probe and never revisited. The paper admits this is suboptimal. It argues that over-tuning a single predictor adds little to the blend (pp. 1–2).
- **Baseline predictors (pp. 2–3).**
  - Item bias uses 30 time bins of about ten weeks each.
  - User bias has three parts: a drift term αu·sign(t−tu)|t−tu|^β with β = 0.4, a per-user-day term but, and a per-user-day scale cu(t) multiplying the item bias.
  - Results: model (9) RMSE 0.9605; adding cu(t), model (10), gives 0.9555. Cinematch's published Quiz RMSE is 0.9514 (p. 3).
- **"Frequency" term.**
  - Definition: fui = ⌊log_a Fui⌋, where Fui is the number of ratings user u gave that day. The idea is credited to the Pragmatic Theory team.
  - It enters as a movie-by-frequency bias bi,fui. This drops baseline RMSE from 0.9555 to 0.9278 (p. 3).
  - The paper says most of this gain disappears in full models that include interaction terms (p. 3).
  - Its explanation is hypothesis only: bulk-rating days reflect biased selection of which movies get rated, not a change in taste (p. 4).
- **Automatic tuning.** Model (11), called [PQ1], is the only model tuned by an automatic parameter tuner (APT1), with log base a = 6.76. APT gave "(only)" 0.0016 RMSE reduction over the manual settings (p. 4).
- **Future dates.** Day-specific parameters take default values (bu,t = 0, cu(t) = cu). The paper frames them as cleaning transient effects out of the long-term parameters (p. 4).
- **timeSVD++ (p. 5).**
  - User factors are time-dependent in the same way as the user bias, eq. 14.
  - A frequency-specific copy of the movie factors, eq. 16, was "barely beneficial".
  - Deliberate over-training (running more than the 40 iterations best for a single model) is reported to help the blend (p. 5).
- **timeSVD++ RMSEs (p. 5).**

  | Variant | f | Iterations | RMSE |
  |---|---|---|---|
  | (13)+(15) | 20 | 40 | 0.8914 |
  | (13)+(15) | 200 | 40 | 0.8814 |
  | (13)+(15) | 500 | 50 | 0.8815 |
  | (14) | 200 | 80 | 0.8825 |
  | (14) | 500 | 110 | 0.8841 |
  | (16), [PQ2] | 200 | 40 | 0.8777 |
  | (16) | 2000 | 40 | 0.8762 |

- **Time-aware neighborhood model (p. 6).**
  - Item-item weights wij and cij are learned globally. Each contribution is decayed by e^(−βu·|tui−tuj|), with a user-specific decay rate βu.
  - RMSE improves from 0.9002 (prior static model) to 0.8870, called [PQ3]. The paper says this beats hybrid neighborhood-on-residuals results from the literature. It concludes that modeling temporal dynamics matters more than complex learners.
  - Runs with bias (10) give 0.8887, 0.8885 and 0.8887.
  - A third weight set dij gives 0.8881, judged not worth it.
- **RBMs (p. 7).**
  - Visible units are conditioned on user, user×date and movie×frequency biases. Frequency-dependent weights barely help and cost runtime.
  - Bias-conditioned RBM, model (20): best RMSE 0.8942 (F = 400, 62 iterations).
  - Frequency RBM [PQ4]: 0.8928 (F = 200, 90 iterations), called the best pure RBM result the authors know of (p. 8).
  - Day-specific hidden units, [PQ6]: 0.9060, with results described as "not encouraging" (p. 8).
- **GBDT blending, settings (p. 8).**
  - Trained on Probe and applied to Qualifying.
  - Extra features: user support, movie support, frequency and date.
  - The paper notes GBDT accuracy "lags behind" neural-network blenders.
- **GBDT blending, results (p. 8).**

  | Input set | RMSE |
  |---|---|
  | 454 team predictors | 0.8603 |
  | 75 forward-selected predictors | 0.8606 |
  | 24 BellKor predictors | 0.8664 |
  | 24 + timeSVD++ factor features | 0.8661 |
  | 24 + RBM user features | 0.8661 |
  | 24 + kNN features | 0.8660 (p. 8–9) |
  | per-movie GBDT on RBM hidden units [PQ7] | 0.9248 (p. 9) |
  | blend of predictors 2, 9, 12, 13 | 0.8713 (p. 9) |

- **Missing evidence.** There are no variance estimates and no Test-set numbers. The frequency hypothesis is untested.
- **The paper's own inconsistencies:**
  - The text writes the data term as ∑(rui − µ + bu + bi)², but eq. (4) has (rui − µ − bu − bi)² (p. 2).
  - Eq. (16) prints a stray "∑ .y j", which looks garbled (p. 5).
  - The GBDT user-factor feature uses |R(u)|^(−1/2)∑ over R(u), while eq. (13) uses N(u) (p. 8 vs p. 5).
  - The 0.8885 → 0.8870 gain "solely attributed to the frequency bias term" compares a 25-iteration run with a 20-iteration run. The matched 20-iteration run with bias (10) gave 0.8887 (p. 6).

## Related in library
