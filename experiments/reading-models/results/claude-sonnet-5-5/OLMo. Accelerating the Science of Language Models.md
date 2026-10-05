# OLMo: Accelerating the Science of Language Models

type: system
read: full
family: fully open model release (1B/7B weights, data, code, checkpoints, logs) with a short technical report
evidence: 8 zero-shot commonsense/science tasks and Paloma bits-per-byte against about 6 public 7B models and 3 small models, plus a chat-tuning check on MMLU, AlpacaEval, ToxiGen and TruthfulQA; strength: authors' own pipeline, one run per model, no ablations shown, no seeds or error bars
conversion: mostly ok. Appendices (Tables 5 and 7, Appendices A, C and E) are not in the text, so references to them can't be checked. Table 1 prints 7B D as 4086, which is probably a typo for 4096; I treat it as unreliable. Table 1's caption mentions WD, but there is no WD column. Table 1 gives a 1B warmup of 2000 steps, while text p. 5 says 5000 steps for all sizes. In Table 4, the Tülu 2+DPO TruthfulQA cell is garbled ("-77", a dash plus footnote 7). The figures (1 and 2) are not readable in text, so only the captions and prose are available.

## Digest

- Mechanism: a decoder-only transformer with no biases, non-parametric layer norm, SwiGLU (hidden size about 8/3 d, rounded to a multiple of 128, 11,008 for 7B), RoPE, and a modified GPT-NeoX BPE tokenizer with PII tokens. Vocabulary is 50,280, with the embedding padded to 50,304 (p. 2). Hyperparameters were chosen for throughput and stability using in-loop evaluation every 1000 steps. The ablation results themselves are not shown (p. 2, p. 4).
- Sizes (p. 1, Table 1): 1B has L=16, D=2048, H=16, 2T tokens, peak LR 4.0E-4, weight tying. 7B has L=32, H=32, 2.46T tokens, peak LR 3.0E-4, no tying. Batch is about 4M tokens for both. AdamW with betas 0.9/0.95, epsilon 1.0E-5.
- Training recipe (p. 4–5): FSDP/ZeRO, bf16 mixed precision with full-precision softmax and gradient reduction, constant batch of 2048 × 2048 tokens. Warmup is 5000 steps (about 21B tokens), then linear decay to a tenth of peak, with gradient clipping at 1.0 (p. 5). Data order is fixed across runs and reconstructible. Some models went into a second epoch with a different shuffle, which the authors call negligible citing Muennighoff et al. (p. 5).
- Data (p. 3, Table 2): Dolma totals 2,668 billion tokens, 4,367 million docs and 11,519 GB. Common Crawl is 2,180B tokens, GitHub 342B, Reddit 80B, Semantic Scholar 57B, Gutenberg 5.2B, Wikipedia 3.7B. Training used a 2T-token sample (p. 5). Pipeline: language, quality and content filtering, dedup, mixing, tokenization. Details are deferred to the separate Dolma report.
- Hardware (p. 5): runs on LUMI (up to 256 nodes of 4× AMD MI250X) and MosaicML (27 nodes of 8× A100 40GB). The claim of "nearly identical performance on our evaluation suite by 2T tokens" gives no numbers.
- Final-checkpoint trick (p. 5): the evaluated 7B checkpoint is the 2.46T-token one. Annealing LR to 0 over the last 1000 steps on Dolma is said to boost perplexity and task scores. Evidence is only the end-of-training jump in Figure 1 (p. 5), with no ablation numbers.
- Downstream results (p. 5, Table 3): average accuracy over 8 zero-shot tasks is 69.3 for OLMo-7B, against Llama 2 7B 70.5, Falcon-7B 70.3, MPT-7B 69.8, LLaMA 7B 69.6, RPJ-INCITE-7B 66.6 and Pythia 6.9B 63.0. For 1B, OLMo is 60.4 against TinyLlama 59.4, Pythia 1B 54.5 and StableLM 1.6B 66.5. The authors call OLMo-7B "competitive", and it is not best on average. OLMo-7B beats Llama 2 on arc challenge only by tying it (48.5 vs 48.5), and trails it on boolq (73.4 vs 80.2) and arc easy (65.4 vs 69.5). Per-task normalization was chosen per dataset (p. 5).
- Disclosure gap: no compute budget, GPU-hours, loss curves or failed runs. The authors say they omitted logs of diverged or failed runs (p. 9). The intro mentions four 7B variants (different architectures, optimizers and hardware, p. 1), but the artifact list names only 7B, 7B-twin-2T and 1B (p. 8). The differences between variants are not described in this text.
- Perplexity (p. 6, Figure 2): bits per byte on 11 of Paloma's 18 sources, with OLMo's pretraining data decontaminated against Paloma. The authors claim OLMo-7B is the largest LM with explicit decontamination (p. 4). Results are described as "competitive", with MPT-7B improving fastest on the combined plot. No numeric values appear in the text.
- Where OLMo is strong or weak (p. 6): OLMo overtakes all other models on C4, attributed to 88.8% Common Crawl data. It is less sample-efficient on WikiText-103, M2D2 S2ORC and M2D2 Wikipedia. The paper gives non-Common-Crawl shares of 27% for MPT, 18% for LLaMA, 12.2% for RPJ and 11.2% for OLMo, as speculative causes (p. 6).
- Adaptation (p. 7, Table 4): Tülu mix SFT then DPO. OLMo base scores MMLU 28.3, ToxiGen 81.4% toxic and TruthfulQA 31.6. OLMo+SFT scores 47.3, 57.0 AlpacaEval, 14.4 and 41.2. OLMo+SFT+DPO scores MMLU 46.2, AlpacaEval 69.3, ToxiGen 1.7 and TruthfulQA 52.0. For comparison, Tülu 2+DPO scores 50.7, 85.1 and 0.5 on MMLU, AlpacaEval and ToxiGen, and Llama-2-Chat scores 46.8 MMLU and 87.3 AlpacaEval. DPO lowers MMLU slightly (47.3 to 46.2), which is not discussed. The authors attribute the Tülu 2 gap to possible Llama 2 MMLU contamination and Tülu being designed for Llama (p. 7).
- Post-release update (p. 9): MMLU improved "by 24 points to 52%" after unreported data and training changes (footnote link only). The report does not describe what changed, so the paper's own numbers are already superseded.
- Evidence quality: authors built and evaluated their own model with their own harness, and baselines are re-run in it. Differences of about 1 point on the average (OLMo 69.3 against LLaMA 69.6, MPT 69.8) are within what the authors call noisy evaluation (p. 9). Task choice was fixed at the start of development (p. 4). Safety and ToxiGen numbers have large swings that depend on the chat template and tuning mix.
- Limitations stated (p. 9): English only, toxic or personal data not fully removable, no failed-run logs, and the Tülu mix was designed for Llama and relies on distilled data. Evaluation tasks are not representative of chat use.
- Main contribution is openness rather than capability: weights, 500+ intermediate checkpoints at 1000-step intervals, W&B metrics, Dolma, data-order tools, training and eval code, and the adaptation code and data (p. 8). Licence is Apache 2.0 (p. 2).

## Related

- Dolma (Soldaini et al., 2024): the pretraining corpus and its curation report, where most data details live.
- Pythia (Biderman et al., 2023) and BLOOM: earlier fully open releases; OLMo compares checkpoints with Pythia-6.9B and beats it on the Table 3 average.
- LLM360 (Liu et al., 2023): contemporaneous open-everything effort with similar goals.
- LLaMA / Llama 2 (Touvron et al., 2023a; 2023b): architecture template and main capability target; Llama 2 7B stays ahead on the Table 3 average and in post-training.
- MPT-7B, Falcon-7B and RPJ-INCITE-7B: baselines in Tables 3 and 4; MPT leads on the Paloma combined plot.
- Paloma (Magnusson et al., 2023) and Catwalk (Groeneveld et al., 2023): the perplexity benchmark and evaluation framework used here.
- Tülu 2 / Open Instruct (Ivison et al., 2023; Wang et al., 2023): the post-training recipe, and the Llama-based comparison for Table 4.
- DPO (Rafailov et al., 2023): the preference-tuning step.
- Muennighoff et al. (2023): cited to justify the small amount of repeated data.
