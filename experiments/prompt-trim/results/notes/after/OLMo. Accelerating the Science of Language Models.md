# OLMo: Accelerating the Science of Language Models

type: system
read: full
family: fully open dense decoder-only LLM release (weights, data, code, logs, checkpoints)
evidence: zero-shot on 8 commonsense tasks against six 7B and three ~1B open models; Paloma bits-per-byte against 6 models (figure only); Tülu chat and safety suite against official chat variants and Tülu 2; strength: single run per model, no ablation results reported, evaluation suite chosen by the authors
conversion: Table 1 gives the 7B hidden dimension D as "4086", which looks wrong (p. 1, Table 1); the Table 1 caption defines WD (weight decay) but the table has no WD column, so those values are missing (p. 1, Table 1); otherwise ok

## Digest

- **Claim.** OLMo is a "truly open" competitive LM. Unlike most releases, which give only weights and inference code, it ships the following:
  - training data (Dolma) and the data-curation tools;
  - training, inference, adaptation and evaluation code;
  - W&B training logs;
  - 500+ intermediate checkpoints at 1000-step intervals;
  - tools to reconstruct the exact batch order.
  - All of it is under Apache 2.0 (p. 1; p. 8).
- **Models.** Four 7B variants (differing in architecture, optimizer and hardware) and one 1B model, all trained on at least 2T tokens (p. 1). Section 5 names the 7B, 7B-twin-2T and 1B weights as released (p. 8).
- **Architecture.** Decoder-only transformer with:
  - no bias terms;
  - non-parametric layer norm, with no affine gain or bias, which the authors call safest and fastest compared with parametric LN and RMSNorm;
  - SwiGLU with hidden size ≈ 8/3·d rounded up to a multiple of 128 (11,008 for 7B);
  - RoPE;
  - a modified GPT-NeoX-20B BPE tokenizer with PII-masking tokens, vocabulary 50,280, embedding matrix padded to 50,304 (p. 2).
- **Configurations** (p. 1, Table 1):
  - 1B: 16 layers, D 2048, 16 heads, 2T tokens, peak LR 4.0E-4, weight tying.
  - 7B: 32 layers, 32 heads, 2.46T tokens, peak LR 3.0E-4, no weight tying.
  - Both: batch ~4M tokens; AdamW with betas 0.9/0.95 and eps 1.0E-5.
- **Inconsistency on warmup.** Table 1 lists 2000 warmup steps for 1B, but the text says all sizes warm up over 5000 steps (~21B tokens) (p. 1, Table 1 vs p. 5).
- **Schedule.** Linear decay to a tenth of peak LR, with gradient clipping at L2-norm 1.0 (p. 5). The evaluated 7B checkpoint was trained to 2.46T tokens, then tuned a further 1000 steps with LR linearly decayed to 0. This is said to boost perplexity and end-task scores, shown only in Figure 1 (p. 5).
- **Distributed training.** ZeRO via PyTorch FSDP and bf16 mixed precision. Sharded weights, optimizer state and gradient reductions are kept in full precision. Global batch is 2048 instances × 2048 tokens (p. 4).
- **Hardware.** Trained on LUMI (up to 256 nodes of 4x AMD MI250X) and on MosaicML (27 nodes of 8x A100 40GB). The two runs are claimed "nearly identical" on the eval suite by 2T tokens, but no numbers are shown (p. 5).
- **Data.** Dolma totals 2,668B tokens and 4,367M docs, of which Common Crawl is 2,180B tokens (p. 3, Table 2). Training uses a 2T-token sample, which is one epoch. The extra tokens for 7B come from a second epoch reshuffled; the effect of this repetition is asserted negligible, citing prior work (p. 5).
- **Decontamination claim.** OLMo-7B is described as "the largest LM with explicit decontamination for perplexity evaluation": pretraining documents with paragraphs leaked from Paloma are removed (p. 4).
- **Downstream setup.** Zero-shot rank classification with normalization chosen per task (p. 5):
  - unconditional normalization for arc and openbookqa;
  - per-token normalization for hellaswag, piqa and winogrande;
  - no normalization for boolq and sciq.
- **7B zero-shot averages** (p. 5, Table 3). The text calls OLMo "competitive against all," but it sits below four of the six 7B baselines on average:

  | Model | Avg. |
  |---|---|
  | Llama 2 7B | 70.5 |
  | Falcon-7B | 70.3 |
  | MPT-7B | 69.8 |
  | LLaMA 7B | 69.6 |
  | **OLMo-7B** | **69.3** |
  | RPJ-INCITE-7B | 66.6 |
  | Pythia 6.9B | 63.0 |

- **1B zero-shot averages** (p. 5, Table 3):
  - OLMo-1B 60.4, against TinyLlama 1.1B 59.4, Pythia 1B 54.5 and StableLM 1.6B 66.5.
  - StableLM is dismissed as "significantly larger" and trained on unknown data.
- **Paloma results** (11 of 18 sources, bits per byte) appear only in Figure 2, with no numbers in the text (p. 6).
  - OLMo is called "competitive" overall, best on C4 (attributed to 88.8% Common Crawl data), and weaker on WikiText-103, M2D2 S2ORC and M2D2 Wikipedia.
  - MPT-7B stands out on the combined sources. Non-Common Crawl data shares are given as MPT 27%, LLaMA 18%, RedPajama 12.2% and OLMo 11.2% (p. 6).
- **Adaptation recipe.** Tülu 2 recipe: SFT on distilled and human instruction data, then DPO on distilled preference data (p. 3).
- **Adaptation results, OLMo base → +SFT → +SFT+DPO** (p. 7, Table 4):

  | Metric | Base | +SFT | +SFT+DPO |
  |---|---|---|---|
  | MMLU | 28.3 | 47.3 | 46.2 |
  | AlpacaEval %win | – | 57.0 | 69.3 |
  | ToxiGen % toxic (lower is better) | 81.4 | 14.4 | 1.7 |
  | TruthfulQA | 31.6 | 41.2 | 52.0 |

- **Comparison with other chat models** (p. 7, Table 4). The text says OLMo "outperforms most other chat variants." Two caveats from the table:
  - OLMo+SFT+DPO trails Llama-2-Chat on MMLU (46.8) and AlpacaEval (87.3).
  - It trails Tülu 2+DPO on MMLU (50.7) and AlpacaEval (85.1).
  - The authors attribute the gap to Llama 2 MMLU contamination and to the Tülu mix being designed for Llama.
- **Not disclosed:**
  - compute, GPU-hours or cost;
  - how the 2T sample was drawn from Dolma;
  - weight decay values (missing in this view);
  - results of the in-loop architecture ablations, which are mentioned but not reported;
  - logs of diverged or failed runs, which the Limitations section admits were omitted (p. 9).
- **Later results.** The conclusion says a later release improved MMLU "by 24 points to 52%," shown in no table (p. 9).
- **Scope.** English-only data (p. 9).

## Related in library

- 2 OLMo 2 Furious: direct successor that revises OLMo's architecture and training recipe.
- LLaMA. Open and Efficient Foundation Language Models: architecture choices (no biases, SwiGLU sizing, RoPE) follow it; LLaMA 7B is a zero-shot baseline.
- Llama 2. Open Foundation and Fine-Tuned Chat Models: Llama 2 7B and Llama-2-Chat are the main baselines; Tülu 2, built on Llama 2, is the adaptation reference.
- PaLM. Scaling Language Modeling with Pathways: cited as a source of the architecture changes (no biases, SwiGLU, RoPE).
- Language Models are Few-Shot Learners: OLMo uses its zero-shot rank-classification evaluation approach.

## Q&A
