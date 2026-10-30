# Are We Really Making Much Progress? A Worrying Analysis of Recent Neural Recommendation Approaches

type: study
family: reproducibility and baseline re-evaluation of neural top-n recommenders
evidence: 7 reproducible deep-learning top-n papers (CMN, MCRec, CVAE, CDL, NCF, SpectralCF, Mult-VAE), run on each paper's own datasets and protocols (CiteULike-a/-t, Pinterest, Epinions, MovieLens100k/1M, HetRec, Amazon Instant Video, Netflix). They are compared with TopPopular, UserKNN, ItemKNN, ItemKNN-CBF, ItemKNN-CFCBF, P3α, RP3β, and SLIM for NCF and Mult-VAE; strength: the authors' original code and evaluation protocols are reused, and the baselines are tuned by Bayesian search, but the neural methods keep the hyper-parameters their papers report and are not re-tuned. There is one run per configuration, except repeated splits where the original protocol used them.

## Digest

- Claim: most recent neural top-n recommenders could not be reproduced. Of those that could, 6 of 7 are often beaten by simple, well-tuned kNN or graph-based heuristics. The 7th, Mult-VAE, beats these baselines but does not consistently beat a tuned linear model, SLIM (p. 1).
- Selection method: the authors hand-screened long papers from KDD, SIGIR, WWW and RecSys published 2015–2018. Papers qualified if they proposed a deep-learning method for top-n recommendation evaluated with classification or ranking metrics, which gave 18 papers. Authors were contacted when code or data was missing, with a 30-day wait (p. 2).
- Definition of "reproducible": working code that needs at most minimal changes, plus at least one public dataset with train-test splits that are either published or can be rebuilt. Skeleton code and private or scraped data count as non-reproducible (p. 2).
- Reproducibility rate: 7/18 (39%) overall. By venue: KDD 3/4 (75%), RecSys 1/7 (14%), SIGIR 1/3 (30%), WWW 2/4 (50%) (p. 3, Table 1). Detailed per-year statistics are not shown; the text only says the rate rose over the years (p. 3).
- Method: the original code is refactored so that training, tuning and prediction are separate from a shared evaluation module that also scores the baselines. Neural methods use the authors' reported optimal hyper-parameters, and re-tuning them is left to future work (p. 3, footnote 4).
- Baseline tuning: Scikit-Optimize Bayesian search with 35 cases, of which the first 5 are random. Ranges: k 5–800, shrink h 0–1000, α and β 0–2 (p. 4). P3α is a 3-step random walk; RP3β divides P3α's similarities by item popularity raised to the power β (p. 3–4).
- CMN (SIGIR '18; CMN-3 reported): it is not the best method on any dataset or measure.
  - CiteULike-a, HR@5: 0.8069, against 0.8226 for RP3β (p. 4, Table 2).
  - Pinterest, HR@5: 0.6872, against 0.7018 for RP3β (p. 4, Table 2).
  - Epinions, HR@5: TopPopular scores 0.5429, against 0.4195 for CMN. CMN does beat the personalized baselines there (p. 4, Table 2).
  - Epinions has a Gini index of 0.69, against 0.37 for CiteULike-a. CMN's lists are 8% to 25% more popular than the baselines' lists (p. 4).
- MCRec (KDD '18): only MovieLens100k could be run, because the meta-paths are hard-coded. ItemKNN scores PREC@10 0.3327 and NDCG@10 0.2603, against 0.3077 and 0.2363 for MCRec (p. 5, Table 3). The original code uses an unusual NDCG (replaced here with the standard one) and picks the best epoch per metric on the test set (p. 4–5).
- CVAE (KDD '18), dense CiteULike-a:
  - REC@50: 0.0772 for CVAE, against 0.0811 for RP3β and 0.1837 for ItemKNN-CFCBF (p. 5, Table 4).
  - REC@300: 0.3602 for CVAE, against 0.4486 for ItemKNN-CFCBF (p. 5, Table 4).
  - The text says CVAE beats the baselines at cutoffs of 100 and above "on two datasets". In Table 4 it beats only the pure-CF baselines at those cutoffs, never ItemKNN-CFCBF. The other dataset configurations are not tabulated (p. 5).
- CDL (KDD '15), dense CiteULike-a: REC@50 is 0.0543, against 0.2135 for ItemKNN-CBF. REC@300 is 0.2627, against 0.4707 for ItemKNN-CBF (p. 5, Table 5). The claim that CDL wins beyond cutoff 100 in two of four configurations is not shown in a table. CVAE is always better than CDL (p. 5).
- NCF/NeuMF (WWW '17): the original code chose the number of epochs on the test set; here it is chosen on a validation set (p. 6).
  - Pinterest, HR@5: 0.7024 for NeuMF, against 0.7105 for RP3β and 0.7100 for ItemKNN (p. 6, Table 6).
  - MovieLens1M, HR@5: 0.5486 for NeuMF beats RP3β at 0.4922, but SLIM (Elastic Net) scores 0.5589. NDCG@10 is 0.4470 for SLIM, against 0.4369 for NeuMF (p. 6, Table 6).
- SpectralCF (RecSys '18): the paper reports a single hyper-parameter set for all datasets. On HetRec and Amazon Instant Video, all baselines, TopPopular included, beat it on every measure (p. 6).
  - On the authors' provided MovieLens split, its Recall@20 is 50% higher than the best baseline. That split's test set has a Gini index of 0.92, against about 0.79 for a random split (p. 6–7; Figure 1 shows the train and test popularity curves).
  - On the authors' own random splits (five repeats), REC@20 is 0.1843 for SpectralCF, against 0.1853 for TopPopular and 0.2910 for RP3β (p. 7, Table 7).
- Mult-VAE (WWW '18): the original paper reports about 3% over its best baseline. Here it is 10% to 20% better than the best simple baseline, and up to 5% better than a tuned SLIM (p. 7).
  - Netflix, REC@20: 0.2626 for Mult-VAE, against 0.2551 for SLIM (p. 7, Table 8).
  - Netflix, NDCG@100: 0.3756 for Mult-VAE, against 0.3745 for SLIM (p. 7, Table 8).
  - Extra cutoffs: NDCG@20 is 0.2473 for SLIM, against 0.2448 for Mult-VAE. REC@100 is 0.5476 for Mult-VAE, against 0.5289 for SLIM (p. 7, Table 9).
  - Weighted MF was also tuned, but its numbers are not tabulated. The "similar phenomenon" on MovieLens is not shown (p. 7).
- Discussion: the papers used more than 20 public datasets and many protocols (80/20 holdout, leave-one-out, 100 or 50 sampled negatives). At least two of the 18 papers were evaluated only on a single private dataset with no code (p. 8, footnote 11). NCF is widely used as a "state-of-the-art" baseline even though it is weak (p. 8).
- Not covered: neural methods are not re-tuned, and matrix factorization baselines are mostly absent (left to future work, p. 9). There are no significance tests. Runtimes are discussed only in general terms (p. 8).
- The paper's own inconsistencies:
  - SIGIR 1/3 is printed as "30%" (p. 3, Table 1), and the overall 7/18 (39%) is described as "about one third" (p. 3).
  - The text says SpectralCF "in all configurations performed worse than our baseline methods and was outperformed even by the TopPopular method". Yet at REC@100 it scores 0.4254, against 0.4244 for TopPopular (p. 7, Table 7).

## Related in library

- Neural Collaborative Filtering: one of the 7 reproduced methods. Tuned kNN/RP3β beat NeuMF on Pinterest and SLIM beats it on MovieLens1M.
- Variational Autoencoders for Collaborative Filtering: Mult-VAE is the only reproduced method that beats the simple baselines. Its edge over tuned SLIM is small and shrinks on NDCG.
- A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research: the same reproducibility-and-baseline design, applied to 12 neural methods.
- Neural Collaborative Filtering vs. Matrix Factorization Revisited: agrees that NCF's MLP-based approach does not beat well-tuned simpler models.
- On the Difficulty of Evaluating Baselines. A Study on Recommender Systems: makes the same argument that poorly tuned baselines inflate reported progress.

## Q&A
