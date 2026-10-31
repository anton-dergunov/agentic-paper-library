## How the KV cache works

**Why it exists.** A decoder-only Transformer generates one token at a time. Each new token attends to every earlier token, so it needs their key and value vectors. Recomputing them at every step would waste work, so the model stores them and reuses them. The paper calls this the KV cache (p. 3, Sec. 2.2: "the key and value vectors of existing tokens are often cached for generating future tokens").

**Two phases** (p. 3, Sec. 2.2):

1. **Prompt (prefill):** all prompt tokens are processed in parallel as a matrix-matrix product. This computes and stores K and V for every prompt position. It uses the GPU well.
2. **Generation (decode):** each step processes one new token. It computes only that token's q, k and v, appends k and v to the cache, and attends over the whole cache. This is matrix-vector work and memory-bound, and it is most of a request's latency.

**The attention step.** The output for position i is a softmax-weighted sum of cached values, with the query scored against cached keys ([p. 3, Eq. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3)). Because the cache holds all earlier positions, each token's K and V depend on its position and on everything before it. The same word at two positions has different cache entries (p. 3).

**Size, the practical constraint.** For OPT-13B in FP16, one token needs 2 (K and V) × 5120 (hidden size) × 40 (layers) × 2 bytes ≈ 800 KB ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=280,345,295,356;54,357,67,368)). A 2048-token request therefore needs about 1.6 GB. Per token, the cost scales with layers × hidden size, and it grows with batch size × sequence length, so memory caps how many requests can run together.

**Toy example (ours, not from the paper).** Suppose a model has 2 layers, hidden size 4 and FP16 values. Each token adds 2 × 4 × 2 × 2 = 32 bytes. A 1,000-token conversation holds 32 KB of cache. At 100 concurrent conversations that is 3.2 MB, and it grows with every token generated, so the cache is allocated and freed continuously during serving.

## What the paper measures

The paper is vLLM / PagedAttention (SOSP '23). Its problem is that serving systems allocate each request's KV cache as one contiguous block sized for the maximum length, which wastes memory.

- **Where the memory goes.** For a 13B model on an A100-40GB, about 65% holds the weights and about 30% holds the dynamic request state, mostly KV cache ([p. 1, Fig. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1&rect=431,607,509,618)).
- **Waste in existing systems.** Only **20.4%–38.2%** of KV memory held actual token states in existing systems ([p. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=216,660,269,671); breakdown in Fig. 2 on p. 2). Waste comes from reserved future slots, internal fragmentation and external fragmentation (Fig. 3, p. 4).
- **The fix.** PagedAttention splits each request's KV cache into fixed-size blocks of 16 tokens, mapped through a block table, as OS virtual memory maps pages ([p. 5, Sec. 4.1–4.2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5)). Blocks are allocated on demand. The attention kernel reads blocks separately, so they need not be contiguous ([p. 5, Eq. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=344,261,559,300)).
- **Sharing.** Reference-counted blocks let sequences share a prompt's KV cache, and beam candidates share prefixes. Copy-on-write copies a block only when a sequence must write to a shared block ([p. 7](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=7&rect=393,608,539,619)).

**Results**

| Measurement | Value | Where |
|---|---|---|
| Throughput vs FasterTransformer and Orca at equal latency | 2–4× | [p. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=382,457,402,467) |
| ShareGPT, sustained request rate vs Orca (Oracle) / Orca (Max) | 1.7–2.7× / 2.7–8× | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=515,614,559,624) |
| Memory saved by sharing, parallel sampling / beam search (Alpaca) | 6.1–9.8% / 37.6–55.2% | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=515,614,559,624) |
| Attention kernel overhead vs FasterTransformer | 20–26% higher latency | [p. 12, Sec. 7.1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=371,408,432,419) |
| Default block size | 16 tokens | [p. 12, Sec. 7.2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=317,708,445,718) |

Hardware and models are in [Table 1, p. 9](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=9&rect=77,73,271,155): 13B on one A100-40GB, 66B on 4×A100, and 175B on 8×A100-80GB. The KV budget is 12 GB, 21 GB and 264 GB, giving 15.7K, 9.7K and 60.1K KV slots.

## Practical takeaways

- Caching makes decoding linear in the sequence length instead of quadratic. The price is memory that grows with batch × length × layers × hidden size.
- Pre-allocating for the maximum length wastes most of the cache. Paging the cache, as the paper does, puts that memory back into batching.
- The block size is a trade-off. Small blocks use the GPU poorly and cost more to swap; large blocks increase internal fragmentation and reduce sharing (p. 12).

**Scope.** This paper covers serving-side memory management. It does not cover reducing the cache itself (quantization, eviction, or compressed attention). I did not search for those, so I can't say what the library lacks there.
