# Deep Neural Networks for YouTube Recommendations

type: system
family: two-stage deep retrieval (candidate generation) and ranking for industrial recommendation
evidence: YouTube's production data. Offline holdout MAP for candidate generation is shown only as a plot. Offline next-day holdout watch-time-weighted pairwise loss is reported for ranking-net depth and width ablations. Live A/B tests are mentioned but give no numbers. Baselines are the earlier YouTube matrix factorization, linear and tree-based systems, with no figures for them; strength: vendor-run, single proprietary dataset, small ablations only, no public benchmark

## Digest

- **Claim.** A funnel of two DNNs gives large gains in YouTube recommendation:
  - candidate generation narrows a corpus of millions to hundreds of videos;
  - ranking then scores those hundreds and presents dozens (p. 2, Figure 2).
- **Scale.** The models learn about one billion parameters and are trained on hundreds of billions of examples (p. 1).

**Candidate generation**

- **Framing.** Recommendation is posed as extreme multiclass classification. A softmax over corpus videos takes a dot product between a learned user/context embedding u and video embeddings v_j (p. 2).
- **Training signal.** The label is implicit feedback: a completed watch is a positive example. Explicit thumbs up/down is not used (p. 2).
- **Sampled softmax.** Training samples negatives and corrects with importance weighting. Several thousand negatives are sampled, which the paper says is "more than 100 times speedup over traditional softmax" (p. 2). Hierarchical softmax reached lower accuracy, and no numbers are given for it (p. 2–3).
- **Serving.** Scoring is approximate nearest-neighbor search in dot-product space. The paper says A/B results were "not particularly sensitive" to the choice of ANN algorithm (p. 3).
- **Inputs.**
  - Averaged watch-ID embeddings; averaging beat sum and component-wise max, with no numbers given (p. 3).
  - Averaged embeddings of search unigrams and bigrams.
  - Geographic and device embeddings.
  - Gender, logged-in state and age, normalized to [0, 1].
  - These feed a "tower" of ReLU layers (p. 3–4, Figure 3).
- **"Example age" feature.**
  - In training, the age of the training example is fed as an input. At serving it is set to zero or slightly negative, which removes the bias toward the average popularity over the training window.
  - It is shown on one arbitrarily chosen video, as a plot only (p. 3, Figure 4).
  - The conclusion says it "increased the watch time dramatically on recently uploaded videos in A/B testing", but no number is printed (p. 7).
- **Label and context choices.**
  - A fixed number of training examples per user, so very active users do not dominate the loss (p. 3).
  - Training examples come from all YouTube watches, not only watches on recommendations (p. 3).
  - Search queries enter as an unordered bag, to hide where the label came from (p. 4).
  - The model predicts the *next* watch from a "rolled-back" history rather than a randomly held-out watch, because the held-out setup leaks future information. The paper says the next-watch setup was better in A/B tests, with no numbers (p. 4–5, Figure 5).
- **Feature and depth experiments.**
  - Setup: 1M videos and 1M search tokens, 256-dimensional embeddings, bags of at most 50 watches and 50 searches. Depths 0 to 4 follow a halving tower, from depth 1 (256 ReLU) up to 2048→1024→512→256 (p. 4–5).
  - Results appear only as holdout MAP % in a plot (p. 5, Figure 6).
  - Depth 0 is said to perform "very similarly" to the predecessor matrix factorization, with no number (p. 4–5).

**Ranking**

- **Model.** A DNN scores each impression with weighted logistic regression. The objective is described as "generally a simple function of expected watch time per impression" (p. 5).
- **Features.**
  - Hundreds of features, roughly half categorical and half continuous (p. 5).
  - The most important features describe the user's past interaction with the item or similar items, such as the channel (p. 6).
  - Features also carry candidate-source scores and impression frequency, the latter to create "churn" between requests (p. 6).
- **Embeddings.**
  - Embedding dimension is approximately proportional to log(cardinality) (p. 6).
  - Vocabularies are truncated to the top N by frequency in clicked impressions; out-of-vocabulary values map to the zero embedding (p. 6).
  - Features in the same ID space share one embedding table but are fed to the network separately (p. 6).
  - The paper's illustration: 1M IDs × 32 dimensions has "7 times more parameters" than fully connected layers 2048 wide (p. 6).
- **Continuous features.** They are quantile-normalized to [0, 1) using the CDF; the integral expression is garbled in the text layer. The network also receives x̃² and √x̃ (p. 7).
- **Watch-time weighting.**
  - Positives are weighted by watch time and negatives get unit weight.
  - The learned odds are given as ΣT_i/(N−k), garbled in the text layer, and are said to be approximately E[T](1+P) ≈ E[T].
  - At inference the output is e^x (p. 7).

**Ranking results**

- Results are watch-time-weighted, per-user pairwise mispredicted-watch-time loss on next-day holdout (p. 7, Table 1):

| Hidden layers | Loss |
|---|---|
| None | 41.6% |
| 256 ReLU | 36.9% |
| 512 ReLU | 36.7% |
| 1024 ReLU | 35.8% |
| 512→256 | 35.2% |
| 1024→512 | 34.7% |
| 1024→512→256 | 34.6% |

- 1024→512→256 was chosen as the best configuration within the serving CPU budget (p. 7).
- Ablations against the 1024→512→256 model (p. 7):
  - Dropping the powers of continuous features raised loss by 0.2%.
  - Weighting positives and negatives equally raised loss by 4.1%.
  - The paper does not say whether these are absolute or relative changes.

**What the text claims beyond its numbers**

- The conclusion says the model outperforms the earlier matrix factorization and the "previous linear and tree-based methods" (p. 7). It also says watch-time weighting "performed much better … compared to predicting click-through rate directly". None of these comparisons has a reported number.
- No live A/B numbers are reported anywhere.

## Related in library
