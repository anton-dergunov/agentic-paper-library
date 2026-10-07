# Command A: An Enterprise-Ready Large Language Model

type: system
read: full
family: dense decoder-only LLM technical report (enterprise RAG/agents/multilingual), post-trained with expert-model merging
evidence: Academic, agent, code, SQL, math, multilingual, safety and long-context benchmarks, plus internal enterprise benchmarks and internal human pairwise evaluations, against GPT-4o, DeepSeek V3, Llama 3.x, Mistral Large 2, Claude 3.5/3.7 Sonnet, Qwen 2.5 and Gemini; Command R7B is compared with ~8B models; strength: vendor-run, many internal reproductions and internal datasets, no ablation of merging against single-model training
conversion: key-content-broken: Table 8 (mArenaHard win rates, p. 20–23) has its header at the bottom, an empty "es" row and fused values in the "en" row ("73.6 82.7", "64.1 63.8", "52.5 52.7"), so its es/en values are unreliable; Table 7 (NTREX/FLORES, p. 20–23) is flattened with the header row at the bottom, though it can be read by order, and its bold "winning cluster" marking is lost; bold best-score marking is also lost in Tables 12, 14, 16 and 19; Figure 9's caption is duplicated over Table 16 (p. 29–30); the stage list in §3.1 is out of order (Instruct listed after the SFT experts, p. 5–6)

## Digest

- **Claim.** Command A is a 111B-parameter model built for enterprise RAG, tool use and agents in 23 languages. The paper claims "best-in-class" results for its size and efficiency. It serves on two A100s or H100s at up to 156 tokens/sec, which it puts at 1.75x GPT-4o and 2.4x DeepSeek V3 (p. 1). No measurement setup is given for this throughput. Weights for Command A and Command R7B are released under CC-BY-NC (p. 2).
- **Architecture** (p. 3):
  - Decoder-only with SwiGLU and GQA.
  - Sliding-window and full attention interleaved 3:1. Sliding-window layers use RoPE; full-attention layers use NoPE.
  - Parallel transformer block, tied input/output embeddings, no bias terms.
- **Not disclosed:** pretraining token count, layer and width sizes, total compute, vocabulary size and data proportions. Contamination checks are not described.
- **Pretraining** (p. 4–5):
  - Hyperparameters are tuned with µP/µTransfer.
  - Training uses JAX/GSPMD on H100 with DP+FSDP+SP sharding and FP8 matmuls; the main weights and optimiser states are kept in FP32.
  - Training fully in FP8 gave a "small but non-trivial" downstream degradation. This was fixed by running some steps in BF16.
  - Cooldown anneals the learning rate from 2.5 × 10⁻⁴ to 1 × 10⁻⁶ over 50,000 steps. Context grows from 8k to 32k, 128k and 256k (p. 5).
- **Post-training: decentralised merging** (p. 5–6):
  - An Instruct model is trained first. Six SFT experts (Code, Safety, RAG, Math, Multilingual, General Long-Context) are trained from it and linearly merged into an SFT soup.
  - Six RL/preference experts are trained on the soup and merged again.
  - A "polishing" phase follows: best-of-N SFT, then alternating offline SRPO and online CoPG ("ping-pong") until human preference plateaus.
- **Preference and RL algorithms** (p. 6–7):
  - SRPO is a min-max self-refinement objective. The paper says it is independent of the preference dataset's sampling distribution and allows iterative self-revision at inference.
  - CoPG is a contrastive policy-gradient loss used offline and online. Pure on-policy CoPG is equivalent to RLOO.
  - SRPO was chosen for the Instruct model because it "performs best" against SLiC, IPO and DPO (p. 9). No numbers are shown for this comparison.
- **Reward model** (p. 7): Bradley-Terry with soft labels, trained in two stages (~4M lower-quality samples, then ~350,000 high-quality). It scores 92.7% on RewardBench and 72.3% on RMB. No comparison model is given.
- **Merging findings** (p. 15–17, p. 34–35):
  - Linear merging with manually searched weights was used. SLERP and task vectors gave "no significant performance improvements".
  - All experts are initialised from a shared model. Leave-one-out merges are used to find "collisions" between experts.
  - The merged model loses a 1.8% average against the best expert, and most metrics stay within 2.5% (p. 34, Fig. 12a).
  - Code is the least well preserved domain (Fig. 12b).
  - At 111B, large changes to the merge weights move domain performance by only 2-3%.
  - A few low-learning-rate SFT steps after merging bring many metrics to 100% of expert performance or above (p. 35).
- **Headline academic and agent results** (p. 2, Table 1; p. 18, Table 3):
  - MMLU 85.5 for Command A, against DeepSeek V3 88.5 and GPT-4o 85.7 (Table 3 lists GPT-4o at 89.2).
  - MATH 80.0, against 70.2 and 68.5.
  - GPQA 50.8, against 59.1 and 53.6.
  - IFEval 90.9, against Llama 3.3 70B 92.1.
  - Taubench 51.7, against GPT-4o 51.2 and DeepSeek V3 39.1.
  - BFCL 63.8, against GPT-4o 72.1.
  - "Best-in-class" therefore holds against the 70B-class models, not against DeepSeek V3 or GPT-4o on MMLU, GPQA, BFCL, MBPP+ or NTREX.
- **Inconsistent GPQA figure.** GPT-4o's GPQA Diamond is 46.0 in Table 15 (p. 26) but 53.6 in Tables 1 and 3.
- **Agents and RAG:**
  - Taubench Retail P@1: 60.0 against GPT-4o 60.6 and Claude 3.5 Sonnet 69.2.
  - Taubench Airline P@1: 45.3 against GPT-4o 43.0 (p. 19, Table 6).
  - ChatRAGBench: 72.9 against GPT-4o 66.6 and DeepSeek V3 40.3 (p. 19, Table 4).
- **Code and SQL** (p. 24–25):
  - RepoQA 92.6 against DeepSeek V3 92.2 (Table 12).
  - HumanEval-COBOL 25.3 against DeepSeek V3 15.2.
  - SWE-Bench Verified 26.8 against DeepSeek V3 42.0 / 45.8 (Table 13). The paper says these code-editing results are post-hoc and were not a target.
  - In agentic mode, gains over direct generation are +5.9% LiveCodeBench, +14.3% BigCodeBench and +12.3% LBPP.
  - The BigCodeBench "leaderboard" claim uses a modified 3-test execution-feedback setup.
  - Bird Dev: 59.5 against Llama 3.1 405B 59.4 (Table 14).
- **Multilingual** (p. 20–23):
  - NTREX COMET-20 average 68.8 against GPT-4o 71.0 (Table 7).
  - mArenaHard average win rates: 78.9 vs Llama 3.3 70B, 78.7 vs Llama 3.1 405B, 65.9 vs Mistral Large 2, 53.4 vs DeepSeek V3 (Table 8; es/en rows broken).
  - Language Confusion Benchmark LPR: 93.0, below its own predecessor Command R+ Refresh at 95.5 (Table 10).
  - Arabic dialect ADI2: 24.2 monolingual and 33.5 crosslingual, against Gemini 1.5 Pro 19.3 and 26.4 (Table 11).
  - Multilingual Taubench Retail average: 34.3 against GPT-4o 37.3 (Table 9).
- **Safety** (p. 29–30):
  - Relative safety (win rate vs Command A, LLM jury) is 49.5. Absolute safety is 70.4, below Claude 3.5 Sonnet 80.0 and Qwen 2.5 72B 71.4 (Table 16).
  - The text calls this "significantly outperforms all competitors". That holds only for the relative metric, which rewards response quality when both responses are safe.
  - XSTest over-refusal is 1.1, against GPT-4o 5.6 (Table 17).
  - Internal over-refusal is 7.1, the same as GPT-4o and above all other large models.
- **Enterprise (internal) benchmarks** (p. 32–33):
  - Generative pass rate across 22 tasks: 94.2% against Claude 3.5 Sonnet v2 84.2 and GPT-4o 79.1 (Table 18).
  - RAG Llama Index Correctness average: 4.73 against Claude 3.5 Sonnet v2 4.72 (Table 19).
  - Answerable/unanswerable accuracy: 96/91 (Table 20).
- **Long context** (p. 34):
  - RULER: 84.6 at 256k against Gemini-1.5-Pro 91.6. The ≤128k average is 95.0 against Claude 3.5 Sonnet 95.4 (Table 21).
  - LongBench-V2 overall: 43.4 against GPT-4o 46.0 (Table 22).
  - KV cache at 128k: 32.9% of Llama 3.3 70B's and 10.4% of Llama 3.1 405B's.
  - Table 2 lists Needle-in-a-Haystack and RulerQA, but §4.8 reports RULER and LongBench-V2.
- **Human evaluation** (p. 37–38, Table 23):
  - Setup: about 800 internal prompts, judged by internal annotators.
  - Win rates against GPT-4o: 50.4 general, 51.4 reasoning, 46.8 code.
  - Against GPT-4.5 Preview: 47.2, 30.7, 38.3.
  - Against DeepSeek V3: 49.0, 49.3, 54.7.
  - Polishing raised the win rate against GPT-4o from 43.2 to 50.4 (general), 41.4 to 51.4 (reasoning) and 30.0 to 46.8 (code), compared with the pre-polish merged checkpoint.

## Related in library

- DeepSeek-V3 Technical Report: DeepSeek V3 is a main comparison model across nearly all tables, and is used as the throughput baseline.
- The Llama 3 Herd of Models: Llama 3.1 and 3.3 models are the main open-weight baselines; its sequential post-training paradigm (Dubey et al., 2024) is the contrast for the merging approach.
- PaLM. Scaling Language Modeling with Pathways: cited for dropping bias terms to improve training stability.
- Gemini 1.5. Unlocking multimodal understanding across millions of tokens of context: Gemini 1.5 Pro is compared on RULER, NTREX and multilingual Taubench.

## Q&A
