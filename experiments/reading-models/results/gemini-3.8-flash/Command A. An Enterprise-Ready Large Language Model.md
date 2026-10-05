# Command A: An Enterprise-Ready Large Language Model

type: system
read: full
family: Cohere Command family (Command A, Command R7B)
evidence: academic benchmarks (MMLU, MATH, IFEval, GPQA), agent/tool-use (Taubench, BFCL), multilingual benchmarks (NTREX, FLORES, mArenaHard), code benchmarks (MBPP+, BigCodeBench, RepoQA, LBPP, HumanEval, Bird-SQL, Spider), enterprise internal evals, and blind human evaluation; strength: vendor-run evaluations against competing closed/open models (GPT-4o, DeepSeek V3, Llama 3.3 70B, Claude 3.5 Sonnet) with internal reproductions and ablations on merging/polishing
conversion: ok (some table header formatting artifacts on p. 21 Table 7 and p. 22 Table 8, but underlying numbers are readable; text and equations intact)

## Digest

- **Model Overview & Serving Footprint**: Command A is a 111B parameter decoder-only model targeted at enterprise use cases (RAG, tool use, 23 languages); Command R7B is an accompanying 7B variant (p. 1-2). Serves on 2x A100 or H100 GPUs delivering up to 156 tokens/sec (reported as 1.75x higher than GPT-4o and 2.4x higher than DeepSeek V3) (p. 1).
- **Core Architecture Innovations**: SwiGLU activations, grouped-query attention (GQA), parallel transformer blocks, shared input/output embeddings, and no bias terms (p. 3-4). Features an interleaved 3:1 ratio of sliding window attention (with RoPE) and full attention layers (with NoPE / No Positional Embeddings) (p. 3).
- **KV Cache Savings**: Interleaved attention reduces KV cache memory at 8k sequence length to 75% of Llama 3.3 70B, 23.8% of Llama 3.1 405B, and 45.5% of Mistral Large; at 128k context, this drops to 32.9%, 10.4%, and 19.9% respectively (p. 34).
- **Training Infrastructure & FP8**: Trained on H100 clusters in JAX via GSPMD using DP, Megatron-style Sequence Parallelism (SP), FSDP, and Tensor Parallelism (TP) (p. 4). Pretrained with FP8 tensor cores (main weights and optimizer in FP32; layer norms, softmaxes, embeddings in FP32; attention in BF16) with initial BF16 steps to avoid downstream degradation (p. 4).
- **Context Extension Cooldown**: Pre-training cooldown linearly anneals learning rate from $2.5 \times 10^{-4}$ to $1 \times 10^{-6}$ for 50,000 steps in BF16: 8k tokens for 30,000 steps, then 32k (10,000 steps), 128k (5,000 steps), and 256k (5,000 steps) with long-context data interleaved every fourth step (p. 5).
- **Decentralized Post-Training Recipe**: Alternates between parallel decentralized expert training and model merging: Base $\rightarrow$ Instruct $\rightarrow$ 6 SFT Experts $\rightarrow$ SFT Soup $\rightarrow$ 6 RL Experts $\rightarrow$ RL Soup $\rightarrow$ Polishing (p. 5-6, Figure 3). The 6 expert tracks: Code, Safety, RAG, Math, Multilingual, and General Long-Context (p. 6).
- **Self-Improving Robust Preference Optimization (SRPO)**: Formulates alignment as a min-max game $\min_{\pi} \max_{\pi_+} \mathbb{E}_x \mathbb{E}_{y_1 \sim \pi, y_2 \sim \pi_+} [P(y_2 \succ y_1|x) - \beta \text{KL}(\pi_+ || \pi_{\text{ref}}) + \beta \text{KL}(\pi || \pi_{\text{ref}})]$ where generator $\pi$ competes against self-improvement policy $\pi_+$, enabling test-time iterative refinement (p. 6-7).
- **Contrastive Policy Gradient (CoPG)**: Uses KL-regularized RL loss $\ell = \frac{1}{k-1} \sum_{i>j} (R_\beta^\pi(x, y_i) - R_\beta^\pi(x, y_j))^2$ without importance sampling, clipping, or a value network, used both offline and online on-policy (equivalent to RLOO) (p. 7).
- **Reward Model Design**: Bradley-Terry model trained in two stages (Stage 1: ~4M lower-quality samples relabeled with ensembles; Stage 2: ~350k high-quality samples at lr $3 \times 10^{-6}$); achieves 92.7% on RewardBench and 72.3% on RMB (p. 7).
- **Expert Merging Mechanics**: Employs linear weight averaging determined by manual heuristic/grid search over 500 evaluation metrics, avoiding complex schemes like SLERP or task vectors (p. 16). Seed merging and base model interpolation are used to recover degraded long-context capability (p. 15).
- **Metric Retention in Merging**: Linear merging preserves domain performance with only a 1.8% average drop across tracked metrics; RAG and general are best preserved, while code suffers the largest degradation (p. 34, Figure 12).
- **Polishing Phase**: Applied to RL Soup via: 1) best-of-4 SFT; 2) offline preference tuning via SRPO; 3) online RLHF via online CoPG in an alternating "ping-pong" schedule (p. 17). Boosts human win rate vs. GPT-4o from 43.2% to 50.4% on general, 41.4% to 51.4% on reasoning, and 30.0% to 46.8% on code (p. 38).
- **Academic Benchmark Performance**: Command A achieves MMLU 85.5 (vs. GPT-4o 89.2, DeepSeek V3 88.5, Llama 3.3 70B 86.0), GPQA 50.8 (vs. GPT-4o 53.6, Llama 3.3 70B 50.5), and IFEval strict average 90.9 (vs. GPT-4o 83.8, Llama 3.3 70B 92.1) (p. 18, Table 3).
- **Agentic & Tool-Use Evals**: On Taubench Retail P@1, Command A reaches 60.0% (vs. GPT-4o 60.6%, DeepSeek V3 54.8%, Llama 3.3 70B 6.2%); Taubench Airline P@1 hits 45.3% (vs. GPT-4o 43.0%, Llama 3.3 70B 35.3%) (p. 19, Table 6). BFCL Overall score is 63.8 (vs. GPT-4o 72.1, DeepSeek V3 58.6) (p. 19, Table 5).
- **Coding & Agentic Code**: MBPP+ pass@1 is 86.2% (vs. GPT-4o 86.5%, DeepSeek V3 89.9%) (p. 2, Table 1). In tool-augmented agentic execution mode, LiveCodeBench jumps from 26.9% to 32.9%, BigCodeBench from 45.4% to 59.7%, and LBPP(All) from 51.5% to 65.4% (p. 24, Table 12).
- **SQL & COBOL Strengths**: Bird-SQL Dev execution accuracy is 59.5% (vs. GPT-4o 50.5%, DeepSeek V3 53.1%, Llama 3.3 70B 58.0%) (p. 25, Table 14). HumanEval-COBOL translation to Python scores 55.7% (vs. DeepSeek V3 63.3%, Llama 3.3 70B 46.2%, Mistral Large 2 46.8%) (p. 24, Table 12).
- **Reasoning**: MATH score is 80.0% (vs. GPT-4o 68.5%, DeepSeek V3 70.2%, Llama 3.3 70B 77.0%) (p. 2, Table 1; p. 27, Table 15). AIME 2024 is 23.3% (vs. GPT-4o 9.3%, Llama 3.3 70B 20.0%) (p. 27, Table 15).
- **Multilingual Capabilities**: Evaluated on 23 business languages; NTREX COMET-20 average is 68.8 (vs. GPT-4o 71.0, DeepSeek V3 69.8, Llama 3.3 70B 62.5) (p. 21, Table 7). Line-level pass rate on Language Confusion Benchmark is 93.0% (vs. GPT-4o 88.9%, Claude 3.7 Sonnet 91.8%) (p. 23, Table 10).
- **Enterprise RAG & Generative Suite**: Scores 94.2% pass rate across 22 enterprise generative tasks (vs. GPT-4o 79.1%, Claude 3.5 Sonnet v2 84.2%) (p. 33, Table 18). On Enterprise RAG QA correctness, scores 4.73 / 5.0 (vs. GPT-4o 4.66, Claude 3.5 Sonnet v2 4.72) with 96% answerable accuracy and 91% unanswerable accuracy (p. 33, Table 19 & 20).
- **Undisclosed Details**: Exact pre-training dataset size (referred to only as "trillions of tokens" on p. 2), exact parameter count breakdown, detailed architecture dimensions (hidden dimension, layer counts, heads), and specific expert merge weights are omitted.

## Related

- **Command R / Command R+**: Prior Cohere foundation models; Command A introduces hybrid sliding window/full attention, decentralized expert merging, and SRPO.
- **Llama 3.3 / Llama 3.1 (Dubey et al., 2024)**: Direct open-weights baseline across benchmarks; Command A achieves competitive metrics at 111B parameters with 2x GPU serving.
- **DeepSeek V3 (Liu et al., 2024a)**: Competitive open baseline; Command A claims 2.4x higher serving throughput and higher MATH/SQL performance.
- **WARP (Ramé et al., 2024)**: Basis for weight-space averaging and interpolation used during RL stage regularisation and long-context capability recovery.
- **Model Soups / Linear Merging (Wortsman et al., 2022; Izmailov et al., 2018)**: Foundational parameter-merging techniques scaled here to multi-stage decentralized post-training pipelines.
- **ReAct (Yao et al., 2022)**: Framework informing Command A's agentic tool use and trajectory-based supervision.
