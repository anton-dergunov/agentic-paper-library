**Paper:** Kwon et al., *Efficient Memory Management for Large Language Model Serving with PagedAttention* (arXiv 2309.06180, the vLLM paper), in `library/ml-systems/inference-and-serving/`.

## How the KV cache works

- **Why it exists:** Generation is autoregressive, so each new token attends to every earlier token. Each earlier token's key and value vectors depend only on that token and its prefix, so they are computed once and stored. Each decode step then computes only the new token's query, key and value, and attends over the stored keys and values ([p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3&rect=170,648,295,659;54,660,112,671)).
- **The attention step** that reads the cache is $o_i=\sum_j a_{ij} v_j$, with $a_{ij}=\mathrm{softmax}_j\!\left(q_i^\top k_j/\sqrt{d}\right)$ ([Eq. 3, p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3)).
- **Two phases:**
  - *Prefill:* the whole prompt goes through in one parallel pass, which fills the cache.
  - *Decode:* one token per step. This is a matrix-vector workload and is memory-bound, so the cache's size and how it is laid out decide throughput.
- **Size per token:** $2 \times L \times d \times \text{bytes}$ (keys and values × layers × hidden size × bytes per value). For OPT-13B in FP16 that is $2 \times 40 \times 5120 \times 2 \approx 800$ KB per token, or about 1.6 GB for a 2048-token request ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=280,345,295,356;54,357,67,368)).
- **Why serving is hard:** on a 40 GB A100, about 65% of memory holds weights and close to 30% holds the KV cache ([p. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1&rect=431,607,560,618)). The cache's size bounds how many requests can be batched.

## The fix the paper proposes (PagedAttention / vLLM)

Existing systems reserve one contiguous chunk per request, sized for the maximum length. The paper measures that only 20.4%–38.2% of that memory holds real token states ([p. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=195,660,269,671)).

vLLM instead:
- splits each sequence's cache into fixed-size blocks of B tokens (default 16) that can sit anywhere in GPU memory;
- uses a per-request block table that maps logical blocks to physical ones, and allocates blocks on demand, so each request wastes at most one block ([p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5)); the attention kernel is changed to read blocks through this table;
- shares blocks by reference count with copy-on-write, for parallel sampling, beam search and shared prompt prefixes.

The paper is about memory layout and sharing. It does not shrink the cache through quantization or eviction.

## Measurements

Metric: **normalized latency** (mean end-to-end latency divided by output length), plotted against request rate. Throughput is the request rate sustained at similar latency. The paper does not say what latency threshold "similar" means.

| Result | Number | Where |
|---|---|---|
| ShareGPT, basic sampling vs Orca (Oracle) | 1.7×–2.7× request rate | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=251,433,295,443) |
| vs FasterTransformer | up to 22× request rate | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=64,541,168,551) |
| Shared 5-shot prefix (LLaMA-13B) | 3.58× throughput vs Orca (Oracle) | p. 12 |
| Memory saved by beam-search sharing (Alpaca) | 37.6%–55.2% | p. 11 |
| Attention kernel cost of block-table lookups | 20–26% slower than FasterTransformer's kernel | [p. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=371,408,536,419) |

## Caveats

- Results are author-run, most are plots only, and no variance is reported.
- The kernel cost is the price of paging; the headline gain comes from batching more requests.
- The abstract's "2–4×" does not match the measured range (1.3× to 3.58× over Orca, up to 22× over FasterTransformer).
- The paper gives beam-search sharing as "up to 55%" on p. 4 and 66.3% on p. 11.
- "Without affecting the model accuracy at all" is asserted, not measured.
