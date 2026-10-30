# Are We Really Making Much Progress? A Worrying Analysis of Recent Neural Recommendation Approaches

type: study
family: reproducibility study of neural top-n recommenders against tuned simple baselines
evidence: 7 reproducible deep-learning top-n papers (CMN, MCRec, CVAE, CDL, NCF/NeuMF, SpectralCF, Mult-VAE), each re-run on its original datasets and protocol, against TopPopular, UserKNN, ItemKNN, ItemKNN-CBF/CFCBF, P3α and RP3β, plus SLIM and weighted MF in some cases; strength: each method tested on the original authors' own protocol; one run per configuration except where the original repeated splits; the reproduced methods were not re-tuned (their reported hyper-parameters were used).

## Digest

- **Claim.** Recent neural top-n recommenders are often not reproducible. When they are, conceptually simple, well-tuned baselines mostly match or beat them. The authors call the apparent gain "phantom progress" and attribute it to weak or untuned baselines and to methodological errors (p. 8).
- **Paper selection.** The authors scanned long papers from 2015–2018 at KDD, SIGIR, WWW and RecSys. They kept deep-learning papers on top-n recommendation that report ranking or classification metrics, which gave 18 papers (p. 2).
- **Reproducibility criteria.** A paper counted as reproducible if:
  - working code was available, or needed only minimal fixes that did not touch the core algorithm;
  - at least one dataset was available, with its splits public or reconstructible;
  - the authors answered within 30 days, when contact was needed.
  
  Skeleton code and private or crawled data counted as non-reproducible (p. 2).
- **Reproducibility result.** 7/18 (39%) papers were reproducible: KDD 3/4, RecSys 1/7, SIGIR 1/3, WWW 2/4 (p. 3, Table 1). Per-year statistics are not shown, but are said to indicate a rising rate (p. 3).
- **Protocol.** Each original implementation was refactored so that its training and tuning code is separate from a shared evaluation code, which reproduces the original paper's evaluation (p. 3).
  - Neural methods used their published hyper-parameters, not re-tuned (p. 3, footnote 4).
  - Baselines were tuned by Bayesian search (Scikit-Optimize), 35 cases each with the first 5 random. Ranges: k 5–800, shrink h 0–1000, α and β 0–2 (p. 4).
- **Baselines** (p. 3):
  - TopPopular: recommends the most popular items to everyone.
  - ItemKNN and UserKNN: cosine similarity with shrink term h and optional TF-IDF or BM25 weighting.
  - ItemKNN-CBF: the same, on item content features.
  - ItemKNN-CFCBF: concatenated rating and weighted feature vectors.
  - P3α: a 3-step random walk on the user-item graph.
  - RP3β: P3α with similarities divided by item popularity raised to β.
- **CMN (SIGIR '18).** Baselines were optimized for HR@5. CMN is never the best method on any dataset (p. 4, Table 2).
  - CiteULike-a, HR@5: RP3β 0.8226 vs CMN 0.8069.
  - Pinterest, HR@5: RP3β 0.7018 vs CMN 0.6872.
  - Epinions: TopPopular wins by a large margin (HR@5 0.5429 vs CMN 0.4195), although CMN beats the personalized baselines.
  - Epinions has a Gini index of 0.69 vs 0.37 for CiteULike-a. CMN recommends items 8% to 25% more popular than the baselines' items; these figures appear in the text only, not in a table (p. 4).
- **MCRec (KDD '18).** Only MovieLens100k could be run, because the meta-paths are hard-coded. The authors replaced MCRec's uncommon NDCG implementation with a standard one (p. 4).
  - ItemKNN beats MCRec on all three measures: PREC@10 0.3327 vs 0.3077; NDCG@10 0.2603 vs 0.2363 (p. 5, Table 3).
  - The original code picked the best epoch per metric on the test set (p. 5).
- **CVAE (KDD '18).** On dense CiteULike-a, ItemKNN-CFCBF beats CVAE at every cutoff: REC@50 0.1837 vs 0.0772; REC@300 0.4486 vs 0.3602 (p. 5, Table 4).
  - The text says CVAE wins only at cutoffs of 100 and above, on two datasets. Those other dataset results are not tabulated.
- **CDL (KDD '15).** On dense CiteULike-a, ItemKNN-CBF beats CDL at every cutoff: REC@100 0.3038 vs 0.1035 (p. 5, Table 5).
  - CVAE is "always better" than CDL, which the authors read as real progress between neural methods (p. 5).
- **NCF/NeuMF (WWW '17).** The epoch count was re-selected on validation data instead of the test set (p. 6).
  - Pinterest: ItemKNN and RP3β beat NeuMF on all metrics. For example, HR@5 is RP3β 0.7105 vs NeuMF 0.7024 (p. 6, Table 6).
  - MovieLens1M: NeuMF beats the simple baselines (HR@5 0.5486 vs RP3β 0.4922), but SLIM via ElasticNet beats NeuMF (HR@5 0.5589) (p. 6, Table 6).
- **SpectralCF (RecSys '18).** A single hyper-parameter set was reported for all datasets (p. 6).
  - HetRec and Amazon Instant Video: all baselines, including TopPopular, win. These results are not tabulated.
  - The provided MovieLens split gives SpectralCF a Recall@20 50% higher than the best baseline (text only).
  - The provided test split is non-random: Gini 0.92, vs about 0.79 for a true random split (p. 7, Figure 1).
  - On the authors' own random splits (5 repeats), SpectralCF is below TopPopular: REC@20 0.1843 vs 0.1853 (p. 7, Table 7).
- **Mult-VAE (WWW '18).** This is the one method that clearly beats the simple baselines: 10% to 20% better than the best baseline, per the text (p. 7).
  - Netflix: Mult-VAE vs SLIM is REC@20 0.2626 vs 0.2551 and NDCG@100 0.3756 vs 0.3745 (p. 7, Table 8).
  - At other cutoffs SLIM is slightly better: NDCG@20 0.2473 vs 0.2448; NDCG@50 0.3196 vs 0.3192 (p. 7, Table 9).
  - A similar pattern on MovieLens is stated but not shown. Improvements over SLIM of "up to 5%" are also stated in the text only (p. 7).
- **Wider observations** (p. 8):
  - Over 20 public datasets appear across the papers.
  - Metrics, cutoffs and protocols vary widely; examples include sampling 100 or 50 negatives per positive.
  - NCF is widely used as a state-of-the-art baseline despite these results.
  - At least two of the 18 papers used only a single private dataset and released no code (footnote 11).
- **Limits.** The study covers only four conference series and only top-n tasks. Matrix-factorization baselines were mostly not used, and the neural methods were not re-tuned (pp. 3, 9).
- **Overstatement.** The abstract says 6 of 7 "can often be outperformed" by simple heuristics. For NeuMF, however, the method that beats it on MovieLens1M is SLIM, not a simple heuristic (p. 6, Table 6). Several supporting results are reported in text only, without tables: SpectralCF on HetRec and Amazon, CVAE and CDL on the other datasets, and Mult-VAE on MovieLens.
- The paper's own inconsistencies:
  - SIGIR reproducibility is printed as "1/3 (30%)" (p. 3, Table 1).
  - CVAE is described as "presented at KDD '18" (p. 5), while reference [23] lists "Proceedings KDD '17" (p. 9).

## Related in library

- A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research: asks the same reproducibility-and-progress question over a larger set (12 neural CF methods) with similar conclusions.
