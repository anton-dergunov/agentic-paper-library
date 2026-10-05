# OLMo: Accelerating the Science of Language Models

type: system
read: full
family: open-weights LM release report (weights, data, code, checkpoints, logs)
evidence: zero-shot rank-classification on 8 commonsense/QA tasks against six public 7B and three ~1B models; Paloma bits per byte on 11 sources against 6 models; Tülu chat/safety suite against five chat models and Tülu 2; strength: author-run on their own pipeline, one checkpoint per model, no seeds or variance, ablations mentioned but none shown, perplexity results only in a figure, and the authors themselves call the evaluations "very noisy"
conversion: main text and Tables 2–4 are readable, with these defects:
- Title is duplicated and the author/affiliation block is scrambled (p. 1).
- Table 1 (p. 1) prints D = 4086 for 7B, which looks wrong, and its caption defines WD but the table has no weight-decay column.
- Figures 1 and 2 are missing (pp. 5–6), so no Paloma numbers are available.
- Footnote markers are fused into the text ("License.11 1", "52%.99 9") and into a Table 4 cell ("-77 7", p. 7).
- The body stops after Acknowledgments: Appendices A, C and E, Tables 5 and 7, Figure 4 and the references are absent.

## Digest

- Claim: a "truly open" LM, releasing weights, training and evaluation code, the full training data (Dolma), logs and adaptation code under Apache 2.0; most prior releases gave only weights and inference code (p. 1).
- Released: the 7B model, 7B-twin-2T and the 1B model, each with 500+ intermediate checkpoints at 1000-step intervals, plus the complete Weights & Biases metrics (p. 8). The introduction instead says "four variants" at 7B and one at 1B (p. 1).
- Architecture: decoder-only transformer with no bias terms, non-parametric layer norm (chosen over parametric layer norm and RMSNorm as "safest" and fastest), SwiGLU and RoPE (p. 2).
- SwiGLU hidden size is about 8/3 d, rounded up to a multiple of 128, giving 11,008 for 7B (p. 2).
- Tokenizer: modified GPT-NeoX-20B BPE with added PII-masking tokens; vocabulary 50,280, embedding matrix padded to 50,304 (p. 2).
- Sizes: 1B has L 16, D 2048, H 16, 2T tokens, peak LR 4.0E-4 and weight tying; 7B has L 32, D printed as 4086 (unreliable), H 32, 2.46T tokens, peak LR 3.0E-4 and no tying (p. 1, Table 1).
- Optimizer: AdamW with betas 0.9 and 0.95 and epsilon 1.0E-5 (p. 1, Table 1); linear decay to a tenth of peak LR; gradients clipped to global l2-norm 1.0 after warmup (p. 5).
- Internal inconsistency: Table 1 gives 2000 warmup steps for 1B and 5000 for 7B (p. 1), while the text says 5000 steps (~21B tokens) "for all model sizes" (p. 5).
- Batch: about 4M tokens (2048 instances × 2048 tokens), with a micro-batch of 4096 tokens per GPU at 7B; FSDP/ZeRO sharding and bfloat16 mixed precision with full-precision shards and gradient reduction (p. 4).
- Data: Dolma totals 2,668 billion tokens over 4,367 million docs; Common Crawl is 2,180 billion, GitHub 342, Reddit 80, Semantic Scholar 57, Gutenberg 5.2 and Wikipedia 3.7 (p. 3, Table 2).
- Training used a 2T-token sample of Dolma with documents concatenated with EOS, chunked at 2048 and shuffled identically across runs; data order is reconstructible, and some runs begin a second epoch (p. 5).
- Dolma's pipeline is listed (language, quality and content filters, deduplication, mixing, tokenization), but the details are deferred to the Dolma report (p. 3).
- Hardware: LUMI with up to 256 nodes of 4x AMD MI250X, and MosaicML with 27 nodes of 8x NVIDIA A100 40GB; the two runs are reported as "nearly identical" by 2T tokens, with no numbers given (p. 5).
- Not disclosed: wall-clock time, GPU-hours and cost; the weight-decay value is missing from this text, and failed or diverged runs are omitted by the authors' own admission (p. 9).
- Late recipe change: 1000 extra steps with LR decayed linearly to 0 improve perplexity and end-task scores; the evidence is Figure 1, which is missing here (p. 5).
- Zero-shot 8-task average: OLMo-7B scores 69.3, against Llama 2 7B 70.5, Falcon-7B 70.3, MPT-7B 69.8, LLaMA 7B 69.6, RPJ-INCITE-7B 66.6 and Pythia 6.9B 63.0, so the claim is "competitive", not best (p. 5, Table 3).
- Zero-shot 8-task average: OLMo-1B scores 60.4, against TinyLlama 1.1B 59.4, Pythia 1B 54.5 and StableLM 1.6B 66.5 (p. 5, Table 3). Likelihood normalization was chosen per dataset (p. 5).
- Paloma: bits per byte on 11 of 18 sources, with OLMo's pretraining data decontaminated against Paloma and the other models' not. OLMo-7B leads on C4 and is less sample-efficient on WikiText-103, M2D2 S2ORC and M2D2 Wikipedia. Non-Common Crawl share is 11.2% for OLMo, against 27% for MPT, 18% for LLaMA and 12.2% for RedPajama (p. 6).
- Adaptation (Tülu SFT, then DPO): MMLU 0-shot goes from 28.3 for OLMo base to 47.3 with SFT and 46.2 with SFT+DPO, against Tülu 2+DPO 50.7 and Llama-2-Chat 46.8 (p. 7, Table 4).
- For OLMo+SFT+DPO, AlpacaEval is 69.3 %win against Tülu 2+DPO 85.1 and Llama-2-Chat 87.3, and ToxiGen is 1.7 % toxic against OLMo base 81.4 (p. 7, Table 4). The authors attribute the gap to Tülu 2 to Llama 2's MMLU contamination and a mix tuned for Llama (p. 7).

## Related

- Llama 2 / LLaMA (Touvron et al., 2023a,b): source of the architecture choices and the 8-task evaluation set, and the main baseline; Llama 2 7B edges OLMo-7B on the average (70.5 against 69.3).
- Dolma (Soldaini et al., 2024): the pretraining corpus; curation details and data ablations live there, not in this paper.
- Pythia (Biderman et al., 2023) and BLOOM (BigScience et al., 2022): cited as the most open prior releases; Pythia-6.9B is a checkpoint-level baseline, which OLMo beats on downstream average.
- LLM360 (Liu et al., 2023): a parallel fully open effort; OLMo claims to narrow the gap from those models to Llama 2.
- MPT-7B (MosaicML NLP Team, 2023): baseline that improves ahead of the others on combined Paloma, attributed to its data mix and semantic deduplication; OLMo's code base derives from MosaicML's.
- Falcon-7B (Almazrouei et al., 2023) and RPJ-INCITE-7B (Together Computer, 2023): size-matched baselines; RPJ-INCITE also releases checkpoints for training-curve comparison.
- Paloma (Magnusson et al., 2023): the perplexity benchmark and the decontamination procedure used.
- Catwalk (Groeneveld et al., 2023): the authors' own evaluation framework, through which all models were scored.
- Tülu 2 / Open Instruct (Ivison et al., 2023; Wang et al., 2023): the SFT+DPO recipe and evaluation suite, reused unchanged; Tülu 2 on Llama 2 remains ahead of adapted OLMo.
- PaLM (Chowdhery et al., 2022) and OpenLM (Gururangan et al., 2023): architecture precedents for no biases, SwiGLU and RoPE.
