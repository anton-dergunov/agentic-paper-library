**Chain-of-Note (CoN)** is a reading strategy for a model that has to answer from retrieved memory. Instead of answering straight from the raw context, the model first writes a short note for each retrieved item, pulling out only the evidence relevant to the question, and then reasons over those notes to answer. It splits one hard long-context reading job into two easier ones: copying the important details, then reasoning over concise notes. It comes from Yu et al., 2023.

**How LongMemEval uses it** ([p. 7](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=7), §5.5):

- It is the **reading stage** of the paper's indexing → retrieval → reading pipeline. Retrieved memory items go in as structured JSON, sorted by timestamp, and the reader applies CoN.
- The paper calls CoN a "small variation" of the original, and gives the prompt in its Figure 13 ([p. 16](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=16), appendix). Generation is greedy, with an 800-token cap.
- It is on by default in the experiments of §5.2 to §5.4 ([p. 7](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=7)).
- Its effect is tested with oracle retrieval, where only the evidence sessions are given. With CoN, JSON input consistently helps readers of different capability. Without it, JSON does not consistently beat plain natural language. The paper reports up to a 10-point gap between the best and worst reading strategy for GPT-4o.

**Why it matters on page 6:** the pilot study ([p. 6](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6), Fig. 3b) shows that long-context models drop 30–60% when reading the full ~115k-token history instead of only the evidence sessions. The paper says this happens "regardless of whether" CoN is applied. So CoN improves reading but does not close the gap caused by long histories. That supports the paper's claim that a memory mechanism is still needed.

Notes: the page-6 claim is from the text layer, and the 10-point figure is from Figure 6 (p. 10 per the existing note, which I did not re-check here).
