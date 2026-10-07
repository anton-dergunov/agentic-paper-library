# Gemma 3 Technical Report

type: system
read: full
family: open dense decoder-only multimodal LLMs (1B–27B) trained by distillation, with interleaved local/global attention
evidence: IT models on LMSYS Chatbot Arena (blind human Elo vs. open and closed models) and 10 zero-shot static benchmarks vs. Gemini 1.5, Gemini 2.0 and Gemma 2 in the vendor's own setting; architecture ablations on 2B text-only models; vision ablations on DocVQA/InfoVQA/TextVQA; strength: vendor-run, no external models on static benchmarks, most ablations shown only as figures, Arena result preliminary
conversion: ok

## Digest

- Claim: Gemma 3 adds vision input, wider language coverage and 128K context to the Gemma family at 1B/4B/12B/27B. The abstract says the post-training recipe makes Gemma3-4B-IT competitive with Gemma2-27B-IT, and Gemma3-27B-IT comparable to Gemini-1.5-Pro.
- Architecture: decoder-only with GQA, pre- and post-norm RMSNorm, and QK-norm in place of Gemma 2's soft-capping.
  - Local sliding-window and global attention layers alternate 5:1, and local layers span 1024 tokens; only the global layers see the long context, which cuts KV-cache memory.
  - RoPE base frequency is 1M on global layers and 10k on local layers.
  - Parameter counts are in (p. 1, Table 1): the 27B has 25,600M non-embedding parameters, 1,416M embedding parameters and a 417M vision encoder; the 1B has no vision encoder.
- Long context: pre-training uses 32K sequences. The 4B/12B/27B models are then scaled to 128K with RoPE rescaling by a factor of 8 (p. 7); the 1B model stays at 32K (p. 1).
  - Per the text, the models generalize to 128K but "rapidly degrade" beyond it (Fig. 7, image only).
- Vision: a frozen, shared 400M SigLIP encoder takes 896×896 input. Its output is condensed to 256 soft tokens, using 4x4 average pooling at 896 resolution.
  - Pan & Scan is an inference-only adaptive cropping step for non-square or high-resolution images.
- Pre-training data and tokenizer: 14T tokens for 27B, 12T for 12B, 4T for 4B and 2T for 1B, described as slightly more than Gemma 2 (p. 2). The tokenizer is shared with Gemini 2.0.
  - The vocabulary is stated as 262k entries (p. 2), but the Table 1 caption says 256k (p. 1). This is an inconsistency in the paper.
- Distillation: 256 logits per token are sampled, weighted by teacher probability. The student fits the renormalized teacher distribution over those samples with cross-entropy (p. 2).
  - The teacher's identity and size are not disclosed.
- Post-training: distillation from a large IT teacher, then RL based on improved BOND, WARM and WARP. Rewards come from weight-averaged reward models, code-execution feedback and math ground truth.
  - No data sizes, hyperparameters or ablation of the post-training recipe are given.
- QAT: about 5,000 steps of finetuning toward per-channel int4, per-block int4 and switched fp8 (p. 3).
  - For 27B, memory falls from 54.0 GB in bf16 to 14.1 GB in int4. With a 32K KV cache it falls from 72.7 to 32.8 GB (p. 3, Table 3).
  - No quality numbers are reported for the quantized models.
- Chatbot Arena: Gemma-3-27B-IT scores 1338 Elo, above DeepSeek-V3 at 1318 and Gemma 2 27B at 1220 (p. 4, Table 5). The result is preliminary, as of March 8, 2025.
  - The text attributes 1257 to "LLaMA 3 405B" and "Qwen2.5-70B". Table 5 lists Llama-3.1-405B at 1269, and gives 1257 to Llama-3.3-70B and Qwen2.5-72B.
- Gemma 3 27B IT vs. Gemma 2 27B IT (p. 4, Table 6):
  - MATH: 89.0 vs 55.6.
  - HiddenMath: 60.3 vs 14.8.
  - MMLU-Pro: 67.5 vs 56.9.
  - LiveCodeBench: 29.7 vs 20.4.
  - GPQA Diamond: 42.4 vs 34.3.
- Gemma 3 27B IT vs. Gemini 1.5 Pro (p. 4, Table 6). The text overstates "comparable": 27B IT trails on most rows.
  - Trails on MMLU-Pro (67.5 vs 75.8), GPQA Diamond (42.4 vs 59.1), SimpleQA (10.0 vs 24.9), LiveCodeBench (29.7 vs 34.2) and Global MMLU-Lite (75.1 vs 80.8).
  - Ties on Bird-SQL at 54.4.
  - Leads only on MATH (89.0 vs 86.5) and HiddenMath (60.3 vs 52.0).
- Gemma 3 4B IT vs. Gemma 2 27B IT (p. 4, Table 6). The "competitive" claim holds mainly for math and grounding.
  - 4B wins on MATH (75.6 vs 55.6), HiddenMath (43.0 vs 14.8) and FACTS Grounding (70.1 vs 62.4).
  - 4B loses on MMLU-Pro (43.6 vs 56.9), LiveCodeBench (12.6 vs 20.4) and Global MMLU-Lite (54.5 vs 68.6).
- Static benchmarks deliberately exclude external models, on fairness grounds (p. 5). Per-benchmark pre-trained results are only in the appendix, which this view omits.
- Local:global ablations (2B, text-only, p. 6): the ratio (up to 7:1) and the sliding-window size have "minimal" impact on perplexity. This is shown only in Figs. 3–4, with no numbers in the text.
  - KV-cache overhead at 32K context is 60% with global-only attention and under 15% with 1:3 and sw=1024 (p. 6, Fig. 5).
  - That ablation reports 1:3, not the 5:1 ratio Gemma 3 actually uses.
- Teacher size (p. 7, Fig. 8, image only): a smaller teacher is better for short training horizons and a larger one for long horizons. This is presented as contradicting the common finding.
- Vision resolution (short-schedule 2B, p. 8, Table 7): DocVQA rises from 31.9 at 256 to 59.8 at 896, and InfoVQA from 23.1 to 33.7.
- Pan & Scan (4-shot, p. 8, Table 8): for 27B, InfoVQA rises from 59.4 to 76.4 (+17.0) and DocVQA from 85.6 to 90.4 (+4.8). For 4B, DocVQA rises from 72.8 to 81.0.
  - The caption says pre-trained checkpoint, but the text says 27B IT model.
- Memorization (discoverable extraction, 50-token prefix and 50-token suffix): Gemma 3 is said to memorize "much lower" than prior Gemma/Gemini models. Approximate memorization runs roughly 24x exact memorization on average, and no personal information was found in memorized outputs (p. 8, Fig. 9).
- Safety: violation rates are called "significantly low" and CBRN knowledge "low" (p. 10). No numbers are disclosed.

## Related in library

- Gemini 1.5. Unlocking multimodal understanding across millions of tokens of context: Gemini 1.5 Flash/Pro are the main external reference in Table 6, and the basis of the "comparable to Gemini-1.5-Pro" claim.
- DeepSeek-V3 Technical Report: DeepSeek-V3 is the open-model comparator in Chatbot Arena (1318 vs Gemma 3 27B IT 1338).
- The Llama 3 Herd of Models: Llama-3.1-405B and Llama-3.3-70B are Arena comparators ranked below Gemma 3 27B IT.

## Q&A
