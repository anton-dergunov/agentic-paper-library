# Improving Language Understanding by Generative Pre-Training

type: method
read: full
family: pre-trained language model, Transformer decoder, task transfer via fine-tuning
evidence: GLUE multi-task benchmark + 11 other NLU datasets (NLI, QA, similarity, classification); compared against prior SOTA on each; strength: established benchmarks, no ensemble used (unlike many baselines), ablation studies included

conversion: ok

## Digest

- **Framework**: Two-stage training—unsupervised language modeling on unlabeled text, then supervised fine-tuning on task-specific labels via task-aware input transformations (Sec. 3, p. 3–4)
- **Architecture** (Sec. 3.1, p. 3): 12-layer Transformer decoder; 768-dim hidden states; 12 attention heads; 3,072-dim feed-forward inner layers; GELU activation; 40,000 BPE vocabulary
- **Pre-training** (Sec. 4.1, p. 4): BooksCorpus dataset (7,000+ books, long contiguous text); language modeling objective on context window of k tokens; achieves 18.4 token-level perplexity; trained 100 epochs, batch size 64, seq length 512, max LR 2.5e−4 with cosine annealing; dropout 0.1, L2 regularization w=0.01
- **Fine-tuning** (Sec. 4.1, p. 4): LR 6.25e−5, batch 32, 3 epochs; auxiliary LM objective with λ=0.5 added to classification loss; adds only Wy parameters + delimiter token embeddings
- **Input transformations** (Sec. 3.3, p. 4): structured inputs (sentence pairs, QA triplets) converted to token sequences with delimiter tokens; no task-specific architecture changes
- **Ablations** (Table 5, p. 7): pre-training critical (−14.8 avg points without it); auxiliary LM helps on larger tasks; Transformer vs LSTM shows 5.6 point avg gain for Transformer; layer transfer analysis shows 9% improvement on MultiNLI with all 12 layers (Fig. 2)
- **What is disclosed**: full hyperparameters, BooksCorpus details, dataset sizes for all 12 tasks, perplexity on pre-training data
- **What is not disclosed**: no model size in parameters, no computational cost or wall-clock training time, no error analysis by task type or example, zero-shot methods described informally without quantitative thresholds

**Main results** (Tables 2–4, p. 5–6):
- GLUE multi-task: 72.8 vs. 68.9 prior SOTA (4-point absolute gain, p. 6)
- Stories Cloze: 86.5% vs. 77.6% (8.9-point gain, p. 5)
- RACE overall: 59.0% vs. 53.3% ensemble baseline (5.7-point gain, p. 5)
- MNLI-m: 82.1% vs. 80.2% ensemble (1.9-point gain, p. 5)
- SciTail: 88.3% vs. 83.3% (5-point gain, p. 5)
- CoLA: 45.4 vs. 35.0 (10.4-point gain, p. 6)
- QQP F1: 70.3 vs. 66.1 (4.2-point gain, p. 6)
- RTE: 56.0% vs. 61.7% multi-task BiLSTM (underperforms, p. 5)
- State-of-the-art on 9 of 12 datasets

## Related

- **Transformer** (Vaswani et al. [62]): underlying architecture; this work applies it as a decoder-only LM, not encoder-decoder
- **ELMo** (Peters et al. [44]): prior LSTM-based pre-trained LM for transfer; this work compares directly and shows Transformer outperforms LSTM by 5.6 avg points
- **GLUE benchmark** (Wang et al. [64]): evaluation suite; prior best was multi-task BiLSTM + ELMo at 68.9; this work achieves 72.8 on single model
- **Dai et al. [13], Howard & Ruder [21]**: prior LSTM-based pre-training for classification; limited by LSTM range compared to Transformer's long-range structure
