# OLMo: Accelerating the Science of Language Models

type: system
read: full
family: fully open dense decoder-only LLM release (weights, data, code, logs, checkpoints)
evidence: zero-shot on 8 commonsense/QA tasks against 1B- and 7B-scale open models; Paloma bits-per-byte (figure only) against 6 7B models; Tülu chat/safety suite against instruction-tuned 7B models; strength: authors' own evaluation pipeline, single runs, in-loop design ablations described but no results reported
conversion: Table 1 (p. 1) gives the 7B hidden dimension as 4086, which looks wrong; its caption defines a WD (weight decay) column that the table does not have. The icon markers before OLMo rows in Tables 3–4 are lost as "\[\]", and a footnote is fused into a Table 4 cell. These are incidental.

## Digest

- **Claim.** OLMo is a competitive, "truly open" LM. The release includes:
  - 1B and 7B weights (the 7B in four variants by architecture, optimizer and hardware);
  - 500+ intermediate checkpoints at 1000-step intervals;
  - the full pretraining data (Dolma) and the tools to rebuild the exact data order;
  - training, evaluation and adaptation code, and W&B training logs;
  - all under Apache 2.0 (p. 1; p. 8).
- **Openness positioning.** The authors place OLMo against releases with partial openness: Mixtral (weights and a brief report), LLaMA, MPT (data distribution but not the data), Falcon (data partly released), and Pythia/BLOOM (most open). LLM360 is named as having similar goals (p. 1).
- **Architecture.** Decoder-only transformer with:
  - no bias terms;
  - non-parametric layer norm (no affine gain or bias), chosen as safest and fastest over parametric LN and RMSNorm;
  - SwiGLU with hidden size ≈8/3·d rounded up to a multiple of 128 (11,008 for 7B);
  - RoPE;
  - a modified GPT-NeoX-20B BPE tokenizer with PII-mask tokens: vocabulary 50,280, embedding padded to 50,304 (p. 2).
- **Model sizes.** 1B: 16 layers, D 2048, 16 heads, 2T tokens, peak LR 4.0E-4, 2000-step warmup, tied weights. 7B: 32 layers, D "4086", 32 heads, 2.46T tokens, peak LR 3.0E-4, 5000-step warmup, untied. Both use a batch of ~4M tokens and AdamW with betas 0.9/0.95 and eps 1.0E-5 (p. 1, Table 1).
- **Warmup inconsistency.** The text says "for all model sizes" warmup is 5000 steps (~21B tokens) (p. 5), which contradicts the 2000 steps in Table 1 for 1B. The weight decay value is not given in the main text.
- **Schedule and clipping.** Linear LR decay to one tenth of peak, and gradient clipping at global ℓ2-norm 1.0 after warmup (p. 5). The evaluated 7B checkpoint gets 1000 more steps with LR decayed linearly to 0, which the authors say improves perplexity and end-task scores (p. 5; Fig. 1).
- **Dolma data.** 2,668B tokens in total, of which Common Crawl is 2,180B; also GitHub 342, Reddit 80, Semantic Scholar 57, Gutenberg 5.2 and Wikipedia 3.7 (GPT-NeoX token counts) (p. 3, Table 2).
- **Training data use.**
  - Training uses a 2T-token sample: documents joined with EOS and chunked into 2048-token instances.
  - The shuffle order is fixed across runs.
  - Training beyond 2T tokens starts a second epoch with a different shuffle, said to be negligible per prior work (p. 5).
- **Infrastructure.** ZeRO through PyTorch FSDP, bf16 mixed precision with fp32 sharded weights, optimizer state and gradient reduction (pp. 4–5).
- **Hardware.** Two clusters: LUMI (up to 256 nodes of 4× AMD MI250X) and MosaicML (27 nodes of 8× A100 40GB). The runs are said to reach "nearly identical performance" by 2T tokens, but no numbers are shown (p. 5).
- **Not disclosed in the main text:**
  - total compute or GPU-hours;
  - in-loop ablation results;
  - failed or diverged runs (acknowledged in Limitations, p. 9);
  - separate results for the four 7B variants.
- **Zero-shot evaluation, 7B (p. 5, Table 3).**
  - Method: rank classification, with normalization chosen per task (p. 5).
  - OLMo-7B averages 69.3.
  - Comparisons: Llama 2 7B 70.5, Falcon-7B 70.3, MPT-7B 69.8, LLaMA 7B 69.6, RPJ-INCITE-7B 66.6, Pythia 6.9B 63.0.
  - "Competitive" in the text means fifth of the seven 7B models on average.
  - OLMo-7B ties for best arc-challenge (48.5, equal to Llama 2) and is close to best on piqa (78.4 vs Falcon 78.5).
- **Zero-shot evaluation, 1B (p. 5, Table 3).**
  - OLMo-1B averages 60.4, against TinyLlama 1.1B 59.4 and Pythia 1B 54.5.
  - StableLM 1.6B averages 66.5. The text sets it aside as "significantly larger" and trained on unknown data.
- **Training curves.** Accuracy rises with tokens on all core tasks except OBQA (p. 5, Fig. 1).
- **Paloma perplexity (p. 6, Fig. 2).**
  - Results are in a figure only; no numbers are in the text.
  - OLMo-7B is described as "competitive" despite being decontaminated against Paloma. It is called the largest LM with explicit perplexity decontamination (p. 4).
  - It is best on C4, attributed to 88.8% Common Crawl in its data.
  - It is weaker on WikiText-103, M2D2 S2ORC/Wikipedia and RedPajama.
  - MPT-7B improves fastest; the paper suggests this is because MPT's data is 27% non-Common Crawl, against 18% for LLaMA, 12.2% for RedPajama and 11.2% for OLMo.
- **Adaptation: method.** Tülu SFT followed by DPO (p. 3).
- **Adaptation: results (p. 7, Table 4).** For OLMo base → +SFT → +SFT+DPO:
  - MMLU: 28.3 → 47.3 → 46.2
  - AlpacaEval %win: – → 57.0 → 69.3
  - ToxiGen %toxic: 81.4 → 14.4 → 1.7
  - TruthfulQA: 31.6 → 41.2 → 52.0
- **Adaptation: comparisons and overclaim (p. 7, Table 4).**
  - Tülu 2+DPO (on Llama 2) scores 50.7 MMLU and 85.1 AlpacaEval; Llama-2-Chat scores 46.8 and 87.3.
  - The text says OLMo "outperforms most other chat variants". It beats MPT Chat, Falcon Instruct and RPJ-INCITE Chat on most metrics, but trails Llama-2-Chat on AlpacaEval and slightly on MMLU.
  - DPO slightly lowers MMLU relative to SFT.
  - The authors attribute the gap to Tülu 2 partly to MMLU contamination in Llama 2 and to a Tülu mix designed for Llama.
- **Later improvement.** Since this release, a later improvement raised MMLU "by 24 points to 52%" (p. 9).
- **Limitations.** English only. Evaluation is noisy and the downstream tasks do not reflect chatbot use (p. 9).

## Related in library

- 2 OLMo 2 Furious: successor release from the same project, building on this framework and recipe
- LLaMA. Open and Efficient Foundation Language Models: architecture choices followed (SwiGLU sizing, RoPE, no biases); LLaMA 7B is a zero-shot baseline, and its commonsense task set is mirrored
- Llama 2. Open Foundation and Fine-Tuned Chat Models: main 7B comparison point; Llama-2-Chat and Llama-2-based Tülu 2 are adaptation baselines
- PaLM. Scaling Language Modeling with Pathways: source of the architecture changes adopted (no biases, SwiGLU, RoPE)
- Language Models are Few-Shot Learners: zero-shot rank-classification evaluation and per-token/unconditional normalization taken from it
- Mixtral of Experts: cited as an example of a weights-plus-brief-report release, in contrast to OLMo's full openness

## Q&A
