# Improving Language Understanding by Generative Pre-Training

type: method
read: full
family: generative language-model pre-training then discriminative fine-tuning (decoder-only Transformer)
evidence: 12 NLU datasets (NLI, QA/commonsense, sentence similarity, classification, GLUE), compared with previously published best results, many of them ensembles; strength: single model, no seeds or variance reported, ablations limited to GLUE tasks (Table 5), dev/test split not stated
conversion: Eq. 5 (the combined fine-tuning objective) is empty in the markdown (p. 3); the prose recovers it as the supervised objective plus the LM objective weighted by λ. Table 1 rows are merged into single cells but readable by order (p. 4).

## Digest

- **Claim.** A single task-agnostic Transformer language model is pre-trained on unlabeled text and then fine-tuned with minimal architecture changes. It improves on the state of the art in "9 out of the 12" tasks studied and beats task-specific architectures (p. 1).
- **Pre-training stage.** Standard left-to-right LM likelihood over a context window k (Eq. 1). Training uses BooksCorpus, over 7,000 unpublished books, chosen for long contiguous text. The 1B Word Benchmark used by ELMo was rejected because it is shuffled at sentence level (p. 3–4). Token-level perplexity is 18.4 on this corpus (p. 4).
- **Model.**
  - 12-layer decoder-only Transformer, 768-dim states, 12 heads, 3072-dim feed-forward inner states.
  - GELU activations, learned position embeddings.
  - BPE vocabulary with 40,000 merges, ftfy and spaCy preprocessing.
- **Pre-training optimisation.**
  - Adam with max learning rate 2.5e-4, linear warmup over 2000 updates, then cosine annealing.
  - 100 epochs on minibatches of 64 × 512-token sequences.
  - Dropout 0.1, modified L2 with w = 0.01 (p. 4).
- **Not disclosed.** Parameter count, compute and training time are not given.
- **Fine-tuning stage.**
  - The final block's activation for the last token feeds a new linear+softmax layer W_y (Eq. 3–4).
  - The LM loss is kept as an auxiliary objective with λ = 0.5. It is claimed to improve generalisation and speed convergence (p. 3–4).
  - The only new parameters are W_y and the delimiter embeddings.
  - Settings: learning rate 6.25e-5, batch 32, typically 3 epochs, warmup over 0.2% of training, classifier dropout 0.1 (p. 4).
- **Task-specific input transformations ("traversal-style").** Structured inputs become one token sequence with start, end and delimiter ($) tokens (p. 4):
  - Entailment: premise $ hypothesis.
  - Similarity: both sentence orderings are encoded and their representations summed element-wise.
  - QA and multiple choice: [z; q; $; a_k] per answer, with a softmax over the answers.
- **NLI results** (p. 5–6, Table 2), against the previous best:
  - MNLI-m 82.1 vs 80.6 (Stochastic Answer Network, 3x ensemble).
  - SNLI 89.9 vs 89.3 (5x ensembles).
  - SciTail 88.3 vs 83.3 (CAFE).
  - QNLI 88.1 vs 82.3 (GenSen).
  - RTE 56.0 loses to 61.7 (Multi-task BiLSTM + Attn). The paper attributes this to the small dataset (2490 examples).
- **QA and commonsense results** (p. 6, Table 3), against the previous best:
  - Story Cloze 86.5 vs 77.6 (Hidden Coherence Model).
  - RACE 59.0 vs 53.3 (BiAttention MRU, 9x ensemble).
  - RACE-m 62.9 vs 60.2 and RACE-h 57.4 vs 50.3, both against the same baseline.
- **Classification and similarity results** (p. 6, Table 4):
  - CoLA 45.4 vs 35.0 (Single-task BiLSTM+ELMo+Attn).
  - STS-B 82.0 vs 81.0 (ECNU mixed ensemble).
  - QQP 70.3 vs 66.1 (Single-task BiLSTM+ELMo+Attn).
  - GLUE 72.8 vs 68.9 (Multi-task BiLSTM+ELMo+Attn).
  - Losses: SST-2 91.3 vs 93.2 (Sparse byte mLSTM), called "competitive"; MRPC 82.3 vs 86.0 (TF-KLD).
- **GLUE claim not supported by the table.** The introduction claims an absolute improvement of "5.5%" on GLUE (p. 1). Table 4 shows 72.8 vs 68.9, which does not match.
- **Transfer depth** (p. 7, Fig. 2 left). Each transferred layer helps, "up to 9%" for full transfer on MultiNLI. The figure is the only evidence; no numeric table is given.
- **Zero-shot heuristics** (p. 7, Fig. 2 right). The heuristics cover CoLA (log-prob threshold), SST-2 ("very" + positive/negative), RACE and DPRD Winograd. Their performance rises steadily over pre-training, and the LSTM shows higher variance. This is reported only qualitatively through the figure.
- **Ablations: no pre-training and LSTM** (p. 7–8, Table 5; average over GLUE tasks), against the full model at 74.7:
  - Without pre-training: 59.9, described as a "14.8% decrease".
  - Single-layer 2048-unit LSTM with aux LM: 69.1, described as a "5.6 average score drop". The LSTM wins only on MRPC (83.2 vs 82.3).
- **Ablation: auxiliary LM.** Without the auxiliary LM objective the average is 75.0, slightly above the full model's 74.7 (Table 5). The paper reads this as larger datasets (NLI, QQP) benefiting and smaller ones not. The method section's claim that the auxiliary objective improves generalisation is therefore not supported by the average.
- **Table inconsistency.** Table 5 gives MNLI 81.8 for the full model, while Table 2 gives MNLI-m 82.1. The difference is not explained.
- **Robustness.** No seeds, confidence intervals or significance tests are reported, even though "significantly" is used throughout.

## Related in library

## Q&A
