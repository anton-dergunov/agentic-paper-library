# DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model

type: system
read: full
family: foundation model technical report, MoE architecture
evidence: evaluated on standard English and Chinese NLP benchmarks against open-weight models (Qwen, LLaMA3, Mixtral); strength: vendor-run in internal evaluation framework
conversion: ok

## Digest

- DeepSeek-V2 is a Mixture-of-Experts (MoE) model with 236B total parameters and 21B activated parameters per token, supporting a 128K token context length (p. 1).
- It introduces Multi-head Latent Attention (MLA), which compresses the Key-Value (KV) cache into a latent vector, reducing the KV cache by 93.3% compared with DeepSeek 67B (p. 2).
- MLA's KV cache per token is $(d_{c}+d_{h}^{R})l\approx\frac{9}{2}d_{h}l$ elements, compared to the $2n_{h}d_{h}l$ elements required by standard Multi-Head Attention (MHA) (p. 8, Table 1).
- By setting the KV compression dimension $d_{c}$ to $4d_{h}$ and the decoupled per-head dimension $d_{h}^{R}$ to $\frac{d_{h}}{2}$, MLA's KV cache size is equal to Grouped-Query Attention (GQA) with 2.25 groups (p. 8, Table 1).
- For Feed-Forward Networks, it uses the DeepSeekMoE architecture with 2 shared experts and 160 routed experts, activating 6 routed experts per token (p. 12).
- The model was pre-trained on 8.1T tokens of a bilingual corpus, wherein Chinese tokens are approximately 12% more than English ones (p. 11).
- Training DeepSeek-V2 requires 172.8K GPU hours per trillion tokens, saving 42.5% of training costs compared to the 300.6K GPU hours required for the dense DeepSeek 67B baseline (p. 16).
- For inference, DeepSeek-V2 achieves a generation throughput exceeding 50K tokens per second, which is 5.76 times the maximum generation throughput of DeepSeek 67B (p. 16).
- On the MMLU benchmark (5-shot), DeepSeek-V2 scores 78.5, compared to Qwen1.5 72B at 77.2, Mixtral 8x22B at 77.6, and LLaMA 3 70B at 78.9 (p. 14, Table 2).
- On GSM8K (8-shot), DeepSeek-V2 scores 79.2, evaluated against Qwen1.5 72B at 77.9 and LLaMA 3 70B at 83.0 (p. 14, Table 2).
- On HumanEval (0-shot), DeepSeek-V2 achieves 48.8 Pass@1, compared to LLaMA 3 70B at 48.2 and Mixtral 8x22B at 53.1 (p. 14, Table 2).
- Alignment includes Supervised Fine-Tuning (SFT) on 1.5M conversational sessions, split into 1.2M instances for helpfulness and 0.3M instances for safety (p. 16).
- Reinforcement Learning (RL) employs Group Relative Policy Optimization (GRPO), saving training costs compared to traditional RL by estimating baselines from group scores rather than using a critic model (p. 17).
- On HumanEval (0-shot) for aligned models, DeepSeek-V2 Chat (RL) scores 81.1, compared to DeepSeek-V2 Chat (SFT) at 76.8 and LLaMA3 70B Instruct at 76.2 (p. 19, Table 3).
- On GSM8K (8-shot), DeepSeek-V2 Chat (RL) scores 92.2, compared to DeepSeek-V2 Chat (SFT) at 90.8 and LLaMA3 70B Instruct at 93.2 (p. 19, Table 3).
- On MT-Bench, DeepSeek-V2 Chat (RL) scores 8.97, compared to DeepSeek-V2 Chat (SFT) at 8.62 and LLaMA3 70B Instruct at 8.95 (p. 20, Table 4).
- On AlpacaEval 2.0 (length-controlled win rate), DeepSeek-V2 Chat (RL) achieves 38.9, compared to DeepSeek-V2 Chat (SFT) at 30.0 and LLaMA3 70B Instruct at 34.4 (p. 20, Table 4).
- On the Chinese AlignBench, DeepSeek-V2 Chat (RL) scores 7.91 Overall, outperforming DeepSeek-V2 Chat (SFT) at 7.74 and the baseline GPT-4-0613 at 7.53 (p. 21, Table 5).
- Disclosed: The MLA formulas, decoupled RoPE strategy, device-limited MoE routing algorithms, balance losses, pre-training hyperparameters, SFT data size, and the GRPO objective.
- Not disclosed: The specific domain mixture of the 8.1T pre-training tokens, the precise sources of the SFT sessions, and the exact pipeline details for compiler-feedback code preference data.

## Related

- DeepSeek 67B: The dense predecessor language model used heavily throughout as the primary baseline for training costs, memory usage, and evaluation.
- DeepSeekMoE (Dai et al., 2024): The specific fine-grained, shared-expert MoE architecture directly integrated into this model's feed-forward networks.
- YaRN (Peng et al., 2023): The context extension technique applied to the decoupled shared key to stretch the model's context window to 128K.
- DeepSeekMath (Shao et al., 2024): The prior work from which the authors adopted the Group Relative Policy Optimization (GRPO) reinforcement learning algorithm.
