# Phi-4 Technical Report

type: method
read: full
family: small dense decoder-only LLM trained mostly on synthetic data, plus preference-tuning (DPO) innovations
evidence: simple-evals and internal-harness benchmarks, HELMET long-context tasks, fresh Nov 2024 AMC-10/12 tests and in-house RAI benchmarks; compared against phi-3, Qwen 2.5 14B/72B, Llama-3.3-70B, GPT-4o-mini and GPT-4o; strength: vendor-run, with ablations of data mix and post-training stages but no ablation of PTS's own design choices; key optimisation benchmark (PhiBench) is internal and unreleased
conversion: Figure 3's colour-coded example text is garbled into long runs of repeated tokens (p. 12–14), which is incidental to the findings; a footnote marker is fused into Table 1's Llama-3.3 MATH cell ("66.311", read as 66.3) (p. 1–3); some cross-references point to the wrong table (Table 1 for Table 9 on p. 16; Table 8 for Table 7 on p. 12–14)

## Digest

- Claim: a 14B model trained on data centred on synthetic tokens, with a new curriculum and new post-training, matches or beats much larger models on reasoning. The paper says it "substantially surpasses" its teacher GPT-4o on STEM QA, which it presents as evidence of going beyond distillation (p. 1).
- Architecture is almost unchanged from phi-3-medium. Changes: tiktoken tokenizer with a padded vocab of 100,352, and full attention over 4K instead of a 2K sliding window (p. 7–8).
- Pretraining: about 10T tokens, peak LR 0.0003, weight decay 0.1, batch 5760 (p. 7–8). Midtraining extends context to 16K over 250B tokens. It uses a mix of 30% long-context data and 70% recall data, with rope base raised to 250K (p. 10–12).
- Synthetic data: 50 dataset types totalling about 400B unweighted tokens (p. 5). Generation methods:
  - seeds filtered from web, books and code;
  - questions kept only when majority-vote answers neither all agree nor are all inconsistent;
  - QA pairs extracted from deduction chains;
  - self-revision and instruction reversal for code;
  - execution-based validation.
- Final mix (p. 9–10, Table 5), as share of training / unique tokens / epochs:

  | Source | Share | Unique tokens | Epochs |
  |---|---|---|---|
  | Web | 15% | 1.3T | 1.2 |
  | Web rewrites | 15% | 290B | 5.2 |
  | Synthetic | 40% | 290B | 13.8 |
  | Code | 20% | 820B | 2.4 |
  | Acquired sources | 10% | 580B | 1.7 |

- Data ablations:
  - A 13B model trained only on synthetic data, compared with phi-3-medium, gains on HumanEval (+12.1) but loses on TQA (-14.8) (p. 8–9, Table 3).
  - Mix ablations were run at 7B scale on 1T tokens, relative to the final mix. Averages: synthetic-heavy +0.8, S+WR +0.4, uniform -2.2, S+W 0.0 (p. 9–10, Table 4).
  - The authors admit the synthetic-heavy mixes are "marginally better". They kept web data for knowledge, where S+W gives TQA +6.9.
- Pretrained phi-4 versus phi-3-medium base, on the internal few-shot/log-likelihood harness: MMLU-pro +10.3, MATH +8.9, TQA -0.7 for the 4k model (p. 7–8, Table 2).
- Post-training:
  - SFT on about 8B tokens at LR 10^-6, with data in 40 languages (p. 12).
  - DPO round 1 uses Pivotal Token Search pairs, e.g. 76,552 math and 132,859 generic MCQ samples (p. 12–14, Table 7).
  - DPO round 2 is "judge-guided": about 850k pairs from GPT-4o, GPT-4t and phi-4 responses, labelled by GPT-4o (p. 12–14, Table 8).
- Pivotal Token Search (PTS) mechanism:
  - It estimates p(success | prefix) by sampling rollouts and checking them with an oracle (tests or ground truth).
  - It recursively bisects the completion to find single tokens that shift p(success) by at least p_gap.
  - Each DPO pair is then a shared prefix plus one accepted token versus one rejected token.
  - Questions are filtered to 0.2 ≤ p(success) ≤ 0.8 (p. 14–16).
  - The value of p_gap is not given.
- Post-training ablation (p. 16, Table 9), on GPQA, MATH and ArenaHard:

  | Benchmark | SFT | PTS-DPO | Judge-DPO only | Both |
  |---|---|---|---|---|
  | GPQA | 47.3 | 53.6 | 52.4 | 56.1 |
  | MATH | 77.1 | 80.5 | 77.6 | 80.4 |
  | ArenaHard | 56.7 | 66.5 | 69.8 | 75.4 |

  The "complementary" claim does not hold for MATH: both stages give 80.4 against 80.5 for PTS-DPO alone.
- Unremarked regressions in Table 9 (p. 16): DROP falls from 86.1 after PTS-DPO to 75.5 final, and IFEval falls from 66.2 after SFT to 63.0.
- Headline results (simple-evals, p. 1–3, Table 1):
  - GPQA 56.1 vs GPT-4o 50.6 and Qwen 2.5 14B 42.9.
  - MATH 80.4 vs GPT-4o 74.6 and Qwen 2.5 72B 80.0.
  - MMLU 84.8 vs Qwen 2.5 14B 79.9 and GPT-4o 88.1.
  - HumanEval 82.6 vs Qwen 2.5 72B 80.4 and GPT-4o 90.6.
- Comparison with Qwen-2.5-14B-Instruct: phi-4 wins 9 of 12 benchmarks (p. 18). It loses on:
  - SimpleQA 3.0 vs 5.4;
  - DROP 75.5 vs 85.5;
  - IFEval 63.0 vs 78.7 (p. 1–3, Table 1).
- How the authors read the losses: they call SimpleQA and DROP "reductive". They argue the SimpleQA drop reflects deliberate refusals rather than hallucinations, noting the base model scores higher than the final one (p. 16, Figure 6; p. 18). They accept IFEval as a real weakness.
- Llama-3.3-70B: simple-evals gives it MATH 66.3 and HumanEval 78.9, against Meta-reported 77 and 88. The authors attribute the gap to strict formatting (p. 1–3, Table 1 footnote).
- Contamination checks:
  - Fresh Nov 2024 AMC-10/12 tests, 100 runs at t=0.5 (p. 3, Figure 1). phi-4's AMC score is shown only in the figure, not the text.
  - QwQ averages 124.5 points but uses "4X more tokens" (p. 3).
  - Decontamination is n-gram based. The authors admit it misses rephrasings (p. 16).
- Long context, HELMET at 16K (p. 10–12, Table 6):
  - ICL 77.0 vs Qwen-2.5-14B 67.6 and GPT-4o 85.6;
  - RAG 57.1, the lowest of the five models (Qwen 59.1);
  - Re-rank 54.4 vs GPT-4o 73.8.
- Safety, in-house RAI benchmarks (p. 19, Table 10):
  - Jailbreak DR1 0.073 vs phi-3 14B 0.111.
  - 3P content harms 0.121 vs 0.251.
  - Harmful-content continuation DR3 0.036 is the worst of the listed models (phi-3 14B 0.01). The text does not discuss this.
- Not disclosed:
  - training compute and hardware;
  - which generator models produced most of the synthetic data;
  - DPO hyperparameters and p_gap;
  - PhiBench contents.
- Admitted weaknesses (p. 20):
  - factual hallucination;
  - strict format-following;
  - errors such as answering that 9.9 is smaller than 9.11;
  - verbose answers;
  - tuning mainly for single-turn use.

## Related in library

- Phi-3 Technical Report. A Highly Capable Language Model Locally on Your Phone: direct predecessor; phi-4 keeps the phi-3-medium architecture and reports gains over it throughout.
- GPT-4 Technical Report: the Phi line distils from GPT-4. phi-4 compares against GPT-4o as "teacher" and uses GPT-4o as its DPO judge.
- The Llama 3 Herd of Models: compared against Llama-3.3-70B, Llama-3.1-405B (claimed) and Llama-3-8B (RAI). The rope-base change cites a Llama 3 reference.
- Mistral 7B: compared on the RAI safety benchmarks (Table 10).

## Q&A
