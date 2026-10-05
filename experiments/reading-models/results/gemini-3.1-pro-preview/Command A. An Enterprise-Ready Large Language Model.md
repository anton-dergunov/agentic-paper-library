# Command A: An Enterprise-Ready Large Language Model

type: system
read: full
family: Cohere foundation model technical report
evidence: Tested on academic (MMLU, MATH, GPQA), tool-use/agentic (BFCL, Taubench), coding (MBPP+, RepoQA, Spider), multilingual (NTREX), safety (XSTest), and enterprise RAG/generative benchmarks, against GPT-4o, DeepSeek V3, Claude 3.5 Sonnet, and Llama 3.3 70B; evaluated by automated metrics, LLM-as-a-judge, and human preference.
strength: vendor-run with extensive ablations on the merging and polishing pipeline; strong internal and external benchmark suite
conversion: ok

## Digest

- Architecture: Command A is a 111B parameter, decoder-only Transformer without bias terms, utilizing SwiGLU activations and Grouped-Query Attention (GQA) (p. 1, 3).
- Attention Mechanism: Features interleaved attention layers with a 3:1 ratio of sliding window attention (using RoPE) to full attention (using NoPE) (p. 3).
- Data Disclosures: Pre-trained on 23 languages of global business using web text, code, and synthetic datasets (p. 3); exact pre-training token counts and mixture proportions are not disclosed.
- Post-Training Pipeline: Alternates centralized and decentralized stages, creating SFT Experts (Code, Math, RAG, etc.), merging them into an "SFT Soup", training RL Experts, merging into an "RL Soup", and finally polishing (p. 5, Figure 3).
- Merging: Uses linear weight merging, which preserves capabilities well, showing an average expert performance drop of only 1.8% upon merging (p. 34).
- RL Algorithms: Introduces Self-improving Robust Preference Optimisation (SRPO) for offline preference training and Contrastive Policy Gradient (CoPG) for reward models and online RL (p. 6-7).
- Efficiency: Serves at up to 156 tokens/sec, a rate 1.75x higher than GPT-4o and 2.4x higher than DeepSeek V3 (p. 1).
- MMLU: Command A scores 85.5, compared to GPT-4o at 89.2, DeepSeek V3 at 88.5, and Llama 3.3 70B Instruct at 86.0 (p. 18, Table 3).
- MATH: Command A achieves 80.0, outperforming Llama 3.3 70B (77.0), DeepSeek V3 (70.2), and GPT-4o (68.5) (p. 2, Table 1).
- IFEval: Command A scores 90.9, compared to Llama 3.3 70B Instruct (92.1), DeepSeek V3 (86.1), and GPT-4o (83.8) (p. 18, Table 3).
- BFCL Overall (Tool-Use): Command A achieves 63.8, against GPT-4o (72.1), DeepSeek V3 (58.6), and Llama 3.3 70B Instruct (51.4) (p. 19, Table 5).
- Taubench Retail P@1: Command A scores 60.0, compared to Claude 3.5 Sonnet (69.2), GPT-4o (60.6), and Mistral Large 2 (53.3) (p. 19, Table 6).
- RepoQA (Code): Command A reaches 92.6, compared to DeepSeek V3 (92.2), GPT-4o (91.2), and Llama 3.3 70B (85.6) (p. 2, Table 1).
- Machine Translation (NTREX Average COMET-20): Command A scores 68.8, against GPT-4o (71.0), DeepSeek V3 (69.8), and Llama 3.3 70B Instruct (62.5) (p. 21, Table 7).
- Relative Safety (Winrate): Command A achieves 49.5, beating Qwen 2.5 72B (32.4) and GPT-4o (26.6) (p. 29, Table 16).
- Over-Refusal (XSTest Full): Command A exhibits a 1.1 refusal rate, compared to GPT-4o (5.6), Claude 3.5 Sonnet (3.6), and Llama 3.3 70B (1.2) (p. 30, Table 17).
- Enterprise Generative Pass Rate: Command A achieves 94.2%, outperforming Claude 3.5 Sonnet v2 (84.2%), DeepSeek V3 (81.3%), and GPT-4o (79.1%) (p. 33, Table 18).
- Enterprise RAG Answerable Acc. (%): Command A scores 96, compared to Llama 3.3 70B Instruct (95), GPT-4o (94), and DeepSeek V3 (93) (p. 33, Table 20).
- Long-Context (RULER Avg ≤ 128k): Command A reaches 95.0, compared to Claude 3.5 Sonnet (10-22) (95.4) and Gemini-1.5-Pro (002) (94.9) (p. 34, Table 21).
- Human Evaluation (Win Rate vs Llama 3.3 70B Instruct): Command A wins 68.8% on General, 71.7% on Reasoning, and 63.4% on Code prompts (p. 38, Table 23).

## Related

- Command R+ (Cohere): Command A serves as the architectural and generational successor, showing significant capability and efficiency improvements over R+ Refresh.
