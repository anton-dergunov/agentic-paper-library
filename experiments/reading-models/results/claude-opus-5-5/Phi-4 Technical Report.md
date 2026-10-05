# Phi-4 Technical Report

type: system
read: full
family: vendor technical report for a small (14B) open-weight LLM; synthetic-data-centric training recipe plus a new post-training technique
evidence: phi-4 on simple-evals plus other public benchmarks, HELMET long-context, fresh AMC-10/12 tests, an internal PhiBench and in-house RAI benchmarks, against phi-3, Qwen 2.5 14B/72B, Llama-3.3-70B, GPT-4o-mini and GPT-4o; strength: vendor-run throughout, single reported scores with no error bars in the tables, internal ablations given only as deltas (absolute values withheld), data-mixture ablations run at 7B scale and 1T tokens rather than on the final model, internal benchmark undisclosed, one contamination-resistant check (AMC) whose phi-4 score sits only in a figure
conversion: body ends at Acknowledgments, so Appendices A–D (judge prompt, hallucination data, decontamination, AMC details, synthetic examples) and the reference list are missing. Figures 1, 2 and 6 are dropped, so the AMC, epoch-scaling and SimpleQA-attempt results are unreadable. Figure 3 is garbled (each token repeated many times) and Figure 4 pseudocode is riddled with `[figure]` placeholders; the chat template is also dropped (p. 12–14). Table 1 has footnote text inlined in the Llama-3.3 MATH and HumanEval cells, values still legible (p. 1). Footnote markers are fused into the text ("organic22 2", "synthetic44 4"). Bold is lost in Table 10 (p. 19). Wrong cross-references: the first DPO round points to "Table 8" where Table 7 is meant (p. 12), and Section 4.5 points to "Table 1" where Table 9 is meant (p. 16).

## Digest

- Architecture is nearly unchanged from phi-3-medium: decoder-only, 14B parameters, default context 4096. The changes are the tiktoken tokenizer (padded vocabulary 100,352) and full attention over 4K instead of phi-3-medium's 2K sliding window (p. 7).
- Pretraining ran for approximately 10T tokens, with linear warm-up and decay, peak learning rate 0.0003, weight decay 0.1 and global batch size 5760 (p. 7).
- Midtraining extends context from 4K to 16K: 250B tokens, maximum learning rate dropped by a factor of 10 versus pretraining, rope base frequency 250K, and a mixture of 30% new long-context data and 70% recall tokens from pretraining (p. 10).
- Synthetic data: 50 broad dataset types, about 400B unweighted tokens. Techniques are seed curation, rewrite-and-augment, self-revision, instruction reversal, execution-validated code, and plurality-vote filtering of questions, with plurality answers standing in for ground truth (p. 5).
- Final pretraining mixture, as fraction / unique tokens / epochs: Web 15% / 1.3T / 1.2; Web rewrites 15% / 290B / 5.2; Synthetic 40% / 290B / 13.8; Code 20% / 820B / 2.4; Acquired sources 10% / 580B / 1.7 (p. 9, Table 5).
- Pretrained phi-4 (4k) is reported only as deltas over pretrained phi-3-medium, under an internal log-likelihood/few-shot harness: MMLU +3.0, MMLU pro +10.3, MATH +8.9, Human-Eval +7.8, TQA -0.7. No absolute scores are given (p. 7, Table 2).
- Synthetic-only ablation: a 13B model seeing over 20 repetitions of each source scores Human-Eval +12.1 and MATH +4.9 but TQA -14.8 versus phi-3-medium. Adding web rewrites gives TQA -7.7 and MATH +8.1 (p. 8, Table 3).
- Mixture ablations (7B scale, 1T tokens, 75% of the token budget varied) are stated relative to the final phi-4 mixture. Synthetic-heavy "S" averages +0.8 (TQA -3.0, Human-Eval -6.1), "Uniform" -2.2, and "S + W" 0.0 with TQA +6.9 (p. 9, Table 4).
- The chosen mixture is therefore not the ablation winner. The authors traded this for knowledge benchmarks and say the gap "largely closes" after post-training, with no numbers (p. 9).
- Post-training has three stages. SFT uses about 8B tokens at learning rate 10^-6, including 40 languages. DPO round 1 uses Pivotal Token Search pairs. DPO round 2 is judge-guided, with approximately 850k pairs from GPT-4o, GPT-4t and phi-4 responses, labelled by GPT-4o (p. 12).
- DPO sample counts: round 1 has 132,859 generic multiple-choice Q&A, 76,552 math, 16,080 python, 21,806 other-language code and 3,000 unknown + safety (p. 12, Table 7). Round 2 has 532,000 "any vs any accuracy", 266,000 "any vs any overall" and 43,842 unknown + safety (p. 12, Table 8).
- Pivotal Token Search estimates p(success | prefix) by sampling completions checked by an oracle, then recursively bisects the completion to find single tokens that shift it by at least p_gap. Each DPO pair is one accepted versus one rejected token after a shared prefix; questions are filtered to 0.2 ≤ p(success) ≤ 0.8 (p. 14).
- Post-training ablation, in the order SFT / DPO stage 1 / DPO stage 2 only / phi-4: GPQA 47.3 / 53.6 / 52.4 / 56.1; MATH 77.1 / 80.5 / 77.6 / 80.4; ArenaHard 56.7 / 66.5 / 69.8 / 75.4 (p. 16, Table 9).
- Regressions in the same table: DROP 82.8 / 86.1 / 71.8 / 75.5, and IFEval 66.2 at SFT versus 63.0 in every later column (p. 16, Table 9).
- Headline results (simple-evals, temperature=0.5): GPQA 56.1 versus GPT-4o 50.6, Qwen 2.5 14b 42.9 and phi-3 14b 31.2; MATH 80.4 versus GPT-4o 74.6, Qwen 2.5 72b 80.0 and phi-3 44.6; MMLU 84.8 versus GPT-4o 88.1 and phi-3 77.9 (p. 1, Table 1).
- Weak spots: SimpleQA 3.0 versus phi-3 7.6 and GPT-4o 39.4; IFEval 63.0 versus Qwen 2.5 14b 78.7 and Llama-3.3 70b 89.3; DROP 75.5 versus Qwen 2.5 14b 85.5; PhiBench 56.2 versus GPT-4o 72.4 (p. 1, Table 1). The authors attribute low SimpleQA to deliberate refusal training (p. 16–18).
- Baseline caveats: Llama-3.3 scores 66.3 on MATH and 78.9 on HumanEval under simple-evals, while a footnote says Meta reports 77 and 88 (p. 1, Table 1 footnote). "9 out of 12 benchmarks" versus Qwen-2.5-14B (p. 18) does not match Table 1, which has 13 rows.
- Contamination check: November 2024 AMC-10/12, four tests, 100 runs at t=0.5, max score 150, collected after the training data. phi-4 is claimed to beat larger frontier models, but its score is only in the missing Figure 1; the text gives QwQ-32B-Preview at 124.5 using 4X more tokens (p. 3).
- HELMET at 16K, phi-4 versus Qwen-2.5-14B versus GPT-4o: ICL 77.0 / 67.6 / 85.6; QA 36.0 / 29.7 / 43.7; RAG 57.1 / 59.1 / 66.7; Re-rank 54.4 / 50.3 / 73.8. Nothing beyond 16K is tested (p. 10, Table 6).
- Safety (in-house RAI benchmark, GPT-4o simulated and judged), phi-4 versus phi-3 (14B-4K): Jailbreak DR1 0.073 versus 0.111; 3P Content Harms DR1 0.121 versus 0.251; Harmful Content Continuation DR3 0.036 versus 0.01 (the worst in the table); Grounding 4.619 versus 4.787 (p. 19, Table 10).
- Not disclosed: which model(s) generate the synthetic data (GPT-4o is called the teacher), layer/width configuration, compute, dataset identities, PhiBench size or items, and variance on any table. Decontamination is admitted to be n-gram based and ineffective against rephrasing (p. 16).

## Related

- phi-3 / phi-3-medium [1]: direct predecessor; same architecture, and the baseline for all pretraining deltas, the two-phase data strategy being revised, and the RAI comparison.
- GPT-4o (and GPT-4, GPT-4t): named as teacher and used as DPO response source and judge; phi-4 is claimed to surpass it on GPQA and MATH, which is the paper's evidence for "beyond distillation".
- Qwen 2.5 14B / 72B instruct: closest in-class baseline; phi-4 wins most rows but loses SimpleQA, DROP and IFEval.
- Llama-3.3-70B instruct: larger open-weight baseline; the scores used here are lower than Meta's own, attributed to simple-evals formatting strictness.
- QwQ-32B-Preview, OpenAI O1, DeepSeek-R1-Lite-Preview: long chain-of-thought models, set aside as a different cost class although QwQ scores highly on AMC.
- DPO [26]: the preference-optimization method used for both rounds; PTS changes how the pairs are built (single-token pairs), not the objective.
- Contrastive estimation of failure tokens [20]: the alternative for token-level DPO weighting; PTS is claimed to avoid its learned proxy and to yield both accepted and rejected data.
- Automated process supervision [33], [19]: search-and-rollout methods for process reward models; PTS is positioned as a token-level variant.
- OpenAI simple-evals [24]: the evaluation harness for the first block of Table 1 and for the AMC temperature choice.
- HELMET [35]: long-context suite used for the 8K/16K comparison.
- Llama-3 [3]: cited for the rope base-frequency increase and as an RAI baseline (Llama-3-instruct-8b).
- Mistral-7b-v0.1/v0.2 [17], Gemma 7b [29]: older, smaller RAI baselines only; no same-generation or same-size models appear in the safety table.
