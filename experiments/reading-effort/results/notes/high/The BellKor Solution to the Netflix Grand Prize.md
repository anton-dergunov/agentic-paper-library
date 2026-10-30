# The BellKor Solution to the Netflix Grand Prize

type: method
family: temporal-dynamics baselines, matrix factorisation (timeSVD++), item-item neighbourhood and RBM collaborative filtering, blended with gradient boosted decision trees
evidence: Netflix Prize data, with RMSE on the Quiz set compared against Netflix Cinematch, the team's own earlier models and its own variants; strength: one dataset, run by the competing team, constants tuned by hand on Probe, no variance or repeated runs reported, Test-set scores never disclosed

## Digest

- Claim: this report covers only what was new in Koren's part of the winning "BellKor's Pragmatic Chaos" solution over the 2008 Progress Prize. The new parts are better baseline predictors with time and "frequency" terms, those baselines placed inside timeSVD++ and a time-aware neighbourhood model, RBMs with conditional visible units, and GBDT blending (p. 1). The paper does not report the final Grand Prize blend's score.
- Data: more than 100 million dated ratings from m = 480,189 users on n = 17,770 movies. The Hold-out set has about 4.2 million ratings (each user's last nine), split into Probe, Quiz and Test. All RMSEs reported are on the Quiz set, and Netflix never disclosed Test scores (p. 1).
- Tuning: constants are set greedily by hand on Probe, are never revisited, and are shared across variants. The author says this is deliberately not optimal, because over-tuning one predictor adds little to the blend (pp. 1–2). The RBM iteration counts are described in terms of the "lowest Quiz RMSE", so the Quiz set also guided some choices (p. 7).
- Baseline predictor mechanism: an item bias split into 30 time bins of about ten weeks each (p. 2). The user bias combines a linear drift term αu·devu(t), with β = 0.4, and a per-user-per-day term bu,t; users rate on 40 different days on average (p. 3). Model (10) adds a per-user, per-day multiplier cu(t) on the item bias (p. 3).
- Baseline results: model (9) reaches RMSE 0.9605. Adding cu(t) gives 0.9555, against Cinematch's published 0.9514 on the same Quiz set (p. 3).
- Frequency: Fui is the number of ratings user u gave on day tui. Its rounded logarithm fui drives an item-by-frequency bias bi,fui. Adding it lowers the baseline RMSE from 0.9555 to 0.9278, which the text calls "significantly better" than Cinematch (p. 3). The term was suggested by the Pragmatic Theory team (p. 3).
- Why frequency works is offered as a hypothesis only, with no test: ratings entered in bulk select movies that people remember as all-time favourites or as bad examples. Most of the gain disappears once user–item interaction terms are added (pp. 3–4).
- Day-specific parameters cannot be trained for future dates and take default values there. The author argues they act as data cleaning that helps fit the long-term parameters (p. 4).
- Tuning effort: an automatic parameter tuner on model (11) improved RMSE by "only" 0.0016 over the manual settings. Log base a = 6.76 (p. 4).
- timeSVD++ (Sec. IV): user factors drift over time in the same way as the user bias (eq. 14), or use a lighter version without per-day terms (eq. 15). Eq. (16) adds frequency-specific movie factors, described as "barely beneficial", with no number given (p. 5).
- timeSVD++ results: eq. (15) at f = 20 gives 0.8914 and at f = 200 gives 0.8814. Eq. (14) at f = 200 with 80 iterations gives 0.8825. Eq. (16) ranges from 0.8777 (f = 200, 40 iterations, called [PQ2]) to 0.8762 (f = 2000, 40 iterations) (p. 5). Deliberate over-training (running many more iterations) is said to help the blend, but no blend numbers are shown for it (p. 5).
- Neighbourhood (Sec. V): global item-item weights wij and cij, with a learned per-user exponential time decay e^(−βu·|Δt|) (eq. 18). Its RMSE is 0.8870, against 0.9002 for the static model [7] (p. 6). The step from 0.8885 to 0.8870 is attributed solely to the frequency bias (p. 6). A third set of weights dij reaches 0.8881, which the author judges not worth adding (p. 6).
- Over-claim: the text says 0.8870 beats the hybrid neighbourhood results in [1, 2, 11, 15] and concludes that temporal modelling matters more than complex algorithms. No comparison numbers are printed (p. 6).
- RBM (Sec. VI): visible units are conditioned on user, user×date and movie×frequency biases (eqs. 20–21). Results: eq. (20) variants score 0.8942–0.8952. The frequency RBM with F = 200 and 90 iterations scores 0.8928, called "the best we know" for a pure RBM. The day-specific hidden-unit RBM scores 0.9060, described as "not encouraging" (pp. 7–8). The frequency-dependent weights "barely" help, with no number given (p. 7).
- GBDT blend: it is trained on Probe and applied to Qualifying, with four extra inputs (user support, movie support, frequency, date). Results are 0.8603 from 454 predictors and 0.8606 from 75 predictors, using 200 trees, tree size 20, shrinkage 0.18 and sampling rate 0.9 (p. 8).
- GBDT on the 24 BellKor predictors scores 0.8664. Adding timeSVD++ factor features gives 0.8661, using RBM hidden units instead also gives 0.8661, and adding kNN features gives 0.8660. Per-movie GBDT on 50-D RBM user vectors ([PQ7]) scores 0.9248. A further blended predictor scores 0.8713 (pp. 8–9).
- On GBDT: the author says its accuracy "lags behind" the neural-network blenders of [13], with no number, and that its impact was smaller than hoped (p. 8). There is no single-blend comparison against a linear blend.
- Conclusion: an accurate treatment of main effects (biases) is "probably at least as significant" as modelling breakthroughs (p. 9).
- Garbled text: the bracketing in eqs. (13) and (16), the cost function (12) and the column alignment of the learning-rate/regularisation tables are broken in the text layer, and eq. (16) contains a stray "∑ .y j" (pp. 4–5). Do not quote these as exact.
- The paper's own inconsistencies:
  - The prose gives the fit term as (rui − µ + bu + bi)², but eq. (4) has (rui − µ − bu − bi)² (p. 2).
  - The GBDT user-factor feature normalises over R(u) (p. 8), while the timeSVD++ rule it is taken from normalises over N(u) (p. 5).

## Related in library

## Q&A
