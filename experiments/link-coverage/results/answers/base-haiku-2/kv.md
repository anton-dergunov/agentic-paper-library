The library has one paper that covers this directly: the vLLM PagedAttention paper. I'll read its key sections.

**Short answer:** the KV cache stores each token's attention keys and values so that generating the next token doesn't recompute them for the whole prefix. Its size grows with every token, and that growth limits how many requests you can batch. The library's main paper on this is the vLLM/PagedAttention paper (Kwon et al., 2023), which is the one source I checked.

## How it works

- **Why cache:** at decoding step *i*, the query of the new token attends to the keys and values of every earlier token. With $q_i = W_q x_i$, $k_j = W_k x_j$, $v_j = W_v x_j$ (Eq. 2, p. 3), the output is $o_i = \sum_j \mathrm{softmax}_j\!\left(\frac{q_i k_j^\top}{\sqrt{d}}\right) v_j$ (Eq. 3, p. 3). The keys and values for earlier tokens never change, so they are stored and only the new token's $k$ and $v$ are added each step.
- **Size:** each token's keys and values exist in every layer and head, so the cache grows linearly with sequence length and batch size. The paper gives up to 1.6 GB for one 2048-token request on a 13B model ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=130,405,160,416)). On a 40 GB A100, weights take about 65% of memory and the KV cache can take the rest ([p. 1, Fig. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1)).
- **The bottleneck:** the batch size is set by how much KV memory is free, so throughput depends on how well the cache is managed.
- **Waste in existing systems:** each request got one contiguous slab sized for its maximum length. Only 20.4–38.2% of the reserved memory held real token states ([p. 2, Fig. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=54,71,295,244)).
- **PagedAttention:** the cache is split into fixed-size blocks of *B* tokens (16 by default) that can sit anywhere in GPU memory. A per-request block table maps logical blocks to physical ones, and the kernel fetches block by block ([p. 5, Fig. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=317,70,560,204)). Blocks are allocated on demand, so each request wastes at most one partly filled block.
- **Sharing:** physical blocks carry reference counts, so parallel sampling, beam search and a shared prompt can reuse the same blocks, with copy-on-write when they diverge ([pp. 6–8](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=6)).
- **Eviction:** when memory runs out, a whole sequence is swapped to CPU RAM or dropped and recomputed later ([p. 8](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=8)).

## Measurements

- **Setup:** OPT-13B/66B/175B and LLaMA-13B on A100 GPUs. Requests come from ShareGPT and Alpaca length distributions with Poisson arrivals ([p. 10](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=10)).
- **Metric:** normalized latency, the mean end-to-end latency divided by output length, plotted against request rate ([p. 10](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=10&rect=54,71,557,280) is the figure).
- **Throughput:** on ShareGPT, vLLM sustains 1.7–2.7× the request rate of Orca (Oracle) and up to 22× that of FasterTransformer. On OPT-13B it batches 2.2× more requests than Orca (Oracle) ([p. 10](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=10)).
- **Sharing:** beam search saves 44–66% of blocks on ShareGPT and 38–55% on Alpaca ([p. 11, Fig. 15](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=317,298,558,404)).
- **Cost:** the attention kernel is 20–26% slower than FasterTransformer's ([p. 12, Fig. 18](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=317,71,550,201)).

## Caveats

- The results are author-run. Most are plots with no variance, and the paper doesn't state the latency threshold behind "similar latency".
- The "2–4×" headline compares against FasterTransformer and Orca. The ratio over the strongest Orca variant is 1.7–2.7× on ShareGPT.
- The paper is inconsistent on sharing savings: it says "up to 55%" on p. 4 and reports 66.3% on p. 11.

Written from the library's agent note (`notes/…PagedAttention.md`) and checked against the text layer for the main numbers. The 800 KB-per-token figure in the note did not appear in the text layer, so I left it out.
