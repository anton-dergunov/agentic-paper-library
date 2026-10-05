# Phi-4 Technical Report

type: method
read: full
family: Foundation model report, Phi series; emphasis on synthetic data quality and token-level preference optimization
evidence: MMLU, GPQA, MATH, HumanEval, MGSM, SimpleQA, DROP, MMLUPro, HumanEval+, ArenaHard, LiveBench, IFEval (OpenAI simple-evals framework); fresh AMC-10/12 test (November 2024, post-training-data); internal PhiBench; HELMET long-context suite; GPQA and MATH also compared against teacher GPT-4o; strength: multiple public benchmarks plus fresh out-of-distribution test, but all evaluation vendor-run; ablations on data mixture at smaller scale (1T tokens, 7B params) than final model (10T tokens, 14B params)
conversion: Figure 3 (p. 13–14) severely garbled: words like "deal", "polynomial", "corresponds", "according" repeated dozens of times in sequence, obscuring the mathematical reasoning shown; Figure 4 (p. 14) pseudocode contains placeholder markers `[figure]` scattered through the code text instead of actual algorithm content, making the PTS algorithm text illegible.

## Digest

- **Architecture**: 14B decoder-only transformer, minimal change from phi-3-medium; switched to tiktoken tokenizer (vocabulary 100,352); uses full 4K attention (not 2K sliding window); context extended 4K→16K in midtraining (p. 7)
- **Data generation**: ~400B unweighted tokens from 50 types of synthetic datasets created via seed curation (web, code, Q&A platforms), rewriting, self-revision, instruction reversal, and validation loops; organic seeds filtered for reasoning depth and educational value (p. 4–6)
- **Pretraining data mixture** (p. 9, Table 5): 40% synthetic (290B unique, 13.8 epochs), 15% web (1.3T unique, 1.2 epochs), 15% web rewrites (290B unique, 5.2 epochs), 20% code (820B unique, 2.4 epochs), 10% acquired sources (580B unique, 1.7 epochs); total ~10T tokens trained
- **Key finding**: more epochs on limited synthetic data outperforms fresh web tokens; models trained on synthetic-only underperform on knowledge benchmarks (p. 8–9, Tables 2–3)
- **Pretraining results vs phi-3-medium** (p. 8, Table 2): +8.9 MATH, +10.3 MMLUPro, +7.8 HumanEval, +6.8 MBPP, +3.0 MMLU; –0.7 TriviaQA (knowledge benchmark gap)
- **Post-training**: 8B tokens SFT; two rounds DPO: (1) novel *Pivotal Token Search* targeting single tokens with high impact on correctness (p. 14–15, Figure 4), (2) judge-guided DPO with GPT-4o scorer; hallucination-mitigation data included (p. 12–16, Tables 7–8)
- **Novel contribution—Pivotal Token Search (PTS)**: identifies tokens where output probability of success changes by ≥*p_gap* via recursive binary search and rollouts; generates preference pairs on isolated pivotal tokens rather than full sequences, avoiding dilution from low-probability errors (p. 14–15). Tested on math, physics, coding; integrated into DPO stage 1 (p. 15, Figure 5 examples)
- **Main benchmark results** (p. 1, Table 1): GPQA 56.1 (vs φ-3: 31.2, GPT-4o: 50.6), MATH 80.4 (vs φ-3: 44.6, GPT-4o: 74.6), MMLU 84.8 (vs φ-3: 77.9, GPT-4o: 88.1), HumanEval 82.6 (vs φ-3: 67.8, GPT-4o: 90.6), ArenaHard 75.4 (vs φ-3: 45.8)
- **Fresh test set** (p. 3, Figure 1): November 2024 AMC-10/12 math contests (150 points max), φ-4 average ~110 points over 4 tests at *t*=0.5 with 2σ error bars; outperforms Llama-3.3-70B, Qwen-2.5-72B, and approaches GPT-4o; stronger evidence against benchmark contamination than standard suites
- **Long-context (HELMET, p. 10, Table 6)**: tested at 8K and 16K on Recall, RAG, Re-rank, ICL, QA, Summarization; φ-4 at 16K: Recall 99.0, RAG 57.1, ICL 77.0, QA 36.0 (GPT-4o at 16K: ICL 85.6, QA 43.7)
- **Post-training ablation** (p. 16, Table 9): PTS (stage 1 DPO) most effective for reasoning (GPQA +6.3 over SFT, MATH +3.3); judge-guided DPO (stage 2) best for ArenaHard (+8.7); both complementary
- **Safety** (p. 18–19, Table 10): RAI benchmarks show φ-4 Jailbreak DR1 = 0.073 (phi-3: 0.107–0.117, competitors 0.13–0.156); red-teaming by Microsoft AIRT found φ-4 showed strong defenses, but further testing recommended
- **Claimed distinction from distillation**: φ-4 surpasses teacher GPT-4o on GPQA and MATH (p. 1, Table 1), offered as evidence synthetic generation + post-training exceed distillation
- **Weaknesses noted** (p. 20): hallucinations on factual knowledge, weak instruction-following (IFEval score 63.0, competitors 78–89), arithmetic errors (e.g., "9.9 vs 9.11"), verbose outputs, designed for single-turn not multi-turn

## Related

- Phi-3 family: phi-4 inherits architecture and two-phase training philosophy but expands synthetic data from ~200B to ~400B tokens and introduces PTS-based DPO
- GPT-4o: cited as teacher model; phi-4 exceeds it on GPQA (+5.5) and MATH (+5.8) while scoring below on MMLU (–3.3), MGSM (–9.8), HumanEval (–8.0)
- QwQ-32B-Preview, DeepSeek-R1-Lite-Preview: inference-time scaling competitors; phi-4 claims 4× lower inference cost per solution attempt
- DPO (Christiano et al. 2023): core technique adapted; PTS is novel refinement targeting token-level preferences
- OpenAI O1: pioneered chain-of-thought scaling; phi-4 uses synthetic chain-of-thought data without inference-time search
