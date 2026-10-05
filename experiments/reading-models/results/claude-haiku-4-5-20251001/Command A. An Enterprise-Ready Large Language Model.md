# Command A: An Enterprise-Ready Large Language Model

type: method | benchmark
read: full
family: Decoder-only Transformer for enterprise; 111B and 7B models with multilingual (23 languages) and agentic capabilities; decentralized post-training via expert models and parameter merging
evidence: Vendor-run evaluation across 500+ internal metrics and public benchmarks (MMLU, MATH, Taubench, BFCL, code, safety, multilingual, long-context); human evaluation (65+ annotators, 800 prompts); internal enterprise-focused RAG and generative benchmarks; strength: extensive but vendor-conducted; many internal benchmarks not independently verifiable; no third-party replication

conversion: ok

## Digest

**Mechanism**: Decoder-only Transformer with SwiGLU activation, grouped-query attention (GQA), interleaved 3:1 sliding-window and full-attention layers (sliding window uses RoPE, full uses NoPE), parallel transformer blocks, shared input/output embeddings, no bias. Distributed training on H100 cluster (JAX/GSPMD) with DP/SP/FSDP/TP parallelism; FP8 tensor cores with mixed precision (FP32 for weights/optimizer, BF16/FP8 for compute). Learning rate annealing over 50k steps; context extended from 8k to 256k tokens with carefully balanced data mixture (p. 3–5).

**Post-training (novel)**: Decentralized approach alternating centralized and decentralized stages. Six SFT expert models (Code, Safety, RAG, Math, Multilingual, Long-Context) trained on shared instruction base, merged via weighted linear averaging into "SFT Soup." Six RL experts trained on SFT Soup, using domain-specific algorithms (verifiable rewards for Math/Code; preference pairs for Safety/Multilingual) and CoPG loss; merged into "RL Soup." Final "polishing" phase combines best-of-N SFT, offline preference tuning (SRPO with self-refinement capability), and online RLHF. Model merging is described as computationally cheap rebalancing; linear merging chosen over SLERP/task vectors with no significant performance loss (p. 5–17).

**Disclosed**: Architecture details (p. 3); distributed training framework and parallelism strategies (p. 4–5); data sources: public web + synthetic + human annotation + vendor data, with quality filtering and de-duplication (p. 3); reward model (Bradley-Terry, 92.7% RewardBench; p. 7); instruction-following, RAG/tool-use, multilingual, code, math, long-context, and safety training methods and datasets (p. 8–14); extensive evaluation across 500+ metrics (p. 15, 18–34); merging analysis showing 1.8% average metric drop (p. 34–35); polishing phase results and human evaluation methodology (p. 17, 36–37).

**Not disclosed**: Exact data mixture percentages; total pretraining tokens; full hyperparameter grids (Appendix B referenced but not provided); compute budget; sizes/sources of internal datasets; specific safety pretraining filtering details; training loss curves; complete ablations on architectural choices.

**Main numbers** (p. 2, 18–37):

- **MMLU** (Table 1, 3): 85.5 (Command A) vs 88.5 (DeepSeek V3), 85.7 (GPT-4o), 86.0 (Llama 3.3 70B)
- **MATH** (Table 1, 15): 80.0 (Command A) vs 70.2 (DeepSeek V3), 68.5 (GPT-4o), 77.0 (Llama 3.3 70B)
- **IFEval** (Table 1, 3): 90.9 (Command A) vs 92.1 (Llama 3.3 70B), 86.1 (DeepSeek V3), 83.8 (GPT-4o)
- **GPQA** (Table 1, 3): 50.8 (Command A) vs 59.1 (DeepSeek V3), 53.6 (GPT-4o)
- **Taubench Retail P@1** (Table 6): 60.0 (Command A) vs 54.8 (DeepSeek V3), 60.6 (GPT-4o), 6.2 (Llama 3.3 70B)
- **BFCL Overall** (Table 5): 63.8 (Command A) vs 72.1 (GPT-4o), 58.6 (DeepSeek V3), 51.4 (Llama 3.3 70B)
- **MBPP+** (Table 12): 86.2 (Command A) vs 89.9 (DeepSeek V3), 86.5 (GPT-4o)
- **RepoQA** (Table 12): 92.6 (Command A) vs 92.2 (DeepSeek V3), 91.2 (GPT-4o)
- **Bird-SQL** (Table 14): 59.5 (Command A) vs 53.1 (DeepSeek V3), 50.5 (GPT-4o)
- **NTREX avg** (Table 7): 68.8 (Command A) vs 71.0 (GPT-4o), 70.5 (Gemini 2.0 Flash)
- **mArenaHard avg 23 languages** (Table 8): 78.9 (Command A) vs 78.7 (Llama 3.3 70B), 65.9 (Llama 3.1 405B), 53.4 (DeepSeek V3)
- **Relative Safety** (Table 16): 49.5 (Command A) vs 26.4 (Claude 3.5 Sonnet), 23.7 (DeepSeek V3)
- **Absolute Safety** (Table 16): 70.4 (Command A) vs 80.0 (Claude 3.5 Sonnet), 49.7 (DeepSeek V3)
- **RULER 128k** (Table 21): 90.0 (Command A) vs 93.8 (Claude 3.5 Sonnet), 91.7 (Gemini 1.5 Pro)
- **Enterprise Generative Pass Rate** (Table 18): 94.2% (Command A) vs 84.2% (Claude 3.5 Sonnet), 81.3% (DeepSeek V3)
- **Enterprise RAG Correctness** (Table 19): 4.73 (Command A) vs 4.72 (Claude 3.5 Sonnet)
- **Human eval vs GPT-4o**: General 50.4%, Reasoning 51.4%, Code 46.8% win rate (Table 23)
- **Throughput**: 156 tokens/sec on 2 H100s; 1.75× faster than GPT-4o, 2.4× faster than DeepSeek V3 (p. 2)
- **Command R7B results** (Table 1, 3): MMLU 65.2, MATH 59.1, GPQA 26.3; BFCL 52.2

**Ablations/analysis**: Expert merging preserves 98.2% of expert performance on average (1.8% drop; p. 34); expert performance largely preserved across domains with RAG/general best preserved, code least preserved (Figure 12b, p. 34); polishing improves human preference win rates by 7–17 percentage points vs merged baseline (p. 36); seed merging and Pareto-optimal candidate selection shown to improve reasoning and cross-capability performance (p. 13, 15).

**Baselines**: Comparison against GPT-4o, DeepSeek V3, Llama 3.3 70B, Llama 3.1 405B/8B, Claude 3.5 Sonnet, Mistral Large 2, Gemini 2.0/1.5, Qwen 2.5 72B/7B across benchmarks. Command R7B vs similar-size open models (Llama 3.1 8B, Ministral 8B). Human evaluation against GPT-4o, GPT-4.5 Preview, DeepSeek V3, Llama models.

## Related

- Transformer architecture (Vaswani et al., 2017): foundational; this paper extends with architectural optimizations
- GQA (Ainslie et al., 2023), RoPE (Su et al., 2021), NoPE (Kazemnejad et al., 2023): components adopted; Yang et al. (2025) cited for interleaved attention design
- DPO (Rafailov et al., 2024), SLiC (Zhao et al., 2023), IPO (Azar et al., 2024): preference training methods; SRPO novel contribution
- CoPG (Flet-Berliac et al., 2024): RL algorithm selected for its theoretical guarantees
- Model merging literature (Izmailov et al., 2018; Wortsman et al., 2022; Ilharco et al., 2023; Ramé et al., 2024): linear merging chosen as sufficiently effective; WARP used for specific capability recovery
- ReAct (Yao et al., 2022): framework adopted for agentic tool use
- Command R+ Refresh: previous Cohere model; Command A shows substantial improvements across benchmarks
