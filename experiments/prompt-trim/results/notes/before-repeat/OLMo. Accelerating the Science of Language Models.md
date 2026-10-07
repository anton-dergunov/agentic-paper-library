# OLMo: Accelerating the Science of Language Models

type: system
read: full
family: fully open decoder-only LLM release (weights, data, code, logs, checkpoints)
evidence: zero-shot accuracy on 8 commonsense/QA tasks against 6 open 7B models and 3 ~1B models; Paloma bits-per-byte on 11 sources against 6 7B models (figure only); Tülu chat/safety suite for SFT/DPO variants against released chat models and Tülu 2; strength: one training run per model, evaluations run by the authors, no ablation results in the main text, no variance reported
conversion: Table 1 lists the 7B hidden dimension as "4086", which looks wrong (32 heads do not divide it evenly), and its caption defines WD (weight decay) but no WD column appears (p. 1, Table 1); Table 1 gives the 1B warmup as 2000 steps while §3.2 says all sizes warm up over 5000 steps (p. 1, p. 5), likely an inconsistency in the paper itself; a footnote is fused into a Table 4 cell but stays readable (p. 7)

## Digest

- Claim: OLMo is a competitive, "truly open" LM. The release includes weights, the training data (Dolma), training, evaluation and adaptation code, training logs and 500+ intermediate checkpoints at 1000-step intervals, all under Apache 2.0 (p. 1; p. 8).
- Models: a 1B model (16 layers, D 2048, 16 heads, 2T tokens, peak LR 4.0E-4, weight tying) and a 7B model (32 layers, 32 heads, 2.46T tokens, peak LR 3.0E-4, no weight tying). Both use AdamW (betas 0.9/0.95, eps 1.0E-5) and a ~4M-token batch (p. 1, Table 1).
- The introduction says four 7B variants were released, differing in architecture, optimizer and hardware (p. 1). §5 names only 7B, 7B-twin-2T and 1B, and the main text does not describe how the variants differ (p. 8).
- Architecture: decoder-only transformer with no bias terms, non-parametric layer norm (chosen over parametric LN and RMSNorm as "safest" and fastest), SwiGLU with hidden size 11,008 for the 7B model, RoPE, and a modified GPT-NeoX BPE tokenizer with PII-masking tokens (vocabulary 50,280, embedding padded to 50,304) (p. 2).
- Training: ZeRO via PyTorch FSDP, bf16 mixed precision with full-precision sharded weights and optimizer state, 2048-token sequences. LR decays linearly to a tenth of peak; gradients are clipped at l2-norm 1.0 after warmup (pp. 4–5).
- Data: a 2T-token sample of Dolma, whose full size is 2,668B tokens, of which 2,180B are Common Crawl (p. 3, Table 2). Models trained past 2T start a second epoch with a different shuffle; the authors call this repetition negligible, citing prior work (p. 5). The batch order can be reconstructed from the released artifacts.
- Hardware: LUMI (up to 256 nodes of 4x AMD MI250X) and MosaicML (27 nodes of 8x A100-40GB). The authors claim "nearly identical performance" on both clusters by 2T tokens, but the main text shows no numbers for this (p. 5).
- The evaluated 7B checkpoint gets an extra 1000 steps with LR decayed linearly to 0. The authors say this boosts perplexity and task scores, evidenced only by Figure 1 with no numbers in the text (p. 5).
- Zero-shot average over 8 tasks: OLMo-7B 69.3 vs Llama 2 7B 70.5, Falcon-7B 70.3, MPT-7B 69.8, LLaMA 7B 69.6, RPJ-INCITE-7B 66.6, Pythia 6.9B 63.0 (p. 5, Table 3). The text calls OLMo-7B "competitive against all"; it sits below four of the six baselines on average.
- OLMo-7B ties Llama 2 7B for the best arc-challenge score (48.5) and is second on piqa (78.4 vs Falcon-7B 78.5) (p. 5, Table 3).
- OLMo-1B averages 60.4 vs TinyLlama 1.1B 59.4, Pythia 1B 54.5 and StableLM 1.6B 66.5 (p. 5, Table 3). StableLM is set aside as larger and trained on unknown data.
- Scoring uses rank classification with per-task normalization: unconditional for arc and openbookqa, per-token for hellaswag, piqa and winogrande, none for boolq and sciq. Auxiliary tasks are moved to the appendix as less stable (p. 5).
- Paloma: bits per byte over 11 of 18 sources, with OLMo's pretraining data decontaminated against Paloma. The authors claim OLMo-7B is the largest LM with such decontamination (p. 4).
- Paloma results are given only in Figure 2, with no numbers in the text. OLMo is "competitive" on the combined sources, fares well on C4 and other Common Crawl–heavy sources, and is less sample-efficient on WikiText-103, M2D2 S2ORC and M2D2 Wikipedia. MPT-7B stands out on the combined plot (p. 6).
- Non-Common Crawl share of pretraining data: MPT 27%, LLaMA 18%, RedPajama 12.2%, OLMo 11.2% (p. 6). The Figure 2 caption gives OLMo 88.8% Common Crawl.
- Adaptation follows the Tülu 2 recipe: SFT, then DPO on distilled preference data (p. 3). Base → SFT → SFT+DPO scores: MMLU 28.3 → 47.3 → 46.2; ToxiGen % toxic 81.4 → 14.4 → 1.7; TruthfulQA 31.6 → 41.2 → 52.0; AlpacaEval %win 57.0 (SFT) → 69.3 (SFT+DPO) (p. 7, Table 4).
- Against chat models, OLMo+SFT+DPO trails Llama-2-Chat on MMLU (46.8), AlpacaEval (87.3) and ToxiGen (0.0), and Tülu 2+DPO on MMLU 50.7 and AlpacaEval 85.1 (p. 7, Table 4). It beats MPT Chat, Falcon Instruct and RPJ-INCITE Chat on MMLU and AlpacaEval, though RPJ-INCITE Chat is slightly higher on TruthfulQA (53.0). The text's "outperforms most other chat variants" holds only in that sense.
- The authors attribute the gap to Tülu 2 to possible MMLU contamination in Llama 2 and to the Tülu mix being designed for Llama (p. 7).
- Not in the main text: compute or energy cost, failed or diverged runs (acknowledged in Limitations, p. 9), in-loop ablation results, and seeds or variance. The data is English-only.
- Postscript: a later improved data and training setup raised MMLU "by 24 points to 52%", cited to a blog post with no details (p. 9).

## Related in library

- LLaMA. Open and Efficient Foundation Language Models: OLMo adopts its architecture choices and its commonsense evaluation set, and compares against LLaMA 7B.
- Llama 2. Open Foundation and Fine-Tuned Chat Models: main 7B baseline for both base and chat models; Tülu 2 (built on Llama 2) is the reference for adaptation.
- PaLM. Scaling Language Modeling with Pathways: source of architecture choices OLMo follows (no biases, SwiGLU, RoPE).
- Language Models are Few-Shot Learners: OLMo uses its rank-classification zero-shot evaluation and its per-token and unconditional normalizations.
- Mixtral of Experts: cited as a weights-plus-brief-report release, a contrast to OLMo's full openness.

## Q&A
