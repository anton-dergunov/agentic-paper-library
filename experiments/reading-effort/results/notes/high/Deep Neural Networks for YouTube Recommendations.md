# Deep Neural Networks for YouTube Recommendations

type: system
family: two-stage deep neural recommender (candidate generation by sampled-softmax classification with nearest-neighbour serving, then a deep ranking model trained with watch-time-weighted logistic regression)
evidence: YouTube's internal data only. Candidate generation is measured by holdout MAP across network depths and feature sets (p. 5, Figure 6). Ranking is measured by a watch-time-weighted pairwise loss on next-day holdout data across hidden-layer settings (p. 7, Table 1). Comparisons are against the paper's own variants: a depth-0 linear factorization, an unweighted model and a model without feature powers. A/B results are claimed but no numbers are given; strength: vendor-run, proprietary data, internal ablations only, no external or published baselines.

## Digest

- Claim: deep learning brought "dramatic performance improvements" to YouTube recommendations. The system is split into two neural networks. Candidate generation narrows a corpus of millions of videos down to hundreds. Ranking scores those hundreds and only a few dozen are shown (p. 2, Figure 2). Other candidate sources can be blended in before ranking (p. 2).
- Scale: the models learn about one billion parameters and are trained on hundreds of billions of examples. The system is built on Google Brain / TensorFlow (p. 1). The paper names three challenges: scale, freshness and noisy implicit feedback (p. 1).
- Candidate generation is posed as extreme multiclass classification. A softmax over corpus videos takes the dot product of a user/context embedding u with video embeddings v_j (p. 2). The softmax equation is spread over lines in the text layer.
- Training uses implicit feedback: a user completing a video is a positive example. Explicit signals (thumbs up/down, surveys) are not used, because implicit history is orders of magnitude larger (p. 2).
- Sampled softmax with importance weighting: "several thousand negatives" per example, giving "more than 100 times speedup over traditional softmax." Hierarchical softmax was tried but did not reach comparable accuracy (pp. 2–3).
- Serving does not need calibrated probabilities, so scoring becomes approximate nearest-neighbour search in dot-product space. A/B results were "not particularly sensitive" to the choice of nearest-neighbour algorithm (p. 3).
- Architecture: bags of watched-video IDs and search tokens (unigrams and bigrams) are embedded and averaged. Averaging beat sum and component-wise max. These are concatenated with embedded geography and device and with gender, logged-in state and age normalized to [0, 1], then passed through a ReLU tower (p. 3, Figure 3).
- "Example age" feature: the age of each training example is fed in during training and set to zero or slightly negative at serving. This removes the model's bias toward the average popularity over a training window of several weeks. Figure 4 illustrates it on a single arbitrarily chosen video (p. 3, Figure 4). In the future-watch setup the feature is defined as tmax − tN (p. 5, Figure 5).
- Label and context choices:
  - Examples come from all YouTube watches, including watches embedded on other sites, not only watches from recommendations.
  - Each user contributes a fixed number of examples, so heavy users do not dominate the loss.
  - Search queries enter as unordered token bags so the model cannot simply replay the last search page (pp. 3–4).
  - The model predicts the *next* watch from a rolled-back history rather than a randomly held-out watch, which leaks future information. The future-watch version did better in A/B testing; no numbers are given (pp. 4–5, Figure 5).
- Candidate-generation experiment setup:
  - 1M videos and 1M search tokens, each embedded in 256 floats.
  - At most 50 recent watches and 50 recent searches per user.
  - Softmax over 1M classes with dimension 256.
  - Trained to convergence over all users (several epochs).
  - Tower depths 0–4, from a linear layer up to 2048→1024→512→256 ReLU (pp. 4–5).
- The depth-0 network "performed very similarly to the predecessor system," a matrix factorization trained under rank loss (pp. 2, 4–5). Adding features (watches only → +searches → +example age → all features) and adding depth raise holdout MAP %. The values appear only in the plot (p. 5, Figure 6).
- Ranking: a DNN similar to candidate generation scores each impression. The objective is "generally a simple function of expected watch time per impression"; ranking by CTR is said to promote clickbait (p. 5). Features are split into categorical vs continuous, univalent vs multivalent, and impression vs query (p. 5). Ranking models use "hundreds of features," roughly half categorical and half continuous (p. 5).
- Ranking features and embeddings:
  - The strongest signals are the user's past interactions with the item and with similar items, such as the channel or topic.
  - Candidate-generation sources and their scores are passed to ranking as features.
  - Features on past impression frequency create churn between requests (p. 6).
  - Embedding dimension grows roughly with the log of vocabulary size. Vocabularies are truncated to the top N by frequency in clicked impressions; out-of-vocabulary values get a zero embedding.
  - Features in the same ID space share one embedding. The paper states that one million IDs in 32 dimensions have "7 times more parameters than fully connected layers 2048 units wide" (p. 6).
- Continuous features are normalized to [0, 1) through their empirical CDF, interpolated from quantiles; x̃² and √x̃ are also input (pp. 6–7). The integral is garbled in the text layer.
- Weighted logistic regression: clicked impressions are weighted by watch time and unclicked ones get unit weight. The learned odds are ΣTi/(N−k), approximately E[T](1+P), which is close to E[T] when the click probability P is small. Serving applies e^x (p. 7). The odds fraction is garbled across lines in the text layer.
- Ranking metric, "weighted, per-user loss": for clicked/unclicked impression pairs on one page, it is the watch time of the clicked impression whenever the unclicked one scores higher, as a fraction of total watch time (p. 7).
- Table 1 results (p. 7, Table 1), lower is better:
  - No hidden layers: 41.6%.
  - Single layer: 256 ReLU 36.9%, 512 ReLU 36.7%, 1024 ReLU 35.8%.
  - Two layers: 512→256 35.2%, 1024→512 34.7%.
  - 1024→512→256: 34.6%. This setting was chosen as best within the serving CPU budget.
- Ablations on the 1024→512→256 model: dropping the feature powers raised loss by 0.2%, and weighting positives and negatives equally raised it by "a dramatic 4.1%." The paper does not say whether these are absolute points or relative changes (p. 7).
- Several claims have no numbers behind them:
  - The deep model "outperform[s] previous matrix factorization approaches" (p. 7, Conclusions), yet the depth-0 result is described only as similar to the predecessor and no comparison against it appears in a table.
  - Ranking "outperformed previous linear and tree-based methods" (p. 7), with no numbers.
  - Example age "increased the watch time dramatically on recently uploaded videos in A/B testing" (p. 7), with no numbers.
  - No live A/B magnitudes are reported anywhere, even though the paper notes that offline and live results are not always correlated (p. 2).
- Not disclosed: the dataset or its size beyond orders of magnitude, training hyperparameters, how many negatives are sampled exactly, the exact final ranking objective, latency figures other than "tens of milliseconds" (p. 3), and any public reproduction.

## Related in library

## Q&A
