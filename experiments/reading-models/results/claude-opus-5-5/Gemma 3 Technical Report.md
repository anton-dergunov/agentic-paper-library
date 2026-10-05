# Gemma 3 Technical Report

type: system
read: full
family: vendor technical report for an open-weights multimodal model family (1B–27B)
evidence: Chatbot Arena Elo for 27B IT against other listed models; ten zero-shot benchmarks against Gemini 1.5/2.0 and Gemma 2, all run by the authors; architecture and vision ablations on 2B or short-schedule models; strength: vendor-run, no external models in the static benchmarks, Arena result preliminary, ablations shown mostly as figures without printed numbers, post-training recipe not ablated
conversion: all figures (Fig. 1–9) are `[figure]` placeholders, so no figure values can be read (p. 1–8). Appendix and references are missing: the body ends at Section 8 (p. 11), though the text defers benchmark details to the appendix. Author footnote is garbled (p. 1) and footnote markers are inlined as "11 1" / "22 2" (p. 8). Tables 5 and 6 float ahead of the sections that cite them, so their pages are approximate. Tables themselves look intact.

## Digest

- Architecture: decoder-only transformer with GQA, pre- and post-norm RMSNorm; QK-norm replaces Gemma 2's soft-capping; 5 local sliding-window layers per global layer, starting with a local layer, against 1:1 in Gemma 2 (p. 1, p. 6).
- Long context: 128K tokens (1B: 32K); the local span is 1024 tokens; RoPE base frequency is raised from 10k to 1M on global layers and kept at 10k on local layers (p. 1).
- Long-context recipe: pre-train at 32K, then scale 4B/12B/27B to 128K at the end of pre-training with RoPE rescaling by a factor of 8; models "rapidly degrade" beyond 128K (p. 7, Fig. 7, figure not readable).
- Sizes: 1B has 0 vision encoder, 302M embedding and 698M non-embedding parameters; 27B has 417M, 1,416M and 25,600M (p. 1, Table 1).
- Vision: a frozen 400M SigLIP encoder shared by 4B/12B/27B, with 896 x 896 input condensed to 256 soft tokens (4x4 average pooling); Pan & Scan cropping is inference-only (p. 2, p. 8).
- Pre-training budget: 14T tokens for 27B, 12T for 12B, 4T for 4B, 2T for 1B, described only as "slightly larger" than Gemma 2, whose figure is not given (p. 2).
- Tokenizer: the Gemini 2.0 SentencePiece tokenizer with 262k entries (p. 2); Table 1's caption says 256k entries (p. 1), an inconsistency in the paper itself.
- Distillation: 256 logits sampled per token weighted by teacher probabilities, cross-entropy on the renormalized samples; the teacher's identity and size are not disclosed (p. 2).
- Compute: 1B used 512 TPUv5e chips, 4B used 2048 TPUv5e, 12B used 6144 TPUv4, 27B used 6144 TPUv5p; training duration is not given (p. 2, Table 2).
- QAT: about 5,000 finetuning steps with the non-quantized checkpoint's probabilities as targets; 27B weights take 54.0 GB in bf16 against 14.1 GB in Int4, and 72.7 against 32.8 GB with a 32k KV cache (p. 3, Table 3).
- Post-training: distillation from a large IT teacher plus RL finetuning based on "improved versions" of BOND, WARM and WARP, with rewards from human-feedback reward models, code execution and ground-truth math. The improvements, data, teacher and hyperparameters are not disclosed, and no ablation isolates the recipe (p. 4).
- Chatbot Arena: Gemma-3-27B-IT has Elo 1338 (95% CI +8/-9, rank 9), against 1220 for Gemma-2-27B-it, 1318 for DeepSeek-V3 and 1302 for Gemini-1.5-Pro-002; marked preliminary, received March 8, 2025 (p. 3–4, Table 5).
- The Arena text is inconsistent with its table: it gives "LLaMA 3 405B (1257)" and "Qwen2.5-70B", where Table 5 lists Llama-3.1-405B at 1269 and Qwen2.5-72B at 1257 (p. 4).
- Static benchmarks, Gemma 3 27B against Gemma 2 27B: MMLU-Pro 67.5 against 56.9, MATH 89.0 against 55.6, HiddenMath 60.3 against 14.8, LiveCodeBench 29.7 against 20.4 (p. 4, Table 6).
- "4B competitive with Gemma2-27B" is mixed in the same table: Gemma 3 4B scores 43.6 on MMLU-Pro against 56.9 and 54.5 on Global MMLU-Lite against 68.6, but 75.6 on MATH against 55.6 and 70.1 on FACTS Grounding against 62.4 (p. 4, Table 6).
- "27B comparable to Gemini-1.5-Pro" is also mixed: 67.5 against 75.8 on MMLU-Pro, 42.4 against 59.1 on GPQA Diamond, 10.0 against 24.9 on SimpleQA, 89.0 against 86.5 on MATH, 54.4 against 54.4 on Bird-SQL (p. 4, Table 6).
- External models are deliberately left out of the static benchmarks, and readers are sent to third-party leaderboards; the authors concede the probes may be contaminated despite decontamination (p. 5).
- Attention ablations (2B, text-only): "minimal impact" on perplexity up to 7-to-1 local:global and with smaller windows, with no numbers printed; KV-cache overhead is 60% for global-only against less than 15% for 1:3 with sw=1024 at 32k context (p. 5–6, Fig. 3–5).
- Teacher size: the smaller teacher is better for short training horizons and the larger one for longer training; no numbers are printed (p. 7, Fig. 8).
- Vision ablations: on a short-schedule 2B model, DocVQA is 59.8 at resolution 896 against 31.9 at 256 (p. 8, Table 7). P&S lifts 27B DocVQA from 85.6 to 90.4 and InfoVQA from 59.4 to 76.4 (p. 8, Table 8), though the caption says pre-trained checkpoint and the text says 27B IT.
- Memorization and safety: memorization is claimed "much lower" than prior models, with approximate memorization roughly 24x exact on average, but the rates sit only in the unreadable Fig. 9 (p. 8); violation rates and CBRN knowledge are reported as "low" with no numbers (p. 10).

## Related

- Gemma 2 (Gemma Team, 2024b): direct predecessor and main baseline; Gemma 3 keeps its distillation pre-training recipe and memorization methodology, and changes the 1:1 local:global ratio to 5:1 and soft-capping to QK-norm.
- Gemma 1 (Gemma Team, 2024a): source of the risk-assessment approach, and the "global only" attention baseline in the KV-cache ablations.
- Gemini 1.5 / Gemini 2.0 (Gemini Team): in-house comparison models in Table 6; Gemini 2.0 supplies the tokenizer.
- SigLIP (Zhai et al., 2023): the vision encoder, used in a 400M variant, finetuned on visual-assistant data and frozen.
- LLaVA (Liu et al., 2024): inspiration for the Pan & Scan flexible-resolution method.
- Chen et al. (2023), positional interpolation: basis for the RoPE rescaling from 32K to 128K.
- Hinton et al. (2015), knowledge distillation: used in both pre-training and post-training.
- BOND (Sessa et al., 2024), WARM (Ramé et al., 2024b), WARP (Ramé et al., 2024a): the RL finetuning phase builds on undisclosed "improved versions" of these.
- Dehghani et al. (2023), Wortsman et al. (2023), Chameleon Team (2024): motivation for QK-norm.
- Beltagy et al. (2020): local sliding-window self-attention used in the local layers.
- Chiang et al. (2024), Chatbot Arena: source of the only third-party-run evaluation, the Elo table.
- DeepSeek-V3, DeepSeek-R1, Llama 3.1 405B, Llama 3.3 70B, Qwen2.5-72B: larger open models compared on Arena Elo only.
- Mirzadeh et al. (2024): cited for the contamination risk of the pre-training probes.
- Nasr et al. (2023): the discoverable-extraction definition used for the memorization audit.
- Sachdeva et al. (2024) and Chung et al. (2023): inspiration for quality reweighing and for handling language imbalance in the data.
