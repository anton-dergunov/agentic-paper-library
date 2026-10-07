# DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model

type: method
read: full
family: sparse MoE decoder LLM with low-rank compressed-KV attention (MLA + DeepSeekMoE)
evidence: base model on about 27 English/Chinese/code/math benchmarks against DeepSeek 67B, Qwen1.5 72B, Mixtral 8x22B and LLaMA3 70B; chat models on the same benchmarks plus MT-Bench, AlpacaEval 2.0 and AlignBench, against open chat models and closed APIs; strength: vendor-run in an internal eval framework, single runs, no error bars; the attention ablations (MHA/GQA/MQA, MLA vs MHA) are in appendices outside this view
conversion: ok

## Digest

- **Claim.** A 236B-total / 21B-active MoE model with 128K context (p. 1). It is stronger than DeepSeek 67B while saving "42.5% of training costs", cutting KV cache by "93.3%" and raising max generation throughput "to 5.76 times" (p. 1; p. 21).
- **MLA.** Keys and values are jointly down-projected into one latent vector c^KV of size d_c, and only that vector is cached. The up-projections W^UK and W^UV can be absorbed into W^Q and W^O at inference (p. 7, Eq. 9–11). Queries are also low-rank compressed, to save training activation memory (Eq. 12–13).
- **Decoupled RoPE.** RoPE on the compressed keys would block that absorption. So extra per-head RoPE queries and one shared RoPE key of dimension d_h^R carry position, and that key is also cached. Total cache is (d_c+d_h^R)l elements (p. 8, Eq. 14–19).
- **KV cache cost.** MLA's cache is ≈ 9/2·d_h·l, "equal to GQA with only 2.25 groups" (p. 8, Table 1), with d_c = 512 and d_h^R = 64 at d_h = 128 (p. 12).
  - Table 1 labels MLA's capability "Stronger" than MHA. The supporting ablation (App. D) is not in the main text.
- **DeepSeekMoE.** Fine-grained routed experts plus always-on shared experts (p. 9, Eq. 20–22). Each MoE layer has 2 shared + 160 routed experts with intermediate dim 1536, and 6 routed experts are active per token. All FFNs except the first layer are MoE. The model has 60 layers and hidden size 5120 (p. 12).
- **Device-limited routing.** Each token's experts must sit on at most M of D devices; DeepSeek-V2 uses M=3 and D=8 (p. 9; p. 12). "M⩾3 … roughly aligned with the unrestricted top-K routing" is stated with no numbers (p. 9).
- **Load balancing.** Three auxiliary losses: expert-level, device-level and communication balance, with α1=0.003, α2=0.05 and α3=0.02 (p. 10; p. 12).
- **Token dropping.** Device-level dropping at capacity factor 1.0 during training. Tokens from about 10% of sequences are never dropped, and nothing is dropped at evaluation (p. 11; p. 12).
- **Data.** 8.1T tokens, with Chinese tokens "approximately 12% more than English ones", and the 100K BBPE tokenizer from DeepSeek 67B (p. 11). "Contentious content" is filtered out. Source mix and proportions are not disclosed.
- **Training setup.** AdamW, max LR 2.4×10^-4, step decay ×0.316 at about 60% and 90% of tokens, batch 2304→9216 over the first 225B tokens, 4K sequence length (p. 12). No tensor parallelism; 16-way pipeline, 8-way expert and ZeRO-1 data parallelism on H800s (p. 12).
- **Long context.** YaRN (s=40, target 160K) is applied to the decoupled RoPE key, then 1000 extra steps at 32K. The NIAH result up to 128K is shown only as a figure (p. 13, Fig. 4).
- **Training cost.** 172.8K H800 GPU hours per trillion tokens vs 300.6K for DeepSeek 67B, i.e. the 42.5% saving (p. 16).
- **Inference.** More than 50K tokens/s generation on one 8×H800 node, "5.76 times" DeepSeek 67B's maximum, and prompt throughput above 100K tokens/s (p. 16).
  - Deployed V2 also uses FP8 weights and KV cache quantized to 6 bits on average. The throughput and 93.3% figures therefore mix architecture with deployment optimisations.
  - The 93.3% derivation is only in Fig. 1(b).
- **Base results vs peers (p. 14–16, Table 2).**
  - MMLU 78.5 vs LLaMA3 70B 78.9, Mixtral 8x22B 77.6, Qwen1.5 72B 77.2, DeepSeek 67B 71.3.
  - MATH 43.6 vs 42.5 (Mixtral) and 42.2 (LLaMA3).
  - C-Eval 81.7 vs Qwen1.5 83.7.
  - CCPM 93.1 vs 88.5 (DeepSeek 67B).
- **Text claims more than Table 2 shows (p. 14–16, Table 2).**
  - "Significantly outperforms DeepSeek 67B on almost all benchmarks", yet HellaSwag is 84.2 vs 86.3.
  - Code and math "comparable" to Mixtral 8x22B, yet HumanEval is 48.8 vs 53.1.
  - LLaMA3 70B leads on GSM8K (83.0 vs 79.2) and MBPP (68.6 vs 66.6). The paper attributes its English gap to training on "fewer than a quarter of English tokens".
- **Alignment.**
  - SFT: 1.5M instances (1.2M helpfulness, 0.3M safety), 2 epochs, LR 5×10^-6 (p. 16).
  - RL: GRPO in two stages. First a reasoning reward model for code and math, then a weighted helpful + safety + rule reward (p. 17, Eq. 32–36).
  - The coefficients c1–c3, reward-model data sizes and RL step counts are not given.
- **Chat results (p. 18–19, Table 3).**
  - Chat (RL) HumanEval 81.1 vs Chat (SFT) 76.8 vs LLaMA3 70B Instruct 76.2.
  - MATH 53.9 vs 52.7 vs 48.5.
  - IFEval 63.8 trails LLaMA3 70B Instruct 79.7 and Mixtral 8x22B Instruct 72.1.
  - DeepSeek 67B Chat scores are copied from the earlier release, not re-run (p. 16).
- **Alignment tax.** The paper names BBH, which drops from 81.3 (SFT) to 79.7 (RL). C-Eval also drops, 80.9 → 78.0 (p. 18–19, Table 3; p. 20). It also cites gains rated by "human evaluators", but gives no human-eval numbers.
- **Open-ended chat (p. 18–19, Table 4).**
  - MT-Bench 8.97 vs LLaMA3 70B Instruct 8.95 and Chat (SFT) 8.62.
  - AlpacaEval 2.0 length-controlled win rate 38.9 vs Qwen1.5 72B Chat 36.6, LLaMA3 70B Instruct 34.4 and Chat (SFT) 30.0.
- **AlignBench (p. 18–19, Table 5).**
  - Overall 7.91 vs GPT-4-1106-Preview 8.01, ERNIEBot-4.0-202404 7.89 and GPT-4-0613 7.53. The judge is GPT-4-0613, which is itself one of the compared models.
  - Reasoning average 7.45 trails GPT-4-1106-Preview 7.73 and ERNIEBot-4.0-202404 7.61, which the paper acknowledges.
- **Claims with no numbers given:**
  - fewer than 10K SFT instances causes a "significant performance decline" on IFEval (p. 20);
  - online RL "significantly outperforms" offline RL (p. 21).

## Related in library

- DeepSeek LLM. Scaling Open-Source Language Models with Longtermism: predecessor (DeepSeek 67B). V2 reuses its tokenizer, data pipeline, LR schedule and minor architecture settings, and uses it as the main efficiency and quality baseline.
- The Llama 3 Herd of Models: LLaMA3 70B base and Instruct are the strongest dense baselines in Tables 2–4.
- GPT-4 Technical Report: GPT-4-0613 and GPT-4-1106-Preview are compared on AlignBench (Table 5), with GPT-4-0613 also acting as judge.

## Q&A
