# Phi-4 Technical Report

type: system
read: full
family: synthetic-data pretraining & token-level preference alignment
evidence: internal benchmarks, standard academic benchmarks (simple-evals, HELMET, ArenaHard), and fresh post-cutoff contest math (AMC 10/12 Nov 2024) vs. phi-3, Qwen 2.5, Llama 3.1/3.3, and GPT-4o / 4o-mini; strength: vendor-run evaluations with clean post-training ablations and held-out fresh test sets
conversion: major rendering artifacts in Figure 3 transcript (repeated tokens) and Figure 4 pseudocode (interleaved tags); tables and text body intact

## Digest

- Architecture: 14B parameter decoder-only transformer following phi-3-medium, switching to `tiktoken` (vocabulary 100,352), replacing 2K sliding-window attention with full attention over 4096 context, later expanded to 16K (p. 7).
- Pretraining compute: trained for approximately 10T tokens, peak learning rate 0.0003 with linear warmup and decay, weight decay 0.1, global batch size 5760 (p. 7).
- Pretraining data mix (Table 5): 40% synthetic (290B unique tokens, 13.8 epochs), 15% web rewrites (290B unique tokens, 5.2 epochs), 15% filtered web (1.3T unique tokens, 1.2 epochs), 20% code (820B unique tokens, 2.4 epochs), 10% acquired sources (580B unique tokens, 1.7 epochs) (p. 9, Table 5).
- Synthetic data role: unweighted synthetic corpus comprises ~400B tokens across 50 categories; repeated synthetic epochs outperformed introducing fresh web tokens on reasoning benchmarks, but web data was retained to prevent knowledge collapse (p. 5, p. 8).
- Pure synthetic ablation: a 13B model trained purely on synthetic data improved Human-Eval by +12.1 and MATH by +4.9 over phi-3-medium, but suffered a -14.8 point degradation on 1-shot TriviaQA (p. 8, Table 3).
- Midtraining context extension: context length increased from 4K to 16K over 250B tokens with base RoPE frequency increased to 250K, using 30% long-context data (>4K/8K/16K) and 70% pretraining recall tokens (p. 10).
- Midtraining long-context results: on HELMET at 16K length, phi-4 scores 99.0 on Recall, 57.1 on RAG, 77.0 on ICL, 54.4 on Re-rank, 36.0 on QA, and 40.5 on Summ compared to GPT-4o's 100.0, 66.7, 85.6, 73.8, 43.7, and 46.3 (p. 10, Table 6).
- Post-training workflow: one round of SFT (~8B tokens, learning rate 10^-6 in chatml format), followed by two DPO rounds: Pivotal Token Search DPO, then judge-guided DPO (p. 12).
- Pivotal Token Search (PTS): binary searches a solution trajectory via oracle rollouts ($0.2 \le p(\mathrm{success}) \le 0.8$) to locate single critical tokens causing a $\ge p_{\mathrm{gap}}$ shift in success probability, forming single-token accepted/rejected preference pairs (p. 14).
- Preference datasets: PTS DPO uses ~250k pairs (132,859 generic MCQA, 76,552 math, 37,886 code, 3,000 safety) (p. 12, Table 7); judge-guided DPO uses ~850k pairs scored by GPT-4o (p. 12, Table 8).
- Post-training ablation on GPQA: SFT scores 47.3, DPO stage 1 (PTS) reaches 53.6, DPO stage 2 only reaches 52.4, and full stage 1 + 2 reaches 56.1 (p. 16, Table 9).
- Post-training ablation on ArenaHard: SFT scores 56.7, DPO stage 1 reaches 66.5, DPO stage 2 only reaches 69.8, and full stage 1 + 2 reaches 75.4 (p. 16, Table 9).
- Core academic benchmark results (simple-evals): GPQA reaches 56.1 (vs GPT-4o 50.6, Qwen 2.5 14b instruct 42.9), MATH reaches 80.4 (vs GPT-4o 74.6, Qwen 2.5 14b instruct 75.6), and MMLU reaches 84.8 (vs GPT-4o 88.1, phi-3 14b 77.9) (p. 1, Table 1).
- Coding performance: HumanEval scores 82.6 and HumanEval+ scores 82.8, exceeding Qwen 2.5 14b instruct (72.1 / 79.1) and Llama-3.3 70b instruct (78.9 / 77.9) (p. 1, Table 1).
- Fresh evaluation on Nov 2024 AMC 10/12: tests occurred after data cutoff; phi-4 outperforms equal-sized and frontier open-weight models, while long-CoT model QwQ-32B-Preview reaches 124.5 using 4X more tokens (p. 3, Figure 1).
- Explicitly acknowledged weaknesses: IFEval score is low at 63.0 (vs Qwen 2.5 14B's 78.7 and GPT-4o's 84.8) due to limited instruction-following data (p. 1, Table 1; p. 18).
- SimpleQA and refusal behavior: SimpleQA score is 3.0 (vs Qwen 2.5 14B's 5.4 and GPT-4o's 39.4), driven by explicit post-training to refuse unknown facts rather than hallucinate (p. 1, Table 1; p. 16).
- RAI evaluation: Jailbreak (DR1) defect rate is 0.073 (vs phi-3 14B's 0.111 and Llama-3 8B's 0.130), while harmful content continuation (DR3) is 0.036 (vs phi-3 14B's 0.010) (p. 19, Table 10).

## Related

- Phi-3: direct predecessor; phi-4 replaces sliding window attention with full 4K context, updates the tokenizer to `tiktoken`, and shifts from 2-phase pretraining to high-ratio synthetic pretraining throughout.
- Direct Preference Optimization (Rafailov et al., 2023): standard preference objective; modified here in Stage 1 via PTS to isolate single pivotal tokens rather than comparing complete divergent sequences.
- OpenAI simple-evals: evaluation harness used for primary benchmark comparisons (MMLU, GPQA, MATH, HumanEval, MGSM, SimpleQA, DROP).
- QwQ-32B-Preview / DeepSeek-R1-Lite / OpenAI o1: contemporary long-CoT models that scale inference compute; phi-4 targets single-turn generation without extended thinking traces.
- HELMET (Smith et al., 2024): used to benchmark midtrained 8K and 16K context processing across multi-document and aggregation tasks.
