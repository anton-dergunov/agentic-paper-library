# Efficient Memory Management for Large Language Model Serving with PagedAttention

type: system
family: KV-cache memory management for LLM serving (paged, virtual-memory-style block allocation)
evidence: throughput (sustained request rate) and normalized latency for OPT-13B/66B/175B and LLaMA-13B on synthetic ShareGPT and Alpaca length-based workloads, plus shared-prefix and chatbot workloads, against FasterTransformer and three self-implemented Orca variants (p. 10–12; Table 1, p. 9); strength: one hardware and workload setup, baselines re-implemented by the authors (Orca not public), no accuracy evaluation; kernel, block-size and swap-vs-recompute ablations present (p. 12–13, Figs 18–19)

## Digest

- Claim: PagedAttention, an attention algorithm that stores each sequence's KV cache in fixed-size blocks that need not be contiguous, and vLLM, a serving engine built on it, give "2-4×" throughput at the same latency versus FasterTransformer and Orca (p. 1, abstract; p. 13, §9).
- Mechanism: each request's KV cache is split into logical blocks of a fixed token count (default 16, p. 12). A per-request block table maps logical to physical GPU blocks. Physical blocks are allocated on demand, and a new one only when the last is full (p. 5–6, Figs 4, 6).
- Attention runs block by block over non-contiguous blocks (Eq. 4, p. 5, Fig. 5). In the printed Eq. 4 the denominator's subscript reads as "1" where the summation index suggests t, so the text layer is ambiguous there (p. 5).
- Sharing: physical blocks carry reference counts. Parallel sampling shares the prompt, and beam search shares most blocks. Writes to a shared block use copy-on-write at block granularity (p. 7, Figs 8–9).
- Scheduling: FCFS. On memory exhaustion, whole sequence groups are preempted all-or-nothing and either swapped to CPU RAM or recomputed (p. 8). Swap space is bounded by the GPU KV memory (p. 8).
- Motivation: for a 13B model on a 40 GB A100, parameters are 26 GB (65%) and KV cache is ">30%" in Fig. 1 (p. 1). For OPT-13B the paper gives 800 KB of KV cache per token and up to 1.6 GB per 2048-token request (p. 4).
- Waste: existing systems use only "20.4% - 38.2%" of KV memory for token states (p. 2, Fig. 2; "as low as 20.4%", p. 4). The per-segment stacked labels in Fig. 2 are garbled in the text layer, so only the text's figures are quoted.
- Most §6 results are sustained request-rate ratios at a "similar" latency that the text never defines. On ShareGPT, vLLM sustains 1.7×–2.7× vs Orca (Oracle), 2.7×–8× vs Orca (Max) and up to 22× vs FasterTransformer (p. 11). Average batched requests for OPT-13B on ShareGPT at 2 req/s are 30.42 (vLLM), 13.62 (Orca Oracle) and 7.00 (Orca Max) (p. 10, Fig. 13a; the 2.2× and 4.3× ratios are stated on p. 11).
- Not every case reaches 2×: Alpaca basic sampling is 1.3× vs Orca (Oracle) (p. 11); the OPT-175B Alpaca advantage is "less pronounced" (p. 11, Fig. 12f); one-shot shared-prefix translation is 1.67× vs Orca (Oracle) (p. 12, Fig. 16a); the chatbot is 2× vs the three Orca variants (p. 12, Fig. 17).
- Memory saving on Alpaca: parallel sampling 6.1%–9.8% and beam search 37.6%–55.2% (p. 11, Fig. 15). Text-only ShareGPT figures are 16.2%–30.5% and 44.3%–66.3% (p. 11). Gain over Orca (Oracle) on OPT-13B Alpaca rises from 1.3× (basic) to 2.3× (beam width 6) (p. 11).
- Shared prefix: throughput 1.67× (one-shot, 80-token prefix) and 3.58× (five-shot, 341-token prefix) vs Orca (Oracle), LLaMA-13B on WMT16 En–De (p. 12, Fig. 16).
- Costs and ablations: attention kernel latency is "20–26% higher" than FasterTransformer's (p. 12, Fig. 18a). Block sizes 16–128 were best on ShareGPT and 16–32 on Alpaca, and the default is 16 (p. 12, Fig. 18b). Recomputation overhead is "never higher than 20% of swapping's latency", and the two methods are comparable end to end at block sizes 16–64 (p. 13, Fig. 19; values only in the plot).
- Setup: OPT-13B/66B/175B and LLaMA-13B on A2 instances with A100 GPUs (p. 10). Table 1 (p. 9) gives KV-cache memory of 12 GB / 21 GB / 264 GB and maximum KV slots of 15.7K / 9.7K / 60.1K for 13B / 66B / 175B.
- Workloads use only input and output lengths from ShareGPT (mean 161.31 in, 337.99 out) and Alpaca (19.31 in, 58.45 out) (p. 9, Fig. 11), with Poisson arrival times. Traces are 1 hour, or 15 minutes for OPT-175B (p. 10).
- Orca was re-implemented under three assumed over-reservation rules: Oracle (knows output lengths, called infeasible), Pow2 (up to 2×) and Max (2048 tokens) (p. 10). FasterTransformer runs under the authors' own dynamic-batching scheduler (p. 10). The baselines are constructed variants, not the original systems.
- Text claims beyond the tables: "without affecting the model accuracy at all" (p. 2), with no accuracy measurements. "More pronounced with larger models" (p. 1), but the OPT-175B Alpaca case runs the other way (p. 11). "Near-zero waste" (p. 1) rests on Fig. 2 alone (p. 2).
- Not disclosed or not tested: no multi-node setup; no experimental comparison with offloading systems such as FlexGen, which appears only in related work (p. 13–14); the "no performance difference" claim for the two block-table layouts (footnote 1, p. 5) is not shown; the 12% prompt share of KV memory (p. 4) is not shown in §6.3; the latency threshold behind "sustained" request rate is not defined.
- The paper's own inconsistencies: Fig. 1 shows the KV-cache share as ">30%" while the text says "Close to 30%" (p. 1); the abstract's "2-4×" headline does not match §6.2's reported ranges of 2.7×–8× over Orca (Max) and up to 22× over FasterTransformer (p. 11).

## Related in library

## Q&A
