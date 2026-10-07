# Improving Language Understanding by Generative Pre-Training

type: method
read: full
family: generative language-model pre-training, then discriminative fine-tuning (decoder-only Transformer transfer)
evidence: 12 NLU datasets (NLI, QA/commonsense, semantic similarity, classification; GLUE), compared with prior state of the art including ensembles; strength: one model size, single runs with no variance reported, one ablation table (aux LM, LSTM, no pre-training)
conversion: Eq. (5), the combined fine-tuning objective, is empty in the markdown (p. 3), but the prose says it is the supervised loss plus the LM loss weighted by λ; Eq. (2) reads "∀i ∈ [1, n]" where the layer index is meant (p. 3); Table 1 is flattened into one row but readable in order (p. 4)

## Digest

- Claim: generative LM pre-training on unlabeled contiguous text, followed by discriminative fine-tuning with minimal architecture change, beats task-specific architectures on 9 of 12 NLU datasets (p. 1, p. 5–7).
- Pre-training maximises the standard next-token likelihood over a context window k (Eq. 1). The model is a 12-layer decoder-only Transformer with masked self-attention, 768-dim states, 12 heads, 3072-dim FFN, GELU and learned position embeddings (p. 3–4).
- Pre-training setup: BooksCorpus (over 7,000 unpublished books). It was chosen for long contiguous text, against the sentence-shuffled 1B Word Benchmark. The setup uses BPE with 40,000 merges, Adam with max lr 2.5e-4, 2000-update warmup with cosine decay, 100 epochs, batches of 64 × 512 tokens, and dropout 0.1 (p. 4). The LM reaches token-level perplexity 18.4 on this corpus (p. 4).
- Fine-tuning adds one linear output layer W_y on the final token's activation, plus delimiter-token embeddings. The LM loss is kept as an auxiliary objective with λ = 0.5. Other settings: lr 6.25e-5, batch 32, typically 3 epochs, classifier dropout 0.1 (p. 3–4).
- Task-specific "traversal-style" input transformations turn structured inputs into one token sequence:
  - Entailment: premise $ hypothesis.
  - Similarity: both orderings, with their representations summed element-wise.
  - QA/multiple choice: [z; q; $; a_k] per answer, then a softmax over answers (p. 4).
- NLI results (Table 2, p. 5–7):
  - MNLI-m 82.1 vs 80.6 for the Stochastic Answer Network (3x ensemble).
  - SNLI 89.9 vs 89.3 for ESIM+ELMo and CAFE (5x).
  - SciTail 88.3 vs 83.3 for CAFE.
  - QNLI 88.1 vs 82.3 for GenSen.
  - RTE 56.0, which loses to 61.7 for Multi-task BiLSTM+Attn.
- QA results (Table 3, p. 5–7):
  - Story Cloze 86.5 vs 77.6 for the Hidden Coherence Model.
  - RACE 59.0 vs 53.3 for BiAttention MRU (9x ensemble). RACE-m is 62.9 vs 60.2 and RACE-h is 57.4 vs 50.3.
- Similarity and classification on GLUE (Table 4, p. 5–7):
  - CoLA 45.4 vs 35.0 for Single-task BiLSTM+ELMo+Attn.
  - STS-B 82.0 vs 81.0 for the ECNU ensemble.
  - QQP 70.3 vs 66.1 for Single-task BiLSTM+ELMo+Attn.
  - MRPC 82.3, below 86.0 for TF-KLD.
  - SST-2 91.3, below 93.2 for Sparse byte mLSTM.
  - GLUE overall 72.8 vs 68.9 for Multi-task BiLSTM+ELMo+Attn.
- The three datasets not won are RTE, MRPC and SST-2. Several "state-of-the-art" margins compare a single model against ensembles (p. 5–7).
- Mismatch: the introduction claims a "5.5%" GLUE improvement (p. 1), but Section 4.2 and Table 4 give 72.8 vs a previous best of 68.9 (p. 5–7).
- Layer-transfer analysis: each transferred layer helps, "up to 9% for full transfer on MultiNLI" (p. 7, Fig. 2 left). This is shown only in a figure, with no numbers in the text.
- Zero-shot heuristics (scoring by LM log-probability) were run on CoLA, SST-2, RACE and DPRD. Performance rises steadily over pre-training, and an LSTM shows higher variance (p. 7, Fig. 2 right). These results exist only as a normalised plot, with no numbers given.
- Ablations (Table 5, p. 7), unweighted average over 8 GLUE tasks:
  - Full model: 74.7.
  - Without pre-training: 59.9, described as a "14.8% decrease"; it is worse on every task.
  - LSTM (single layer, 2048 units) with aux LM: 69.1, described as a "5.6 average score drop"; it beats the Transformer only on MRPC (83.2 vs 82.3).
  - Without aux LM: 75.0, higher than the full model's average.
- On the aux LM, the paper says it helps on NLI tasks and QQP and suggests larger datasets benefit while smaller ones do not (p. 7). The table does not support a net benefit: the average is 75.0 without vs 74.7 with, and CoLA, SST-2, MRPC and STS-B are higher without it. This weakens the Section 3.2 statement that the aux objective improves generalisation (p. 3).
- Table 5 lists MNLI 81.8 for the full model, while Table 2 lists MNLI-m 82.1 (p. 5–7). The paper does not explain the difference, for example a split or a matched/mismatched average.
- Not disclosed:
  - total parameter count;
  - pre-training compute and time;
  - whether reported scores are dev or test (apart from Table 4 "done using the GLUE benchmark");
  - seeds or variance;
  - per-task deviations from the default fine-tuning hyperparameters ("for most tasks").
- The paper never uses the name "GPT"; its model is called "Finetuned Transformer LM".

## Related in library

## Q&A
