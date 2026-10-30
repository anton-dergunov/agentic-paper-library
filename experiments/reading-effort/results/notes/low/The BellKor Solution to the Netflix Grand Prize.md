# The BellKor Solution to the Netflix Grand Prize

type: system
family: Netflix Prize ensemble: temporal baseline biases, timeSVD++ matrix factorisation, time-aware item-item neighbourhood, conditional RBMs, GBDT blending
evidence: Netflix Prize data, RMSE on the Quiz set, compared with Cinematch and with the authors' own earlier variants; strength: one benchmark, single-author contest report, constants tuned greedily by hand on Probe, no Test-set scores, no systematic ablations

## Digest

- The paper describes only the predictors added since the 2008 Progress Prize report to the "BellKor's Pragmatic Chaos" Grand Prize blend. These are improved baseline predictors, timeSVD++ built on them, a time-aware neighbourhood model, RBMs with conditional visible units, and GBDT blending (p. 1).
- **Data:** more than 100 million ratings, m = 480,189 users, n = 17,770 movies (p. 1). The Hold-out set of about 4.2 million ratings is split into Probe, Quiz and Test. Reported RMSEs are on Quiz; Test scores were never disclosed (p. 1).
- **Tuning:** constants are tuned greedily by hand on Probe and never revisited. The one exception is the frequency baseline (11), tuned with an automatic tuner (APT1); it gained only 0.0016 RMSE over the manual settings (p. 1, p. 4).
- **Baseline biases** combine:
  - a time-binned item bias (30 bins of about ten weeks);
  - a user drift term αu·devu(t), with devu(t) = sign(t−tu)|t−tu|^β and β = 0.4;
  - a per-user-per-day bias but;
  - a per-day user scaling cu(t) (pp. 2–3).
- **Baseline results:**
  - Model (9) gives 0.9605.
  - Adding cu(t), model (10) gives 0.9555. Cinematch's published Quiz RMSE is 0.9514 (p. 3).
- **Frequencies:** fui = ⌊log_a Fui⌋, where Fui is the number of ratings user u gave that day. The idea is credited to the Pragmatic Theory team. It enters as an item×frequency bias bi,fui (p. 3).
  - It lowers baseline RMSE from 0.9555 to 0.9278 (p. 3); the log base is a = 6.76 (p. 4).
  - The paper hypothesises that frequency reflects biased selection of movies during bulk rating, not a change in taste. It says most of the gain disappears once interaction terms are added; this is an argument, not a measured result (pp. 3–4).
- **Future dates:** for days with no training data, the day-specific parameters fall back to their defaults (p. 4).
- **timeSVD++:** user factors are made time-dependent as puk + αuk·devu(t) + pukt (p. 5).
  - Variants with the memory-efficient factors (15): f=20 gives 0.8914, f=200 gives 0.8814 (p. 5).
  - Adding frequency biases and frequency-specific movie factors, model (16): best is 0.8762 at f=2000; [PQ2] (f=200, 40 iterations) gives 0.8777 (p. 5).
  - The frequency-dependent factors themselves were "barely beneficial" (p. 5).
- **Over-training helps the blend:** factor models and RBMs are deliberately run past their Quiz-optimal iteration count because this improves the blend (p. 5, p. 7).
- **Time-aware neighbourhood model (18):**
  - Learned item-item weights wij and cij, with user-specific exponential decay e^{−βu|Δt|} (p. 6).
  - RMSE improves from 0.9002 for the static model to 0.8870 with frequency biases [PQ3]; the frequency term alone accounts for 0.8885 → 0.8870 (p. 6).
  - The paper says this beats published hybrid neighbourhood results, but prints no comparison numbers (p. 6).
- **RBM with user, user×date and movie×frequency visible biases:**
  - F=200 with frequencies gives 0.8928, called the best known pure-RBM result (p. 7).
  - The day-specific hidden units gave 0.9060 [PQ6], described as "not encouraging" (pp. 7–8).
- **GBDT blending:** trained on Probe, with support, frequency and date added as extra features (p. 8).
  - 454 predictors give 0.8603; 75 predictors give 0.8606; 24 BellKor predictors give 0.8664 (p. 8).
  - Adding timeSVD++ factors gives 0.8661, RBM user factors also 0.8661, and kNN features 0.8660 (pp. 8–9).
  - The per-movie GBDT on RBM hidden units [PQ7] gives 0.9248 (p. 9).
  - The paper says GBDT accuracy lags behind the neural-network blenders, and the contribution was less than hoped (p. 8).
- **Not disclosed:** the final blend's RMSE, any Test-set results, and the effect of each component on the final blend.
- The paper's own inconsistencies:
  - The text writes the first term of eq. (4) as (rui − µ + bu + bi)² while the equation has (rui − µ − bu − bi)² (p. 2).
  - Eq. (16) is garbled ("∑ .y j") (p. 5).
  - The GBDT user-factor feature normalises over R(u), while model (13)/(16) uses N(u) (p. 8 vs p. 5).
  - The attributed 0.8885 → 0.8870 gain compares a 25-iteration run with a 20-iteration run; the 20-iteration run without frequencies scored 0.8887 (p. 6).

## Related in library

- (none)
