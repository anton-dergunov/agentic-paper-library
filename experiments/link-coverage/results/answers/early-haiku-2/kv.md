The paper is **Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention"** (SOSP '23, the vLLM paper). It's in the library at `ml-systems/inference-and-serving/`.

## How the KV cache works

During generation, each new token has to attend to every earlier token. Recomputing the keys and values for the whole prefix at every step would be wasteful, so the model stores them:

- **Prefill:** the whole prompt is processed in parallel, and the keys and values for every prompt token are computed and stored. [p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3)
- **Decode:** each step takes one token, computes only its own query, key and value, appends the new key and value to the cache, and attends over the cache. Keys and values from earlier positions are reused, not recomputed. [p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3)
- The attention output is a softmax-weighted sum over the cached values, with scores from the query against the cached keys (Eq. 3, p. 3). Each step is a matrix-vector product, which is why decoding is memory-bound. [p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3)

**Size per token** is 2 (keys and values) × layers × hidden size × bytes per value. For OPT-13B in FP16, that is 2 × 40 × 5120 × 2 bytes ≈ 800 KB per token, so one 2048-token request can need up to 1.6 GB. [p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=161,357,265,368)

**Why it matters for serving:** the weights are fixed, so the cache sets how many requests fit in a batch. On a 13B model on an A100 40GB, about 65% of memory is weights and about 30% holds request state, mostly KV cache. [p. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1&rect=431,607,560,618;317,619,333,630)

## The fix: PagedAttention

Older systems allocate one contiguous buffer per request, sized for its maximum length. That wastes memory three ways: slots reserved for future tokens, over-provisioning for the maximum length, and fragmentation between buffers. [p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4)

PagedAttention borrows OS paging:

- The KV cache is split into fixed-size blocks, each holding the keys and values for a fixed number of tokens. [p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=317,169,360,180)
- Blocks are allocated on demand and need not be contiguous. A block table maps a request's logical blocks to physical ones. [p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=317,169,360,180)
- The attention kernel computes the score for each block separately and sums the results (Eq. 4, p. 5), so non-contiguous blocks cost nothing extra in the math. [p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=363,238,383,248)
- Blocks can be shared across sequences, for example the prompt in parallel sampling or the common prefix in beam search. [p. 6](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=6)
- The default block size is 16 tokens. Larger blocks hurt when sequences are short. [p. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=425,672,547,683)

## Measurements

| What | Result | Where |
|---|---|---|
| Effective KV memory use in prior systems | Only 20.4–38.2% held real token state; the rest was waste | [p. 2, Fig. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=54,222,92,232) |
| Throughput vs. FasterTransformer and Orca, same latency | 2–4× | [p. 1, abstract](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1&rect=239,352,295,362;54,364,210,374) |
| Request rate sustained on ShareGPT | 1.7–2.7× Orca (Oracle), 2.7–8× Orca (Max) | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=251,433,295,443;54,445,134,455) |
| Memory saved by sharing, parallel sampling | 6.1–9.8% (Alpaca) | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=515,614,559,624;317,626,383,636) |
| Memory saved by sharing, beam search | 37.6–55.2% (Alpaca) | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=490,626,545,636) |

The sharing numbers are block savings: blocks saved divided by blocks needed without sharing. [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11)

**Caveats:** these are 2023 results on OPT and LLaMA models on A100s, with their own traces (ShareGPT and Alpaca). The gains are largest with long sequences, big models and complex decoding, and smaller where the GPU has spare memory. [p. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1) The paper's gain is in batch size and throughput, not per-token latency.

I didn't write a note or review for this paper, and I didn't change anything in the repo.
