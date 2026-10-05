# DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model

type: system
read: full
family: open-source MoE foundation model
evidence: internal framework evaluation across standard English/Chinese NLP benchmarks, math, code, and LLM-as-a-judge benchmarks (MT-Bench, AlpacaEval 2.0, AlignBench) against open and proprietary models; strength: vendor-run
conversion: ok (appendices B–G listed in TOC are omitted from the document body)

## Digest

- DeepSeek-V2 is a Mixture-of-Experts Transformer with 236B total parameters and 21B activated parameters per token across 60 layers (hidden dimension 5120), natively trained on 4K context and extended to 128K context (p. 1, p. 12).
- Multi-Head Latent Attention (MLA) jointly compresses keys and values into latent vector $\mathbf{c}_t^{KV} \in \mathbb{R}^{d_c}$ ($d_c = 512 = 4d_h$) and queries into $\mathbf{c}_t^Q \in \mathbb{R}^{d_c'}$ ($d_c'=1536$), absorbing projection matrices into $W^Q$ and $W^O$ at inference (p. 6–7, p. 12).
- Decoupled RoPE applies rotary embeddings to a separate multi-head query and shared key of dimension $d_h^R = 64 = d_h / 2$, allowing KV cache compression while retaining relative position encodings (p. 8, p. 12).
- MLA reduces per-token KV cache to $(d_c + d_h^R)l \approx \frac{9}{2}d_h l$ (equivalent to GQA with 2.25 groups), cutting KV cache by 93.3% relative to dense DeepSeek 67B (p. 1, p. 8, Table 1).
- DeepSeekMoE replaces FFNs from layer 2 onwards with 2 shared experts and 160 routed experts (intermediate dimension 1536), activating 6 routed experts per token alongside shared experts (p. 9, p. 12).
- Device-limited routing constrains the 6 routed experts per token to at most $M=3$ devices out of $D=8$ expert-parallel devices to bound communication overheads (p. 9–10, p. 12).
- Training uses three auxiliary balance losses: expert-level ($\alpha_1=0.003$), device-level ($\alpha_2=0.05$), and communication balance ($\alpha_3=0.02$), combined with device-level token dropping (capacity factor 1.0, preserving ~10% of sequences) (p. 10–12).
- Pre-training data totals 8.1T tokens (Chinese tokens ~12% more than English), tokenized with a 100K BBPE vocabulary; the exact data mix and sources are not disclosed (p. 11).
- Training uses AdamW (max lr $2.4\times 10^{-4}$ with warmup and step-decay at 60% and 90% tokens) with batch size expanding from 2304 to 9216 over the first 225B tokens; no SFT data was included in pre-training (p. 12, p. 14).
- Long context is scaled from 4K to 128K using YaRN applied to decoupled key $\mathbf{k}_t^R$ with scale $s=40$, trained for 1000 steps at 32K context length (batch size 576 sequences) (p. 13).
- DeepSeek-V2 required 172.8K GPU hours per 1T tokens on H800 GPUs, saving 42.5% training cost compared to 300.6K GPU hours per 1T tokens for dense DeepSeek 67B (p. 16).
- Inference with FP8 weights and 6-bit average KV cache quantization yields generation throughput exceeding 50K tokens/s on an 8 $\times$ H800 node (5.76 times DeepSeek 67B) and prompt input throughput exceeding 100K tokens/s (p. 16).
- On MMLU (5-shot), base DeepSeek-V2 scores 78.5, compared to 71.3 for DeepSeek 67B, 77.2 for Qwen1.5 72B, 77.6 for Mixtral 8x22B, and 78.9 for LLaMA 3 70B (p. 14, Table 2).
- On GSM8K (8-shot) and MATH (4-shot), base DeepSeek-V2 scores 79.2 and 43.6, compared to 63.4 and 18.7 for DeepSeek 67B, and 83.0 and 42.2 for LLaMA 3 70B (p. 14, Table 2).
- SFT alignment uses 1.5M conversational sessions (1.2M helpfulness, 0.3M safety) for 2 epochs; the authors note reducing SFT below 10K instances causes a significant drop on IFEval (p. 16, p. 20).
- Post-training uses Group Relative Policy Optimization (GRPO) without a critic model in two stages: reasoning alignment (math/code RM) followed by human preference alignment (helpful, safety, and rule-based RMs) (p. 16–17).
- DeepSeek-V2 Chat (RL) scores 81.1 on HumanEval (0-shot) and 92.2 on GSM8K (8-shot), compared to 76.8 and 90.8 for DeepSeek-V2 Chat (SFT) and 76.2 and 93.2 for LLaMA 3 70B Instruct (p. 18, Table 3).
- On MT-Bench and AlpacaEval 2.0 (length-controlled win rate), DeepSeek-V2 Chat (RL) reaches 8.97 and 38.9, compared to 8.62 and 30.0 for DeepSeek-V2 Chat (SFT), and 8.95 and 34.4 for LLaMA 3 70B Instruct (p. 19, Table 4).
- On AlignBench, DeepSeek-V2 Chat (RL) scores 7.91 overall, surpassing Qwen1.5-72B-Chat (7.19), ERNIEBot-4.0-202404 (7.89), and GPT-4-0613 (7.53), while trailing GPT-4-1106-Preview (8.01) (p. 19, Table 5).

## Related

- DeepSeek 67B (DeepSeek-AI, 2024): previous dense baseline which DeepSeek-V2 outperforms while saving 42.5% training FLOPs/hours and 93.3% KV cache.
- DeepSeekMoE (Dai et al., 2024): architectural predecessor that introduced fine-grained routed experts and shared expert isolation, adapted here at 236B scale.
- DeepSeekMath (Shao et al., 2024): introduced Group Relative Policy Optimization (GRPO), used here for critic-free two-stage RL alignment.
- YaRN (Peng et al., 2023): context window extension method applied specifically to MLA's decoupled RoPE keys to scale context to 128K.
- LLaMA 3 70B (AI@Meta, 2024) and Mixtral 8x22B (Mistral, 2024): primary dense and sparse open-weight competitors evaluated across general, code, and math benchmarks.
