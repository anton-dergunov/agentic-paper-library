I'm checking the paper text for the KV cache definition and the main numbers, then I'll generate the PDF links.

Now generating the links in one `paperlib locate` call.

The library has one paper that covers this: Kwon et al., *Efficient Memory Management for Large Language Model Serving with PagedAttention* (vLLM, 2023). It explains what the KV cache is (§2) and then how to manage it. I read the text layer and the paper's existing note. The note's page numbers matched the text, apart from the Fig. 12 page, which I corrected below.

## How the KV cache works

**Intuition.** A decoder generates one token at a time. Each new token's attention needs the key and value vectors of every earlier token. Without a cache, you would recompute those vectors for the whole prefix at every step. With a cache, you compute only the new token's key and value, [append them to the cache, and reuse the rest (p. 3)](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=3&rect=317,246,435,256). This trades memory for compute. Per generated token, the cost drops from re-encoding the whole prefix to one new position that attends to the cached keys and values.

**Example.** The prompt is 1,000 tokens. The prefill step computes keys and values for all 1,000 positions in one pass. Decoding token 1,001 then computes only $k_{1001}, v_{1001}$ and attends over the stored 1,001 entries.

**The cost is memory, and it grows with every token.** For OPT-13B the cache is [about 800 KB per token (p. 4)](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=280,345,295,356), which comes from 2 (key and value) × hidden size 5120 × layers × 2 bytes. A single 2048-token request therefore takes [up to 1.6 GB (p. 4)](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=4&rect=130,405,160,416). On a 40 GB A100, [weights take about 65% of memory and the KV cache close to 30% (Fig. 1, p. 1)](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=1&rect=317,177,560,409). That 30% caps the batch size, so it caps throughput.

**What the paper fixes.** Earlier systems give each request one contiguous chunk sized for its maximum possible length. That chunk is mostly empty, and it fragments the memory. [Only 20.4–38.2% of KV memory held real token states (Fig. 2, p. 2)](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=2&rect=54,71,295,244). These values are read from a plot.

**PagedAttention** applies operating-system paging to the cache:
- Each sequence's cache is split into fixed-size blocks of B tokens (the default is 16). The blocks can sit anywhere in GPU memory.
- A per-request block table maps logical blocks to physical blocks. The attention kernel [computes attention block by block through that table (Eq. 4, p. 5)](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=5&rect=344,261,559,300).
- Blocks are allocated on demand, so a request wastes at most one partly filled block.
- Physical blocks carry reference counts with copy-on-write. Parallel sampling, beam search and shared system prompts can therefore share them (pp. 6–8).
- When memory runs out, a whole sequence is evicted. Its blocks are either swapped to CPU RAM or recomputed later (p. 8).

## Measurements

The setup is author-run: OPT-13B/66B/175B and LLaMA-13B on A100s ([Table 1, p. 9](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=9&rect=77,73,271,155)). The traces are synthetic Poisson arrivals built from ShareGPT and Alpaca length distributions. The metric is normalized latency, meaning mean end-to-end latency divided by output length, plotted against request rate. The baselines are FasterTransformer and the authors' own reimplementation of Orca.

| Result | Number | Where |
|---|---|---|
| Throughput at similar latency, ShareGPT | 1.7–2.7× vs Orca (Oracle), 2.7–8× vs Orca (Max), up to 22× vs FasterTransformer | [Fig. 12, p. 10](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=10&rect=54,71,557,280); the 22× is in [the text on p. 11](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=11) |
| Batch size, OPT-13B | 2.2× vs Orca (Oracle), 4.3× vs Orca (Max) | Fig. 13a, p. 10 |
| Memory saved by sharing, Alpaca | 6.1–9.8% for parallel sampling, 37.6–55.2% for beam search | Fig. 15, p. 11 |
| Shared prefix (LLaMA-13B) | 1.67× throughput with a one-shot prefix, 3.58× with a five-shot prefix | [Fig. 16, p. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=53,71,295,234) |
| Cost: attention kernel latency | [20–26% slower](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=371,408,402,419) than FasterTransformer, from the block-table lookups | p. 12 |
| Block size | 16–128 works on ShareGPT, only 16–32 on Alpaca; swap and recompute perform about the same at 16–64 | [Fig. 18, p. 12](http://pdf.invalid/ml-systems/inference-and-serving/Efficient%20Memory%20Management%20for%20Large%20Language%20Model%20Serving%20with%20PagedAttention.pdf?page=12&rect=317,71,550,201), Fig. 19, p. 13 |

## Caveats

- The abstract's "2–4×" understates the measured range. Against Orca (Oracle) the gain runs from 1.3× to 3.58×, and against FasterTransformer it reaches 22×.
- Results come from the authors' runs on A100s only. The paper reports no variance, nearly all results are plots, and Orca is a reimplementation.
- "Without affecting accuracy" is asserted, not measured (p. 2).
- Paging fixes memory management, not the cache's size. Reducing the cache itself (fewer KV heads, quantization) is a separate line of work. This paper doesn't cover it, and I didn't find a paper on it in the library.

Related papers in the library: Orca (the main baseline, with iteration-level scheduling), FlashAttention (used for the prefill step) and FlexGen.

I made no repository changes, so there is no commit message.
