# Reading list: experimentation and metrics

The library holds 10 papers here: two Microsoft ExP papers (Online Experimentation at Microsoft, five puzzling outcomes), CUPED with the delta-method and Netflix sensitivity papers, a long-term-effects paper, the metric-power paper (2024), and a few causal-recommendation items. It lacks most of the canon. This list adds the Kohavi/ExP pitfalls and SRM papers, sequential testing and confidence sequences, the regression-adjustment and ML control-variate successors to CUPED (through 2026), interference and marketplace designs (switchback, cluster, two-sided, budget-split), metric design and surrogate-based long-term effects, heterogeneous effects and uplift, and off-policy evaluation for general policies. Sequential testing and interference have no folder of their own, so they sit in ab-testing; OPE sits in causal-inference (scope: logged data). Interleaving and ranker OPE are left to search-and-ranking. Many papers are not on arXiv and carry a publisher DOI.

## Proposed

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | Controlled experiments on the web: survey and practical guide | 2009 | https://doi.org/10.1007/s10618-008-0114-1 | experimentation-and-metrics/ab-testing | The founding survey of online controlled experiments (Kohavi et al.); the reference everyone else cites. |
| 2 | Online controlled experiments at large scale | 2013 | https://doi.org/10.1145/2487575.2488217 | experimentation-and-metrics/ab-testing | Bing ExP lessons on running hundreds of concurrent experiments and what goes wrong at scale. |
| 3 | Seven rules of thumb for web site experimenters | 2014 | https://doi.org/10.1145/2623330.2623341 | experimentation-and-metrics/ab-testing | Kohavi et al.: concrete rules on small effects, sample size, novelty and trust that shaped ExP practice. |
| 4 | Trustworthy analysis of online A/B tests: pitfalls, challenges and solutions | 2017 | https://doi.org/10.1145/3018661.3018677 | experimentation-and-metrics/ab-testing | Deng, Lu and Litz: invalid p-values, multiple testing, peeking and other pitfalls with fixes, from Microsoft. |
| 5 | Diagnosing sample ratio mismatch in online controlled experiments: a taxonomy and rules of thumb | 2019 | https://doi.org/10.1145/3292500.3330722 | experimentation-and-metrics/ab-testing | The standard reference on SRM causes and diagnosis (Fabijan et al., Microsoft). |
| 6 | How A/B tests could go wrong: automatic diagnosis of invalid online experiments | 2019 | https://doi.org/10.1145/3289600.3291000 | experimentation-and-metrics/ab-testing | Automated detection of invalid experiments (SRM and beyond) as a platform feature. |
| 7 | Top challenges from the first practical online controlled experiments summit | 2019 | https://doi.org/10.1145/3331651.3331655 | experimentation-and-metrics/ab-testing | Cross-company list of open problems (OEC, long-term, interference, trust) from Google, Microsoft, Netflix and others. |
| 8 | A/B testing intuition busters: common misunderstandings in online controlled experiments | 2022 | https://doi.org/10.1145/3534678.3539160 | experimentation-and-metrics/ab-testing | Kohavi et al.: the misreadings of p-values, power, ratio metrics and variance that trip up practitioners. |
| 9 | Statistical Challenges in Online Controlled Experiments: A Review of A/B Testing Methodology | 2022 | 2212.11366 | experimentation-and-metrics/ab-testing | Best recent methodology survey of A/B testing, covering variance, sequential, interference and long-term issues. |
| 10 | Novelty and Primacy: A Long-Term Estimator for Online Experiments | 2021 | 2102.12893 | experimentation-and-metrics/ab-testing | Estimates the long-run effect despite novelty and primacy bias in short tests. |
| 11 | Always Valid Inference: Bringing Sequential Analysis to A/B Testing | 2015 | 1512.04922 | experimentation-and-metrics/ab-testing | mSPRT-based always-valid p-values (Optimizely), the basis of peeking-safe A/B tests. |
| 12 | Continuous Monitoring of A/B Tests without Pain: Optional Stopping in Bayesian Testing | 2016 | 1602.05549 | experimentation-and-metrics/ab-testing | Deng, Lu and Chen (Microsoft): why Bayesian A/B tests tolerate optional stopping, and its limits. |
| 13 | Time-uniform, nonparametric, nonasymptotic confidence sequences | 2018 | 1810.08240 | experimentation-and-metrics/ab-testing | The foundational confidence-sequence paper (Howard, Ramdas et al.) underlying modern anytime-valid testing. |
| 14 | Time-uniform central limit theory and asymptotic confidence sequences | 2021 | 2103.06476 | experimentation-and-metrics/ab-testing | Asymptotic confidence sequences, the practical variant used in A/B platforms for means and treatment effects. |
| 15 | Estimating means of bounded random variables by betting | 2020 | 2010.09686 | experimentation-and-metrics/ab-testing | Betting-based confidence sequences that are tight and simple, widely used as a modern baseline. |
| 16 | Anytime-Valid Linear Models and Regression Adjusted Causal Inference in Randomized Experiments | 2022 | 2210.08589 | experimentation-and-metrics/ab-testing | Combines CUPED-style regression adjustment with anytime-valid inference. |
| 17 | Anytime-Valid Confidence Sequences in an Enterprise A/B Testing Platform | 2023 | 2302.10108 | experimentation-and-metrics/ab-testing | Adobe's production deployment of confidence sequences; a rare industry account of sequential testing in practice. |
| 18 | Hypothesis testing with e-values | 2024 | 2410.23614 | experimentation-and-metrics/ab-testing | Ramdas and Wang's monograph on e-values, the current theoretical frame for anytime-valid testing. |
| 19 | Design and Analysis of Switchback Experiments | 2020 | 2009.00148 | experimentation-and-metrics/ab-testing | Bojinov, Simchi-Levi and Zhao: the reference theory for time-randomised experiments with carryover. |
| 20 | Data-Driven Switchback Experiments: Theoretical Tradeoffs and Empirical Bayes Designs | 2024 | 2406.06768 | experimentation-and-metrics/ab-testing | Chooses switchback block length from data, a practical 2024 advance. |
| 21 | Design and analysis of experiments in networks: Reducing bias from interference | 2014 | 1404.7530 | experimentation-and-metrics/ab-testing | Eckles, Karrer and Ugander: how network interference biases A/B tests and what cluster designs buy. |
| 22 | Graph cluster randomization: network exposure to multiple universes | 2013 | 1305.6979 | experimentation-and-metrics/ab-testing | The cluster-randomisation design for social networks (LinkedIn/Facebook line). |
| 23 | Estimating Average Causal Effects Under General Interference, with Application to a Social Network Experiment | 2013 | 1305.6156 | experimentation-and-metrics/ab-testing | Aronow and Samii's exposure-mapping framework, the standard formal basis for interference. |
| 24 | Network experimentation at scale | 2020 | 2012.08591 | experimentation-and-metrics/ab-testing | Facebook's production system for network-interference experiments. |
| 25 | Using Ego-Clusters to Measure Network Effects at LinkedIn | 2019 | 1903.08755 | experimentation-and-metrics/ab-testing | LinkedIn's ego-cluster design for estimating network effects in live experiments. |
| 26 | Why marketplace experimentation is harder than it seems: the role of test-control interference | 2014 | https://doi.org/10.1145/2600057.2602837 | experimentation-and-metrics/ab-testing | Blake and Coey (eBay): the classic demonstration of interference bias in marketplace tests. |
| 27 | Experimental Design in Two-Sided Platforms: An Analysis of Bias | 2020 | 2002.05670 | experimentation-and-metrics/ab-testing | Johari et al.: bias of customer-side, seller-side and two-sided randomisation in marketplaces. |
| 28 | Interference, Bias, and Variance in Two-Sided Marketplace Experimentation: Guidance for Platforms | 2021 | 2104.12222 | experimentation-and-metrics/ab-testing | Practical guidance on choosing marketplace designs; bias-variance tradeoff between them. |
| 29 | Multiple Randomization Designs: Estimation and Inference with Interference | 2021 | 2112.13495 | experimentation-and-metrics/ab-testing | Two-sided randomisation (Bajari et al.), the main alternative to cluster designs in marketplaces. |
| 30 | Trustworthy Online Marketplace Experimentation with Budget-split Design | 2020 | 2012.08724 | experimentation-and-metrics/ab-testing | Budget-split design for ads marketplaces (Google/LinkedIn); the reference for budget interference. |
| 31 | Choosing Online Experiment Designs under Interference in Ads, Recommendations, and Member-Experience Systems | 2026 | 2605.25290 | experimentation-and-metrics/ab-testing | 2026 practitioner guide to picking a design under interference across ads and recommender systems. |
| 32 | Boosted decision tree regression adjustment for variance reduction in online controlled experiments | 2016 | https://doi.org/10.1145/2939672.2939688 | experimentation-and-metrics/variance-reduction | Yandex's ML-based regression adjustment; an early non-linear CUPED. |
| 33 | Machine Learning for Variance Reduction in Online Experiments | 2021 | 2106.07263 | experimentation-and-metrics/variance-reduction | Booking.com's ML control variates (CUPAC-style) with a clear account of what to expect. |
| 34 | Towards Optimal Variance Reduction in Online Controlled Experiments | 2021 | 2110.13406 | experimentation-and-metrics/variance-reduction | Characterises the optimal control variate and compares CUPED and its ML successors. |
| 35 | Consistent Transformation of Ratio Metrics for Efficient Online Controlled Experiments | 2018 | https://doi.org/10.1145/3159652.3159699 | experimentation-and-metrics/variance-reduction | Microsoft Bing: replaces ratio metrics with a linearised form for better sensitivity and valid analysis. |
| 36 | Variance reduction combining pre-experiment and in-experiment data | 2024 | 2410.09027 | experimentation-and-metrics/variance-reduction | Extends CUPED to use in-experiment covariates, a recent industry advance. |
| 37 | Bridging Control Variates and Regression Adjustment in A/B Testing: From Design-Based to Model-Based Frameworks | 2025 | 2509.13944 | experimentation-and-metrics/variance-reduction | Unifies the control-variate and regression-adjustment views; deployed at ByteDance. |
| 38 | Data-driven metric development for online controlled experiments: seven lessons learned | 2016 | https://doi.org/10.1145/2939672.2939700 | experimentation-and-metrics/metric-design | Deng and Shi (Microsoft): how to build directional, sensitive metrics; the core OEC-design paper. |
| 39 | Measuring Metrics | 2016 | https://doi.org/10.1145/2983323.2983356 | experimentation-and-metrics/metric-design | Dmitriev and Wu (Microsoft): how to quantify a metric's sensitivity and directionality. |
| 40 | A dirty dozen: twelve common metric interpretation pitfalls in online controlled experiments | 2017 | https://doi.org/10.1145/3097983.3098024 | experimentation-and-metrics/metric-design | Dmitriev et al.: the canonical checklist of metric misreadings. |
| 41 | Choosing a Proxy Metric from Past Experiments | 2023 | 2309.07893 | experimentation-and-metrics/metric-design | Netflix/Google: picks short-term proxies for a long-term north star using past experiments. |
| 42 | Estimating Treatment Effects using Multiple Surrogates: The Role of the Surrogate Score and the Surrogate Index | 2016 | 1603.09326 | experimentation-and-metrics/metric-design | Athey, Chetty, Imbens and Kang: the surrogate index, the base of long-term effect estimation. |
| 43 | Long-term Causal Inference Under Persistent Confounding via Data Combination | 2022 | 2202.07234 | experimentation-and-metrics/metric-design | Long-run effects from short experiments plus observational data, allowing unobserved confounding. |
| 44 | The Proximal Surrogate Index: Long-Term Treatment Effects under Unobserved Confounding | 2026 | 2601.17712 | experimentation-and-metrics/metric-design | 2026 extension of surrogate indices robust to hidden confounders. |
| 45 | Evaluating for the long term: Learnings from industry | 2026 | 2608.08043 | experimentation-and-metrics/metric-design | 2026 industry synthesis on measuring long-term impact from short experiments. |
| 46 | Generalized Random Forests | 2016 | 1610.01271 | experimentation-and-metrics/causal-inference | Athey, Tibshirani and Wager: the forest framework behind causal forests and most HTE in practice. |
| 47 | Meta-learners for Estimating Heterogeneous Treatment Effects using Machine Learning | 2017 | 1706.03461 | experimentation-and-metrics/causal-inference | S-, T- and X-learners: the baseline taxonomy for uplift and CATE. |
| 48 | Quasi-Oracle Estimation of Heterogeneous Treatment Effects | 2017 | 1712.04912 | experimentation-and-metrics/causal-inference | The R-learner; a standard modern CATE baseline. |
| 49 | Double/Debiased Machine Learning for Treatment and Causal Parameters | 2016 | 1608.00060 | experimentation-and-metrics/causal-inference | The orthogonalisation plus cross-fitting framework behind ML-based causal estimators and ML control variates. |
| 50 | A Large Scale Benchmark for Individual Treatment Effect Prediction and Uplift Modeling | 2021 | 2111.10106 | experimentation-and-metrics/causal-inference | Criteo's public RCT uplift dataset (25M rows) used as the standard benchmark. |
| 51 | A Large Scale Heterogeneous Treatment Effect Estimation Framework and Its Applications of Users' Journey at Snap | 2025 | 2512.03060 | experimentation-and-metrics/causal-inference | Production HTE system on 1.2B observations; shows how it is run at industry scale. |
| 52 | Doubly Robust Policy Evaluation and Learning | 2011 | 1103.4601 | experimentation-and-metrics/causal-inference | Dudik, Langford and Li: the doubly robust estimator at the core of OPE for general policies. |
| 53 | Counterfactual Reasoning and Learning Systems | 2012 | 1209.2355 | experimentation-and-metrics/causal-inference | Bottou et al. (Microsoft Bing ads): counterfactual estimation for real ad systems. |
| 54 | Offline A/B testing for Recommender Systems | 2018 | 1801.07030 | experimentation-and-metrics/causal-inference | Criteo's clipped importance-sampling estimators for replaying A/B tests offline. |
| 55 | Open Bandit Dataset and Pipeline: Towards Realistic and Reproducible Off-Policy Evaluation | 2020 | 2008.07146 | experimentation-and-metrics/causal-inference | Standard benchmark and library for OPE on real logged data. |
| 56 | Off-Policy Evaluation for Large Action Spaces via Embeddings | 2022 | 2202.06317 | experimentation-and-metrics/causal-inference | MIPS: OPE when the action space is large and standard IPS breaks. |
| 57 | Double Reinforcement Learning for Efficient Off-Policy Evaluation in Markov Decision Processes | 2019 | 1908.08526 | experimentation-and-metrics/causal-inference | Efficient OPE for sequential policies, extending DR beyond bandits. |
| 58 | Anytime-valid off-policy inference for contextual bandits | 2022 | 2210.10768 | experimentation-and-metrics/causal-inference | Confidence sequences for OPE; links sequential testing with off-policy evaluation. |
| 59 | Off-Policy Evaluation and Learning for the Future under Non-Stationarity | 2025 | 2506.20417 | experimentation-and-metrics/causal-inference | 2025 OPE when the environment drifts between logging and deployment. |
| 60 | A Review of Off-Policy Evaluation in Reinforcement Learning | 2022 | 2212.06355 | experimentation-and-metrics/causal-inference | The one survey for OPE across bandits and RL. |

## Added from "Considered" at Anton's request (2026-10-01)

| # | Paper | Year | arXiv / URL | Folder |
|--:|---|--:|---|---|
| 61 | A Survey on Causal Inference | 2020 | 2002.02770 | experimentation-and-metrics/causal-inference |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
| A/B Testing: A Systematic Literature Review | 2023 | 2308.04929 | experimentation-and-metrics/ab-testing | Software-engineering literature review; less useful than the statistical review already proposed |
| Bayesian structural time-series (CausalImpact) | 2015 | 1506.00356 | experimentation-and-metrics/causal-inference | Observational impact estimation, not online experimentation; marginal for this reader |
| Synthetic Difference in Differences | 2018 | 1812.09970 | experimentation-and-metrics/causal-inference | Panel econometrics, off the core topic |
| The Econometrics of Randomized Experiments | 2016 | 1607.00698 | experimentation-and-metrics/causal-inference | Econometrics handbook chapter; overlaps the proposed reviews and Double ML |
| Estimating individual treatment effect: generalization bounds and algorithms | 2016 | 1606.03976 | experimentation-and-metrics/causal-inference | Representation-learning CATE; little uptake in A/B practice |
| Generic Machine Learning Inference on Heterogeneous Treatment Effects in Randomized Experiments | 2017 | 1712.04802 | experimentation-and-metrics/causal-inference | Useful but econometric and dense; meta-learners and GRF cover the practice |
| Recursive Partitioning for Heterogeneous Causal Effects | 2015 | 1504.01132 | experimentation-and-metrics/causal-inference | Superseded by causal forests and GRF, both proposed |
| A Survey on Causal Inference | 2020 | 2002.02770 | experimentation-and-metrics/causal-inference | Broad survey, not specific to experiments or uplift |
| Prediction-Powered Inference / PPI++ | 2023 | 2301.09633, 2311.01453 | experimentation-and-metrics/variance-reduction | PPI is already in the library under llm/evaluation; PPI++ is an incremental follow-up |
| Anytime-valid, Bayes-assisted, Prediction-Powered Inference | 2025 | 2505.18000 | experimentation-and-metrics/ab-testing | Too niche and recent, little uptake yet |
| Anytime-Valid Inference for Double/Debiased Machine Learning of Causal Parameters | 2024 | 2408.09598 | experimentation-and-metrics/ab-testing | Theory-heavy; the regression-adjusted anytime-valid paper is the practical one |
| Game-theoretic statistics and safe anytime-valid inference; Safe Testing | 2022 | 2210.01948, 1906.07801 | experimentation-and-metrics/ab-testing | Overlap with the e-values monograph, which is the better entry point |
| Design-Based Confidence Sequences for panel experiments | 2022 | 2210.08639 | experimentation-and-metrics/ab-testing | Panel and economic experiments rather than online A/B |
| Treatment Effects in Market Equilibrium; Experimenting in Equilibrium | 2021 | 2109.11647, 1903.02124 | experimentation-and-metrics/ab-testing | Theory-heavy equilibrium interference; the proposed marketplace papers cover the practice |
| Markovian Interference in Experiments | 2022 | 2206.02371 | experimentation-and-metrics/ab-testing | Theory; geometric-mixing switchback paper covers it |
| Price Experimentation and Interference; Correcting for Interference in Experiments: A Case Study at Douyin | 2023 | 2310.17165, 2305.02542 | experimentation-and-metrics/ab-testing | Narrower case studies, lower priority than the proposed interference papers |
| Policy Learning for Balancing Short-Term and Long-Term Rewards | 2024 | 2405.03329 | experimentation-and-metrics/metric-design | Policy-learning extension of surrogates, little uptake |
| Variance Reduction for Heavy-Tailed Monetization Metrics via Post-Stratification | 2026 | 2606.04110 | experimentation-and-metrics/variance-reduction | Single-company case study; too new to judge |
| Effective OPE and Learning in Contextual Combinatorial Bandits; OPE via Conjunct Effect Modeling | 2024 | 2408.11202, 2305.08062 | experimentation-and-metrics/causal-inference | Incremental variants of MIPS |
| Data-Efficient Off-Policy Policy Evaluation for RL; Doubly Robust Off-policy Value Evaluation for RL | 2016 | 1604.00923, 1511.03722 | experimentation-and-metrics/causal-inference | RL-specific OPE; the double RL and review papers cover it |
| Counterfactual Risk Minimization | 2015 | 1502.02362 | experimentation-and-metrics/causal-inference | Learning rather than evaluation; ranker/policy learning belongs to search-and-ranking |
| Benchmarks for Deep Off-Policy Evaluation; Empirical Study of OPE for RL | 2021 | 2103.16596, 1911.06854 | experimentation-and-metrics/causal-inference | Deep-RL focus, far from product experimentation |
| Making Contextual Decisions with Low Technical Debt | 2016 | 1606.03966 | experimentation-and-metrics/causal-inference | Systems paper for contextual bandits, not evaluation |
| Off-Policy Evaluation for Large Action Spaces (2025 follow-ups: context-action embeddings, cross-domain) | 2025 | 2509.00648, 2607.22012 | experimentation-and-metrics/causal-inference | Incremental and not verified as adopted |
| AgentA/B and other LLM-agent A/B simulation papers | 2025 | 2504.09723 | experimentation-and-metrics/ab-testing | Simulated users rather than real-experiment methodology; unproven |
| The evolution of continuous experimentation in software product development | 2017 | https://doi.org/10.1109/ICSE.2017.76 | experimentation-and-metrics/ab-testing | Maturity-model paper; less technical than the rest of the canon |
| Anytime-Valid Inference for Multinomial Count Data | 2020 | 2011.03567 | experimentation-and-metrics/ab-testing | Narrow (categorical counts); confidence-sequence papers cover the core |
| Switchback Experiments under Geometric Mixing | 2022 | 2209.00197 | experimentation-and-metrics/ab-testing | Theory refinement of the proposed switchback paper |
| Sequentially-Rerandomized Switchback Experiments | 2026 | 2604.02489 | experimentation-and-metrics/ab-testing | Very recent, no uptake yet; switchback basics are covered |
| Reducing Interference Bias in Online Marketplace Pricing Experiments | 2020 | 2004.12489 | experimentation-and-metrics/ab-testing | Pricing-specific case; lower priority |
| Seller-Side Experiments under Interference Induced by Feedback Loops in Two-Sided Platforms | 2024 | 2401.15811 | experimentation-and-metrics/ab-testing | Narrow; the marketplace guidance papers cover it |
| Leveraging covariate adjustments at scale in online A/B testing | 2023 | 2305.01109 | experimentation-and-metrics/variance-reduction | Incremental platform report after CUPED |
| Variance Reduction in Ratio Metrics for Efficient Online Experiments | 2024 | 2401.04062 | experimentation-and-metrics/variance-reduction | Incremental; the ratio-metric transformation and delta-method papers cover it |
| Accelerating A/B-Tests with Counterfactual Estimation: Reducing Variance through Policy Overlap | 2026 | 2607.14604 | experimentation-and-metrics/variance-reduction | Too new to judge (2026) |
| Learning sensitive combinations of A/B test metrics | 2017 | https://doi.org/10.1145/3018661.3018708 | experimentation-and-metrics/metric-design | Overlaps the metric-power paper already in the library |
| Future user engagement prediction and its application to improve the sensitivity of online experiments | 2015 | https://doi.org/10.1145/2736277.2741116 | experimentation-and-metrics/metric-design | Overlaps the long-term and proxy papers proposed |
| Targeting for long-term outcomes | 2020 | 2010.15835 | experimentation-and-metrics/metric-design | Incremental over the surrogate-index papers |
| Estimation and Inference of Heterogeneous Treatment Effects using Random Forests | 2015 | 1510.04342 | experimentation-and-metrics/causal-inference | Superseded by Generalized Random Forests, proposed |
| Uplift Modeling with Multiple Treatments and General Response Types | 2017 | 1705.08492 | experimentation-and-metrics/causal-inference | Covered by meta-learners and the Criteo benchmark |
| Optimal and Adaptive Off-policy Evaluation in Contextual Bandits | 2016 | 1612.01205 | experimentation-and-metrics/causal-inference | Incremental over DR |
| Doubly robust off-policy evaluation with shrinkage | 2019 | 1907.09623 | experimentation-and-metrics/causal-inference | Incremental over DR |
| Off-Policy Evaluation for Large Action Spaces via Policy Convolution | 2023 | 2310.15433 | experimentation-and-metrics/causal-inference | Incremental over MIPS |
| Breaking the Curse of Horizon: Infinite-Horizon Off-Policy Estimation | 2018 | 1810.12429 | experimentation-and-metrics/causal-inference | RL-specific; double RL paper covers it |
