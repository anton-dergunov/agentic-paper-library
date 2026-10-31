I'll start by searching the library for KV cache papers.

The library has the PagedAttention paper (vLLM). I'll check for an existing note and the text.

There's an existing note. I'll read it and pull the evaluation numbers from the text.

The note covers the main results. I'll get exact link rectangles for the passages I plan to cite.

**KV cache, in short:** during generation the model makes one token at a time, and each new token attends to the keys and values of every earlier token. The cache stores those keys and values so they are computed once and reused, instead of being recomputed at every step. The cost is memory, and that memory limits how many requests a GPU can serve at once.

The paper in the library is Kwon et al., 2023, *Efficient Memory Management for Large Language Model Serving with PagedAttention* (the vLLM paper, SOSP '23). It is in `library/ml-systems/inference-and-serving/`, and it describes the KV cache and how to manage it.

**How it works**

- **Decoding is sequential.** Each step computes attention for the new token against all previous ones. The paper gives the attention formula as [Eq. 3, p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3):
  $$a_{ij}=\frac{\exp(q_i^\top k_j/\sqrt{d})}{\sum_{t=1}^{i}\exp(q_i^\top k_t/\sqrt{d})},\qquad o_i=\sum_j a_{ij}\,v_j$$
- **Only the new token's key and value are computed.** The keys and values of earlier positions are read from the cache. [p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3) describes the prompt phase, which fills the cache in parallel, and the generation phase, which reads it one token at a time and is memory-bound.
- **The cache grows with every token.** For OPT-13B, the paper gives 2 (K and V) × 5120 (hidden size) × 40 (layers) × 2 bytes = [800 KB per token](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=280,345,295,356;54,357,67,368), or about 1.6 GB for one 2048-token request (p. 4).
- **Memory limits the batch.** On a 13B model on a 40 GB A100, weights take about 65% of memory and the KV cache about 30% ([p. 1, Fig. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1)). Batching many requests is what gives throughput, so the cache's memory use caps throughput.

**The problem with existing systems:** they allocate each request one contiguous chunk sized for its maximum length. This wastes memory through reserved slots, internal fragmentation and external fragmentation. Only [20.4–38.2% of KV memory holds real tokens](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=130,660,152,671) (p. 2, Fig. 2, read from a plot).

**The fix, PagedAttention (vLLM):**

- Split each request's KV cache into fixed-size blocks of B tokens. The blocks need not be contiguous in GPU memory (§4.1, [pp. 5–6](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=6)).
- A per-request block table maps logical blocks to physical ones, like OS page tables. Blocks are allocated on demand, so a request wastes at most one partly filled block.
- Blocks are reference-counted and can be shared between sequences (parallel sampling, beam search, a shared prompt prefix), with copy-on-write when they diverge (pp. 6–8).
- The attention kernel loops over blocks (Eq. 4, [p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=363,238,383,248)). The default block size is 16 tokens (p. 12).

**Measurements**

- **Metric:** normalized latency, meaning mean end-to-end latency divided by output length, plotted against request rate ([p. 10](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=10)). Throughput is the request rate sustained at similar latency.
- **Setup:** OPT-13B/66B/175B and LLaMA-13B on A100 GPUs; ShareGPT and Alpaca length distributions; 1-hour traces (15 minutes for OPT-175B). Baselines are FasterTransformer and Orca, which the authors reimplemented in three memory-allocation variants.
- **Headline:** 2–4× throughput over FasterTransformer and Orca at the same latency (p. 1).
- **Basic sampling (ShareGPT):** 1.7–2.7× over Orca (Oracle), 2.7–8× over Orca (Max), and up to 22× over FasterTransformer ([p. 10](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=10)). OPT-13B batches 2.2× more requests than Orca (Oracle).
- **Beam search:** the gain over Orca (Oracle) on Alpaca rises from 1.3× (basic sampling) to 2.3× (beam width 6) (p. 11).
- **Memory saved by sharing:** beam search [37.6–55.2%](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=490,626,545,636) on Alpaca and 44.3–66.3% on ShareGPT; parallel sampling 6–10% (Alpaca) and 16–31% (ShareGPT) (p. 11).
- **Shared prefix (LLaMA-13B, translation):** [1.67× with a one-shot prefix and 3.58× with five-shot](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=203,436,227,446) (p. 12).
- **Cost:** the paged attention kernel is [20–26% slower](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=371,408,402,419) than FasterTransformer's attention, because of block-table lookups (p. 12).

**Caveats**

- The results come from the authors' own runs. The Orca baseline is their reimplementation, most results are plots only, and no variance is reported.
- The paper asserts that accuracy is unaffected but does not measure it (p. 2).
- It contradicts itself on beam-search savings: the introduction says "up to 55%" (p. 4), while §6.3 reports 66.3% (p. 11).
- This is 2023 hardware and models. Later serving stacks use grouped-query attention and quantized KV caches, which shrink the per-token size. That is general knowledge, not from this paper.

For a quick sizing estimate, the paper's formula gives KV bytes = 2 × layers × hidden × bytes × tokens. The library has a note with more detail at `notes/Efficient Memory Management for Large Language Model Serving with PagedAttention.md`. I made no changes to the repository.
