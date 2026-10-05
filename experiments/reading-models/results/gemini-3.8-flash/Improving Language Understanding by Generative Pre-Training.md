# Improving Language Understanding by Generative Pre-Training

type: method
read: full
family: autoregressive pretrained transformer (decoder-only) + discriminative fine-tuning
evidence: 12 downstream NLP tasks (NLI, QA, semantic similarity, classification) evaluated against existing task-specific architectures and ELMo; strength: vendor-run, comprehensive benchmark suite, includes architectural/objective ablations and zero-shot probing
conversion: formula text for Equation (5) is missing entirely (p. 4)

## Digest

- Two-stage framework: unsupervised autoregressive language modeling on unlabeled text followed by supervised discriminative fine-tuning with a task-specific linear head (p. 3).
- Architecture: 12-layer decoder-only Transformer with masked self-attention, 768-dimensional states, 12 attention heads, 3072-dimensional feed-forward inner states, GELU activations, and learned position embeddings (p. 4).
- Input traversal formatting: structures tasks (premise/hypothesis, QA tuples, sentence pairs) into contiguous linear token sequences using delimiter tokens (`$`, `<s>`, `<a>`), eliminating task-specific architectural additions (p. 3–4, Figure 1).
- Pre-training data: BooksCorpus (over 7,000 unique unpublished books) selected for contiguous long-range context; achieves token-level perplexity of 18.4 (p. 4).
- Pre-training optimization: Adam with max learning rate 2.5e-4, cosine decay, 2000 linear warmup steps, batch size 64 sequences of 512 tokens, 100 epochs, BPE vocabulary of 40,000 merges (p. 4); compute hardware and total training hours are not disclosed.
- Fine-tuning setup: 3 epochs, batch size 32, learning rate 6.25e-5 with warmup over 0.2% of training, adding an auxiliary LM objective weighted by $\lambda = 0.5$ (p. 4–5).
- Natural Language Inference results (p. 6, Table 2): achieves 82.1% on MNLI-m (vs. 80.6% for Stochastic Answer Network 3x), 81.4% on MNLI-mm (vs. 80.1% for SAN 3x), 89.9% on SNLI (vs. 89.3% for ESIM + ELMo 5x), 88.3% on SciTail (vs. 83.3% for CAFE), 88.1% on QNLI (vs. 82.3% for GenSen), and 56.0% on RTE (lagging behind 61.7% for Multi-task BiLSTM + Attn).
- Question Answering and Commonsense results (p. 6, Table 3): achieves 86.5% on Story Cloze (vs. 77.6% for Hidden Coherence Model) and 59.0% on RACE overall (vs. 53.3% for BiAttention MRU 9x).
- Semantic similarity results (p. 6, Table 4): achieves 82.0 Pearson correlation on STS-B (vs. 81.0 for ECNU mixed ensemble) and 70.3 F1 on QQP (vs. 66.1 for Single-task BiLSTM + ELMo + Attn), but reaches 82.3 F1 on MRPC (below 86.0 for TF-KLD and 83.5 for Multi-task BiLSTM + ELMo + Attn).
- Text classification results (p. 6, Table 4): achieves 45.4 Mathews correlation on CoLA (vs. 35.0 for Single-task BiLSTM + ELMo + Attn) and 91.3% accuracy on SST-2 (below 93.2% for Sparse byte mLSTM and 91.6% for Multi-task BiLSTM + ELMo + Attn).
- GLUE benchmark summary (p. 6, Table 4): achieves an overall score of 72.8 (vs. 68.9 for Multi-task BiLSTM + ELMo + Attn).
- Pre-training ablation (p. 7, Table 5): removing pre-training drops the average score across 8 tasks from 74.7 to 59.9 (a 14.8% decrease reported on p. 7).
- Architecture ablation (p. 7, Table 5): replacing the Transformer with a single-layer 2048-unit LSTM drops the average score from 74.7 to 69.1 (a 5.6 point drop, p. 7).
- Auxiliary LM ablation (p. 7, Table 5): removing the auxiliary LM objective during fine-tuning yields an average score of 75.0 (vs. 74.7 for full model), helping on large datasets (MNLI: 81.8 vs. 81.1; QNLI: 88.1 vs. 86.9) but slightly hurting on smaller ones.
- Layer transfer analysis (p. 7, Figure 2 left): each transferred transformer layer provides incremental benefit up to 9% for full transfer on MultiNLI over embedding-only transfer.
- Zero-shot analysis (p. 7, Figure 2 right): heuristic zero-shot task evaluations (e.g., token probability comparisons for SST-2, RACE, DPRD, CoLA) show steady gains over pre-training updates, showing task-relevant functionality emerges prior to fine-tuning.

## Related

- Attention Is All You Need (Vaswani et al., 2017): provides the underlying Transformer architecture, used here as a decoder-only language model.
- ELMo (Peters et al., 2018): uses bi-directional LSTM LM representations as frozen auxiliary features for task-specific architectures, whereas GPT pre-trains a Transformer and fine-tunes all parameters directly with minimal task-specific heads.
- ULMFiT (Howard & Ruder, 2018): pre-trains an LSTM language model and fine-tunes it for classification, which GPT replaces with a Transformer decoder and traversal-style inputs to support multi-sentence tasks.
- BooksCorpus (Zhu et al., 2015): source of unlabeled pre-training text chosen specifically for contiguous, long-range discourse structure over shuffled sentence corpora.
