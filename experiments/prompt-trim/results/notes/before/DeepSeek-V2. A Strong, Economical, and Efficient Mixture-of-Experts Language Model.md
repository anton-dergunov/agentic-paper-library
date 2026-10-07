# DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model

type: method
read: full
family: sparse MoE Transformer LLM with low-rank latent-KV attention (MLA plus DeepSeekMoE)
evidence: base model on about 29 English, Chinese, code and math benchmarks against DeepSeek 67B, Qwen1.5 72B, Mixtral 8x22B and LLaMA3 70B; chat models on standard benchmarks, MT-Bench, AlpacaEval 2.0 and AlignBench (GPT-4-0613 as judge); efficiency measured against DeepSeek 67B; strength: vendor-run in an internal eval framework, single runs, no ablations in the main text (attention ablations are deferred to appendices not in this view)
conversion: ok — the bold and underline marking for best and second-best in Table 2 (p. 14–16) is lost, but every value is present, so the ranking can be recomputed.

## Digest

- **Claim.** DeepSeek-V2 is a 236B-total, 21B-activated MoE model with 128K context. Against its dense predecessor DeepSeek 67B it is stronger, "saves 42.5% of training costs, reduces the KV cache by 93.3%, and boosts the maximum generation throughput to 5.76 times" (p. 1; p. 21).
- **MLA mechanism.** Keys and values are jointly compressed into one latent vector per token, of dimension d_c, via a down-projection. Only that latent is cached. The up-projections are absorbed into W^Q and W^O at inference (p. 7). Queries are also low-rank compressed, but only to save activation memory in training.
- **Decoupled RoPE.** RoPE would block that absorption. So extra per-head RoPE queries and a single shared RoPE key of dimension d_h^R carry position. The cache becomes (d_c+d_h^R)l elements per token (p. 8).
- **KV cache size.** MLA's cache is ≈ 9/2·d_h·l, "equal to GQA with only 2.25 groups". MHA needs 2n_h·d_h·l (p. 8, Table 1).
- **MLA vs MHA quality.** Table 1 rates MLA "Stronger" than MHA, but only qualitatively. The supporting MHA, GQA and MQA ablations are in Appendix D, not in the main text.
- **DeepSeekMoE.** Fine-grained routed experts plus always-on shared experts, with softmax affinity and top-K gating (p. 9).
- **Device-limited routing.** Each token's experts are drawn from at most M devices. M≥3 is said to "roughly" match unrestricted top-K, with no numbers given (p. 9).
- **Load balance and token dropping.** Three auxiliary losses balance experts, devices and communication (p. 10). Device-level token dropping uses capacity factor 1.0, and about 10% of sequences are never dropped (p. 11).
- **Configuration.**
  - 60 layers, hidden size 5120; n_h=128 heads, d_h=128; d_c=512, d_c'=1536, d_h^R=64 (p. 12).
  - Each MoE layer has 2 shared and 160 routed experts, 6 activated, expert width 1536. D=8, M=3; α1=0.003, α2=0.05, α3=0.02 (p. 12).
- **Data and pretraining.**
  - 8.1T tokens, with Chinese tokens about 12% more than English; same 100K BBPE tokenizer as DeepSeek 67B (p. 11).
  - "Contentious content" is filtered out, without detail.
  - AdamW, max LR 2.4×10^-4 with step decay ×0.316 at about 60% and 90% of tokens. Batch size grows 2304→9216 over the first 225B tokens; sequence length 4K (p. 12).
- **Long context.** YaRN is applied only to the decoupled RoPE key: s=40, α=1, β=32, target 160K, √t=0.0707 ln s+1. Then 1000 steps at 32K length with batch 576. 128K support rests only on the NIAH figure (p. 13, Fig. 4).
- **Base model results (Table 2, p. 14–16).** Scores are DeepSeek-V2 vs LLaMA3 70B / Mixtral 8x22B / Qwen1.5 72B / DeepSeek 67B.
  - MMLU: 78.5 vs 78.9 / 77.6 / 77.2 / 71.3.
  - MATH: 43.6 vs 42.2 / 42.5 / 41.4 / 18.7.
  - C-Eval: 81.7 vs 67.5 / 59.6 / 83.7 / 66.1.
  - Pile BPB: 0.606 vs LLaMA3 0.602.
- **Where Table 2 does not back the text.**
  - "Strongest open-source MoE": Mixtral 8x22B is ahead on HumanEval (53.1 vs 48.8), RACE-High (56.7 vs 52.7), CRUXEval-O (52.8 vs 49.8), TriviaQA, NaturalQuestions and HellaSwag (p. 14–16, Table 2).
  - "Outperforms DeepSeek 67B on almost all benchmarks": HellaSwag is lower (84.2 vs 86.3) (p. 14–16, Table 2).
- **Training cost.** 172.8K H800 GPU hours per trillion tokens vs 300.6K for DeepSeek 67B (p. 16).
- **Inference throughput.** On 8 H800s, generation exceeds 50K tokens/s, 5.76× DeepSeek 67B's maximum; prompt input exceeds 100K tokens/s (p. 16).
  - This deployment also uses FP8 weights and KV quantization to about 6 bits, so the gain is not attributable to MLA and MoE alone.
  - The main text does not derive the 93.3% KV-cache figure.
- **Alignment recipe.**
  - SFT: 1.5M instances (1.2M helpfulness, 0.3M safety), 2 epochs, LR 5×10^-6 (p. 16).
  - RL uses GRPO, which has no critic and takes its baseline from group scores. Stage one optimises against a reasoning reward model; stage two combines helpful, safety and rule-based rewards (p. 17).
  - Not disclosed: the reward coefficients c1–c3, ε, β, and RL data sizes.
- **Chat results (Table 3, p. 18–19).** DeepSeek-V2 Chat (RL) vs LLaMA3 70B Inst.:
  - HumanEval: 81.1 vs 76.2.
  - MATH: 53.9 vs 48.5.
  - LiveCodeBench: 32.5 vs 30.5.
  - It trails on IFEval (63.8 vs 79.7) and MMLU (77.8 vs 80.3).
  - DeepSeek 67B Chat scores are copied from the earlier report, not re-run (p. 16).
- **Alignment tax from RL.** RL lowers some scores relative to SFT: BBH 79.7 vs 81.3 and C-Eval 78.0 vs 80.9 (p. 18–19, Table 3). The paper acknowledges this as "alignment tax" (p. 20).
- **Open-ended English (Table 4, p. 18–19).** MT-Bench 8.97 vs LLaMA3 70B Inst. 8.95 and SFT 8.62. AlpacaEval 2.0 length-controlled win rate 38.9 vs Qwen1.5 72B Chat 36.6, LLaMA3 34.4 and SFT 30.0.
- **AlignBench (Table 5, p. 18–19).**
  - RL scores 7.91 overall, vs GPT-4-1106-Preview 8.01, ERNIEBot-4.0-202404 7.89 and GPT-4-0613 7.53.
  - The text says RL "outperforms all models" in Chinese language understanding. That holds for Language Avg. (8.36, highest), but not for the Chi. sub-column, where ERNIEBot-4.0-202404 has 8.53 vs 8.28.
- **Discussion claims without numbers (p. 19–21).** Fewer than 10K SFT instances causes a "significant" IFEval drop. Online RL "significantly outperforms" offline RL.
- **Limitations stated.** The model is text-only. Data is mainly Chinese and English, so other languages may be weak (p. 21).

## Related in library

- DeepSeek LLM. Scaling Open-Source Language Models with Longtermism: the predecessor DeepSeek 67B is the main baseline; V2 reuses its data pipeline, tokenizer, LR schedule and other architectural details.
- Mixtral of Experts: Mixtral 8x22B (a later model than the 8x7B in that paper) is the main open MoE baseline in the base and chat comparisons.
- The Llama 3 Herd of Models: LLaMA3 70B and 70B Instruct are compared throughout; V2 concedes a slight English gap, attributed to fewer than a quarter of the English training tokens.
- GPT-4 Technical Report: GPT-4-0613 and GPT-4-1106-Preview are reference points on AlignBench, and GPT-4-0613 is the judge.

## Q&A
