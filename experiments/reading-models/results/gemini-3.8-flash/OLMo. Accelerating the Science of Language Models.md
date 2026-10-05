# OLMo: Accelerating the Science of Language Models

type: system
read: full
family: open-source autoregressive language model framework
evidence: 8 zero-shot core downstream tasks, 11 Paloma perplexity benchmarks, and 4 adaptation tasks (MMLU, AlpacaEval, ToxiGen, TruthfulQA) evaluated against LLaMA, Llama 2, MPT, Falcon, Pythia, and RPJ-INCITE; strength: vendor-run with standardized harnesses (Catwalk, Paloma) and AMD/NVIDIA cluster cross-validation
conversion: ok

## Digest

- Truly open framework: releases weights, 500+ intermediate checkpoints (every 1000 steps), training code, W&B logs, the 2.67T-token Dolma dataset and curation pipeline, and evaluation/adaptation suites under Apache 2.0 (p. 1-2, 8).
- OLMo-1B configuration: 16 layers, hidden dimension 2048, 16 attention heads, weight tying enabled, peak LR 4.0E-4, 2000 warmup steps, global batch size $\sim$4M tokens, trained for 2T tokens (p. 1, Table 1).
- OLMo-7B configuration: 32 layers, hidden dimension 4086, 32 attention heads, no weight tying, peak LR 3.0E-4, 5000 warmup steps, global batch size $\sim$4M tokens, trained for 2.46T tokens (p. 1, Table 1).
- Architectural deviations: excludes all bias terms, uses non-parametric layer norm without affine transform, SwiGLU with hidden size 11,008 (closest multiple of 128 to $\frac{8}{3}d$), and RoPE (p. 2-3).
- Tokenizer: modified GPT-NeoX-20B BPE tokenizer with PII masking tokens, vocabulary size 50,280, padded to embedding matrix size 50,304 (p. 3).
- Training recipe: AdamW ($\beta_1=0.9$, $\beta_2=0.95$, $\epsilon=\text{1.0E-5}$), linear LR decay to 0.1 peak over the run, followed by a final 1000-step linear decay to 0, with gradient clipping norm 1.0 (p. 1, Table 1; p. 5).
- Distributed training: PyTorch FSDP ZeRO sharding, bfloat16 mixed precision with full-precision softmax and gradient reduction, run on AMD MI250X (LUMI, up to 256 nodes) and NVIDIA A100 (MosaicML, 27 nodes) with matched performance (p. 4-5).
- Dolma pretraining corpus composition: 11,519 GB across 4,367 million documents and 2,668 billion tokens, comprising Common Crawl (2,180B tokens), GitHub (342B), Reddit (80B), Semantic Scholar (57B), Gutenberg (5.2B), and Wikipedia (3.7B) (p. 3, Table 2).
- OLMo-7B downstream average score: 69.3 on 8 core zero-shot tasks, compared to LLaMA 7B (69.6), Llama 2 7B (70.5), Falcon-7B (70.3), MPT-7B (69.8), RPJ-INCITE-7B (66.6), and Pythia 6.9B (63.0) (p. 5, Table 3).
- OLMo-7B individual core downstream scores: arc challenge 48.5 (vs Llama 2 7B 48.5), arc easy 65.4 (vs Llama 2 7B 69.5), boolq 73.4 (vs Llama 2 7B 80.2), hellaswag 76.4 (vs Llama 2 7B 76.8), openbookqa 50.4 (vs Llama 2 7B 48.4), piqa 78.4 (vs Llama 2 7B 76.7), sciq 93.8 (vs Llama 2 7B 94.5), and winogrande 67.9 (vs Llama 2 7B 69.4) (p. 5, Table 3).
- OLMo-1B downstream average score: 60.4 on 8 core tasks, compared to Pythia 1B (54.5), TinyLlama 1.1B (59.4), and StableLM 1.6B (66.5) (p. 5, Table 3).
- Decontamination: OLMo-7B pretraining data was explicitly decontaminated against Paloma evaluation data by removing documents containing leaked paragraphs (p. 4, 6).
- Intrinsic language modeling: OLMo-7B bits per byte is competitive on 11 Paloma sources combined and overtakes all compared models on C4, reflecting its 88.8% Common Crawl composition, but lags on non-web text such as WikiText-103 and M2D2 S2ORC (p. 6, Figure 2).
- Base to adapted progression: OLMo-7B base scores 28.3 on 0-shot MMLU, 81.4% on ToxiGen, and 31.6% on TruthfulQA (p. 7, Table 4).
- Post-training (SFT and DPO): OLMo+SFT reaches 47.3 MMLU, 57.0% AlpacaEval win rate, 14.4% ToxiGen, and 41.2% TruthfulQA; OLMo+SFT+DPO reaches 46.2 MMLU, 69.3% AlpacaEval win rate, 1.7% ToxiGen, and 52.0% TruthfulQA (p. 7, Table 4).
- Adaptation comparisons: OLMo+SFT+DPO AlpacaEval win rate is 69.3%, compared to MPT Chat (46.8%), Falcon Instruct (14.0%), RPJ-INCITE Chat (38.0%), Llama-2-Chat (87.3%), and Tülu 2+DPO (85.1%) (p. 7, Table 4).
- ToxiGen reduction: OLMo+SFT+DPO achieves 1.7% toxic generation, compared to base OLMo (81.4%), Falcon Instruct (70.7%), and RPJ-INCITE Chat (46.4%), while Llama-2-Chat reports 0.0% (p. 7, Table 4).
- Subsequent update disclosed: post-release improvements to data and training increased MMLU by 24 points to 52% (p. 9).

## Related

- LLaMA / Llama 2 (Touvron et al., 2023a,b): architecture and core downstream task suite are mirrored by OLMo, but OLMo releases the full training data, training code, and intermediate checkpoints.
- Pythia (Biderman et al., 2023) and BLOOM (BigScience, 2022): open-science predecessors releasing intermediate checkpoints and data, which OLMo surpasses in downstream capability at the 7B scale.
- LLM360 (Liu et al., 2023): parallel concurrent effort for fully open-source LLMs across weights, data, and code.
- Tülu 2 (Ivison et al., 2023; Wang et al., 2023): provides the adaptation recipe (SFT mix and DPO preference alignment) applied to adapt base OLMo.
- Dolma (Soldaini et al., 2024): the companion open pretraining dataset and curation pipeline used to train all OLMo models.
- Paloma (Magnusson et al., 2023): the 585-domain perplexity benchmark against which OLMo was specifically decontaminated and evaluated.
