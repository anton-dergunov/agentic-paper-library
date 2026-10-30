# Are We Really Making Much Progress? A Worrying Analysis of Recent Neural Recommendation Approaches

type: study
family: reproducibility study of neural top-n recommenders against tuned simple baselines
evidence: 7 reproducible neural methods (CMN, MCRec, CVAE, CDL, NCF/NeuMF, SpectralCF, Mult-VAE), each rerun on its original datasets and protocol against TopPopular, UserKNN, ItemKNN, P3α and RP3β (plus content-based KNN variants and SLIM where relevant); strength: one rerun per paper on the original setups, original methods not re-tuned, no significance tests

## Digest

- **Claim.** Recent deep-learning top-n recommenders are rarely reproducible, and most do not consistently beat well-tuned simple baselines. Of 18 relevant papers, 7 could be reproduced (p. 1, abstract). 6 of those 7 "can often be outperformed" by nearest-neighbor or graph-based heuristics. The remaining one, Mult-VAE, beat those heuristics but did not consistently beat the linear method SLIM.
- **Corpus.** Long papers from 2015–2018 at KDD, SIGIR, WWW and RecSys that propose a deep-learning technique for top-n recommendation and evaluate it with classification or ranking metrics (p. 2).
- **Reproducibility criterion.**
  - The authors' code works, or needs only minimal fixes that leave the core algorithm untouched.
  - At least one original dataset is public, and its splits are either public or can be reconstructed from the paper (p. 2).
  - When artifacts were not public, the authors were contacted and given 30 days to respond.
- **Reproducibility rates by venue (p. 3, Table 1).**
  - KDD 3/4 (75%)
  - RecSys 1/7 (14%)
  - SIGIR 1/3 (30%)
  - WWW 2/4 (50%)
  - Total 7/18 (39%)
  - The text calls this "about one third" and says reproducibility increased over the years, but the per-year data are not shown.
- **Protocol.**
  - The original code was refactored so that training and tuning are separated from evaluation, and each paper's own evaluation procedure was then applied to all methods.
  - Neural methods use the hyper-parameters reported by their authors and are not re-optimized (left as future work, p. 3).
  - Baselines were tuned by Bayesian search (Scikit-Optimize) over 35 cases, 5 of them random initial points. Ranges: k 5–800, shrink h 0–1000, α and β 0–2 (p. 4).
- **Baselines (p. 3).**
  - ItemKNN: cosine similarity with a shrink term, optionally weighted by TF-IDF or BM25.
  - P3α: a 3-step random walk, with transition probabilities (r_ui/N_u)^α.
  - RP3β: P3α with similarities divided by item popularity raised to β.
- **CMN (p. 4, Table 2).** CMN is the best method in no case.
  - CiteULike-a, HR@5: RP3β 0.8226 vs CMN 0.8069.
  - Pinterest, HR@5: RP3β 0.7018 vs CMN 0.6872.
  - Epinions: TopPopular wins all metrics, with HR@5 0.5429 vs CMN 0.4195. CMN does beat the personalized baselines there.
  - Epinions has a Gini index of 0.69 vs 0.37 for CiteULike-a. CMN's recommended items are 8% to 25% more popular than the baselines' recommendations.
- **MCRec (p. 5, Table 3).** Evaluated on MovieLens100k only.
  - ItemKNN beats MCRec on all metrics: PREC@10 0.3327 vs 0.3077.
  - The original NDCG implementation was nonstandard, so a standard NDCG is used here.
  - The original code reports the best epoch per metric chosen on the test set.
- **CVAE (p. 5, Table 4), CiteULike-a.**
  - REC@50: CVAE 0.0772 vs RP3β 0.0811 and ItemKNN-CFCBF 0.1837.
  - REC@300: CVAE 0.3602 vs ItemKNN-CFCBF 0.4486.
  - CVAE wins only at cutoffs of 100 and above, on two datasets.
- **CDL (p. 5, Table 5).**
  - REC@50: CDL 0.0543 vs ItemKNN-CBF 0.2135.
  - CVAE is always better than CDL.
- **NCF/NeuMF (p. 6, Table 6).** The original code chose the number of epochs on the test set; this rerun uses a validation set instead.
  - Pinterest: ItemKNN and RP3β beat NeuMF on all metrics, e.g. HR@5 0.7105 (RP3β) vs 0.7024.
  - MovieLens1M: NeuMF beats the KNN and graph baselines (HR@5 0.5486 vs RP3β 0.4922), but SLIM is higher still (0.5589).
- **SpectralCF (pp. 6–7, Table 7, Figure 1).**
  - On HetRec and Amazon Instant Video, all baselines, including TopPopular, win on all measures.
  - On the provided MovieLens split, SpectralCF's Recall@20 was 50% above the best baseline. That provided test split has a Gini index of 0.92, against about 0.79 for a random split.
  - On the authors' own random splits: REC@20 0.1843 vs TopPopular 0.1853 and RP3β 0.2910.
- **Mult-VAE (p. 7, Tables 8–9).**
  - It is 10% to 20% better than the best simple baseline, stated in text only.
  - Netflix REC@20: 0.2626 vs SLIM 0.2551.
  - Netflix NDCG@100: 0.3756 vs SLIM 0.3745.
  - Netflix NDCG@20: SLIM 0.2473 vs Mult-VAE 0.2448.
- **Gaps.**
  - Re-tuning the neural methods themselves is not done.
  - Matrix-factorization baselines are mostly absent; WMF is mentioned for Mult-VAE but not tabulated.
  - Results for several datasets, such as CiteULike-t and the Mult-VAE MovieLens run, are described in text only, with details online.
- **Overclaim.** The abstract's "6 of 7 outperformed by simple heuristics" overstates the NCF result: on MovieLens1M NeuMF beat the heuristics and was beaten only by SLIM.
- The paper's own inconsistencies:
  - SIGIR "1/3 (30%)" (p. 3, Table 1).
  - CVAE is said to be "presented at KDD '18" (p. 5), while its reference [23] reads "Proceedings KDD '17" (p. 9).
  - CVAE's two datasets are called "dense CiteULike-a" and "sparse CiteULike-t" (p. 5).

## Related in library

- A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research: the extended follow-up of this study, covering 12 methods.
- On the Difficulty of Evaluating Baselines. A Study on Recommender Systems: makes the same argument that poorly tuned baselines create apparent progress.
- Improving Accountability in Recommender Systems Research Through Reproducibility: shares the reproducibility concern.
- Exploring Data Splitting Strategies for the Evaluation of Recommendation Models: also addresses data splitting, which this paper finds manipulated in the SpectralCF split.
- Bias and Debias in Recommender System. A Survey and Future Directions: surveys popularity bias, which this paper links to CMN's Epinions result and to the SpectralCF test split.
