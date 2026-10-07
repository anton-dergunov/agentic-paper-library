# Phi-4 Technical Report

type: method
read: full
family: small dense decoder-only LLM trained on mostly synthetic data, with token-level preference post-training (Phi series)
evidence: OpenAI simple-evals (MMLU, GPQA, MATH, HumanEval, MGSM, SimpleQA, DROP), plus MMLU-Pro, HumanEval+, ArenaHard, LiveBench, IFEval, internal PhiBench, HELMET long-context, November 2024 AMC-10/12, and in-house RAI benchmarks; compared against phi-3, Qwen 2.5 14B/72B instruct, GPT-4o-mini, Llama-3.3-70B and GPT-4o; strength: vendor-run, single runs with no variance (except AMC), data-mixture ablations at 7B/13B scale, post-training ablation on one model, internal benchmark used both for tuning and for reporting
conversion: Figure 3's colour-coded pivotal-token example is flattened into many repeated tokens with figure placeholders, so the illustration cannot be read (p. 12–14); the Figure 4 PTS pseudocode is interleaved with [figure] placeholders but stays readable (p. 12–14); a footnote is fused into Table 1's Llama-3.3 MATH cell ("66.311 1 …"), and the value is recoverable as 66.3 (p. 1–3); the Table 10 bold marks only phi-4's column "for readability" (p. 19); Section 4.5 cites "Table [1]" where Table 9 is meant (p. 16).

## Digest

- **Claim.** phi-4 is a 14B model built on a recipe centred on data quality, with synthetic data used throughout training.
  - It "substantially surpasses" its teacher GPT-4o on STEM QA, which the paper takes as evidence that its methods go beyond distillation.
  - The architecture changes little from phi-3-medium (p. 1).
- **Architecture and pretraining** (p. 7):
  - Changes from phi-3-medium: the tiktoken tokenizer with a padded vocabulary of 100,352, and full attention over a 4K context in place of phi-3-medium's 2K sliding window.
  - Pretraining runs for about 10T tokens, with peak LR 0.0003, weight decay 0.1 and global batch 5760.
- **Midtraining** (p. 10):
  - Extends context from 4K to 16K over 250B tokens.
  - Raises the RoPE base to 250K and cuts the maximum LR by 10x.
  - The mix is 30% long-context data and 70% recall tokens from pretraining.
  - Naturally long documents beat artificially padded ones in their ablations.
- **Synthetic data** (p. 5):
  - 50 dataset types, about 400B unweighted tokens.
  - Generation techniques: seed curation from filtered web, code and book passages; questions filtered by majority-vote agreement, dropping the all-agree and all-disagree cases; question-answer extraction from deduction chains; rewriting; self-revision against rubrics; instruction reversal for code; execution-based validation.
  - The generating models are not specified.
- **Pretraining mixture** (p. 9, Table 5). Each line gives share of training, unique tokens and epochs:

  | Source | Share | Unique tokens | Epochs |
  |---|---|---|---|
  | Synthetic | 40% | 290B | 13.8 |
  | Web | 15% | 1.3T | 1.2 |
  | Web rewrites | 15% | 290B | 5.2 |
  | Code | 20% | 820B | 2.4 |
  | Acquired sources | 10% | 580B | 1.7 |

- **Data ablations** (p. 8, Figure 2; Table 3).
  - In phase-2 runs, 12 epochs over synthetic data beat 4 epochs plus fresh web tokens on MMLU (shown in a figure only).
  - A 13B model trained only on synthetic data reaches TQA −14.8 relative to phi-3-medium.
  - Adding web rewrites brings that to −7.7, while most other benchmarks improve.
- **Mixture ablations** (1T tokens at 7B scale; p. 9, Table 4). All values are averages relative to the final mixture:
  - synthetic-heavy: +0.8
  - synthetic + web rewrites: +0.4
  - uniform allocation: −2.2

  The synthetic-heavy mixes scored slightly higher. The authors kept web data for knowledge (TQA) and say the gap mostly closes after post-training, but show no numbers for that.
- **Post-training** (p. 12):
  - SFT on about 8B tokens at LR 10^-6, including multilingual data in 40 languages.
  - DPO round 1 uses Pivotal Token Search pairs (Table 7).
  - DPO round 2 is judge-guided, with about 850k pairs labelled by GPT-4o from GPT-4o, GPT-4t and phi-4 responses (Table 8).
- **Pivotal Token Search (PTS)** (p. 14):
  - A pivotal token is one whose generation shifts p(success) by at least p_gap. p(success) is estimated by sampling rollouts and checking them with an oracle (tests or ground truth).
  - The method recursively bisects a solution to find these tokens.
  - DPO pairs are then single-token accepted/rejected continuations of the shared prefix.
  - It is applied only to questions with 0.2 ≤ p(success) ≤ 0.8.
  - The search is not guaranteed to find all pivotal tokens unless success is near-monotone over the solution.
  - The p_gap value and the rollout counts used in training are not given. Figure 3 uses N=529 and boxes changes ≥ 0.2.
- **Main results against Qwen 2.5 14B instruct and GPT-4o** (p. 1–3, Table 1):

  | Benchmark | phi-4 | Qwen 2.5 14B | GPT-4o |
  |---|---|---|---|
  | GPQA | 56.1 | 42.9 | 50.6 |
  | MATH | 80.4 | 75.6 | 74.6 |
  | MMLU | 84.8 | 79.9 | 88.1 |
  | HumanEval | 82.6 | 72.1 | 90.6 |

- **Weak benchmarks** (p. 1–3, Table 1). phi-4 trails Qwen 2.5 14B on:
  - IFEval: 63.0 vs 78.7
  - DROP: 75.5 vs 85.5
  - SimpleQA: 3.0 vs 5.4

  The paper reports winning 9 of 12 benchmarks against Qwen 2.5 14B, which agrees with Table 1 when PhiBench is excluded (p. 18).
- **Overclaim on Llama-3.1-405B.** The introduction says phi-4 "meets or exceeds" Llama-3.1-405B on many reasoning benchmarks (p. 1). No Llama-3.1-405B number appears in any table.
- **Llama-3.3-70B scores** are lower under simple-evals than Meta's own figures. Meta reports 77 on MATH and 88 on HumanEval, against the paper's 66.3 and 78.9 (p. 1–3, Table 1 footnote).
- **Contamination checks** (p. 3, Figure 1):
  - The paper relies on fresh November 2024 AMC-10/12 tests (100 runs, t=0.5) to argue its MATH score does not come from contamination.
  - phi-4's AMC score appears only in the figure.
  - QwQ-32B-Preview averages 124.5 of 150 on the same tests but uses 4X more tokens than phi-4.
  - Decontamination details are in an appendix not included here.
- **Post-training ablation** (p. 16, Table 9). Values go from SFT → PTS-DPO → judge-DPO only → both stages:
  - GPQA: 47.3 → 53.6 → 52.4 → 56.1
  - MATH: 77.1 → 80.5 → 77.6 → 80.4
  - ArenaHard: 56.7 → 66.5 → 69.8 → 75.4

  Two drops are not discussed: DROP falls from 86.1 after stage 1 to 75.5 in the final model, and IFEval falls from 66.2 after SFT to 63.0.
- **Hallucination trade-off.** Hallucination-mitigation data makes the model decline SimpleQA questions more often. The base model scores higher on SimpleQA F1 than the final model, and the authors accept this as better behaviour (p. 16, Figure 6).
- **Long context** (HELMET at 16K; p. 10, Table 6):
  - ICL: phi-4 77.0, Qwen-2.5-14B 67.6, GPT-4o 85.6.
  - Re-rank: phi-4 54.4, Llama-3.3-70B 63.3.
- **Safety** (p. 19, Table 10):
  - Jailbreak DR1: phi-4 0.073 vs phi-3 14B 0.111.
  - 3P content harms DR1: phi-4 0.121 vs phi-3 14B 0.251.
  - Harmful content continuation DR3: phi-4 is worst in the table at 0.036 (phi-3 14B 0.01). The text does not discuss this.
- **Not disclosed:** training compute and hardware; which generator models produced which data; synthetic token counts per type. PhiBench is internal and was used to guide data mixtures and hyperparameters, so its reported scores are not independent. Stated weaknesses include factual hallucination, strict instruction following, and verbosity (p. 20).

## Related in library

- Phi-3 Technical Report. A Highly Capable Language Model Locally on Your Phone: direct predecessor; phi-4 follows the phi-3-medium architecture and reports gains relative to it.
- The Llama 3 Herd of Models: source cited for the RoPE base of 250K; Llama-3 8B is compared in the RAI benchmarks.
- GPT-4 Technical Report: GPT-4 family as the teacher model that phi-4 claims to surpass on STEM QA.
- Mistral 7B: Mistral-7B v0.1/v0.2 compared in the RAI safety benchmarks.

## Q&A
