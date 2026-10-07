# DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model

type: method
read: full
family: sparse Mixture-of-Experts decoder LLM with low-rank compressed-KV attention (MLA)
evidence: base model tested on 28 English/Chinese/code/math benchmarks against DeepSeek 67B, Qwen1.5 72B, Mixtral 8x22B and LLaMA3 70B; chat models tested on standard benchmarks, MT-Bench, AlpacaEval 2.0 and AlignBench (judged by GPT-4) against open and closed chat models; strength: vendor-run (all baselines re-run in DeepSeek's internal framework), single runs, attention ablations only in appendices outside this view, efficiency figures measured against their own previous model only
conversion: ok — the bold/underline marking of best and second-best in Table 2 (p. 14) is lost, but the values are present and can be compared directly.

## Digest

- **Claim.** DeepSeek-V2 is a 236B-parameter MoE model with 21B parameters active per token and a 128K context (p. 1). Against DeepSeek 67B it is reported as "significantly stronger", saving 42.5% of training costs, cutting the KV cache by 93.3% and raising maximum generation throughput to 5.76 times (p. 1, Fig. 1).
- **MLA mechanism.** Keys and values are jointly projected down to a latent vector c_t^KV of dimension d_c. Only that latent is cached, and the up-projections W^UK and W^UV are absorbed into W^Q and W^O at inference (p. 7). Queries are also low-rank compressed, but only to save activation memory during training (p. 7).
- **Decoupled RoPE.** RoPE cannot be applied to the compressed keys without breaking the matrix absorption. MLA therefore adds extra per-head RoPE queries and one shared RoPE key of dimension d_h^R, and that key is also cached. Cache per token becomes (d_c+d_h^R)l elements, ≈ 9/2·d_h·l. The paper says this equals GQA with "2.25 groups" while being "stronger than MHA" (p. 8, Table 1).
- **Support for "better than MHA".** The paper points to Appendix D (D.1 compares MHA, GQA and MQA; D.2 compares MLA with MHA). That appendix is outside this view, so the main text contains no numbers backing the claim.
- **DeepSeekMoE.** It uses fine-grained routed experts plus always-on shared experts (p. 9, Eq. 20–22).
- **Additions for expert parallelism.**
  - Device-limited routing: each token's experts must lie on at most M devices. With M≥3 this is said to roughly match unrestricted top-K, but no numbers are given (p. 9).
  - Three auxiliary balance losses, at expert level, device level and for communication (p. 10).
  - Device-level token dropping with a capacity factor of 1.0, where ~10% of sequences are never dropped (p. 11).
- **Configuration (p. 12).**
  - 60 layers, hidden size 5120; n_h=128, d_h=128, d_c=512, d_c'=1536, d_h^R=64.
  - 2 shared + 160 routed experts with 6 active, expert width 1536.
  - D=8, M=3; α1=0.003, α2=0.05, α3=0.02.
  - AdamW with maximum LR 2.4×10^-4; batch size ramps from 2304 to 9216.
- **Data and context extension.** The corpus has 8.1T tokens, with "Chinese tokens are approximately 12% more than English ones" (p. 11). The tokenizer is the same 100K BBPE as DeepSeek 67B. Context was extended from 4K to 128K with YaRN (s=40), applied only to the decoupled RoPE key, plus 1000 steps at 32K. NIAH results are shown only as a figure (p. 13, Fig. 4).
- **Base results vs. LLaMA3 70B (p. 14, Table 2).**
  - MMLU: 78.5 vs LLaMA3 70B 78.9, Mixtral 8x22B 77.6, Qwen1.5 72B 77.2, DeepSeek 67B 71.3.
  - MATH: 43.6 vs 42.2 (LLaMA3) and 42.5 (Mixtral).
  - BBH: 78.9 vs LLaMA3 81.0.
  - V2 trails LLaMA3 70B on most English rows; the paper attributes this to fewer than a quarter of LLaMA3's English tokens.
- **Base results vs. other baselines (p. 14, Table 2).**
  - Chinese benchmarks are strong: C-Eval 81.7 vs Qwen1.5 72B 83.7 and LLaMA3 70B 67.5; CCPM 93.1 vs DeepSeek 67B 88.5.
  - The text says V2 beats DeepSeek 67B "on almost all benchmarks". HellaSwag is an exception (84.2 vs 86.3, the lowest of the five models), and WinoGrande ties at 84.9.
- **Training cost.** Per trillion tokens on H800, DeepSeek 67B needs 300.6K GPU hours and V2 needs 172.8K, which is the basis of the 42.5% saving (p. 16). The comparison is per trillion tokens; total training compute is not stated.
- **Inference efficiency.** On one 8×H800 node, generation throughput exceeds 50K tokens/s, "5.76 times" DeepSeek 67B's maximum, and prompt throughput exceeds 100K tokens/s (p. 16).
  - The deployed V2 also uses FP8 weights and KV quantization to ~6 bits per element, so these gains are not attributable to MLA/MoE alone.
  - How the 93.3% KV reduction was computed is not shown in the main text.
- **Alignment recipe.**
  - SFT on 1.5M instances (1.2M helpfulness, 0.3M safety), 2 epochs, LR 5×10^-6 (p. 16).
  - GRPO in two stages (p. 17):
    - a reasoning reward model for code and math;
    - a weighted mix of helpful, safety and rule-based reward models.
  - Not disclosed: the RL hyperparameters (ε, β, c1–c3), reward-model data sizes, the data mixture, and the criteria for filtering "contentious content".
- **Chat results (p. 18, Tables 3–4).**
  - V2 Chat (RL): MT-Bench 8.97 vs LLaMA3 70B Instruct 8.95; AlpacaEval 2.0 LC win rate 38.9 vs Qwen1.5 72B Chat 36.6 and LLaMA3 34.4.
  - SFT→RL changes: BBH falls from 81.3 to 79.7, the "alignment tax" the paper mentions. HumanEval rises from 76.8 to 81.1 and MATH from 52.7 to 53.9.
  - IFEval is weak: 64.1 (SFT) vs LLaMA3 70B Instruct 79.7.
  - DeepSeek 67B Chat numbers are copied from its earlier report, not re-run.
- **AlignBench (p. 18, Table 5).** V2 Chat (RL) scores 7.91 overall vs GPT-4-1106-Preview 8.01, GPT-4-0613 7.53 and Qwen1.5-72B-Chat 7.19.
  - The text says it beats all models "in Chinese language understanding". That holds for the Language average (8.36, highest) but not for the 中文理解 subcolumn, where it scores 8.28 against ERNIEBot-4.0-202404 at 8.53.
  - Its reasoning average (7.45) is below both GPT-4 models.
- **Claims without numbers (p. 20–21).**
  - Using fewer than 10K SFT instances causes a "significant" IFEval decline.
  - Online RL "significantly outperforms" offline RL.
- **Limitations stated.** The model is text-only and has limited proficiency outside Chinese and English (p. 21). A 15.7B/2.4B-active DeepSeek-V2-Lite is described in Appendix B, which is not in this view (p. 4).

## Related in library

- DeepSeek LLM. Scaling Open-Source Language Models with Longtermism: the direct predecessor (DeepSeek 67B); its data pipeline, tokenizer and LR schedule are reused, and it is the baseline for every efficiency claim.
- Mixtral of Experts: V2 is compared against Mixtral 8x22B (base and Instruct), a larger sibling of the model in that paper, as the main rival open MoE.
- The Llama 3 Herd of Models: V2 is compared against LLaMA3 70B base and Instruct, its strongest dense open baseline.
- GPT-4 Technical Report: GPT-4-0613 and GPT-4-1106-Preview are the closed-model reference points on AlignBench, and GPT-4-0613 is also the judge.

## Q&A
