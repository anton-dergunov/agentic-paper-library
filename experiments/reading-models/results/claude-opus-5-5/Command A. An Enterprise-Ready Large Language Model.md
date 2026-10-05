# Command A: An Enterprise-Ready Large Language Model

type: system
read: full
family: vendor technical report for an open-weights (non-commercial) enterprise LLM; post-training by parallel expert tracks plus weight merging
evidence: public academic, agentic, code, multilingual, long-context and safety benchmarks plus internal enterprise sets and blind human pairwise evaluation, against GPT-4o, DeepSeek V3, Llama 3.3 70B / 3.1 405B, Mistral Large 2, Claude 3.5/3.7 Sonnet, Gemini and Qwen 2.5; strength: vendor-run, mix of externally reported and internal reproductions of competitor scores, many internal benchmarks and LLM judges, merging and polishing ablations only as figures or prose, no confidence intervals
conversion: body ends at the Conclusion, with no references and no appendices, so Appendix B.2–B.7, Tables 26–27 and Figures 15–16 are cited but absent. All figures are missing (1, 5, 7, 8, 10, 12, 13, 14). Table 7 (NTREX, in §4.3, p. 20) is rotated with the header at the bottom, and its FLORES row has a merged cell ("76.3 72.6") that shifts columns. Table 8 (p. 20) is rotated, with the es and en rows merged and es mostly blank. Bold "winning cluster" and best-score markings are lost in all tables. Table 13 (p. 24) has a duplicated empty Aider Polyglot column. The §3.1 stage list (p. 5) is out of order. The SRPO equation (p. 6) writes π_+ where the text writes π†. Exponents are flattened ("2.5 × 10 -4", p. 5).

## Digest

- Command A is a 111B-parameter decoder-only model covering 23 languages, and Command R7B is a smaller sibling; weights are released under CC-BY-NC with an acceptable-use addendum (p. 1–2).
- Efficiency claims are a serving footprint of "two A100s or H100s" and up to 156 tokens/sec, stated as 1.75x GPT-4o and 2.4x DeepSeek V3; no measurement setup is given (p. 1).
- Architecture: SwiGLU, GQA, sliding-window and full attention interleaved 3:1 (RoPE on window layers, NoPE on full layers), parallel transformer block, tied input/output embeddings, no bias terms (p. 3).
- Not disclosed: layer count, widths, vocabulary size, window size, pre-training token count, data mixture proportions, compute, merge weights, and nearly all Command R7B specifics; component ablations are asserted without numbers (p. 3).
- Pre-training data is web text and code, internal synthetic data, annotator instruction data and vendor data, with the mixture chosen by ablations on smaller models; hyperparameters are tuned with µP/µTransfer (p. 3–4).
- Training runs on H100s in a JAX framework with FP8 matmuls over FP32 master weights; full-FP8 training gives a "small but non-trivial" downstream degradation, mitigated by BF16 steps and not quantified (p. 4).
- Cooldown anneals the learning rate linearly from 2.5 × 10⁻⁴ to 1 × 10⁻⁶ over 50,000 BF16 steps; context is 8k for the first 30,000 steps, then 32k, 128k and 256k for 10,000, 5,000 and 5,000 steps (p. 5).
- Post-training pipeline: Instruct model → six SFT experts (Code, Safety, RAG, Math, Multilingual, General Long-Context) → linear-merge "SFT Soup" → six RL experts → "RL Soup" → polishing (best-of-N SFT, then offline SRPO and online CoPG alternated); claimed as the first large-scale use of parallel expert tracks with merging (p. 5–6).
- Methods are SRPO, a min-max preference objective that also learns a self-refinement policy, and CoPG for KL-regularised reward optimisation; SRPO was picked over SLiC, IPO and DPO for the Instruct model with no numbers shown (p. 6–9).
- The Bradley-Terry reward model is trained on approximately 4 million "lower quality" samples and then approximately 350,000 high-quality ones; it scores 92.7% on RewardBench and 72.3% average on RMB, with no baseline given (p. 7).
- Merging uses linear weights found by manual search, informed by 500 evaluation metrics; SLERP and task vectors gave "no significant performance improvements" (p. 16).
- Merging costs a 1.8% average drop versus the best expert, with most metrics within 2.5% and code the least preserved; this evidence is in the missing Figure 12 (p. 34).
- Headline academics, Command A vs GPT-4o / DeepSeek V3 / Llama 3.3 70B: MMLU 85.5 vs 89.2 / 88.5 / 86.0, GPQA 50.8 vs 53.6 / 59.1 / 50.5, IFEval 90.9 vs 83.8 / 86.1 / 92.1 (p. 18, Table 3). It trails the closed models on MMLU and GPQA despite the "best-in-class" framing.
- The paper's tables disagree on GPT-4o: MMLU is 85.7 in Table 1 but 89.2 in Table 3, and GPQA is 53.6 in Table 3 but 46.0 in Table 15 (p. 2, p. 18, p. 26).
- MATH: 80.0 vs GPT-4o 68.5 and Llama 3.3 70B 77.0; AIME 2024: 23.3 vs 9.3 and 20.0 (the latter internally evaluated) (p. 26, Table 15).
- Agents: Taubench P@1 is 60.0 retail / 45.3 airline vs GPT-4o 60.6 / 43.0 and Claude 3.5 Sonnet 69.2 / 46.0 (p. 19, Table 6). BFCL overall is 63.8 vs GPT-4o 72.1, and multi-turn is 25.5 vs 47.6 (p. 19, Table 5). How Table 1's Taubench 51.7 is aggregated is not explained (p. 2).
- Code: SWE-Bench Verified 26.8 vs DeepSeek V3 42.0 / 45.8 and Llama 3.3 70B 29.4; LiveCodeBench 26.9 vs DeepSeek V3 33.5; the authors say code editing was not a training target (p. 24, Tables 12–13). The text says Command A "leads" Spider Dev, but Table 14 gives 79.5 vs Qwen 2.5 72B 83.5; only Command A Expert, at 85.5, leads (p. 24).
- Long context: RULER at 128k is 90.0 vs Claude 3.5 Sonnet 93.8 and Mistral Large 2 48.1, and at 256k is 84.6 vs Gemini-1.5-Pro 91.6 (p. 34, Table 21). KV cache is 75% of Llama 3.3 70B's at 8k and 32.9% at 128k (p. 34).
- Safety: default absolute safety is 70.4 vs Claude 3.5 Sonnet 80.0 and Qwen 2.5 72B 71.4, LLM-judged on internal prompts (p. 29, Table 16). The LLM jury for relative safety has 77.7% human agreement and Cohen's Kappa 0.55 (p. 27). XSTest over-refusal is 1.1 vs GPT-4o 5.6 (p. 29, Table 17).
- Human evaluation uses about 800 internal prompts and on average 65 annotators; win rates on general / reasoning / code are 50.4 / 51.4 / 46.8 vs GPT-4o and 47.2 / 30.7 / 38.3 vs GPT-4.5 Preview (p. 37, Table 23). Polishing moved the win rate vs GPT-4o from 43.2 → 50.4, 41.4 → 51.4 and 30.0 → 46.8 against the pre-polish merge (p. 37).

## Related

- Llama 3 (Dubey et al., 2024): cited as the classic single-model sequential post-training paradigm this report departs from; its reward-based sample refinement is reused; Llama 3.3 70B and 3.1 405B are main baselines.
- Gemma (Team et al., 2024): cited as the sequential post-training paradigm and for seed merging; Gemma 2 9B is a small-model baseline.
- SRPO (Choi et al., 2025): Cohere's own preference-optimisation method, used for the Instruct model and for polishing.
- Contrastive Policy Gradient (Flet-Berliac et al., 2024): the loss used for all offline and online reward optimisation.
- DPO / IPO / SLiC (Rafailov et al., 2024; Azar et al., 2024; Zhao et al., 2023): preference-tuning baselines; IPO is kept for the Safety expert.
- Yang et al. (2025): source for details of the interleaved sliding-window/full-attention design, which this report defers to.
- Model soups and weight averaging (Wortsman et al., 2022; Izmailov et al., 2018): basis for linear expert and seed merging.
- WARP (Ramé et al., 2024): interpolation back to the parent checkpoint, for RL stability and capability recovery.
- Task vectors (Ilharco et al., 2023): a more complex merging method tried and found no better than linear merging.
- PaLM (Chowdhery et al., 2023): precedent for removing bias terms.
- µP / µTransfer (Yang et al., 2021): hyperparameter transfer from small to large models.
- Command R+ Refresh / Command R Refresh: predecessors; internal baselines and generator of synthetic long-context data.
- GPT-4o, DeepSeek V3, Claude 3.5/3.7 Sonnet, Mistral Large 2, Qwen 2.5, Gemini 1.5/2.0: comparison models, with scores partly externally reported and partly reproduced internally.
- τ-bench (Yao et al., 2024) and BFCL (Yan et al., 2024): agentic benchmarks; τ-bench is also human-translated by the authors into a multilingual version.
- Verga et al. (2024): LLM-jury evaluation procedure used for RAG correctness, relative safety and enterprise checks.
- Seshadri & Goldfarb-Tarrant (2025): method and metric for the resume-summarisation fairness test.
