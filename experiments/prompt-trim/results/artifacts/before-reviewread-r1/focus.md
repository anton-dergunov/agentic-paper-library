# Focus: experimentation-and-metrics/variance-reduction

Likely themes:
- Covariate adjustment with pre-experiment data (CUPED/CUPAC, control variates vs regression adjustment) and its ML successors (boosted trees, MLRATE, cross-fitting).
- Ratio and count metrics: delta method, linearisation, user-level transformations, and how adjustment carries over to them.
- In-experiment covariates: which are safe (unaffected by treatment) and how to combine them with pre-experiment ones without bias.
- Other sensitivity levers beyond covariates: stratification, trigger/dilution, metric capping and transformation (Netflix case studies).

Questions to ask of each paper:
- What estimator exactly, and what does it assume (randomisation unit, covariate independence of treatment, model fitting/cross-fitting)?
- Is it unbiased / consistent, and under which framework (design-based vs model-based)? How is the variance estimated?
- Variance reduction achieved: on what metrics, how many experiments, against which baseline (difference-in-means, CUPED), and as A/A or real tests?
- How does it handle ratio metrics, heavy tails, new users without pre-period data?
- Practical cost: what must be logged or trained, and was it deployed in production?
