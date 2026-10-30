# Deep Neural Networks for YouTube Recommendations

type: system
family: two-stage deep retrieval + ranking (embedding-based candidate generation, weighted-logistic ranker)
evidence: YouTube holdout data (MAP for candidate generation, watch-time-weighted pairwise loss for ranking) and unquantified live A/B tests, compared against the predecessor matrix-factorization system and against own ablations; strength: single proprietary production system, no public benchmark, no external baselines, A/B gains not given as numbers

## Digest

- Claim: deep neural networks give "dramatic performance improvements" in YouTube's two-stage recommender. A candidate-generation network narrows millions of videos to hundreds, and a ranking network scores those hundreds (p. 1–2, Figure 2).
- Scale: about one billion parameters, trained on hundreds of billions of examples, built on Google Brain / TensorFlow (p. 1).
- Candidate generation is posed as extreme multiclass classification. A softmax over corpus videos is computed from a user/context embedding u and video embeddings v_j (p. 2). Training uses sampled softmax with importance weighting. "Several thousand" negatives give "more than 100 times speedup over traditional softmax" (p. 2). Hierarchical softmax did not reach comparable accuracy (p. 2–3).
- Serving uses approximate nearest-neighbor search in dot-product space. A/B results were "not particularly sensitive" to the choice of search algorithm (p. 3).
- Inputs (p. 3–4, Figure 3):
  - averaged embeddings of watched video IDs; averaging beat sum and component-wise max;
  - averaged search-token embeddings (unigrams and bigrams);
  - geography and device embeddings;
  - gender, logged-in state and age, normalized to [0, 1].
- "Example age" feature: the age of the training example is fed in during training and set to zero (or slightly negative) at serving. This removes the bias toward the past and fits upload-time popularity. It is shown only for one video in a plot (p. 3, Figure 4).
- Label and context choices, all reported as A/B lessons with no numbers:
  - training examples come from all watches, not just watches on recommendations;
  - each user contributes a fixed number of examples;
  - search order is discarded (bags of tokens) so the model cannot reproduce the last search page;
  - the model predicts the next watch from prior history (rollback) rather than a held-out random watch (p. 3–5, Figure 5).
- Depth/feature experiments: 1M videos and 1M search tokens, 256-dim embeddings, up to 50 recent watches and 50 recent searches, tower networks of depth 0–4 (depth 4: 2048→1024→512→256) (p. 4–5).
  - Depth 0 "performed very similarly to the predecessor system" (p. 4–5).
  - Holdout MAP rises with depth and with added features (watches only → watches & searches → watches, searches & example age → all features). The values appear only in a plot (p. 5, Figure 6).
- Ranking network:
  - scores each impression; hundreds of features, roughly half categorical and half continuous (p. 5–6, Figure 7);
  - each embedding has its own dimension, growing roughly with the log of vocabulary size; vocabularies are truncated to the top N by clicked-impression frequency, and out-of-vocabulary values map to the zero embedding (p. 6);
  - shared embeddings serve all features that use the same ID space (p. 6);
  - continuous features are quantile-normalized to [0, 1), and x̃² and √x̃ are also input (p. 6–7).
- The most important ranking signals are the user's past interactions with the item or similar items (e.g. the channel), candidate-source features, and the frequency of past impressions (which produces "churn") (p. 6).
- Watch-time objective: weighted logistic regression. Clicked impressions are weighted by watch time and unclicked ones get unit weight. The learned odds are approximately E[T](1+P), close to E[T], and e^x is used at inference (p. 7). The odds formula (ΣT_i / (N−k)) is garbled in the text layer.
- Ranking results (p. 7, Table 1): weighted per-user loss on next-day holdout is 41.6% with no hidden layers. It falls with width and depth (e.g. 256 ReLU 36.9%, 1024 ReLU 35.8%, 1024→512 34.7%) to 34.6% for 1024→512→256. That configuration was chosen as best within the serving CPU budget.
- Ranking ablations on the 1024→512→256 model (p. 7):
  - dropping the power features raises loss by 0.2%;
  - weighting positives and negatives equally raises it by 4.1%.
- Claims stated without numbers in the text (p. 7):
  - the ranker outperformed previous linear and tree-based methods;
  - example age "increased the watch time dramatically" on recently uploaded videos in A/B testing;
  - the candidate model outperforms prior matrix factorization.
- The paper states that offline metrics and live A/B results are not always correlated (p. 2).
- Not disclosed: the full feature list, training hardware and time, the exact sampling distribution, and live A/B magnitudes.

## Related in library
