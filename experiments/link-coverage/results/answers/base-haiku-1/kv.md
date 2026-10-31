The paper is **"Efficient Memory Management for Large Language Model Serving with PagedAttention"** (Kwon et al., 2023; vLLM). It's in `library/ml-systems/inference-and-serving/`. I read the paper's text, not a note or review.

## What the KV cache is

During autoregressive generation, each new token attends to the keys and values of every earlier token. Those vectors don't change, so the server stores them and reuses them instead of recomputing them. [Kwon et al., p. 3](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3&rect=0,0,0,0) describes this as the prompt phase (all prompt tokens processed in parallel, which fills the cache) followed by the generation phase (one token per step, appending one key and one value per layer). The generation phase is memory-bound, which is why cache management decides throughput.

## Size, in practice

Per token, the cache holds one key and one value vector per layer. The paper's example for OPT-13B is 2 (K and V) × 5120 (hidden size) × 40 (layers) × 2 bytes (FP16) ≈ 800 KB per token. A 2048-token request then needs up to 1.6 GB ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=121,345,279,356)). As a rule of thumb (ours, from that example), bytes per token ≈ 2 × layers × hidden size × bytes per element, ignoring grouped-query attention, which shrinks it.

## Why naive management wastes memory

Frameworks want contiguous tensors, so existing servers reserved one chunk per request sized for the maximum length. [Figure 2 on p. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=195,660,269,671) shows that only 20.4%–38.2% of the KV memory held actual token states. The waste comes from reserved slots, internal fragmentation and external fragmentation ([p. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=317,708,382,718)).

## How PagedAttention works

- **Blocks instead of chunks.** The KV cache is split into fixed-size blocks of a few tokens each. Blocks need not be contiguous in GPU memory. The paper uses the OS virtual-memory analogy: blocks are pages, tokens are bytes, requests are processes.
- **Attention over blocks.** Eq. 4 computes the softmax and output block by block, so the kernel fetches each key/value block separately ([p. 5, Eq. 4](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=344,261,559,300)).
- **Block table.** A per-request table maps logical blocks to physical ones and records how many slots are filled. A new physical block is allocated only when the last one fills ([Fig. 6, p. 6](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=6&rect=129,196,222,206)). Waste is therefore bounded to the last block of each request.
- **Sharing.** Blocks can be shared across sequences, e.g. a prompt shared by parallel samples or beams, with copy-on-write when they diverge.

## Measurements

- **Setup:** OPT-13B, 66B and 175B, and LLaMA-13B, on A100 GPUs. Table 1 gives 12 GB of KV memory on a 40 GB A100 for OPT-13B, and 15.7K KV slots ([Table 1, p. 9](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=9&rect=77,73,271,155)). That matches 12 GB ÷ 800 KB ≈ 15K.
- **Workloads:** ShareGPT and Alpaca traces, with Poisson arrivals. The metric is normalized latency (end-to-end latency ÷ output length) against request rate, with throughput read as the highest rate before latency explodes.
- **Headline:** vLLM gives 2–4× throughput over FasterTransformer and Orca at similar latency ([p. 2](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=0,0,0,0)).
- **ShareGPT:** vLLM sustains 1.7–2.7× the request rate of Orca (Oracle) and 2.7–8× that of Orca (Max) ([p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=63,433,249,443)).
- **Sharing:** memory saved by sharing is 6.1–9.8% for parallel sampling and 37.6–55.2% for beam search on Alpaca ([p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11&rect=490,626,545,636)).
- **Block size:** 16 is the default. Smaller blocks cost more kernel overhead, and larger ones add internal fragmentation ([p. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=0,0,0,0)).

## Caveats

- Orca was not public, so the authors reimplemented it with three over-reservation assumptions, which makes the Orca numbers their own construction.
- Gains are largest for long sequences, big models and complex decoding, and smallest for OPT-175B on Alpaca, where memory is ample.
- The 2023 paper predates later work on KV offloading and disaggregated serving. The inference-and-serving README lists some of it (e.g. LMCache, Mooncake, FlowKV) under [`library/ml-systems/inference-and-serving/README.md`](library/ml-systems/inference-and-serving/README.md).
