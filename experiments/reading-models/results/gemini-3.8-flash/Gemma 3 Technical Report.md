# Gemma 3 Technical Report

type: system
read: full
family: Gemma (multimodal lightweight dense decoder-only models)
evidence: standard academic benchmarks (MMLU-Pro, LiveCodeBench, GSM8K-style MATH, MMMU, etc.), Chatbot Arena human evaluations, and internal ablations against Gemma 2 and Gemini 1.5/2.0; strength: vendor-run evaluations and preliminary Chatbot Arena scores; external open models omitted from benchmark tables
conversion: ok (figure images replaced with placeholder text `[figure]`, equations lightly formatted, citations slightly clipped like `[Macknight et al. ()]`)

## Digest

- Introduces Gemma 3: lightweight multimodal models released in 1B (text-only, 32K context) and 4B, 12B, and 27B variants (multimodal, 128K context) (p. 1-2).
- Architecture switches from soft-capping (used in Gemma 2) to QK-norm with pre- and post-RMSNorm, and uses Grouped-Query Attention (GQA) with a 262k SentencePiece tokenizer inherited from Gemini 2.0 (p. 1-2).
- Replaces standard dense attention with a 5:1 interleaving pattern of local sliding-window attention (window size 1024) to global attention, starting with a local layer (p. 1-2).
- To manage 128K context, RoPE base frequency is set to 1M on global layers and left at 10k on local layers, pre-training first on 32K sequences and scaling context via positional interpolation with a scaling factor of 8 (p. 2, 7).
- Local-to-global 5:1 ratio and 1024-token sliding window drop KV-cache inference memory overhead from ~60% in global-only down to under 15% at 32k context (p. 6, Fig. 5-6).
- Multimodal capability uses a frozen 400M parameter SigLIP ViT encoder operating at 896x896 native resolution, condensed via 4x4 average pooling into a fixed budget of 256 soft tokens per image (p. 2, 8).
- Introduces inference-time Pan & Scan (P&S) adaptive windowing that segments high-resolution/non-square images into 896x896 crops; improves 27B IT performance on InfoVQA by +17.0 (59.4 to 76.4) and DocVQA by +4.8 (85.6 to 90.4) (p. 8, Table 8).
- Pre-training token budgets: 1B on 2T tokens, 4B on 4T tokens, 12B on 12T tokens, and 27B on 14T tokens across text and pre-computed image tokens (p. 2).
- Distillation recipe samples 256 logits per token weighted by teacher probabilities, setting un-sampled logits to zero probability before renormalizing (p. 2-3).
- Quantization Aware Training (QAT) is run for ~5,000 steps to export per-channel int4, per-block int4 (block size 32), and switched fp8 (SFP8); e.g., 27B bf16 footprint of 54.0 GB drops to 14.1 GB in Int4 and 27.4 GB in SFP8 (p. 3, Table 3).
- Training infrastructure spans 512 TPUv5e chips for 1B, 2048 TPUv5e chips for 4B, 6144 TPUv4 chips for 12B, and 6144 TPUv5p chips for 27B using ZeRO-3 sharding and Pathways (p. 3, Table 2).
- Post-training combines knowledge distillation from a larger instruction-tuned teacher with RL fine-tuning based on BOND, WARM, and WARP, utilizing code execution, ground-truth math verifiers, and weight-averaged reward models (p. 4).
- Formatting difference: PT models require `<eos>` output while IT models require `<end_of_turn>`; both require an explicit input `[BOS]` token (p. 4, Table 4).
- Chatbot Arena Elo (preliminary as of March 8, 2025): Gemma-3-27B-IT reaches 1338 (95% CI +8/-9), ranking 9th, outscoring DeepSeek-V3 (1318), LLaMA-3.1-405B-Instruct (1269), Qwen2.5-72B-Instruct (1257), and Gemma-2-27B-it (1220) (p. 4, Table 5).
- On MMLU-Pro (zero-shot), Gemma-3-27B-IT scores 67.5 vs Gemma-2-27B's 56.9 and Gemini-1.5-Flash's 67.3 (p. 5, Table 6).
- On MATH (zero-shot), Gemma 3 jumps across all sizes: 1B achieves 48.0 (vs Gemma 2 2B at 27.2), 4B achieves 75.6, 12B achieves 83.8, and 27B reaches 89.0 (vs Gemma 2 27B at 55.6) (p. 5, Table 6).
- On MMMU (val), multimodal Gemma 3 reaches 48.8 (4B), 59.6 (12B), and 64.9 (27B) (p. 5, Table 6).
- Teacher ablation reveals that distilling from a smaller teacher yields lower perplexity on short training horizons, but distilling from a larger teacher dominates as the training horizon lengthens (p. 7, Fig. 8).
- Training data exact composition, teacher model identities, and data mixture ratios are not disclosed (p. 2-4).
- Memorization audits show approximate memorization is roughly 24x higher than exact memorization, with total memorization rates significantly lower than Gemma 1 and Gemma 2 (p. 8, Fig. 9).

## Related

- **Gemma 2 (Gemma Team, 2024b)**: Baseline architecture; Gemma 3 replaces soft-capping with QK-norm, shifts sliding window attention from 1:1 to 5:1 local:global, and expands context from 8K to 128K.
- **Gemini 2.0 (Gemini Team)**: Provides the 262k SentencePiece tokenizer with split digits and byte-level fallbacks used across Gemma 3 models.
- **SigLIP (Zhai et al., 2023)**: Vision encoder adapted and frozen at 400M parameters to extract visual representations pooled into 256 soft tokens.
- **LLaVA (Liu et al., 2024)**: Inspires Gemma 3's Pan and Scan (P&S) dynamic cropping algorithm for handling variable aspect ratios and high resolutions.
- **WARM / WARP / BOND (Ramé et al., 2024a/b; Sessa et al., 2024)**: Post-training reinforcement learning and reward-model weight averaging framework utilized in the instruction-tuning phase.
