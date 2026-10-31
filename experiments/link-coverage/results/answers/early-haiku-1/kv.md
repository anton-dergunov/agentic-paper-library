**Paper:** [Efficient Memory Management for LLM Serving with PagedAttention](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1) (Kwon et al., SOSP 2023, arXiv 2309.06180). It introduces vLLM.

## How the KV cache works

1. **Why it exists.** Generation is autoregressive: each new token attends to all earlier tokens. At step *t*, the model needs the keys and values of every earlier position, but only computes the new token's *k* and *v*. Earlier ones are cached ([p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3)). The attention output for position *i* is

$$o_i = \sum_{j=1}^{i} a_{ij}\, v_j, \qquad a_{ij} = \frac{\exp(q_i^\top k_j/\sqrt{d})}{\sum_{t=1}^{i} \exp(q_i^\top k_t/\sqrt{d})}$$

   Only $q_i$ is new per step. Every $k_j$ and $v_j$ is reused from the cache.

2. **How big it is.** Per token: $2 \times d_{\text{hidden}} \times L \times \text{bytes}$. For OPT-13B in FP16 that is $2 \times 5120 \times 40 \times 2 \approx 800$ KB per token, or up to 1.6 GB for one 2048-token request ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=280,345,295,356;54,357,67,368)). On a 40 GB A100 serving a 13B model, weights take about 65% of memory and the KV cache about 30% ([p. 1, Fig. 1](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1)). The KV cache therefore caps the batch size, and batch size sets throughput.

3. **The problem with the usual layout.** Systems store each request's cache as one contiguous tensor sized for the maximum length. That wastes memory through reservation, internal fragmentation (short outputs leave slots unused) and external fragmentation (chunks differ in size). Only 20.4%–38.2% of KV memory holds real token states ([p. 2, Fig. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=54,222,92,232)).

4. **The fix: paging.** The cache is split into fixed-size blocks of *B* tokens (default 16). Blocks can live anywhere in GPU memory, and a per-request block table maps logical blocks to physical ones. Blocks are allocated on demand, so waste is limited to the last partly filled block. Attention is computed block by block:

$$A_{ij} = \frac{\exp(q_i^\top K_j/\sqrt{d})}{\sum_{t=1}^{\lceil i/B\rceil} \exp(q_i^\top K_t/\sqrt{d})}, \qquad o_i = \sum_{j} V_j A_{ij}^\top$$

   ([Eq. 4, p. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=363,238,383,248); the non-contiguous layout is shown in [Fig. 5](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=317,169,360,180).) Blocks can also be shared across sequences, for example for a common prompt in parallel sampling or beam search.

## What was measured

- **Setup:** OPT-13B/66B/175B and LLaMA-13B on A100 GPUs. Workloads are Poisson arrivals with ShareGPT and Alpaca length distributions. The metric is normalized latency (end-to-end latency divided by output length) against request rate.
- **Throughput at similar latency:** on ShareGPT, vLLM sustains [1.7–2.7× the request rate of Orca (Oracle), 2.7–8× that of Orca (Max), and up to 22× that of FasterTransformer](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=251,433,295,443) (p. 11, Fig. 12). For OPT-13B it batches 2.2× more requests than Orca (Oracle) (p. 11, Fig. 13a).
- **Sharing savings** (blocks saved over blocks without sharing): on Alpaca, [6.1–9.8% for parallel sampling and 37.6–55.2% for beam search](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=515,614,534,624) (p. 11, Fig. 15).
- **Shared prefix** (LLaMA-13B, WMT16): [1.67× with an 80-token prefix and 3.58× with a 341-token one](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=203,436,227,446) (p. 12, Fig. 16).
- **Costs:** the paged attention kernel is 20–26% slower than FasterTransformer's (p. 12, Fig. 18a). Swapping to CPU is expensive with small blocks, so recomputation is competitive at block sizes 16–64 ([p. 13, Fig. 19](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=13&rect=54,171,98,181)).

## Caveats

- The "2–4×" headline ([abstract](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1&rect=190,364,210,374)) is a summary. The measured ratios over Orca (Oracle) run from 1.3× to 3.58×, and the 22× figure is against FasterTransformer.
- Most results are plots. No variance is reported, and the Orca baselines were reimplemented by the authors.
- "Without affecting the model accuracy at all" is asserted, not measured.
- The paper contradicts itself on beam-search sharing: the text says "up to 55%" in one place and reports 66.3% on ShareGPT in another.

The library has a reading note for this paper with a digest and related papers at `notes/Efficient Memory Management for Large Language Model Serving with PagedAttention.md`. The page references in the note are sometimes off by one; I corrected those above where `paperlib locate` disagreed.
