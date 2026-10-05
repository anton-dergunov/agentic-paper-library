# Gemma 3 Technical Report

type: method
read: full
family: autoregressive multimodal foundation models
evidence: standard multimodal and text benchmarks (MMLU, MATH, MMMU, etc.) and LMSYS Chatbot Arena against Gemini, Gemma 2, Llama 3, and other state-of-the-art models
strength: vendor-run / zero-shot evaluations / human-rated arena / ablations provided
conversion: ok

## Digest

* Gemma 3 is a family of lightweight open multimodal models (1B, 4B, 12B, 27B) featuring image understanding, extended context limits of 128K tokens, and improved multilingual capabilities (p. 1).
* Architecture: Decoder-only transformer utilizing Grouped-Query Attention (GQA), RMSNorm, and replacing soft-capping with QK-norm (p. 1).
* To prevent KV-cache memory explosions during long context generation (32K for the 1B model, 128K for the rest), the network interleaves 5 local sliding-window self-attention layers for every 1 global layer (p. 1).
* Global self-attention layers use an increased RoPE base frequency of 1M, while local layers (using a small span of 1024 tokens) retain a 10k frequency (p. 1).
* Interleaving with a 1:3 ratio and sliding windows of 1024 ("sw=1024") reduces inference memory overhead to less than 15%, compared to an overhead of 60% for a standard "global only" configuration (p. 6).
* The vision modality relies on a frozen 400M SigLIP encoder (896 x 896 fixed resolution) that condenses inputs into 256 soft image tokens (p. 2).
* To support flexible aspect ratios and high resolutions, inference utilizes a Pan and Scan (P&S) adaptive windowing algorithm that segments images into non-overlapping crops (p. 2).
* P&S improves visual text reading: on DocVQA, 27B w/ P&S achieves 90.4, a gain of (+4.8) over the 27B without P&S at 85.6 (p. 8, Table 8).
* Pre-training spans a token budget of 14T tokens for the 27B model, 12T for 12B, 4T for 4B, and 2T for 1B, using the Gemini 2.0 tokenizer with 262k entries (p. 2).
* Models are trained via knowledge distillation, sampling 256 logits per token from a teacher distribution and learning it via cross-entropy loss (p. 2).
* Post-training instruction tuning relies on knowledge distillation from a large IT teacher alongside reinforcement learning from reward models, code execution feedback, and ground-truth math rewards (p. 4).
* Disclosed: Exact parameter counts (Table 1), TPU compute infrastructure sharding (Table 2), and detailed quantization memory footprints across formats (Table 3).
* Undisclosed: Specific training data compositions, RLHF hyperparameters, and the exact sizes or identities of the teacher models.
* On Chatbot Arena, Gemma-3-27B-IT achieves an Elo of 1338 (+8/-9), significantly outperforming Gemma-2-27B-it at 1220 (+3/-2) and Meta-Llama-3.1-405B-Instruct-bf16 at 1269 (+4/-3) (p. 4, Table 5).
* On zero-shot MMLU-Pro, Gemma 3 27B achieves 67.5, improving upon Gemma 2 27B at 56.9 but trailing Gemini 1.5 Pro at 75.8 (p. 4, Table 6).
* On zero-shot MATH, Gemma 3 27B scores 89.0, massively outperforming Gemma 2 27B at 55.6 and beating Gemini 1.5 Pro at 86.5 (p. 4, Table 6).
* On zero-shot LiveCodeBench, Gemma 3 27B reaches 29.7, compared to Gemma 2 27B at 20.4 and Gemini 1.5 Pro at 34.2 (p. 4, Table 6).
* On zero-shot MMMU (val), the Gemma 3 27B model scores 64.9, closely approaching the Gemini 1.5 Pro score of 65.9 (p. 4, Table 6).

## Related

- Gemma 2: The direct predecessor model architecture built upon and surpassed in this report.
- SigLIP: The vision encoder architecture directly utilized to afford Gemma 3 its multimodality.
