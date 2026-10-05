# DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model

type: system
read: full
family: vendor technical report for an open-weight MoE LLM (new attention variant, sparse FFN, SFT and RL post-training)
evidence: about 28 English/Chinese/code/math benchmarks plus MT-Bench, AlpacaEval 2.0 and AlignBench, against DeepSeek 67B, Qwen1.5 72B, Mixtral 8x22B and LLaMA3 70B, with efficiency compared only against the authors' own DeepSeek 67B; strength: vendor-run in an internal evaluation framework, single runs with no variance, no ablations in the available text (they sit in the missing Appendix D), and several claims stated without numbers
conversion: body ends after Section 5, so the References and Appendices A–G listed in the Contents (p. 2) are missing, including V2-Lite details (B), the MHA/GQA/MQA and MLA-vs-MHA ablations (D), data debiasing (E) and extra math/code evaluations (F). Figures 1, 2, 3 and 4 are placeholders only, so the MMLU-vs-parameters plot, the efficiency bars and the NIAH results cannot be checked. Bold/underline best and second-best marks in Table 2 and the underlining of Chinese benchmarks in 3.2.1 are lost (pp. 13–16). The title is duplicated with a stray `\reportnumber 001` (p. 1). Equations and the cell values of Tables 1–5 appear intact.

## Digest

- **Model size:** 236B total parameters, 21B activated per token, 128K context; the predecessor DeepSeek 67B is dense with 67B parameters (p. 1; pp. 14–16, Table 2). Checkpoints are released, as is a smaller DeepSeek-V2-Lite with 15.7B total and 2.4B activated parameters, whose details are in the missing Appendix B (pp. 4–6).
- **MLA mechanism:** Multi-head Latent Attention jointly compresses keys and values into one latent c^KV of dimension d_c, and only that latent is cached. The up-projections W^UK and W^UV are absorbed into W^Q and W^O at inference, and queries are also low-rank compressed (dimension d_c′) to cut training activation memory (p. 7).
- **Decoupled RoPE:** RoPE on compressed keys would block that absorption, so extra per-head queries and one shared key of dimension d_h^R carry the positions and are concatenated to the compressed parts (p. 8).
- **KV cache size:** MLA caches (d_c + d_h^R)·l ≈ 9/2·d_h·l elements per token, against 2·n_h·d_h·l for MHA, 2·n_g·d_h·l for GQA and 2·d_h·l for MQA; the paper equates this to GQA with only 2.25 groups (p. 8, Table 1).
- **Capability claim for MLA:** Table 1 rates MLA "Stronger" than MHA ("Strong"), GQA ("Moderate") and MQA ("Weak"), but these are qualitative labels; the supporting ablation is in Appendix D, absent from this text (p. 6; p. 8, Table 1).
- **FFN:** DeepSeekMoE (fine-grained routed experts plus always-on shared experts) replaces every FFN except the first layer. Each MoE layer has 2 shared and 160 routed experts, 6 routed experts active per token, expert hidden dimension 1536 (p. 9; p. 12).
- **Routing additions for expert parallelism:** device-limited routing sends each token's experts to at most M devices, with M ≥ 3 said to be "roughly aligned" with unrestricted top-K (no numbers given). Three auxiliary losses balance expert load, device load and communication, with α1 = 0.003, α2 = 0.05, α3 = 0.02, D = 8, M = 3 (p. 9; p. 10; p. 12).
- **Token dropping:** during training, the lowest-affinity tokens on each device are dropped down to a capacity factor of 1.0, while approximately 10% of sequences are never dropped; no tokens are dropped at evaluation (p. 11; p. 12).
- **Architecture hyper-parameters:** 60 layers, hidden dimension 5120, n_h = 128, d_h = 128, d_c = 512, d_c′ = 1536, d_h^R = 64, init std 0.006, with extra RMS Norm and scaling factors at the width bottlenecks (p. 12).
- **Pre-training data:** 8.1T tokens, with Chinese tokens approximately 12% more than English ones, and a BBPE tokenizer with 100K vocabulary carried over from DeepSeek 67B. Sources, composition and filtering rules are not disclosed beyond "improved" cleaning and removal of "contentious content" (pp. 11–12).
- **Training recipe:**
  - AdamW with β1 = 0.9, β2 = 0.95, weight decay 0.1, and gradient clipping at 1.0.
  - Maximum learning rate 2.4×10^-4 with 2K warmup steps, multiplied by 0.316 at about 60% and again at about 90% of tokens.
  - Batch size raised from 2304 to 9216 over the first 225B tokens, with maximum sequence length 4K.
  - 16-way pipeline parallelism, 8-way expert parallelism and ZeRO-1 on H800 GPUs; cluster size and total GPU hours are not stated (p. 12).
- **Long context:** YaRN is applied to the shared RoPE key (s = 40, α = 1, β = 32, target length 160K), followed by 1000 extra steps at sequence length 32K with batch size 576, against a default 4K window. The only evidence for 128K is the NIAH plot in Figure 4, which is missing (p. 13).
- **Training cost:** 172.8K GPU hours per trillion tokens against 300.6K for DeepSeek 67B on the same H800 cluster, stated as a 42.5% saving (p. 16).
- **Inference:** generation throughput exceeds 50K tokens per second on one node with 8 H800 GPUs, stated as 5.76 times DeepSeek 67B's maximum, and prompt input throughput exceeds 100K tokens per second. This is measured after FP8 conversion and KV-cache quantization to 6 bits per element on average, and the report does not say whether the 67B baseline had the same treatment, so MLA's own share is not isolated (p. 16).
- **KV cache reduction:** the 93.3% reduction versus DeepSeek 67B appears only as a headline; its derivation is in Figure 1(b), which is missing (p. 1; p. 21).
- **Base model results** (pp. 14–16, Table 2; all models run in the authors' framework):
  - MMLU 78.5, against LLaMA3 70B 78.9, Mixtral 8x22B 77.6, Qwen1.5 72B 77.2 and DeepSeek 67B 71.3.
  - MATH 43.6, against Mixtral 42.5, LLaMA3 42.2, Qwen 41.4 and DeepSeek 67B 18.7.
  - C-Eval 81.7, against Qwen 83.7 and LLaMA3 67.5; CMMLU 84.0, against Qwen 84.3.
  - HumanEval 48.8, against Mixtral 53.1 and LLaMA3 48.2.
  - HellaSwag 84.2, below DeepSeek 67B at 86.3 and LLaMA3 at 87.9.
  - Qwen's CHID score is blank because of a tokenizer error in the authors' framework.
- **Position versus LLaMA3 70B:** the authors concede a "slight gap in basic English capabilities" and attribute it to training on "fewer than a quarter of English tokens"; the "top-tier among open-source models" claim rests on activated-parameter efficiency and Chinese benchmarks (pp. 14–16).
- **Post-training:**
  - SFT uses 1.5M instances (1.2M helpfulness, 0.3M safety), 2 epochs, learning rate 5×10^-6 (p. 16).
  - RL uses GRPO, which has no critic and takes its baseline from group rewards, in two stages: reasoning alignment with a code/math reward model, then preference alignment with helpful, safety and rule-based rewards.
  - Reward models are initialised from the SFT chat model; ε, β, c1–c3, group size and preference-data size are not disclosed (pp. 16–18).
- **Chat results** (pp. 18–19, Tables 3–4):
  - RL versus SFT: HumanEval 81.1 against 76.8, LiveCodeBench 32.5 against 28.7 (LLaMA3 70B Inst. 30.5), MATH 53.9 against 52.7 (LLaMA3 48.5).
  - IFEval 63.8 (RL) and 64.1 (SFT), well below LLaMA3 at 79.7 and Mixtral at 72.1.
  - MT-Bench 8.97 (RL), against LLaMA3 8.95 and SFT 8.62.
  - AlpacaEval 2.0 length-controlled win rate 38.9 (RL), against Qwen1.5 72B Chat 36.6, LLaMA3 34.4 and SFT 30.0.
  - DeepSeek 67B Chat numbers are copied from the earlier release rather than rerun (p. 16).
- **AlignBench** (rated by GPT-4-0613): overall 7.91 for Chat (RL), against GPT-4-1106-Preview 8.01, ERNIEBot-4.0-202404 7.89, GPT-4-0613 7.53 and Qwen1.5-72B-Chat 7.19. Its reasoning average of 7.45 trails GPT-4-1106-Preview at 7.73. Some rows are taken from the original papers and some rerun by the authors (pp. 18–19, Table 5).
- **Unquantified observations:**
  - An "alignment tax" from RL is acknowledged; it is visible in BBH 79.7 (RL) against 81.3 (SFT) and C-Eval 78.0 against 80.9 (pp. 18–19, Table 3; p. 20).
  - Fewer than 10K SFT instances is said to cause a "significant" IFEval decline, with no numbers (p. 20).
  - Online RL is said to "significantly" outperform offline, with no numbers (p. 21).

## Related

- DeepSeek 67B (DeepSeek-AI, 2024): the dense predecessor and sole efficiency baseline; tokenizer, data pipeline stages, LR schedule and minor architecture settings are inherited from it.
- DeepSeekMoE (Dai et al., 2024): the FFN architecture adopted as-is; this report adds device-limited routing, two further balance losses and token dropping.
- GShard (Lepikhin et al., 2021): the conventional MoE that DeepSeekMoE is claimed to beat "by a large margin" (no numbers here); also the source of expert parallelism and the expert-level balance loss.
- MHA (Vaswani et al., 2017), GQA (Ainslie et al., 2023), MQA (Shazeer, 2019): the KV-cache baselines for MLA; the paper claims MLA beats MHA while caching less than GQA, with the ablation in the missing Appendix D.
- RoPE (Su et al., 2024): incompatible with low-rank KV compression as-is, which motivates the decoupled RoPE design.
- YaRN (Peng et al., 2023): used for the 4K-to-128K context extension, with a modified length-scaling factor.
- DeepSeekMath / GRPO (Shao et al., 2024): the source of the critic-free RL algorithm used for the Chat (RL) model.
- Riquelme et al. (2021): inspiration for dropping the lowest-affinity tokens to meet a device compute budget.
- LLaMA3 70B (AI@Meta, 2024): the strongest open-weight comparison; ahead on most English benchmarks and IFEval, behind on Chinese.
- Mixtral 8x22B (Mistral, 2024): the open MoE comparison (39B activated, 141B total); roughly matched on English, code and math, far behind on Chinese.
- Qwen1.5 72B (Bai et al., 2023): the bilingual comparison; ahead on C-Eval and CMMLU, behind on most English, code and math benchmarks.
- Young et al. (2024), Zhou et al. (2024): they claim fewer than 10K SFT instances suffice; this report contradicts that on IFEval, without numbers.
- Ouyang et al. (2022): the source of the "alignment tax" notion that the authors report observing after RL.
- Hu et al. (2024): cited as prior work that mixes SFT data into pre-training, which the authors say DeepSeek-V2 never did.
