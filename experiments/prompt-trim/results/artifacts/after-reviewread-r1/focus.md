# Focus: experimentation-and-metrics/variance-reduction

Likely themes of the review:
- Covariate adjustment with pre-experiment data (CUPED, control variates) and how it relates to regression adjustment (design-based vs model-based views).
- ML-based adjustment (boosted trees, MLRATE, cross-fitting) versus linear CUPED: how much more variance it removes, and at what cost or risk.
- Ratio and count metrics: the delta method, linearization / consistent transformations, and adjusting them.
- In-experiment covariates: when they can be used without bias.
- Practice at companies (Microsoft, Yandex, Netflix, Facebook, LinkedIn, ByteDance, Etsy): what was deployed and what the gains were.

Questions to ask of each paper:
- Which estimator is proposed, and what does it reduce variance relative to (difference in means, CUPED, another baseline)?
- What covariates does it use (pre-experiment metric, other features, in-experiment data, ML predictions), and how is bias avoided (cross-fitting, randomization-based arguments)?
- Which metric types does it handle (user-level means, ratio, count, heavy-tailed), and how is the analysis unit handled?
- Variance-reduction numbers: how measured (A/A tests, real experiments, simulations), on how many metrics/experiments, and with what spread across metrics?
- Assumptions and failure modes: new users without history, covariate drift, heavy tails, small samples, interaction with sequential testing.
- How it connects to the other papers here (CUPED lineage, delta method, PPI-style prediction-powered inference).
