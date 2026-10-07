# Gemma 3 Technical Report

type: system
read: full
family: open dense decoder-only LLM family (multimodal, distilled, local/global interleaved attention)
evidence: internal zero-shot benchmarks of IT models against Gemma 2 and Gemini 1.5/2.0 (no external models in static benchmarks), preliminary LMSYS Chatbot Arena Elo, and small-scale ablations (2B text-only, short-schedule vision); strength: vendor-run, ablations mostly figure-only, no external static-benchmark baselines
conversion: ok

## Digest

- **Claim.** Gemma 3 is a family of open models at 1B, 4B, 12B and 27B. It adds three things to Gemma 2:
  - vision (except the 1B);
  - 128K context (32K for the 1B);
  - wider multilingual coverage.
- **KV-cache memory.** It is cut by interleaving 5 local sliding-window layers per global layer, with a 1024-token window (p. 1). Abstract claims: 4B-IT is "competitive with" Gemma2-27B-IT, and 27B-IT is "comparable to" Gemini-1.5-Pro.
- **Architecture.**
  - GQA, with both pre-norm and post-norm using RMSNorm.
  - QK-norm replaces Gemma 2's soft-capping.
  - RoPE base frequency is 1M on global layers and 10k on local layers.
  - The first layer is local (p. 1).
  - Parameter counts: non-embedding 698M / 3,209M / 10,759M / 25,600M; vision encoder 417M on the 4B, 12B and 27B models (p. 1, Table 1).
  - Inconsistency in the paper: Table 1 gives a "256k" vocabulary, while the tokenizer text says 262k entries (p. 1, p. 2).
- **Vision.**
  - Frozen 400M SigLIP encoder at 896×896, shared across the 4B, 12B and 27B models.
  - Images are condensed to 256 soft tokens.
  - Pan & Scan is an inference-time adaptive cropping step for non-square or high-resolution images (p. 2).
- **Pre-training.**
  - Token budgets: 14T (27B), 12T (12B), 4T (4B), 2T (1B), counting image and text tokens (p. 2).
  - Uses the Gemini 2.0 SentencePiece tokenizer and adds more monolingual and parallel multilingual data.
  - All models are trained by distillation. 256 logits are sampled per token, weighted by teacher probability; non-sampled logits get zero probability and the distribution is renormalised (p. 2).
  - The teacher model and the data mixture are not disclosed.
- **Long context.** Models are trained on 32K sequences, then the 4B, 12B and 27B are extended to 128K at the end with RoPE rescaling, using a factor of 8. The paper says perplexity "generalize[s] to 128K, but rapidly degrade[s]" beyond that, shown in a figure only (p. 7, Fig. 7).
- **Post-training.**
  - Distillation from a "large IT teacher", followed by RL based on improved BOND, WARM and WARP.
  - Rewards come from weight-averaged reward models, code execution feedback and math ground truth (p. 4).
  - Teacher, data sizes and RL hyperparameters are not disclosed.
- **QAT.**
  - About 5,000 steps to produce per-channel int4, per-block int4 and SFP8 versions.
  - 27B memory: 54.0 GB in bf16 vs 14.1 GB in int4; with a 32K KV cache, 72.7 vs 32.8 GB (p. 3, Table 3).
  - Table 3's caption says "quantized in 8 bits" even though the table includes int4 columns.
- **Chatbot Arena.**
  - Gemma-3-27B-IT scores 1338 (+8/-9), rank 9.
  - Comparisons: DeepSeek-V3 1318, Gemma-2-27B-it 1220, Gemini-1.5-Pro-002 1302 (p. 3, Table 5).
  - The scores are preliminary, as of March 8, 2025.
- **Arena text vs table.**
  - The text gives "LLaMA 3 405B (1257)", but the table lists Meta-Llama-3.1-405B-Instruct at 1269.
  - The text says "Qwen2.5-70B", but the table lists Qwen2.5-72B-Instruct (p. 4 vs p. 3, Table 5).
- **Static benchmarks, Gemma 3 27B IT vs Gemma 2 27B IT** (p. 4, Table 6):

  | Benchmark | Gemma 3 27B IT | Gemma 2 27B IT |
  |---|---|---|
  | MMLU-Pro | 67.5 | 56.9 |
  | MATH | 89.0 | 55.6 |
  | HiddenMath | 60.3 | 14.8 |
  | LiveCodeBench | 29.7 | 20.4 |
  | GPQA Diamond | 42.4 | 34.3 |

- **27B-IT vs Gemini-1.5-Pro is mixed rather than "comparable"** (p. 4, Table 6):
  - Gemma 3 27B is ahead on MATH (89.0 vs 86.5).
  - It is behind on MMLU-Pro (67.5 vs 75.8), GPQA Diamond (42.4 vs 59.1), SimpleQA (10.0 vs 24.9) and MMMU (64.9 vs 65.9).
- **4B-IT vs Gemma2-27B-IT is also mixed** (p. 4, Table 6):
  - Gemma 3 4B is better on MATH (75.6 vs 55.6), HiddenMath (43.0 vs 14.8) and FACTS Grounding (70.1 vs 62.4).
  - It is worse on MMLU-Pro (43.6 vs 56.9), Global MMLU-Lite (54.5 vs 68.6) and LiveCodeBench (12.6 vs 20.4).
- **Choice of baselines.** The authors deliberately do not compare with external models on static benchmarks, citing differing evaluation settings (p. 5).
- **Attention ablations** (2B, text-only, figures only):
  - Local:global ratio up to 7:1 has "minimal" impact on perplexity (p. 5, Fig. 3).
  - The sliding window can be reduced "significantly" without hurting perplexity (p. 6, Fig. 4).
  - With a 32K context, global-only attention adds 60% memory overhead, against "less than 15%" for 1:3 with sw=1024 (p. 6, Fig. 5). The text names 1:3 here, not the 5:1 ratio actually used.
- **Small vs large teacher.** A smaller teacher is better for short training horizons, but the trend reverses for long ones (p. 7, Fig. 8). No numbers are given in the text.
- **Vision ablations.**
  - Encoder resolution 896 vs 256 (short-schedule 2B model): DocVQA 59.8 vs 31.9, TextVQA 58.0 vs 44.1 (p. 8, Table 7).
  - Pan & Scan, 4-shot: 27B InfoVQA 76.4 vs 59.4 without P&S (+17.0); 4B DocVQA 81.0 vs 72.8 (+8.2) (p. 8, Table 8).
  - The text calls the P&S comparison "our 27B IT model", but the caption says it is a pre-trained checkpoint.
- **Memorisation.**
  - Gemma 3 memorises "much lower" than prior Gemma and Gemini models (figure only, log scale).
  - Approximate memorisation is about 24x exact memorisation on average.
  - No personal information was detected by SDP in memorised outputs (p. 8, Fig. 9).
- **Safety.**
  - Violation rates are described only as "significantly low"; no numbers are given.
  - CBRN knowledge is judged "low" on an internal MCQ set (p. 10).

## Related in library

- Gemini 1.5. Unlocking multimodal understanding across millions of tokens of context: Gemini 1.5 Flash/Pro are the main external baselines in Table 6, and 27B-IT is claimed comparable to 1.5-Pro.
- DeepSeek-V3 Technical Report: DeepSeek-V3 is the larger open MoE that Gemma 3 27B-IT out-scores in Chatbot Arena (Table 5).
- The Llama 3 Herd of Models: Llama-3.1-405B and Llama-3.3-70B are open dense baselines in the Arena comparison.

## Q&A
