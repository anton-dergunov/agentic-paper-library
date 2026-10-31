## Short answer

During generation, each new token attends to the keys and values of every earlier token. The KV cache stores those vectors so each step computes only the new token's key and value, instead of recomputing the whole prefix. The cache's memory, not compute, limits how many requests a GPU can serve at once. The paper is **Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention"** (vLLM), in `library/ml-systems/inference-and-serving/`.

## How it works

- **Size.** Each token costs 2 (K and V) × hidden size × layers × bytes. For OPT-13B in FP16 that is 2 × 5120 × 40 × 2 B ≈ 800 KB per token, so one 2048-token request can need 1.6 GB ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf&page=4&rect=280,345,295,356;54,357,67,368)).
- **Why it hurts.** Prompt processing is parallel and compute-bound. Generation runs one token at a time, is memory-bound, and its cache grows with an unknown output length ([§2.2, p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf&page=3)).
- **Old way: one contiguous chunk per request**, sized for the maximum length. Only 20.4–38.2% of the reserved memory held real token states in the systems the paper measured ([p. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf&page=2); the figure is read from a plot).
- **PagedAttention: fixed-size blocks, like OS virtual memory.**
  - The cache is split into blocks of B tokens (default 16). They can sit anywhere in GPU memory.
  - A per-request **block table** maps logical blocks to physical ones.
  - Attention is computed block by block, so the softmax is split into per-block partial sums ([Eq. 4, p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf&page=5&rect=363,238,383,248)).
  - Blocks are allocated on demand, so a request wastes at most one partly filled block.
- **Sharing.** Blocks are reference-counted and copy-on-write. Parallel samples, beam search and a shared prompt prefix can point at the same blocks.
- **Preemption.** When memory runs out, a whole sequence is evicted and later restored, either by swapping its blocks to CPU RAM or by recomputing them in one prefill pass.

## Measurements

Setup: OPT-13/66/175B and LLaMA-13B on A100s. Workloads are Poisson arrivals with ShareGPT and Alpaca length distributions. Baselines are FasterTransformer and a reimplementation of Orca. The main metric is **normalized latency**, mean end-to-end latency divided by output length, plotted against request rate ([p. 10](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf&page=10)).

| Setting | Result (vs. baseline) |
|---|---|
| ShareGPT, basic sampling | 1.7–2.7× request rate vs Orca (Oracle); 2.7–8× vs Orca (Max); up to 22× vs FasterTransformer ([p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf&page=11&rect=251,433,295,443)) |
| OPT-13B, batch size | 2.2× vs Orca (Oracle), 4.3× vs Orca (Max) (p. 11) |
| Beam search, width 6 | gain over Orca (Oracle) rises from 1.3× to 2.3× (p. 11, Fig. 14) |
| Memory saved by block sharing, beam search | 37.6–55.2% (Alpaca), 44.3–66.3% (ShareGPT) (p. 11, Fig. 15) |
| Shared prefix (WMT16) | 1.67× (one-shot), 3.58× (five-shot) throughput vs Orca (Oracle) (p. 12, Fig. 16) |
| Kernel cost | attention kernel 20–26% slower than FasterTransformer's, from block-table lookups ([p. 12, Fig. 18a](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf&page=12&rect=527,396,560,407)) |

Caveats:
- The authors ran all the comparisons. Orca is their own reimplementation, and almost every result is a plot. No variance is reported.
- The abstract's "2–4×" is a headline. The measured ratios against Orca (Oracle) run from 1.3× to 3.58×.
- "Without affecting the model accuracy at all" is asserted, not measured.
- The paper contradicts itself in places. Beam-search savings are "up to 55%" on p. 4 but 66.3% on p. 11. It also gives two opposite claims about swap vs recompute on p. 13.

## Practical takeaways

- To size a serving box, estimate KV bytes per token as 2 × layers × KV-dim × bytes. The paper uses full multi-head attention. Models with grouped-query attention store fewer KV heads, so use their KV-head count (my addition; the paper doesn't cover it).
- Batch size is set by free KV memory, so fragmentation directly costs throughput. Paging recovers that memory, and the gain is largest with long sequences, big models and sampling or beam search.
- Block size 16 was the default. Swap costs rise with small blocks, so swap is cheaper with larger blocks. Recompute is roughly flat across block sizes 16–64 (p. 13, Fig. 19).
