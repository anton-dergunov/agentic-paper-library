**Short answer:** during generation, a transformer caches each token's key and value vectors so it doesn't recompute them for every later token. The cache grows with every token and every request, and in serving it is usually what limits how many requests fit on a GPU. The paper I'd read is the vLLM / PagedAttention paper, which is in the library under `ml-systems/inference-and-serving`. It's a systems paper, so it's strong on how the cache is managed and measured, but its evidence is author-run and mostly plots.

## How it works

1. **Prefill.** The prompt's tokens are processed in one pass, and their keys and values are stored. Each position gets $q_i = W_q x_i$, $k_i = W_k x_i$, $v_i = W_v x_i$ ([p. 3, Eq. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3&rect=108,283,295,293)).
2. **Decode.** Each new token computes only its own $k_{n+t}$ and $v_{n+t}$ and appends them to the cache. Its attention is a softmax over the query against all cached keys, applied to the cached values. Earlier positions are never recomputed.
3. **Why it is a memory problem.** Each decode step is a matrix-vector product that reads the whole cache, so it is memory-bound and underuses the GPU. The cache for one token is large: about 800 KB for OPT-13B, or up to 1.6 GB for a 2,048-token request ([p. 1, Fig. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1); the note also cites p. 4). On a 40 GB A100, about 30% of memory holds the KV cache, and that share caps the batch size.
4. **Waste in existing systems.** Frameworks reserve one contiguous slab per request, sized for the maximum length. The paper finds that only **20.4%–38.2%** of KV memory holds real token states ([p. 2, Fig. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=54,71,295,244); values read from a plot).
5. **PagedAttention fix.** Each sequence's KV cache is split into fixed blocks of $B$ tokens (default 16) that can sit anywhere in GPU memory. A per-request block table maps logical blocks to physical ones. The attention is computed block by block ([p. 5, Eq. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=344,261,559,300)). Blocks are allocated on demand, so each request wastes at most one partly filled block. Blocks are reference-counted, so requests with a shared prefix, parallel samples and beams can share them copy-on-write.

## Measurements

- **Memory.** Share of KV memory that holds real tokens (above). Memory saved by block sharing: 6.1–9.8% for parallel sampling and 37.6–55.2% for beam search on Alpaca; 16.2–30.5% and 44.3–66.3% on ShareGPT (pp. 11, Fig. 15).
- **Latency and throughput.** The metric is normalized latency: mean end-to-end latency divided by output length, plotted against request rate, on Poisson-arrival traces built from ShareGPT and Alpaca lengths. vLLM sustains **1.7–2.7×** the request rate of Orca (Oracle) and up to **22×** that of FasterTransformer ([p. 10, Fig. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=10&rect=54,71,557,280)).
- **Prefix sharing.** On WMT16 with a shared prefix, throughput is **1.67×** (one-shot) and **3.58×** (five-shot) that of Orca (Oracle) ([p. 12, Fig. 16](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12)).
- **Costs.** The custom attention kernel is 20–26% slower than FasterTransformer's because of block-table lookups (p. 12, Fig. 18a). Block sizes of 16–128 work best on ShareGPT, and 16–32 on Alpaca (p. 12, Fig. 18b).
- **Swap vs recompute.** Evicted blocks can be swapped to CPU RAM or recomputed. The two cost about the same at block sizes 16–64 (p. 13, Fig. 19).

## Caveats

- The abstract's "2–4×" headline doesn't match the measured ratios, which range from 1.3× to 3.58× against Orca. The 22× figure is against FasterTransformer.
- Most results are plots, and there is no variance reporting. The "no accuracy change" claim is asserted rather than measured (p. 2).
- The paper contradicts itself in places: it gives a 55% beam-search saving in one spot and 66.3% in another (pp. 4, 11). The note lists these.
- Hardware is A100 only, and the Orca baseline is the authors' reimplementation.

The note for this paper is at `notes/Efficient Memory Management for Large Language Model Serving with PagedAttention.md`, and the paper itself is at `library/ml-systems/inference-and-serving/Efficient Memory Management for Large Language Model Serving with PagedAttention.txt`. I didn't change either file.
