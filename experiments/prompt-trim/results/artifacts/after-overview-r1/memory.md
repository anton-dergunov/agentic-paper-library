# Improving Language Understanding by Generative Pre-Training

type: method
read: full
family: language-model pre-training, then full fine-tuning per task
evidence: 12 NLU datasets (NLI, QA, similarity, classification, GLUE) against task-specific SOTA; ablations on 8 GLUE tasks; strength: one model size, single runs, vendor-run
conversion: Eq. 5 (the combined fine-tuning objective, L3 = L2 + λ·L1) is empty in the markdown (p. 3); Table 2 CAFE row has blank cells (p. 6)

## Digest

- GPT-1 (Radford et al., OpenAI, 2018). Two stages: pre-train a left-to-right Transformer language model on unlabelled text, then fine-tune all weights on each labelled task with one added linear layer (p. 3, §3.1–3.2).
- Model: 12-layer decoder-only Transformer, 768-d states, 12 heads, 3072-d feed-forward, GELU, learned position embeddings, BPE with 40,000 merges, 512-token context (p. 4, §4.1). The parameter count is not stated in the paper (the usual "117M" is not in the text).
- Data: BooksCorpus, over 7,000 unpublished books, chosen because it keeps long contiguous text (1B Word Benchmark is sentence-shuffled); LM perplexity 18.4 (p. 4).
- Recipe: Adam, max LR 2.5e-4, 2,000 linear warmup updates then cosine to 0, 100 epochs, batch 64 × 512 tokens, dropout 0.1, modified L2 0.01, init N(0, 0.02) (p. 4). Compute and hardware are not given.
- Fine-tuning: LR 6.25e-5, batch 32, 3 epochs, auxiliary LM loss with weight λ = 0.5 (p. 4). The only new parameters are the output layer and delimiter-token embeddings (p. 3).
- Task-specific input transformations instead of task-specific architectures: entailment = premise $ hypothesis; similarity = both orders, representations added; multiple choice = one sequence per answer, softmax over them (p. 4, §3.3, Figure 1).
- Results: state of the art on 9 of 12 datasets. Story Cloze 86.5 vs 77.6; RACE 59.0 vs 53.3 (9x ensemble) (p. 5–6, Table 3). MNLI-m 82.1 vs 80.6, SciTail 88.3 vs 83.3, QNLI 88.1 vs 82.3, RTE 56.0 vs 61.7 (a loss) (p. 5–6, Table 2). GLUE 72.8 vs 68.9; CoLA 45.4 vs 35.0 (p. 5–6, Table 4).
- Ablations (p. 7, Table 5): no pre-training drops the average from 74.7 to 59.9; an LSTM in the same framework gets 69.1; removing the auxiliary LM loss gives 75.0, slightly higher on average (it helps the larger datasets, hurts the smaller).
- Each transferred layer helps, up to 9% on MultiNLI for full transfer (p. 7, Figure 2 left).
- Zero-shot heuristics (scoring by token log-probability, restricting outputs to "positive"/"negative") improve steadily during pre-training (p. 7, Figure 2 right): the seed of GPT-2's zero-shot framing.
- Nothing on memorisation, contamination or limits beyond the RTE loss; no code or weights mentioned in the paper.

## Related in library

- Language Models are Unsupervised Multitask Learners: GPT-2, the same architecture scaled up and evaluated zero-shot with no fine-tuning
- Language Models are Few-Shot Learners: GPT-3, which replaces fine-tuning with in-context examples
- GPT-4 Technical Report: the same lineage five years later, with almost no architecture or data disclosed
- BERT. Pre-training of Deep Bidirectional Transformers for Language Understanding: the same pre-train-then-fine-tune recipe with a bidirectional masked-LM encoder, compared directly against GPT-1
- Deep contextualized word representations: ELMo, the feature-based transfer baseline (frozen biLSTM features into task-specific models) GPT-1 argues against
- Attention Is All You Need: the Transformer that GPT-1 uses in decoder-only form

## Q&A
