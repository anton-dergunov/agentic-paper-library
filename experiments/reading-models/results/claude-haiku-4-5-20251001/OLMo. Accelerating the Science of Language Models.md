# OLMo: Accelerating the Science of Language Models

type: system
read: full
family: open foundation model framework with full transparency (data, training, evaluation)
evidence: downstream zero-shot on 8 tasks, Paloma perplexity benchmark (585 domains, 11 sources), adaptation evaluation on chat/safety; compared against LLaMA, Llama-2, MPT, Pythia, Falcon, RPJ-INCITE; strength: vendor-run on established benchmarks, decontaminated perplexity eval, but no ablation studies shown
conversion: ok; minor markdown artifacts (`$\sim$<!-- -->4M`) in numbers but readable

## Digest

- Decoder-only transformer, 1B and 7B variants; standard architecture: no biases, non-parametric layer norm, SwiGLU activation, RoPE positional embeddings, modified BPE tokenizer (50,280 vocab). (p. 2, Table 1)
- 1B: 16 layers, 2048 hidden dim, 2T tokens; 7B: 32 layers, 4096 hidden dim, 2.46T tokens (p. 2, Table 1).
- Dolma pretraining dataset: 2,668B tokens from 6 sources (Common Crawl 2,180B, GitHub 342B, Reddit 80B, Semantic Scholar 57B, Project Gutenberg 5.2B, Wikipedia 3.7B). Full dataset openly released with curation code and tools. (p. 3, Table 2)
- Training: AdamW optimizer, 5000-step warmup (~21B tokens) to peak LR (7B: 3.0E-4), linear decay to 1/10 peak, gradient clipping at l2-norm 1.0, FSDP sharding, mixed-precision bfloat16, global batch ~4M tokens. Trained on LUMI (AMD MI250X) and MosaicML (NVIDIA A100) clusters. (p. 4-5)
- Released 500+ intermediate checkpoints, full training logs from Weights & Biases, inference code, data curation tools (WIMBD), evaluation frameworks (Catwalk, Paloma).
- **Downstream evaluation** (8 zero-shot tasks): OLMo-7B 69.3 average, competitive with LLaMA-7B (69.6), Llama-2-7B (70.5), MPT-7B (69.8). OLMo-1B 60.4. (p. 5, Table 3)
- Individual OLMo-7B scores: arc_challenge 48.5, arc_easy 65.4, boolq 73.4, hellaswag 76.4, openbookqa 50.4, piqa 78.4, sciq 93.8, winogrande 67.9. (p. 5, Table 3)
- **Paloma perplexity benchmark**: OLMo-7B competitive on 11 sources; strong on C4 (in-distribution, 88.8% of training data from Common Crawl); weaker on curated sources (Wikipedia, S2ORC papers). First 7B model with explicit decontamination against evaluation set. (p. 6, Figure 2)
- **Instruction tuning + DPO**: OLMo+SFT MMLU 47.3, ToxiGen 14.4% toxic; OLMo+SFT+DPO MMLU 46.2, AlpacaEval 69.3%win, ToxiGen 1.7%, TruthfulQA 52.0%. Outperforms most instruction-tuned baselines; gap remains vs Tülu-2 (likely Llama-2 MMLU contamination). (p. 7, Table 4)
- All code and weights under Apache 2.0 license; full transparency goal (unlike LLaMA/Llama-2 proprietary models).
- **Not disclosed**: Systematic ablation studies for architecture/hyperparameter choices; detailed discussion of failed training runs (authors note this limitation); exact justification for non-parametric layer norm beyond speed.

## Related

- Llama-2, LLaMA: main commercial models OLMo positions as open-science alternative; uses same architectural choices (no bias, SwiGLU, RoPE, non-parametric norm)
- Pythia, BLOOM: prior open model frameworks; OLMo applies lessons from their approaches and narrows capability gap toward SOTA
- LLM360: concurrent work targeting similar goals of full transparency
- Dolma (Soldaini et al., 2024): companion dataset paper with detailed curation analyses
- Catwalk, Paloma, Open Instruct, Tülu: evaluation and adaptation frameworks OLMo integrates and builds on
