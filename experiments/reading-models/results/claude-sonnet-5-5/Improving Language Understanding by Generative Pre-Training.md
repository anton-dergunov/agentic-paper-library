# Improving Language Understanding by Generative Pre-Training

type: method
read: full
family: original GPT-1 report; generative LM pre-training plus discriminative fine-tuning with a decoder-only Transformer
evidence: 12 NLU datasets (NLI, QA/commonsense, similarity, classification) against published task-specific SOTA, many of them ensembles or multi-task models; ablations on 8 tasks (Table 5); strength: authors' own runs, one model and one pre-training corpus, no variance or seeds reported, ablations not replicated
conversion: ok. Eq. 5 (combined objective L3 = L2 + λ·L1) is blank in the markdown (p. 3), but the text gives λ = 0.5. Table 2: the CAFE [58] single-model row has empty QNLI and RTE cells, and the SciTail cell reads 83.3 in a row whose other columns look shifted, so treat that row as unreliable. Table 2 prints MNLI as 82.1 / 81.4, while Table 5 prints MNLI 81.8 for the "full" model. The paper does not explain the difference. The text refers to "Figure 1" for the task overview, but that is Table 1 (p. 5). Figures 1 and 2 are images and their data is not in the text.

## Digest

- Mechanism: two stages. (1) Unsupervised pre-training with a standard LM objective, L1 = Σ log P(u_i | u_{i-k..i-1}; Θ), on contiguous text (p. 3, Eq. 1). (2) Supervised fine-tuning of all parameters with a linear softmax head on the last block's final-token activation (p. 3, Eqs. 3–4).
- Fine-tuning objective adds the LM loss as an auxiliary term with weight λ, set to 0.5 (p. 3, p. 4). The paper says it helps generalization and convergence. The only extra parameters are W_y and delimiter-token embeddings (p. 3).
- Task-specific input transformations (traversal-style) turn structured inputs into one token sequence: entailment is premise $ hypothesis; similarity uses both orderings, with the two representations added element-wise; QA and commonsense use [z; q; $; a_k] for each candidate, normalized by a softmax (p. 4, Figure 1).
- Architecture: 12-layer decoder-only Transformer, 768-d states, 12 heads, 3072-d feed-forward, GELU, learned position embeddings, BPE with 40,000 merges, dropout 0.1 (p. 4).
- Pre-training recipe: BooksCorpus, "over 7,000 unique unpublished books"; Adam with max LR 2.5e-4, 2000 warmup updates, cosine decay; 100 epochs, batches of 64 sequences of 512 tokens (p. 4). The paper reports a token-level perplexity of 18.4 on this corpus. It does not say whether that is on held-out data (p. 4).
- Fine-tuning recipe: LR 6.25e-5, batch size 32, 3 epochs "sufficient for most cases", linear decay with 0.2% warmup (p. 4). The paper does not describe how hyperparameters were chosen, what validation set was used, or how many runs were done. Total parameter count and compute are not stated in the text.
- Data rationale: BooksCorpus has long contiguous spans. The 1B Word Benchmark used by ELMo is about the same size but shuffled at sentence level, which destroys long-range structure (p. 4). There is no experiment swapping corpora, so this is asserted rather than tested.
- Headline claim: new state of the art on 9 of 12 datasets (p. 1, p. 7). Abstract and intro gains are absolute: Story Cloze +8.9%, RACE +5.7%, MultiNLI +1.5%, GLUE +5.5% (p. 1, p. 2).
- NLI (p. 5, Table 2): fine-tuned Transformer LM scores MNLI-m 82.1 / MNLI-mm 81.4, SNLI 89.9, SciTail 88.3, QNLI 88.1, RTE 56.0. Comparators include the Stochastic Answer Network 3x ensemble at 80.6 / 80.1 on MNLI, CAFE 5x at 80.2 / 79.0 on MNLI and 89.3 on SNLI, and ESIM+ELMo 5x at 89.3 on SNLI. RTE is a loss: the multi-task BiLSTM scores 61.7 against 56.0 (p. 5).
- QA and commonsense (p. 6, Table 3): Story Cloze 86.5 against 77.6 for the Hidden Coherence Model. RACE 59.0 against 53.3 for the BiAttention MRU 9x ensemble. RACE-m 62.9 and RACE-h 57.4 against 60.2 and 50.3 for the same ensemble.
- Similarity and classification (p. 6, Table 4): CoLA 45.4 against 35.0 for single-task BiLSTM+ELMo+Attn. STS-B 82.0 against 81.0 for the ECNU mixed ensemble. QQP 70.3 against 66.1 for single-task BiLSTM+ELMo+Attn. GLUE score 72.8 against 68.9 for multi-task BiLSTM+ELMo+Attn. It does not win on SST-2 (91.3 against 93.2 for sparse byte mLSTM and 91.6 for multi-task BiLSTM) or on MRPC (82.3 against 86.0 for TF-KLD).
- Comparison caveat: baselines differ in kind (single models, ensembles, multi-task, single-task) and in pre-training (some use ELMo). The paper's own SOTA claims therefore mix several comparison types. Its own results are single models.
- Layers transferred (p. 7, Figure 2 left): transferring embeddings helps and each further layer adds benefit, "up to 9% for full transfer on MultiNLI". The figure data is not in the text.
- Zero-shot heuristics (p. 7, Figure 2 right): LM scoring is used on CoLA, SST-2 (append "very", compare "positive" and "negative"), RACE (highest average token log-probability) and DPRD (Winograd). Performance rises steadily with pre-training updates. The LSTM varies more. No numbers appear in the text, and the heuristics were hand-designed.
- Ablations (p. 7–8, Table 5): the full model averages 74.7. Without pre-training it averages 59.9, which the paper describes as a "14.8% decrease". With an LSTM and the auxiliary LM it averages 69.1, which the paper describes as a 5.6 average score drop. Without the auxiliary LM it averages 75.0, higher than the full model. The auxiliary LM helps on the NLI tasks and QQP but not on the small datasets, so the paper's own ablation does not support the auxiliary loss on average (p. 7, Table 5).
- Confound in the LSTM ablation: it is a single-layer 2048-unit LSTM. The paper does not match its parameters or compute to the Transformer, so architecture and capacity are mixed (p. 7).
- Not disclosed or not tested: pre-training compute and wall-clock time; deduplication or contamination checks of BooksCorpus against the evaluation sets; variance across seeds; scaling with model or data size; model weights. No safety or limitation discussion appears.

## Related

- ELMo (Peters et al. [44]): feature-based transfer with task-specific architectures on top; GPT fine-tunes the whole model with minimal changes and compares directly (p. 2, Tables 2 and 4).
- ULMFiT (Howard and Ruder [21]) and Dai et al. [13]: the closest LM pre-train and fine-tune work, with LSTMs and text classification only; this paper claims longer-range context from Transformers and broader tasks (p. 2).
- Transformer (Vaswani et al. [62]) and the Transformer decoder LM (Liu et al. [34]): the architecture it builds on (p. 3).
- Traversal-style input approach (Rocktäschel et al. [52]): source of the input transformations (p. 4).
- GLUE baselines (Wang et al. [64]): BiLSTM+ELMo+Attn, GenSen and multi-task models serve as the comparison on GLUE tasks (p. 5, p. 6).
- Rei [50] and Collobert and Weston [10]: auxiliary LM objectives; the paper's own ablation shows mixed value (p. 2, p. 7).
- BooksCorpus (Zhu et al. [71]) and the 1B Word Benchmark: the corpus choice is contrasted with ELMo's data (p. 4).
