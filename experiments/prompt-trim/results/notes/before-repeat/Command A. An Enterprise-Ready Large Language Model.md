# Command A: An Enterprise-Ready Large Language Model

type: system
read: full
family: dense decoder-only LLM technical report; expert-merging post-training
evidence: academic, agentic, code/SQL, multilingual, safety and long-context benchmarks plus internal enterprise suites and internal human pairwise evaluation, against GPT-4o, DeepSeek V3, Llama 3.x, Mistral Large 2, Claude 3.5/3.7 Sonnet, Qwen 2.5, Gemini and small 7–9B models; strength: vendor-run, many internal benchmarks, a mix of externally reported and internally reproduced baselines, design choices stated without ablation numbers, no confidence intervals
conversion: key-content-broken: in Table 8 (p. 20–23) the es and en rows are merged, with es missing three values and en holding two values per cell, and the header is flattened below the rows; in Table 7 (p. 20–23) the header is flattened below the rows, the FLORES row is misaligned (a fused "76.3 72.6" cell and an empty cell), and the bold winning-cluster marking is lost; the bold "best ±1%" / best-per-column marking is also lost in Tables 12, 14, 16 and 19 (p. 24–33)

## Digest

- **Claim.** Command A is a 111B model built for enterprise RAG, tool use and agents, and multilingual use in 23 languages. It is served on two A100s or H100s. The report also gives results for Command R7B. Weights for both are released under CC-BY-NC (p. 1–2).
- **Architecture (p. 3).** SwiGLU; GQA with document masking; sliding-window and full attention interleaved 3:1, with RoPE on the window layers and NoPE on the full layers; a parallel attention/FFN block; tied input and output embeddings; no biases.
- **Not disclosed.** Pre-training token count, compute, layer and width counts, vocabulary size, and the data mixture proportions.
- **Pre-training (p. 4–5).**
  - Hyperparameters tuned with µP/µTransfer.
  - JAX/GSPMD training with DP, SP, FSDP and TP axes.
  - FP8 matmuls, preceded by BF16 steps to remove a "small but non-trivial" downstream degradation. No number is given for the degradation.
  - Cooldown anneals the learning rate from 2.5 × 10^-4 to 1 × 10^-6 over 50,000 steps. Context stays at 8k for 30,000 steps, then 32k/128k/256k for 10,000/5,000/5,000 steps (p. 5).
- **Post-training pipeline (p. 5–6, Fig. 3).**
  - An Instruct model is trained first.
  - Six SFT experts (Code, Safety, RAG, Math, Multilingual, General Long-Context) are linearly merged into an "SFT soup".
  - Six RL experts are trained on the soup and merged into an "RL soup".
  - Polishing follows: best-of-N SFT, then offline SRPO and online CoPG RLHF alternated in a "ping-pong" until human preference plateaus.
- **Losses (p. 6–7).**
  - SRPO is a min-max objective: a self-refinement policy π† improves samples of π under a preference model, with KL to a reference.
  - CoPG is a squared-difference contrastive loss on the KL-regularised reward. On-policy it is equivalent to RLOO.
  - For instruction following, SRPO "performs best" against SLiC, IPO and DPO; no numbers are given (p. 9). The safety expert uses IPO plus an equally weighted SFT loss (p. 14).
- **Merging method (p. 16).**
  - Linear weight averaging, with weights found by heuristics and brute-force perturbation. SLERP and task vectors gave "no significant performance improvements".
  - All experts start from a common instruct checkpoint.
  - Leave-one-out merges are used to detect "collisions", and each expert gets a small amount of cross-domain data as a regulariser.
  - The final model was informed by 500 evaluation metrics.
- **Merging results (p. 34–35, Fig. 12).**
  - Linear merging loses 1.8% on average against the best expert, and most metrics stay within 2.5% of it. Code is the least well preserved.
  - Large changes to expert weights shift domain performance by 2-3%.
  - A few SFT steps at a 10–20x lower learning rate after merging bring many metrics to at least 100% of the expert. This is not quantified.
- **Reward model.** It scores 92.7% on RewardBench and 72.3% on RMB, with no comparison model given (p. 7).
- **Academic benchmarks (p. 2, Table 1; p. 18, Table 3).**
  - MATH: 80.0, against DeepSeek V3 70.2, GPT-4o 68.5 and Llama 3.3 70B 77.0.
  - IFEval: 90.9, against Llama 3.3 70B 92.1.
  - GPQA: 50.8, against DeepSeek V3 59.1 and Claude 3.5 Sonnet 65.0.
  - MMLU: 85.5, against DeepSeek V3 88.5.
  - The paper is internally inconsistent: GPT-4o MMLU is 85.7 in Table 1 but 89.2 in Table 3, and GPT-4o GPQA is 53.6 in Tables 1 and 3 but 46.0 (GPQA Diamond) in Table 15 (p. 26).
- **Agents and RAG (p. 19).**
  - Taubench retail P@1: 60.0, against GPT-4o 60.6 and Claude 3.5 Sonnet 69.2.
  - Taubench airline P@1: 45.3, against Claude 3.5 Sonnet 46.0 and GPT-4o 43.0 (Table 6). The aggregate Taubench 51.7 in Table 1 is not explained.
  - BFCL overall: 63.8, against GPT-4o 72.1 and Qwen 2.5 72B 63.5 (Table 5).
  - ChatRAGBench: 72.9, against GPT-4o 66.6 and DeepSeek V3 40.3 (Table 4).
- **Multilingual (p. 20–23).**
  - NTREX COMET-20 average: 68.8, against GPT-4o 71.0 and DeepSeek V3 69.8 (Table 7).
  - mArenaHard average win rates (LLM judge, Table 8): 78.9 against Llama 3.3 70B, 65.9 against Mistral Large 2, and 53.4 against DeepSeek V3.
  - ADI2 Arabic dialect scores: 24.2 monolingual and 33.5 crosslingual, against Gemini 1.5 Pro 19.3 and 26.4 (Table 11).
  - Multilingual Taubench retail average: 34.3, against GPT-4o 37.3 (Table 9).
- **Overclaim on language confusion (Table 10).** The text says Command A and Command R+ Refresh have the "highest and second highest" aggregate scores. In Table 10, Command A's 93.0 ties Qwen 2.5 72B Turbo's 93.0, and R+ Refresh's 95.5 is the top score.
- **Code (p. 24–25, Tables 12–13).**
  - MBPP+: 86.2, against DeepSeek V3 90.0.
  - RepoQA: 92.6, against DeepSeek V3 92.2.
  - HumanEval-COBOL: 25.3, against DeepSeek V3 15.2.
  - The agentic variant gets gold-unit-test execution feedback that the baselines do not get. It scores LiveCodeBench 32.9, BigCodeBench 59.7 and LBPP 65.4.
  - The stated LBPP gain of +12.3% does not match Table 12's 51.5 → 65.4.
  - SWE-Bench Verified: 26.8, against DeepSeek V3 42.0/45.8. Aider Polyglot: 14.7, against 49.6/51.6. The paper says code editing was not targeted.
- **Overclaim on SQL (Table 14).** The text says Command A leads Spider Dev, but its 79.5 trails Qwen 2.5 72B (83.5) and Llama 3.1 405B (83.0). Only the Command A Expert (85.5) leads. On Bird, 59.5 is against Llama 3.1 405B 59.4. The internal SQL average is 55.3, against DeepSeek V3 60.8.
- **Default safety (p. 29–30, Table 16).**
  - Absolute safety: 70.4, against Claude 3.5 Sonnet 80.0 and Qwen 2.5 72B 71.4. The text calls this "closely following".
  - Competitor relative-safety win rates against Command A are all ≤32.4 for large models.
- **Over-refusal (Table 17).**
  - XSTest: 1.1. The text calls this "marginally better" than open models, but DeepSeek V3 (0.8), Mistral Large 2 (0.8) and Qwen 2.5 72B (0.4) refuse less.
  - Internal over-refusal: 7.1, tied with GPT-4o as the highest among large models.
  - The relative-safety LLM jury agrees with humans 77.7%, with kappa 0.55 (p. 27).
- **Demographic fairness.** Command A has a median of 1% race-invariance failures and none for gender (p. 28, Fig. 8).
- **Internal enterprise suites (p. 32–33).**
  - Generative pass rate over 22 internal tasks: 94.2, against Command R+ Refresh 87.4, Claude 3.5 Sonnet v2 84.2 and GPT-4o 79.1 (Table 18).
  - RAG correctness average: 4.73, against Claude 3.5 Sonnet v2 4.72. Claude is higher on Workplace Policies, 4.63 against 4.59 (Table 19).
- **Long context (p. 34).**
  - RULER average up to 128k: 95.0, against Claude 3.5 Sonnet 95.4 and Gemini 1.5 Pro 94.9. At 256k: 84.6, against Gemini 1.5 Pro 91.6 (Table 21).
  - LongBench-V2: 43.4, against GPT-4o 46.0 (Table 22).
  - KV cache at 8k is 75% / 23.8% / 45.5% of Llama 3.3 70B / Llama 3.1 405B / Mistral Large; at 128k it is 32.9% / 10.4% / 19.9%.
- **Human evaluation and polishing (p. 37–38, Table 23).**
  - On about 800 internal prompts, win rates (general / reasoning / code) are 50.4/51.4/46.8 against GPT-4o, 49.0/49.3/54.7 against DeepSeek V3, and 47.2/30.7/38.3 against GPT-4.5 Preview. No intervals or significance tests are given.
  - Polishing raised the win rate against GPT-4o from 43.2 → 50.4 (general), 41.4 → 51.4 (reasoning) and 30.0 → 46.8 (code).
- **Throughput.** 156 tokens/sec, 1.75x GPT-4o and 2.4x DeepSeek V3 (p. 1). The measurement setup is not given.
- **Command R7B.** It is claimed "best-in-class" for its size (p. 1), but Table 3 puts it below Llama 3.1 8B (71.1) and Gemma 2 9B (73.5) on MMLU, where it scores 65.2. On GPQA its 26.3 is below Gemini 1.5 Flash-8B's 31.6 (p. 18).

## Related in library

- The Llama 3 Herd of Models: Llama 3.1 405B and 3.3 70B are main baselines; the paper contrasts its expert-merge post-training with the sequential recipe of Dubey et al. (2024) and follows its reward-based sample refinement.
- DeepSeek-V3 Technical Report: DeepSeek V3 is a headline baseline throughout, including throughput (2.4x) and human evaluation.
- PaLM. Scaling Language Modeling with Pathways: the paper adopts PaLM's no-bias design for training stability.
- Gemini 1.5. Unlocking multimodal understanding across millions of tokens of context: Gemini 1.5 Pro is compared on RULER, NTREX, multilingual Taubench and Arabic dialect adherence.
- Mixtral of Experts: Mixtral is compared in the demographic-fairness evaluation (lacks robustness to race).

## Q&A
