The paper is **"Efficient Memory Management for Large Language Model Serving with PagedAttention"** (the vLLM paper, Kwon et al. 2023). It's in your library under `ml-systems/inference-and-serving`. Its §2–3 explain the KV cache, and the rest is about managing it. I read the text and your existing note. The numbers below come from the note, with page links added.

## How the KV cache works

**The idea.** A Transformer generates one token at a time. Each token's attention needs the key and value vectors of all earlier tokens. Those vectors depend only on the earlier tokens, so they never change. Recomputing them at every step would be wasteful, so you store them. That store is the KV cache.

**The equations.** Each position gets $q_i = W_q x_i$, $k_i = W_k x_i$, $v_i = W_v x_i$. Attention is then

$$a_{ij} = \frac{\exp(q_i^\top k_j/\sqrt d)}{\sum_{t=1}^{i}\exp(q_i^\top k_t/\sqrt d)},\qquad o_i=\sum_{j=1}^{i} a_{ij}v_j$$

See [p. 3, Eq. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3&rect=90,360,295,398). Here $q_i$ is the query at position $i$, and it is multiplied by all earlier keys $k_j$.

**Two phases.**
1. **Prompt (prefill).** All prompt tokens go through the model in parallel, and their K and V are written to the cache.
2. **Generation (decode).** Each step feeds in one token and computes only its new $k$ and $v$. It reads the rest from the cache ([p. 3: "only the new key and value vector…"](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3&rect=317,246,464,256)). This step is a matrix-vector product, so it is memory-bound and uses the GPU poorly.

**Example.** For a 100-token prompt, step 101 computes one new $k$ and $v$. It attends over the 100 cached pairs instead of recomputing them. The cost per step drops from reprocessing the whole sequence to one token plus a cache read.

**What it costs.** The cache is big. For OPT-13B, one token takes 2 (K and V) × 5120 (hidden size) × 40 layers × 2 bytes (FP16) = **800 KB** ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=161,357,265,368)). A 2048-token request therefore needs up to 1.6 GB. Serving throughput depends on how many requests fit in GPU memory at once, so the cache size sets the batch size.

## What the paper does about it

Older systems reserve one contiguous chunk per request, sized for its maximum length. That wastes memory on slots reserved for future tokens and on internal and external fragmentation. Only **20.4–38.2%** of KV memory held real token states ([p. 2, Fig. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=54,71,295,244), read off a plot).

PagedAttention works like OS virtual memory:
- It splits each sequence's cache into fixed blocks of 16 tokens by default.
- Blocks can sit anywhere in GPU memory.
- A per-request block table maps logical blocks to physical ones.
- The kernel attends block by block ([p. 5, Eq. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=344,261,559,300)).
- Blocks are allocated on demand, so each request wastes at most one block.
- Reference counts and copy-on-write let requests share blocks. This helps with parallel sampling, beam search and shared system prompts.

## Measurements

The paper ran OPT-13B/66B/175B and LLaMA-13B on A100s. The workloads were synthetic Poisson arrivals built from ShareGPT and Alpaca length distributions. The baselines were FasterTransformer and the authors' own reimplementation of Orca. The metric is normalized latency (mean end-to-end latency divided by output length) against request rate.

| Result | Number | Source |
|---|---|---|
| Sustained request rate on ShareGPT, vs Orca (Oracle) / Orca (Max) / FasterTransformer | 1.7–2.7× / 2.7–8× / up to 22× | [p. 10, Fig. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=10&rect=54,71,557,280) |
| Batch size on OPT-13B, vs Orca (Oracle) / Orca (Max) | 2.2× / 4.3× | p. 10, Fig. 13a |
| Memory saved by sharing, beam search / parallel sampling (Alpaca) | 37.6–55.2% / 6.1–9.8% | p. 11, Fig. 15 |
| Shared prefix throughput vs Orca (Oracle), 1-shot / 5-shot | 1.67× / 3.58× | p. 12, Fig. 16 |
| Attention kernel overhead vs FasterTransformer | 20–26% slower | [p. 12, Fig. 18a](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=317,71,550,201) |

**Caveats.**
- The headline "2–4×" is not what the figures show. Gains over Orca (Oracle) range from 1.3× to 3.58×, and over FasterTransformer they reach 22×.
- All numbers are author-run on A100s, with no variance reported.
- Most results exist only as plots.
- "No accuracy impact" is asserted, not measured.
- The paper never states the latency threshold behind "similar latency".

**Related in your library:** Orca (iteration-level scheduling, the main baseline), FlashAttention (the kernel used for prefill), FlexGen (offloading) and Megatron-LM (the tensor parallelism vLLM adopts).

I can read further into a particular part if you want, such as the swap-versus-recompute trade-off or the copy-on-write mechanics.

**Suggested commit message:** No repository files changed, so there is nothing to commit.
