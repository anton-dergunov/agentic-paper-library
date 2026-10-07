# Improving Language Understanding by Generative Pre-Training

type: method
read: full
family: generative language-model pre-training followed by discriminative fine-tuning (decoder-only Transformer)
evidence: 12 NLU datasets covering NLI, QA/commonsense, semantic similarity, classification and GLUE, against the previous state of the art per dataset, often task-specific architectures and ensembles; strength: single runs with no variance or significance tests, one pre-training corpus, one model size, ablations on GLUE tasks only
conversion: Eq. 5 (the fine-tuning objective combining the supervised loss with the auxiliary LM loss weighted by λ) is empty in the markdown (p. 3), but the prose says what it combines; Table 1 is flattened into one cell per column but readable by order (p. 4)

## Digest

- **Claim.** A task-agnostic Transformer language model, pre-trained on unlabeled contiguous text and then fine-tuned with minimal architecture changes, beats discriminatively trained, task-specific models. The paper says it improves the state of the art on "9 out of the 12" tasks (p. 1, Abstract; p. 5–6).
- **Stage 1, pre-training.** A standard left-to-right LM objective over a context window k, Eq. 1 (p. 3). The model is a multi-layer Transformer decoder with masked self-attention, learned position embeddings and an output softmax tied to the token embeddings, Eq. 2 (p. 3).
- **Stage 2, fine-tuning.** A linear layer W_y is added on the final-token activation, Eq. 3–4 (p. 3).
  - An auxiliary LM loss weighted by λ is kept during fine-tuning (Eq. 5, missing in the conversion). λ was set to 0.5 (p. 4–5).
  - The only new parameters are W_y and the delimiter embeddings (p. 3).
- **Task-specific input transformations.** Structured inputs are turned into one token sequence, with randomly initialised start/end tokens and a delimiter "$" (p. 4, Fig. 1).
  - Entailment: premise $ hypothesis.
  - Similarity: both sentence orders are encoded and their representations added element-wise.
  - QA and multiple choice: [z; q; $; a_k] for each answer, with a softmax over the answers.
- **Setup.**
  - Data: BooksCorpus, "over 7,000" unpublished books. It was chosen over the 1B Word Benchmark because it keeps long-range structure (p. 4).
  - Model: 12 layers, 768-dim states, 12 heads, 3072-dim FFN, GELU, 40,000 BPE merges.
  - Pre-training: Adam with max learning rate 2.5e-4, 2000 warmup updates and cosine decay; 100 epochs on batches of 64 × 512 tokens (p. 4–5).
  - Fine-tuning: learning rate 6.25e-5, batch size 32, usually 3 epochs (p. 4–5).
  - The LM's token-level perplexity is 18.4, with no baseline given (p. 4).
- **Not disclosed:**
  - parameter count, compute and training time;
  - corpus size in tokens;
  - number of runs or seeds;
  - which splits each result uses (dev or test);
  - any check for overlap between the corpus and the benchmarks.
- **NLI, against the previous best** (p. 5, Table 2):
  - MNLI-m 82.1 / MNLI-mm 81.4 vs 80.6 / 80.1 (Stochastic Answer Network, 3x ensemble);
  - SNLI 89.9 vs 89.3 (ESIM+ELMo 5x and CAFE 5x);
  - SciTail 88.3 vs 83.3 (CAFE);
  - QNLI 88.1 vs 82.3 (GenSen);
  - RTE 56.0, below 61.7 (Multi-task BiLSTM+Attn).
- **QA and commonsense, against the previous best** (p. 5–6, Table 3):
  - Story Cloze 86.5 vs 77.6 (Hidden Coherence Model);
  - RACE 59.0 vs 53.3 (BiAttention MRU, 9x ensemble);
  - RACE-m 62.9 vs 60.2;
  - RACE-h 57.4 vs 50.3.
- **Similarity and classification on GLUE** (p. 5–6, Table 4):
  - CoLA 45.4 vs 35.0 (Single-task BiLSTM+ELMo+Attn);
  - STS-B 82.0 vs 81.0 (ECNU ensemble);
  - QQP 70.3 vs 66.1 (Single-task BiLSTM+ELMo+Attn);
  - GLUE overall 72.8 vs 68.9 (Multi-task BiLSTM+ELMo+Attn).
- **The three losses** in the 9-of-12 count: SST-2 91.3 vs 93.2 (Sparse byte mLSTM), MRPC 82.3 vs 86.0 (TF-KLD), and RTE (above).
- **Claims the tables do not support:**
  - "Significantly" is used throughout with no statistical test (p. 1, p. 5).
  - The introduction claims "5.5%" on GLUE (p. 1). Table 4 lists 72.8 vs a previous best of 68.9, and the text does not reconcile the two.
- **Ablations** (p. 7–8, Table 5):

  | Variant | Avg. score |
  |---|---|
  | Full model (Transformer with aux LM) | 74.7 |
  | Without pre-training | 59.9 |
  | Without aux LM | 75.0 |
  | LSTM with aux LM | 69.1 |

  - The text reports these as a "14.8% decrease" without pre-training and a "5.6 average score drop" with the LSTM.
  - The LSTM is described as a single-layer, 2048-unit LSTM in the same framework. It beats the Transformer only on MRPC (83.2 vs 82.3).
- **Auxiliary LM caveat.** The variant without the auxiliary LM has a higher average (75.0 vs 74.7) and is better on CoLA, SST-2, MRPC and STS-B (p. 7–8, Table 5). The paper only claims the auxiliary objective helps larger datasets: NLI and QQP.
- **Unexplained MNLI mismatch.** Table 5 gives MNLI 81.8 for the full model, while Table 2 gives MNLI-m 82.1. The text does not explain the difference.
- **Layer transfer.** Transferring more pre-trained layers helps steadily, "up to 9%" for full transfer on MultiNLI (p. 7, Fig. 2 left). The figure only, no table.
- **Zero-shot heuristics** with the bare LM, no fine-tuning:
  - CoLA: thresholded average token log-probability;
  - SST-2: append "very" and compare the probabilities of "positive" and "negative";
  - RACE: pick the answer with the highest average log-probability;
  - DPRD: substitute each pronoun referent and compare.

  These improve steadily over pre-training, and the LSTM shows higher variance (p. 7, Fig. 2 right). The results appear only as a normalised plot, with no numbers in the text.

## Related in library

## Q&A
