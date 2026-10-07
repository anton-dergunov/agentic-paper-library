# Command A: An Enterprise-Ready Large Language Model

type: system
read: full
family: dense decoder-only LLM tech report (hybrid sliding-window/full attention, expert-merging post-training)
evidence: about 40 public benchmarks plus internal enterprise, safety and human-preference sets, against GPT-4o, DeepSeek V3, Llama 3.x, Mistral Large 2, Claude 3.5/3.7 Sonnet, Qwen 2.5 and others; many baseline scores are internal reproductions; strength: vendor-run, no ablations reported for architecture, merging-vs-joint training or SRPO choice, internal benchmarks unreleased
conversion: key-content-broken: Table 8 (mArenaHard win rates, p. 20–23) is printed bottom-up with column headers shredded, the es row lacks three values and the en row has two values fused per cell, so the es/en entries are unreliable (Avg row intact); Table 7 (NTREX COMET-20, p. 20–23) is reversed with headers at the bottom, the FLORES row has a merged cell that shifts the last columns, and the bold "winning cluster" marking the text relies on is lost; bold best-score marking in Tables 12, 14, 16, 19 is lost but the tables are readable; the stage list in §3.1 (p. 5–6) is out of order (cosmetic)

## Digest

- Claim: Command A (111B) is an enterprise-focused LLM for RAG, tool use/agents, 23 languages, code/SQL and safety. It is served on two A100s/H100s at up to 156 tokens/sec, stated as "1.75x higher than GPT-4o and 2.4x higher than DeepSeek V3" (p. 1). No measurement setup is given for these speeds. Weights are released for Command A and Command R7B under CC-BY-NC (p. 2).
- Architecture (p. 3): decoder-only Transformer with SwiGLU, GQA and document masking. Sliding-window and full attention are interleaved 3:1, with RoPE on the sliding-window layers and NoPE on the full layers. It uses parallel attention/FFN blocks, tied input/output embeddings and no bias terms.
- Not disclosed: layer count, window size, vocabulary size, pretraining token count, data mixture proportions and compute.
- Pretraining (p. 4–5): µP/µTransfer hyperparameter transfer; JAX/GSPMD with DP+FSDP+SP sharding on H100s; FP8 matmuls.
  - The authors see no FP8 instability, but all-FP8 training gives a "small but non-trivial" downstream degradation. They fix it with initial BF16 steps; no numbers are given.
  - Cooldown: learning rate annealed linearly from 2.5 × 10^-4 to 1 × 10^-6 over 50,000 steps. Context is 8k for 30,000 steps, then 32k/128k/256k for 10,000/5,000/5,000 steps (p. 5).
- Post-training pipeline (p. 5–6, Fig. 3):
  - An Instruct model is trained first.
  - Six SFT experts are trained from it: Code, Safety, RAG, Math, Multilingual, General Long-Context.
  - A linear-merge "SFT soup" combines them, followed by six RL/preference experts on top of that soup and a second merge.
  - A final "polishing" stage applies best-of-N SFT, then alternates offline SRPO with online CoPG RLHF ("ping-pong").
  - §3.4.3 calls the second soup an "off-pref soup" trained with offline preference optimisation, while §3.1 calls it an RL soup.
- Preference and RL methods (p. 6–7):
  - SRPO is a min-max objective that learns a self-refinement policy plus a policy whose outputs it cannot improve. It is claimed to be independent of the preference-data sampling distribution.
  - CoPG is a contrastive policy-gradient loss over k > 1 completions. It is used offline and on-policy, and is said to equal RLOO in the pure on-policy case.
  - SRPO "performs best" over SLiC/IPO/DPO for instruction following, with no numbers (p. 9). The Safety expert uses IPO plus an equally weighted SFT loss (p. 14).
- Reward model (p. 7): Bradley-Terry with soft labels, trained in two stages (about 4 million relabelled lower-quality samples, then about 350,000 high-quality ones). It scores 92.7% on RewardBench and 72.3% on RMB. No comparison model is given.
- Merging (p. 15–17):
  - Linear weight averaging with manually searched weights. SLERP and task vectors gave "no significant performance improvements".
  - All experts start from a shared instruct model, and cross-domain data is added to each expert to avoid "collisions".
  - The authors find that evaluating each candidate merge, not merging itself, is the bottleneck. The final model was informed by 500 evaluation metrics.
- Merging results (p. 34–35, Fig. 12): an average drop of 1.8% against the best expert. Most metrics stay within 2.5% of the best expert, and code is the least preserved. Large changes to expert weights shift domain scores by only 2–3%.
- A few low-learning-rate SFT steps after merging bring many metrics to at least 100% of expert level (p. 35). No numbers are given for this.
- Academic benchmarks (p. 18–19, Table 3): Command A scores MMLU 85.5, MMLU-Pro 69.6, GPQA 50.8, IFEval 90.9 and InFoBench 94.9.
  - Comparisons: GPT-4o scores 89.2/77.9/53.6/83.8/94.0 and DeepSeek V3 scores 88.5/75.9/59.1/86.1/94.3.
  - Llama 3.3 70B scores higher on IFEval (92.1).
  - Table 1 gives GPT-4o MMLU as 85.7 against 89.2 in Table 3 (p. 2 vs p. 18). Table 15 gives GPT-4o GPQA Diamond as 46.0 against 53.6 in Table 3 (p. 26). Both inconsistencies are the paper's own.
- Math (p. 26, Table 15): MATH 80.0 against GPT-4o 68.5 and Llama 3.3 70B 77.0. AIME 2024 is 23.3 against 20.0* for Llama (internal evaluation).
- Agents and RAG (p. 19–20):
  - BFCL overall is 63.8 against GPT-4o 72.1 and Qwen 2.5 72B 63.5. On BFCL multi-turn it scores 25.5 against Claude 3.7 Sonnet 48.4 (Table 5).
  - Taubench P@1 is retail 60.0 and airline 45.3, against Claude 3.5 Sonnet 69.2/46.0 and GPT-4o 60.6/43.0 (Table 6).
  - ChatRAGBench is 72.9 against GPT-4o 66.6 and DeepSeek V3 40.3 (Table 4).
  - Table 1 reports only the Taubench aggregate 51.7 and omits Claude.
- Multilingual (p. 20–23):
  - NTREX COMET-20 average is 68.8 against GPT-4o 71.0 and DeepSeek V3 69.8 (Table 7).
  - mArenaHard average win rates are 78.9 against Llama 3.3 70B, 78.7 against 405B, 65.9 against Mistral Large 2 and 53.4 against DeepSeek V3 (Table 8, Avg row).
  - Multilingual Taubench averages are retail 34.3 and airline 43.4, against GPT-4o 37.3/45.2 (Table 9).
  - The Arabic dialect score ADI2 is 24.2 monolingual and 33.5 crosslingual, against Gemini 1.5 Pro 19.3/26.4 (Table 11).
  - On language confusion Command A scores 93.0. It is tied with Qwen 2.5 72B (93.0) and below Command R+ Refresh (95.5) (Table 10).
- Code direct generation (p. 24–26, Table 12):
  - LiveCodeBench 26.9 against DeepSeek V3 33.5; BigCodeBench 45.4 against 50.0/48.6; RepoQA 92.6 against 92.2.
  - HumanEval-COBOL 25.3 against DeepSeek V3 15.2.
- Code with an execution-feedback tool ("Command A Agentic"): LiveCodeBench 32.9, BigCodeBench 59.7* and LBPP 65.4 (Table 12).
- Code editing (Table 13): SWE-Bench Verified 26.8 against DeepSeek V3 42.0/45.8. The paper says code editing was not targeted.
- Overclaim on SQL (Table 14): the text says Command A "leads in both Spider Dev, and Bird". Command A's Spider Dev is 79.5, below Qwen 2.5 72B 83.5, Llama 3.1 405B 83.0 and its own Code Expert 85.5. Bird 59.5 against 59.4 for Llama 3.1 405B does lead.
- Long context (p. 34):
  - RULER is 90.0 at 128k and 84.6 at 256k. The average up to 128k is 95.0, against Claude 3.5 Sonnet 95.4 and Gemini 1.5 Pro 94.9 (Table 21).
  - LongBench-V2 is 43.4 against GPT-4o 46.0 (Table 22).
  - KV cache at 8k is 75% of Llama 3.3 70B's, falling to 32.9% at 128k (and 10.4% of Llama 3.1 405B's at 128k).
- Safety (p. 27–31):
  - Absolute safety is 70.4, ranked third among large models after Claude 3.5 Sonnet 80.0 and Qwen 2.5 72B 71.4 (Table 16).
  - XSTest over-refusal is 1.1. On the internal over-refusal set Command A scores 7.1, tied worst among large models with GPT-4o 7.1 (Table 17). The text cites only the XSTest figure.
  - Racial-bias failures in resume summaries are 1% (Fig. 8, p. 28).
- Enterprise and human evaluation:
  - The internal generative pass rate is 94.2, against Claude 3.5 Sonnet v2 84.2 and Command R+ Refresh 87.4 (p. 32–34, Table 18).
  - RAG correctness is 4.73 against Claude 4.72 (Table 19).
  - In human pairwise evaluation (about 800 internal prompts) against GPT-4o, Command A wins 50.4 general, 51.4 reasoning and 46.8 code. Against GPT-4.5 Preview it wins 47.2/30.7/38.3 (p. 37, Table 23).
  - Polishing lifted the win rates against GPT-4o from 43.2→50.4, 41.4→51.4 and 30.0→46.8 (p. 37).
- Overclaim for Command R7B: the intro says both models are "best-in-class" for their sizes. In Table 3, R7B scores below Llama 3.1 8B and Gemma 2 9B on MMLU (65.2 vs 71.1/73.5) and GPQA (26.3 vs 23.4/31.3 — below Gemma) (p. 18).

## Related in library

- DeepSeek-V3 Technical Report: main open-weights competitor in nearly every table; Command A is behind on MMLU and GPQA and ahead on MATH and Taubench.
- The Llama 3 Herd of Models: Llama 3.1/3.3 are baselines throughout; it is cited as the classic sequential post-training paradigm that Command A's expert merging departs from, and as the model for reward-based iterative sample refinement.
- PaLM. Scaling Language Modeling with Pathways: the no-bias-terms architecture choice follows PaLM.
- Gemini 1.5. Unlocking multimodal understanding across millions of tokens of context: Gemini 1.5 Pro and Flash-8B are baselines on RULER, NTREX and multilingual Taubench.
- Mixtral of Experts: Mixtral is compared in the demographic-fairness evaluation, where it lacks robustness to race.

## Q&A
