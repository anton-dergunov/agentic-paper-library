I'll search the library for papers on KV caching first, before going to the web.

The library has one KV-cache paper, PagedAttention (vLLM). I'll check its text and whether a note or review exists.

The paper is the key source. I'll read the passages on KV size, waste, the algorithm, and the evaluation.

Next, the evaluation numbers: the throughput results, the memory-capacity table, and the block-size ablation.

I have the passages and page numbers. Next I'll get exact highlight rectangles for the citations, as the library's conventions ask.

The library's only KV-cache paper is **PagedAttention / vLLM** (Kwon et al., SOSP 2023, [arXiv:2309.06180](https://arxiv.org/abs/2309.06180)), filed under `ml-systems/inference-and-serving`. It has no note or review yet.

## How the KV cache works

**Why it exists.** Generation is autoregressive: each new token attends to every earlier token. The key and value vectors of earlier tokens don't change, so they're computed once and cached. Each decode step then computes only the new token's query, key and value. The prompt is processed in parallel (prefill), while decoding is sequential and memory-bound ([p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3)). The attention computation the cache serves is:

$$
a_{ij} = \frac{\exp(q_i^\top k_j/\sqrt{d})}{\sum_{t=1}^{i} \exp(q_i^\top k_t/\sqrt{d})}, \qquad o_i = \sum_{j=1}^{i} a_{ij}\, v_j
$$

Here $q_i$ is the query of token $i$, and $k_j, v_j$ are the cached keys and values of earlier tokens ([Eq. 3, p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3&rect=90,360,295,398)).

**How big it is.** Per token, the cache holds keys and values for every layer:

$$
\text{bytes/token} = 2 \times n_{\text{layers}} \times d_{\text{kv}} \times \text{bytes per element}
$$

For OPT-13B in FP16 this is $2 \times 5120 \times 40 \times 2 \approx 800$ KB per token, so a 2048-token request needs about 1.6 GB ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=242,345,295,356)). The formula is my general form, not the paper's; models with grouped-query attention have a smaller $d_{\text{kv}}$.

**The practical problem.** Length is unknown in advance and the cache grows token by token. Earlier systems reserved one contiguous chunk per request at its maximum length, which wastes memory through reservation, internal fragmentation and external fragmentation. Only 20.4–38.2% of the KV memory held real token states ([p. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=195,660,269,671)). Wasted memory limits the batch size, and batch size sets throughput.

**The fix (PagedAttention).** Treat the cache like OS virtual memory ([p. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=406,254,473,264): "blocks as pages, tokens as bytes, requests as processes"):

- Split each request's cache into fixed-size blocks, each holding a fixed number of tokens. The default is 16 ([p. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=425,672,547,683)).
- Allocate blocks on demand, and map logical blocks to physical ones through a block table. The blocks need not be contiguous ([p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=148,617,281,627)).
- The attention kernel reads the blocks separately and combines their partial scores ([p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5)).
- Share blocks across sequences: prompts in parallel sampling and beam search, and common prefixes.

## Measurements

| What | Result | Where |
|---|---|---|
| Serving throughput vs FasterTransformer and Orca, at the same latency | 2–4× | [p. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1&rect=54,364,210,374) |
| ShareGPT, sustainable request rate | 1.7–2.7× vs Orca (Oracle), 2.7–8× vs Orca (Max), up to 22× vs FasterTransformer | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=120,505,244,515) |
| Memory saved by sharing, parallel sampling | 6.1–9.8% (Alpaca), 16.2–30.5% (ShareGPT) | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=515,614,559,624) |
| Memory saved by sharing, beam search | 37.6–55.2% (Alpaca), 44.3–66.3% (ShareGPT) | [p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=490,626,545,636) |
| Setup: 13B model on one 40 GB A100 | 12 GB of KV cache, about 15.7K token slots | [Table 1, p. 9](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=9&rect=77,138,150,147) |
| Swapping to CPU vs recomputing evicted blocks | Recomputation costs at most 20% of swapping's latency; swapping wins at large block sizes | [p. 13](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=13&rect=135,379,295,390) |

The paper reports no accuracy change: the gain is "without affecting the model accuracy at all" ([p. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1)).

## Caveats

- All numbers come from 2023 vLLM against 2023 baselines (A100 GPUs, OPT and LLaMA, ShareGPT and Alpaca traces). They measure serving throughput and capacity, not single-request latency.
- The paper covers only the memory layout. It does not cover shrinking the cache: quantization, eviction, or grouped-query attention. The library has nothing on those, so a fuller answer would need papers from outside it.

I haven't written a note for this paper; I can add one to `notes/` or search the web for the cache-compression papers.
