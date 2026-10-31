**Paper:** *Efficient Memory Management for Large Language Model Serving with PagedAttention* (Kwon et al., SOSP '23, arXiv 2309.06180). It's in the library at `ml-systems/inference-and-serving/`. It introduces PagedAttention and the vLLM serving system, and it is a systems paper, so it covers the memory side of the KV cache rather than the attention math.

## How the KV cache works

**1. Why it exists.** Generation is autoregressive: each new token attends to all earlier tokens. Keys and values for past positions don't change, so they are cached and each step computes only the new token's $q$, $k$, $v$. Attention is then

$$a_{ij}=\frac{\exp(q_i^\top k_j/\sqrt{d})}{\sum_{t=1}^{i}\exp(q_i^\top k_t/\sqrt{d})},\qquad o_i=\sum_{j=1}^{i} a_{ij}\,v_j$$

([p. 3, Eq. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3&rect=90,360,295,398)). The cache is the $k_j, v_j$ for $j<i$.

**2. How big it is.** Per token, the cache is

$$\text{bytes/token} = 2 \times d_{\text{model}} \times L \times \text{bytes per value}$$

For OPT-13B in FP16 that is $2 \times 5120 \times 40 \times 2 \approx 800$ KB per token, so a 2048-token request can need about 1.6 GB ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=280,345,295,356;54,357,105,368)). The cache grows with every generated token and differs per request, so it is the main memory consumer at serving time.

**3. The problem.** Existing systems allocate one contiguous chunk per request, sized for the maximum length. This wastes memory three ways: reserved slots for future tokens, internal fragmentation from over-provisioning, and external fragmentation between chunks ([Fig. 3, p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4)). Effective memory in those systems can be as low as 20.4% ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4); [Fig. 2, p. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=54,71,295,244)).

**4. The fix: paging.** The cache is split into fixed-size blocks, each holding the K/V of a fixed number of tokens. A per-request block table maps logical blocks to physical blocks, which need not be contiguous. Blocks are allocated only when the last one fills, and freed when the request finishes. Attention is computed block by block ([Eq. 4, p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=344,261,559,300)). The paper's analogy is OS virtual memory: blocks are pages, tokens are bytes, requests are processes ([p. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2)).

**5. Sharing.** Sequences from one prompt (parallel sampling, beam search) can point their block tables at the same prompt blocks, and only diverge when they generate new tokens ([§4.4, pp. 6–7](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=6)).

**6. Scheduling.** When memory runs out, requests are preempted FCFS-style. Evicted blocks are either swapped to CPU RAM or recomputed, and [Fig. 19, p. 13](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=13) compares the two.

**Practical numbers:** block size 16 is vLLM's default ([p. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12)). Small blocks underuse the GPU, and large ones add internal fragmentation.

## Measurements

- **Memory budget** ([Table 1, p. 9](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=9&rect=77,73,271,155)): 13B model on one A100-40GB: 26 GB weights, 12 GB KV cache, about 15.7K KV slots. A 66B model on 4×A100 has 21 GB of cache, and 175B on 8×A100-80GB has 264 GB.
- **Throughput** (abstract, [p. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1)): 2–4× the throughput of FasterTransformer and Orca at the same latency.
- **Request rate** ([p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11)): on ShareGPT, 1.7–2.7× Orca (Oracle), 2.7–8× Orca (Max), up to 22× FasterTransformer.
- **Sharing savings** ([Fig. 15, p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=515,614,559,624;490,626,545,636)): 6.1–9.8% for parallel sampling and 37.6–55.2% for beam search on Alpaca. On ShareGPT, the ranges are 16.2–30.5% and 44.3–66.3%.
- **Cost of paging:** attention kernel latency is 20–26% higher than FasterTransformer's, but end-to-end throughput is still higher ([p. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12)).
- **Setup:** A100 GPUs, OPT and LLaMA models, ShareGPT and Alpaca traces ([Table 1, p. 9](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=9&rect=77,73,271,155); [§6.1, p. 10](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=10)).

**Caveats:** Gains depend on the workload's length distribution and on how badly the baselines over-reserve, so the ratios won't transfer directly to other traffic. The Orca variants are the paper's own baselines. The paper predates grouped-query attention and other ways of shrinking the cache, which reduce the size numbers above. Those points are from my own knowledge, not the paper.

I haven't written a `notes/` memory file for this paper.
