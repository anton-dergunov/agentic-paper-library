The paper to read is **PagedAttention / vLLM** (Kwon et al., SOSP '23), the only KV-cache paper in the library. Its note is at `notes/Efficient Memory Management for Large Language Model Serving with PagedAttention.md`, and I checked the claims below against the PDF text.

## How the KV cache works

**Why it exists.** A decoder-only LLM generates one token at a time. Each new token attends to every earlier token. Without a cache, every step would recompute keys and values for the whole prefix. So each layer stores the key and value vectors of each token and reuses them. Each step computes only the new token's `k` and `v`, then attends over the stored ones. The attention is `o_i = Σ_j a_ij v_j`, with `a_ij = softmax_j(q_iᵀk_j / √d)` ([p. 3, Eqs. 2–3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3&rect=90,360,295,398)).

**Why it's big.** Per token, the cache is `2 (K and V) × hidden × layers × bytes`. For OPT-13B in FP16 that is 2 × 5120 × 40 × 2 B ≈ 800 KB per token, or about 1.6 GB for one 2048-token request ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=280,345,295,356;54,357,67,368)). On a 40 GB A100, about 65% of memory holds weights and about 30% holds the KV cache ([p. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1)). The cache, not compute, limits how many requests you can batch.

**The waste problem.** Existing servers reserve one contiguous chunk per request, sized for the maximum length. Only 20.4–38.2% of that memory holds real token states; the rest is reserved-but-unused, internal fragmentation, or external fragmentation ([p. 2, Fig. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=54,71,295,244)). The values come from a plot.

**The fix (PagedAttention).**
- Split each sequence's cache into fixed-size blocks of `B` tokens (default 16). Blocks can sit anywhere in GPU memory.
- A per-request block table maps logical blocks to physical blocks and records how many slots are filled ([p. 6](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=6)). Blocks are allocated on demand, so each request wastes at most one partial block.
- The kernel computes attention block by block: `o_i = Σ_j V_j A_ijᵀ`, where `A_ij` is the slice of attention scores on block `j` ([p. 5, Eq. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=344,261,559,300)).
- Physical blocks are reference-counted and copy-on-write. Parallel sampling, beam search and shared prompts can point at the same blocks. The kernel does not need to know about the sharing.
- When memory runs out, a whole sequence is either swapped to CPU RAM or recomputed from the prompt ([p. 8](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=8), [p. 13](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=13)).

## Measurements

Setup: OPT-13/66/175B and LLaMA-13B on A100 instances. Workloads are Poisson-arrival traces built from ShareGPT and Alpaca length distributions. The metric is normalized latency (mean end-to-end latency divided by output length) against request rate ([p. 10](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=10)).

| Result | Number | Where |
|---|---|---|
| ShareGPT, sustainable request rate vs Orca (Oracle / Max) | 1.7–2.7× / 2.7–8× | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11) |
| Same, vs FasterTransformer | up to 22× | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11) |
| Requests batched, OPT-13B, vs Orca (Oracle / Max) | 2.2× / 4.3× | [p. 11, Fig. 13a](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11) |
| Parallel sampling / beam width 6, vs Orca (Oracle) | 1.3× → 2.3× | [p. 11, Fig. 14](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11) |
| Memory saved by sharing, beam search (Alpaca / ShareGPT) | 37.6–55.2% / 44.3–66.3% | [p. 11, Fig. 15](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11) |
| Shared prefix (WMT16), one-shot / five-shot, vs Orca (Oracle) | 1.67× / 3.58× | [p. 12, Fig. 16](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12) |
| Kernel overhead vs FasterTransformer's kernel | 20–26% slower | [p. 12, Fig. 18a](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=371,408,402,419) |
| Block size | 16–128 best on ShareGPT; 16–32 on Alpaca; default 16 | [p. 12, Fig. 18b](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12) |

The abstract's headline is 2–4× throughput at the same latency ([p. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1)). Against Orca (Oracle), the measured ratios range from 1.3× to 3.58×.

## Caveats

- Most results are plots, not tables. The "near-zero waste" claim is shown only in Fig. 2 as a plot.
- The authors ran all the experiments. Orca was reimplemented, and no variance is reported.
- The paper does not state the latency threshold behind "similar latency".
- The paper contradicts itself in places. The beam-search memory saving is "up to 55%" on p. 4 but 66.3% on p. 11. It also says recomputation is never more than 20% of swapping's latency, yet also that swapping wins at large block sizes (p. 13).
- It is an A100-only study, and the paper does not compare against compaction.

## Practical takeaway

For serving, the KV cache sets your batch size. Allocate it in small blocks on demand, rather than one max-length chunk per request. Share blocks wherever requests have a common prefix or sample several outputs. The gain grows with longer contexts, larger models and more complex decoding, per the authors' own summary (p. 1).
