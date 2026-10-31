**Chain-of-Note (CoN)** is a reading strategy from Yu et al. (2023). The model first goes through each retrieved item and writes a short note with the evidence it contains, or says it is irrelevant. Then it answers from those notes instead of from the raw context. This splits one hard long-context reading task into two easier ones: copy the important details, then reason over concise notes.

**How LongMemEval uses it**

- **Default reader setting.** CoN is applied throughout the main experiments (§5.2–5.4), alongside JSON-formatted memory items (p. 6 figure and §5.5). Retrieved items are sorted by timestamp before reading.
- **Prompt.** The reading prompt (Figure 13, p. 23) is a small variant of CoN. It asks the model to go through the documents, extract evidence, then answer. Decoding is greedy, with an 800-token limit.
- **Why it matters.** §5.5 presents CoN as one of two reading optimizations, with the structured format, and says that a poor reading strategy can cost up to 10 points even with perfect retrieval.

**What page 6 shows**

[p. 6, Figure 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6) compares full-history reading (column S) with and without CoN:

| Reader | S, no CoN | S, with CoN |
|---|---|---|
| GPT-4o | 0.606 | 0.640 |
| Llama 3.1 70B | 0.334 | 0.286 |
| Llama 3.1 8B | 0.454 | 0.420 |
| Phi-3 14B | 0.380 | 0.344 |
| Phi-3.5 Mini 4B | 0.342 | 0.324 |

CoN helps GPT-4o a little and lowers the score for every open model in the full-history setting. The text on the same page says the long-context drop occurs "regardless of whether" CoN is applied. That holds for the drop size, but the open-model numbers are lower with CoN. The page also cross-references CoN to §4.2, but the method is described in §5.5, so that pointer is probably a typo.

Reading the table takes care: the Oracle column varies by row, so compare the S column within each model.
