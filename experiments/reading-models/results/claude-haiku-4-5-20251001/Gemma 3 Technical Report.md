# Gemma 3 Technical Report

type: system
read: full
family: Multimodal LLM report; architecture and training of a model family (1-27B parameters)
evidence: vendor-run benchmarks (MMLU, LiveCodeBench, Bird-SQL, GPQA, SimpleQA, FACTS, MATH, HiddenMath, MMMU, Chatbot Arena human Elo); strength: extensive ablations on architecture, comparisons to prior Gemma versions and Gemini models, some third-party evaluation (Chatbot Arena crowd-sourced)
conversion: ok; vocabulary size inconsistent within paper (256k in Table 1 caption, 262k in section 2.2 text)

## Digest

**Architecture:** Decoder-only transformer with two key innovations for long context: (1) 5:1 ratio of local to global attention layers with 1024-token sliding window (vs 1:1 in Gemma 2), reducing KV-cache from 60% to <15% memory overhead at 32k context; (2) QK-norm replacing soft-capping. Supports 128K context (32K for 1B), increased RoPE base from 10k to 1M on global layers. Vision added via frozen 400M SigLIP encoder (shared across 4B/12B/27B), condensed to 256 image tokens per image. Pan & Scan inference method handles variable aspect ratios without retraining. (p. 1–2)

**Model sizes:** 1B (1.0B total: 302M embedding), 4B (3.9B), 12B (11.8B), 27B (27.0B); vision encoder 417M (4B/12B/27B only). (p. 2, Table 1)

**Pre-training:** 14T tokens (27B), 12T (12B), 4T (4B), 2T (1B)—larger than Gemma 2 to account for image+text mix. Knowledge distillation with 256 sampled logits per token. Increased multilingual data and new Gemini 2.0 tokenizer (vocabulary: 256k per caption, 262k per text—inconsistency in paper). Decontamination, quality reweighting, filtering of sensitive data. Training on TPUv4/v5e/v5p with ZeRO-3 optimizer sharding. (p. 2–3, Table 2)

**Post-training:** Improved knowledge distillation from large teacher + RL (BOND/WARM/WARP variants) with multiple reward functions: weight-averaged models, code execution feedback, ground-truth math rewards. Data filtering removes unsafe content, personal info, duplicates. Distinct IT formatting with `<end_of_turn>` tokens vs PT models' `<eos>`. (p. 4, Table 4)

**Key quantitative results on instruction-tuned models:**
- **Chatbot Arena Elo** (p. 4, Table 5): Gemma-3-27B-IT 1338 (vs Gemma-2-27B-it 1220; +118); ranks 9th overall, above LLaMA-3.1-405B (1269) and Qwen2.5-72B (1257)
- **MATH** (p. 5, Table 6): Gemma-3-27B 89.0 vs Gemma-2-27B 55.6; 4B 75.6 vs prior 2B 27.2
- **HiddenMath** (p. 5): 27B 60.3 vs prior 14.8; 4B 43.0 vs prior 1.8
- **MMLU-Pro** (p. 5): 27B 67.5 vs prior 56.9; 4B 43.6 vs prior 15.6
- **Vision (Table 8, p. 8):** Pan & Scan improves DocVQA: 27B from 85.6 to 90.4 (+4.8); InfoVQA 59.4 to 76.4 (+17.0)
- **Memory** (p. 3, Table 3): 27B raw bf16 54.0 GB; int4 14.1 GB; with 32k KV-cache: 72.7 GB (raw) → 32.8 GB (int4)

**Ablations:** 5:1 vs 1:1 local:global ratio has minimal perplexity impact (Fig. 3, p. 6). Sliding window can reduce to 512 tokens with <0.2 loss; full 32k context KV-cache memory reduced from 60% overhead (global-only) to <15% (5:1 + sw=1024) (Figs. 4–6, p. 6–7). Long context: RoPE rescaling by 8× extends from 32k→128k training; perplexity stable but degrades beyond 128k (Fig. 7, p. 7). Distillation from larger teacher outperforms smaller teacher after short training (Fig. 8, p. 7). Image resolution: 896×896 SigLIP encoder outperforms 448 and 256 (Table 7, p. 8).

**Memorization (p. 8, Fig. 9):** Gemma 3 exhibits significantly lower exact memorization (<0.001% on log scale) than all prior Gemma/Gemini models. Approximate memorization (≤10% edit distance) shows ~24× relative increase vs exact. No personal information detected in memorized outputs.

**What is disclosed:** Parameter counts, training token budgets, architecture hyperparameters, quantization formats, vision encoder details, RL objectives, multiple benchmark evaluations, extensive ablations, memorization methodology.

**What is not disclosed:** Specific pre-training data sources or composition beyond "multilingual" and "images"; exact inference latency/throughput; detailed teacher model architecture; RL training hyperparameters; specific safety violation rates (only "significantly low").

## Related

- Gemma 2: direct predecessor, replaced soft-capping with QK-norm, changed attention ratio from 1:1 to 5:1; large performance gains in math (+34 points MATH), instruction-following, and competitive with 70B+ models at 27B.
- Gemini 1.5/2.0: uses same tokenizer (Gemini 2.0), inspired by architecture choices; Gemma-3-27B Elo 1338 comparable to claimed Gemini-2.0-Flash (1357).
- LLaVA: Pan & Scan method adapted for handling variable-resolution images.
- SigLIP, CLIP: vision encoders; Gemma uses frozen 400M SigLIP.
