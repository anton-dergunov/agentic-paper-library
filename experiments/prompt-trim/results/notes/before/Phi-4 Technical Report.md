# Phi-4 Technical Report

type: method
read: full
family: synthetic-data-centric small dense LLM (Phi series), plus token-level DPO
evidence: simple-evals and internal-framework academic benchmarks, fresh Nov 2024 AMC-10/12, HELMET long-context tasks and in-house RAI benchmarks, against Qwen 2.5 14B/72B Instruct, GPT-4o, GPT-4o-mini, Llama-3.3-70B and phi-3; strength: vendor-run, mostly single runs with no variance (AMC has 100 runs and 2σ error bars), data-mix and post-training ablations, main development benchmark (PhiBench) internal and unreleased
conversion: Table 1 Llama-3.3-70B MATH and HumanEval cells have footnote text fused in ("66.311 1 These scores…", "78.911footnotemark: 1"); readable as 66.3 and 78.9 followed by footnote 1 (pp. 1–3). The Figure 3 token-coloured example repeats each token many times (pp. 12–14). The Figure 4 pseudocode is interleaved with [figure] placeholders but readable. The Table 10 bold for phi-4 is lost; the caption says it was only for readability (p. 19).

## Digest

- **Claim.** phi-4 is a 14B decoder-only model whose recipe centres on data quality, with synthetic data used through pretraining, midtraining and post-training. It is said to "substantially surpass" its teacher GPT-4o on STEM QA, offered as evidence that the method goes beyond distillation (p. 1).
- **Architecture and training.** Changes from phi-3-medium are minimal:
  - tiktoken tokenizer with a padded vocabulary of 100,352;
  - full attention over 4K, instead of phi-3-medium's 2K sliding window;
  - about 10T pretraining tokens, peak LR 0.0003, weight decay 0.1, global batch 5760 (p. 7).
- **Midtraining.** Context goes from 4K to 16K: RoPE base 250K, max LR divided by 10, 250B tokens, a mix of 30% new long-context data and 70% recall tokens (pp. 10–12). Naturally long documents beat padded-together samples; no numbers are given.
- **Synthetic data.** 50 dataset types, about 400B unweighted tokens (p. 5). Techniques:
  - curated web, code and book seeds;
  - questions filtered by plurality vote: drop those where all answers agree or none do, and use the plurality answer as ground truth;
  - LLM extraction of QA pairs from deduction chains;
  - rewrites and self-revision against rubrics;
  - instruction reversal for code, kept only when the regenerated code matches the original;
  - execution-based validation.
  - The main text does not say which models generated each dataset, beyond calling GPT-4o the teacher.
- **Organic data.** Tens of millions of organic Q&A items were collected; ablations found organic questions "substantially more effective" than synthetic ones, with no numbers (p. 6). Web dumps are filtered by small non-LLM classifiers trained on ~10^6 LLM annotations, plus a separate non-STEM pipeline. Multilingual data uses fastText language ID (176 languages) (p. 6).
- **Synthetic-only ablation.** A 13B model trained on synthetic data only (>20 repetitions), relative to phi-3-medium (p. 8, Table 3):
  - TQA −14.8, or −7.7 with web rewrites added;
  - HumanEval +12.1 / +13.3.
  - Figure 2 shows 12 epochs of synthetic data beating 4 epochs plus more fresh web data on 5-shot MMLU; the values are not in the text.
- **Final mixture** (pp. 9–10, Table 5):

  | Source | Share | Unique tokens | Epochs |
  |---|---|---|---|
  | Web | 15% | 1.3T | 1.2 |
  | Web rewrites | 15% | 290B | 5.2 |
  | Synthetic | 40% | 290B | 13.8 |
  | Code | 20% | 820B | 2.4 |
  | Acquired sources | 10% | 580B | 1.7 |

- **Mixture ablations.** Run at 7B and a 1T-token horizon, reported relative to the final mix (p. 9, Table 4):
  - average: Uniform −2.2, S +0.8, S+WR +0.4, S+W 0.0;
  - S+W helps clearly only on TQA (+6.9).
  - The authors kept more web data despite the synthetic-heavy mixes scoring slightly better. They say the gap "largely closes" after post-training, but show no numbers for this.
- **Base model vs phi-3-medium base (4k).** MMLU +3.0, MMLU-pro +10.3, MATH +8.9, HumanEval +7.8, TQA −0.7 (pp. 7–8, Table 2). These use internal log-likelihood and few-shot evaluations.
- **Post-training.**
  - SFT: about 8B tokens, LR 10^-6, 40 languages.
  - DPO round 1 on PTS pairs, e.g. 132,859 generic MCQ and 76,552 math (Table 7).
  - DPO round 2, "judge-guided": about 850k pairs from GPT-4o, GPT-4t and phi-4 responses, labelled by a GPT-4o judge on accuracy, style and detail; 532,000 "accuracy" and 266,000 "overall" pairs (Table 8) (p. 12).
- **Pivotal Token Search (PTS).**
  - Estimate p(success | prefix) by sampling completions and checking them with an oracle (tests or ground truth).
  - Recursively split the response at the cumulative log-prob midpoint until each segment changes p(success) by less than p_gap or is a single token.
  - A single-token segment that changes p(success) by at least p_gap becomes a DPO pair: shared prefix as the query, one accepted token vs one rejected token.
  - Search is limited to questions with 0.2≤p(success)≤0.8.
  - It finds only pivotal tokens, and all of them only if success probability is near-monotone (pp. 14–16, Fig. 4).
  - The p_gap and rollout counts used are not disclosed.
- **Why PTS.** In full-length DPO, low-probability tokens add noise. In Figure 3 (GPT-4o, initial success 0.31, N=529), the harmful token "(a" (probability 0.12) would get a strong positive signal (pp. 12–14).
- **Post-training ablation** (p. 16, Table 9), as SFT → +PTS DPO → +judge DPO, with judge-only in brackets:

  | Benchmark | SFT | +PTS DPO | +judge DPO (final) | Judge-only |
  |---|---|---|---|---|
  | GPQA | 47.3 | 53.6 | 56.1 | 52.4 |
  | MATH | 77.1 | 80.5 | 80.4 | 77.6 |
  | ArenaHard | 56.7 | 66.5 | 75.4 | 69.8 |
  | DROP | 82.8 | 86.1 | 75.5 | 71.8 |
  | IFEval | 66.2 | 63.0 | 63.0 | 63.0 |

  - The text cites "Table [1]" here, apparently meaning Table 9.
  - The DROP and IFEval drops after DPO are not discussed.
- **Headline results** (pp. 1–3, Table 1; simple-evals at t=0.5):
  - vs GPT-4o: GPQA 56.1 vs 50.6 and MATH 80.4 vs 74.6, but MMLU 84.8 vs 88.1 and HumanEval 82.6 vs 90.6.
  - vs Qwen 2.5 14B Instruct: GPQA 56.1 vs 42.9, HumanEval 82.6 vs 72.1; loses on IFEval 63.0 vs 78.7, DROP 75.5 vs 85.5 and SimpleQA 3.0 vs 5.4.
  - vs phi-3 14B: GPQA 31.2, MATH 44.6.
- **Overclaims.**
  - The intro says phi-4 meets or exceeds Llama-3.1-405B on many reasoning benchmarks, but no 405B model appears in any table (p. 1).
  - "9 out of 12" wins vs Qwen-2.5-14B (p. 18).
  - Llama-3.3-70B scores 66.3 on MATH and 78.9 on HumanEval under simple-evals, against Meta's reported 77 and 88 (footnote, pp. 1–3).
- **SimpleQA.** The paper argues post-training deliberately traded score for abstention, from 3.7 after SFT to a final 3.0 (p. 16, Table 9). It claims the base model beats Qwen's 5.4, but the base score appears only in the Figure 6 image (pp. 16, 18).
- **Contamination checks.**
  - n-gram decontamination is improved (details in Appendix B), but the authors concede it misses rephrasings (pp. 16–18).
  - Fresh Nov 2024 AMC-10/12: 100 runs at t=0.5, maximum score 150. phi-4's own score is only in the Figure 1 image.
  - QwQ-32B-Preview averages 124.5 on AMC, using 4X more tokens than phi-4 (p. 3).
- **PhiBench** is team-written and was used to choose data mixtures and post-training hyperparameters, so it is not a held-out test. On it, phi-4 scores 56.2 vs GPT-4o 72.4 and Qwen 2.5 14B 49.8 (pp. 1–3, Table 1; p. 16–18).
- **HELMET at 16K**, averaged over 5 runs (pp. 10–12, Table 6):

  | Model | Recall | RAG | ICL | Re-rank | QA | Summ |
  |---|---|---|---|---|---|---|
  | phi-4 | 99.0 | 57.1 | 77.0 | 54.4 | 36.0 | 40.5 |
  | Qwen-2.5-14B | 100.0 | 59.1 | 67.6 | 50.3 | 29.7 | 42.3 |

  GPT-4o is higher than phi-4 on every task.
- **Safety** (p. 19, Table 10; lower is better except Grounding):
  - Jailbreak DR1 0.073 vs phi-3 14B 0.111.
  - Third-party content DR1 0.121 vs 0.251.
  - Harmful-content-continuation DR3 is 0.036, the highest in the table (phi-3 14B: 0.01); the text does not discuss this.
  - GCG suffixes built on phi-3-medium did not transfer to phi-4.
- **Not disclosed and limitations.** Compute, hardware, layer and width configuration, p_gap, and per-dataset generator models are not given. Stated weaknesses: factual hallucination, strict instruction following, a "9.9 vs 9.11" error, verbose answers, and tuning for single-turn use (p. 20).

## Related in library

- Phi-3 Technical Report. A Highly Capable Language Model Locally on Your Phone: direct predecessor; phi-4 keeps the phi-3-medium architecture and reports gains over phi-3 throughout (Tables 1–3, 10).
- The Llama 3 Herd of Models: phi-4 compares against Llama-3-instruct-8b (RAI table) and Llama-3.3-70B.
- Mistral 7B: Mistral-7b-v0.1 is a baseline in the RAI safety benchmark (Table 10).

## Q&A
