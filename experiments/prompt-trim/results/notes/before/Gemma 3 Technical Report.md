# Gemma 3 Technical Report

type: system
read: full
family: open dense decoder-only multimodal LLM family trained by distillation (1B–27B)
evidence: in-house zero-shot benchmarks of the IT models against Gemma 2 and Gemini 1.5/2.0 (Table 6); a preliminary LMSYS Chatbot Arena Elo against open and closed models (Table 5); architecture ablations measured by perplexity on 2B text-only models (Figs. 3–8, figure-only); vision ablations on a short-schedule 2B model and on pre-trained checkpoints; strength: vendor-run, no static-benchmark comparison with external models, ablations reported mostly in figures and without numbers
conversion: ok

## Digest

- **Claim.** Gemma 3 is the multimodal successor to Gemma 2, in 1B, 4B, 12B and 27B sizes.
  - It adds vision, wider language coverage and at least 128K context. The 1B model has 32K context and no vision.
  - The KV cache is kept small by using mostly local attention layers.
  - The abstract says Gemma3-4B-IT is "competitive with" Gemma2-27B-IT and Gemma3-27B-IT is "comparable to" Gemini-1.5-Pro.
- **Architecture.**
  - GQA, with both pre-norm and post-norm RMSNorm.
  - QK-norm replaces Gemma 2's soft-capping.
  - 5 local sliding-window layers per global layer; the local window is 1024 tokens; the first layer is local.
  - The RoPE base frequency of the global layers rises from 10k to 1M; local layers stay at 10k (p. 1–2).
- **Long context.** Pre-training uses 32K sequences. At the end of pre-training the 4B, 12B and 27B models are scaled to 128K by RoPE rescaling, with a scaling factor of 8 (p. 7). Perplexity "rapidly degrade[s]" beyond 128K (p. 7, Fig. 7); no numbers are given.
- **Vision.**
  - The encoder is a frozen 400M SigLIP at 896×896, shared across 4B, 12B and 27B. Images become 256 soft tokens via 4x4 average pooling (p. 2, p. 8).
  - Pan & Scan is an inference-time method: it splits an image into non-overlapping equal crops.
  - Image embeddings are precomputed, so the vision part adds no training cost (p. 3).
- **Parameter counts.** Non-embedding parameters are 698M, 3,209M, 10,759M and 25,600M for 1B, 4B, 12B and 27B. The vision encoder is 417M (p. 1, Table 1).
- **Vocabulary inconsistency.** The Table 1 caption gives a vocabulary of "256k" entries, but the tokenizer text gives 262k (Gemini 2.0 SentencePiece) (p. 2). This is an inconsistency in the paper itself.
- **Pre-training.**
  - Token budgets: 14T tokens for 27B, 12T for 12B, 4T for 4B and 2T for 1B, described as slightly more than Gemma 2 (p. 2).
  - Data: more multilingual data, both monolingual and parallel.
  - Distillation: 256 logits are sampled per token, weighted by teacher probability. Non-sampled logits get zero probability and the distribution is renormalised (p. 2).
  - The teacher's identity and size are not disclosed.
  - Data composition is not quantified.
- **Post-training.**
  - Distillation from a large IT teacher, followed by RL based on improved BOND, WARM and WARP.
  - Rewards come from weight-averaged reward models, code execution and math ground truth (p. 4).
  - Called "novel", but the details are undisclosed.
- **Quantisation-aware training.** About 5,000 steps produce int4, per-block int4 and SFP8 checkpoints. For 27B, bf16 weights take 54.0 GB versus 14.1 GB for int4, or 72.7 vs 32.8 GB with the KV cache at 32,768 context (p. 3, Table 3). QAT accuracy is not reported.
- **Chatbot Arena.**
  - Gemma-3-27B-IT has Elo 1338 (rank 9), above Gemma-2-27B-it at 1220 and DeepSeek-V3 at 1318 (p. 4, Table 5). The results are preliminary, as of March 8, 2025.
  - The text gives "LLaMA 3 405B (1257)", but Table 5 lists Meta-Llama-3.1-405B-Instruct at 1269. The 1257 belongs to Llama-3.3-70B and Qwen2.5-72B; the text also calls the latter "Qwen2.5-70B".
- **Table 6: 27B IT against Gemini-1.5-Pro** (p. 4, Table 6).
  - Better or equal: MATH 89.0 vs 86.5; Bird-SQL 54.4 vs 54.4.
  - Worse: MMLU-Pro 67.5 vs 75.8; GPQA Diamond 42.4 vs 59.1; SimpleQA 10.0 vs 24.9.
  - So "comparable" overstates the result on knowledge and science benchmarks.
- **Table 6: 4B IT against Gemma 2 27B IT** (p. 4, Table 6).
  - Better: MATH 75.6 vs 55.6; HiddenMath 43.0 vs 14.8.
  - Worse: MMLU-Pro 43.6 vs 56.9; LiveCodeBench 12.6 vs 20.4; Global MMLU-Lite 54.5 vs 68.6.
  - So "competitive" holds mainly for math.
- **Comparison scope.** Section 4.2 declines to compare with external models on static benchmarks, citing differing evaluation settings (p. 5).
- **Local:global ablation.** Moving from 1:1 (Gemma 2) to 5:1, and even 7:1, has "minimal" impact on perplexity, and the sliding window "can be reduced significantly" (p. 6, Figs. 3–4). The figures carry no numbers, and the runs are 2B text-only models.
- **KV cache memory.** At 32k context, global-only attention costs 60% memory overhead, versus "less than 15%" for 1:3 with sw=1024 (p. 6, Fig. 5). The reported configuration is 1:3, not the 5:1 actually used.
- **Small versus large teacher.** A smaller teacher is better for short training horizons, but a larger teacher wins for longer ones (p. 7, Fig. 8). No numbers are given.
- **Encoder resolution.** On DocVQA, scores are 31.9 at 256, 45.4 at 448 and 59.8 at 896, using a short-schedule 2B model (p. 8, Table 7).
- **Pan & Scan gains** (p. 8, Table 8).
  - InfoVQA: +12.9 for 4B (44.1 to 57.0) and +17.0 for 27B (59.4 to 76.4).
  - TextVQA: only +1.9 for 4B and +1.6 for 27B.
  - The caption says the evaluation used a pre-trained checkpoint, 4-shot, but the text says the 27B IT model.
- **Memorisation.** Gemma 3 memorises "much lower" than prior Gemma and Gemini models (log-scale figure). Approximate memorisation is about 24x exact memorisation on average (p. 8, Fig. 9). The SDP tool found no personal information in memorised outputs.
- **Safety.** Violation rates are called "significantly low" and CBRN knowledge "low" (p. 10), with no numbers given.

## Related in library

- Gemini 1.5. Unlocking multimodal understanding across millions of tokens of context: Gemini 1.5 Flash and Pro are direct comparison baselines in Table 6.
- The Llama 3 Herd of Models: Llama 3.1 405B and Llama 3.3 70B are Arena comparisons, and the global-only attention baseline in the KV-memory ablation is attributed to Llama.
- DeepSeek-V3 Technical Report: DeepSeek-V3 is the open MoE model that Gemma 3 27B ranks above in Chatbot Arena (1338 vs 1318).

## Q&A
