# DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model

type: method
read: full
family: MoE language model with low-rank KV attention and fine-grained expert routing
evidence: comprehensive evaluation on 20+ benchmarks (MMLU, C-Eval, CMMLU, TriviaQA, HellaSwag, ARC, BBH, GSM8K, MATH, HumanEval, MBPP, CRUXEval, AGIEval, MT-Bench, AlpacaEval 2.0, AlignBench, etc.) compared to DeepSeek 67B, Qwen1.5 72B, Mixtral 8x22B, LLaMA3 70B in author's internal evaluation framework; strength: vendor-run, no independent replication, but comprehensive across English and Chinese with dense baseline comparisons

conversion: ok

## Digest

- **Model scale**: 236B total parameters, 21B activated per token, 128K context length, 60 layers, hidden dimension 5120, 128 attention heads per layer (p. 1, p. 12)
- **Multi-Head Latent Attention (MLA)**: low-rank joint compression of keys and values into latent vector $\mathbf{c}^{KV}_t$ with dimension $d_c$; KV cache reduced from $2n_h d_h l$ (MHA) to $(d_c + d_h^R)l \approx \frac{9}{2}d_h l$ elements per token, equal to GQA with only 2.25 groups but stronger performance than MHA (p. 6–8, Table 1)
- **Decoupled RoPE**: separate position embeddings for compressed and latent attention dimensions to enable $W^{UK}$ absorption during inference without recomputing keys (p. 8)
- **DeepSeekMoE**: 2 shared experts + 160 routed experts per layer; 6 routed experts activated per token; fine-grained expert segmentation with isolation of shared experts (p. 9, p. 12); device-limited routing restricting each token to at most $M=3$ devices to control communication overhead (p. 9)
- **Load balancing**: three auxiliary losses—expert-level, device-level, and communication balance—with coefficients $\alpha_1=0.003$, $\alpha_2=0.05$, $\alpha_3=0.02$; token-dropping strategy during training to mitigate unbalanced load (p. 10–11)
- **Pre-training data**: 8.1T tokens, 12% more Chinese tokens than English, processed with BBPE tokenizer (100K vocab); data quality improved over DeepSeek 67B through recovery of mistakenly deleted data and enhanced filtering (p. 11)
- **Training setup**: AdamW optimizer with $\beta_1=0.9$, $\beta_2=0.95$, weight decay 0.1, max learning rate $2.4 \times 10^{-4}$; batch size 2304–9216; max sequence length 4K; infrastructure: 16-way pipeline parallelism, 8-way expert parallelism, ZeRO-1 data parallelism on H800 GPU cluster (p. 12)
- **Long context extension**: YaRN applied to decoupled shared key after pre-training; additional 1000 training steps with 32K sequence length to extend from 4K to 128K context robustly (p. 13, Figure 4: NIAH tests show consistent performance across all context lengths)
- **Training efficiency**: 172.8K GPU hours per trillion tokens vs. 300.6K for DeepSeek 67B, saving **42.5% training costs** (p. 16)
- **Inference efficiency**: generation throughput **5.76x** that of DeepSeek 67B; 50K tokens/second generation, 100K tokens/second prompt input on single 8-GPU H800 node; **93.3% KV cache reduction** via MLA and KV cache quantization to 6 bits (p. 1, p. 16)
- **Supervised fine-tuning**: 1.5M instruction instances (1.2M helpfulness, 0.3M safety); 2 training epochs, learning rate $5 \times 10^{-6}$ (p. 16)
- **Reinforcement learning**: GRPO (Group Relative Policy Optimization) with group-based advantage estimation; two-stage strategy—first reasoning alignment on code/math via $RM_{reasoning}$, then human preference alignment via multi-reward combination $c_1 \cdot RM_{helpful} + c_2 \cdot RM_{safety} + c_3 \cdot RM_{rule}$ (p. 17–18)
- **Evaluation results—base model** (Table 2, p. 14): MMLU 78.5% (vs Mixtral 77.6%, LLaMA3 78.9%), MATH 43.6% (vs Mixtral 42.5%, LLaMA3 42.2%), HumanEval 48.8% (vs Mixtral 53.1%, LLaMA3 48.2%); outperforms DeepSeek 67B (71.3% MMLU) across nearly all benchmarks
- **Chat model performance** (Table 4, p. 19): DeepSeek-V2 Chat (RL) achieves **38.9 length-controlled win rate on AlpacaEval 2.0**, **8.97 on MT-Bench**, compared to LLaMA3 70B Instruct (34.4%, 8.95); on AlignBench Chinese tasks (Table 5, p. 20): **7.91 overall score**, outperforming GPT-4-0613 (7.53), second only to GPT-4-1106-Preview (8.01)
- **Not disclosed**: full training time details, complete ablation on MLA design choices beyond appendix comparisons, exact composition of the 8.1T token corpus by source, detailed analysis of failure modes or dataset contamination risks

## Related

- **DeepSeek 67B** (DeepSeek-AI, 2024): previous dense baseline; V2 achieves stronger performance with fewer activated parameters and 42.5% lower training cost
- **Mixtral 8x22B** (Mistral, 2024): competing MoE architecture with 39B activated parameters; V2 is comparable or superior on most benchmarks despite 21B activations
- **LLaMA3 70B** (Meta, 2024): dense model trained on more English data; V2 matches or exceeds on code/math with fewer tokens and is overwhelmingly better on Chinese
- **GShard, MoE transformers** (Lepikhin et al., 2021): conventional MoE architectures; DeepSeekMoE fine-grained segmentation and shared expert isolation outperform
- **Grouped-Query Attention, Multi-Query Attention** (Ainslie et al., 2023; Shazeer, 2019): prior KV cache reduction methods; MLA achieves lower cache than GQA-2.25 with MHA-level performance
- **YaRN** (Peng et al., 2023): rotary position embedding scaling applied to extend context window
- **GRPO** (Shao et al., 2024): RL algorithm adopted to avoid critic model overhead in preference alignment stage
