**Paper:** *Efficient Memory Management for Large Language Model Serving with PagedAttention* (Kwon et al., SOSP '23, arXiv 2309.06180). It's the vLLM paper, in `ml-systems/inference-and-serving/`. Its 2026 summary and notes are in the library.

## How the KV cache works

- **Why it exists:** Generation is autoregressive. Each new token attends to the keys and values of every earlier token. The model caches those K and V tensors so it doesn't recompute them at each step. [Page 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1&rect=317,177,560,409) (Fig. 1) shows the memory split for a 13B model on an A100: about 65% weights, about 30% KV cache.
- **Size:** For OPT-13B the cache is about 800 KB per token, so a 2048-token request needs up to 1.6 GB ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=130,405,160,416)). That matches 2 (K and V) × 40 layers × 5120 hidden × 2 bytes (fp16) ≈ 820 KB per token. The arithmetic is mine, not the paper's.
- **The problem:** Systems like Orca and FasterTransformer reserve one contiguous chunk per request, sized for the maximum length, since the output length is unknown in advance. That causes three kinds of waste: reserved slots for future tokens, internal fragmentation, and external fragmentation between chunks. Batch size is capped by this memory, and batch size sets throughput.
- **PagedAttention:** It splits each request's cache into fixed blocks of B tokens (default 16), which can sit anywhere in GPU memory. A per-request block table maps logical blocks to physical ones. The attention kernel reads block by block ([Eq. 4, p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=344,261,559,300)). Blocks are allocated on demand, so each request wastes at most one partly filled block.
- **Sharing:** Blocks carry reference counts and are copy-on-write. Parallel sampling, beam search and a shared prompt prefix can reuse the same physical blocks (pp. 6–8).
- **Preemption:** When memory runs out, a whole sequence's blocks are either swapped to CPU RAM or recomputed later (p. 8).

## Measurements

| What | Result | Where |
|---|---|---|
| KV memory that holds token states, existing systems | 20.4–38.2% (a plot, not a table) | [p. 2, Fig. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=54,71,295,244) |
| Throughput vs FasterTransformer and Orca | 2–4× (abstract, p. 1) | p. 1 |
| Request rate vs Orca (Oracle), ShareGPT | 1.7–2.7× higher | p. 10, Fig. 12 |
| Request rate vs FasterTransformer, ShareGPT | up to 22× | p. 10, Fig. 12 |
| Requests batched vs Orca (Oracle), OPT-13B, Alpaca | 2.2× | p. 10, Fig. 13a |
| Memory saved by sharing, beam search | Alpaca 37.6–55.2%, ShareGPT 44.3–66.3% | p. 11, Fig. 15 |
| Memory saved by sharing, parallel sampling | Alpaca 6.1–9.8%, ShareGPT 16.2–30.5% | p. 11, Fig. 15 |
| Shared prefix throughput vs Orca (Oracle) | 1.67× (one-shot), 3.58× (five-shot) | p. 12, Fig. 16 |
| Attention kernel cost vs FasterTransformer | 20–26% slower | p. 12, Fig. 18a |
| Block size | 16–128 best on ShareGPT; 16 is the default | [p. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=340,499,433,510) |

Setup: OPT-13B/66B/175B and LLaMA-13B on A100 GPUs. Workloads are synthetic Poisson traces built from ShareGPT and Alpaca length distributions.

## Caveats

- **Headline vs measured:** The 2–4× headline is not the ratio over Orca (Oracle) in the figures, which runs from 1.3× to 3.58×. The up-to-22× figure is against FasterTransformer.
- **Plots only:** Most results are plots. The "near-zero waste" claim has no table behind it, and no variance is reported.
- **Author-run baselines:** Orca was reimplemented by the authors, since it isn't public.
- **Internal inconsistencies:** Beam-search sharing is "up to 55%" on p. 4 but 66.3% on p. 11. The swap-vs-recompute discussion on p. 13 also contradicts itself.
- **Scope:** Hardware is A100 only.
