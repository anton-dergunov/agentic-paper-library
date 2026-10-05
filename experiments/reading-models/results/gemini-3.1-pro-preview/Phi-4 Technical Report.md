# Phi-4 Technical Report

type: system
read: full
family: language models / synthetic pretraining
evidence: academic benchmarks (MMLU, MATH, GPQA, SimpleQA, etc.), HELMET long-context, safety benchmarks, and fresh AMC-10/12 exams; against size-matched (Qwen 2.5 14b instruct) and larger frontier models (GPT 4o, Llama-3.3 70b)
conversion: Figure 3 (p. 13) and Figure 4 (p. 14) are heavily broken; the pseudocode for Pivotal Token Search is flattened into a garbled list of `[figure]` tags and scattered words, making the exact algorithmic details unreadable.

## Digest

- phi-4 is a 14-billion parameter decoder-only transformer with a 100,352 padded vocabulary size (tiktoken), pretrained on approximately $10$T tokens (p. 7).
- Disclosed training parameters: default 4096 context extended to 16K during midtraining, peak learning rate of $0.0003$, constant weight decay of $0.1$, and global batch size of $5760$ (p. 7).
- Disclosed pretraining data mixture: 40% Synthetic, 20% Code data, 15% Web, 15% Web rewrites, 10% Acquired sources (p. 9, Table 5).
- Not disclosed: Exact prompts used to generate the synthetic data, specific parameter counts for layers/heads, and the exact scoring algorithms of the internal PhiBench.
- The model shifts away from learning strictly over organic data to relying on synthetic data that spoonfeeds logical reasoning linearly via rewriting, instruction reversal, and multi-agent self-revision (p. 4-5).
- To rule out data contamination, the model was tested on fresh November 2024 AMC-10 and AMC-12 math competitions, where it outperformed Llama-3.3-70B and Qwen-2.5-72B-Instruct, though it uses fewer tokens than the QwQ model which averages 124.5 points (p. 3, Figure 1).
- On MMLU, phi-4 14b scores 84.8, beating Qwen 2.5 14b instruct (79.9) and GPT 4o-mini (81.8) (p. 2, Table 1).
- On the GPQA benchmark, phi-4 14b achieves 56.1, outperforming its teacher GPT 4o (50.6) and Qwen 2.5 14b instruct (42.9) (p. 2, Table 1).
- On MATH, phi-4 14b scores 80.4, beating GPT 4o (74.6) and Qwen 2.5 14b instruct (75.6) (p. 2, Table 1).
- On SimpleQA, phi-4 14b only scores 3.0 compared to Qwen 2.5 14b instruct's 5.4, a deliberate trade-off where the post-training explicitly penalizes hallucinations in favor of refusals (p. 2, Table 1).
- In pretraining ablations, a 13B model trained solely on synthetic data showed huge gains over phi-3-medium on MATH (+4.9) but degraded severely on knowledge-based 1-shot TQA (-14.8) (p. 8, Table 3).
- Adding "Web Rewrites" to the synthetic 13B ablation pushed MATH to +8.1 and recovered some knowledge, reducing the TQA deficit against phi-3-medium to -7.7 (p. 8, Table 3).
- Context extension to 16K in midtraining utilized 250B tokens (70% recall tokens from pretraining, 30% new >8K context data) (p. 10).
- On the HELMET long-context benchmark, phi-4 16K achieves 100.0 on Recall, and scores 36.0 on QA compared to its 8K context score of 26.7, though it trails GPT-4o at 16K (43.7) (p. 10, Table 6).
- Post-training SFT uses $\sim$ 8B tokens with a learning rate of $10^{-6}$, followed by two rounds of Direct Preference Optimization (DPO) (p. 12).
- Pivotal Token Search (PTS) is introduced for DPO Stage 1: it generates preference data by isolating single tokens that significantly shift the model's success probability on a trajectory, avoiding noisy gradients from penalizing generally low-probability tokens (p. 14).
- Ablating PTS shows its necessity for reasoning: dropping it (DPO stage 2 only) reduces GPQA from 56.1 to 52.4 and MATH from 80.4 to 77.6 (p. 16, Table 9).
- DPO Stage 2 uses $\sim$ 850k desired/undisclosed pairs judged by GPT-4o evaluating accuracy, style, and detail (p. 12).

## Related

- phi-3: The predecessor model architecture that phi-4 builds upon and uses as a baseline in pretraining data ablations.
- Qwen-2.5-14B: The primary size-matched open-weight foundation model used as a baseline across benchmarks.
- GPT-4o: Used as the teacher model for distilling data, as a judge for DPO Stage 2, and as a frontier baseline target.
- HELMET: The benchmark suite used to evaluate the document-level and RAG capabilities of the 16K midtraining phase.
