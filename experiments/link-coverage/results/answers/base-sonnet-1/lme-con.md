**Chain-of-Note (CoN)** is a reading strategy from Yu et al. (2023). Before answering, the reader LLM goes through each retrieved item and writes a short note on what is relevant in it. It then reasons over those notes to produce the answer. This splits long-context reading into two easier steps: extract, then reason.

**How LongMemEval uses it**
- It is the reading step after memory retrieval. The prompt asks the model to "answer the question step by step: first extract all the relevant information, and then reason over the information". The non-CoN prompt just says "answer the question" ([Figure 13, p. 25](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=25&rect=108,456,505,562)).
- It is paired with a JSON format for the retrieved items, so the model sees them as data. The authors' "Our Design" uses round-level values, keys expanded with extracted facts, time-aware queries and CoN ([p. 10](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=10&rect=216,452,406,462)). Experiments in §5.2–5.4 use CoN and JSON by default.
- Even with perfect retrieval (oracle sessions), a poor reading strategy costs up to 10 absolute points for GPT-4o. JSON only helps consistently when CoN is also on ([Figure 6, p. 10](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=10&rect=108,219,505,321)).
- The paper's CoN prompt is a small variation on the original, and it generates up to 800 tokens with greedy decoding (Appendix, p. 24).

The CoN discussion itself is on p. 10, not p. 6. Page 6 only lists it among the contributions.

I didn't check any numbers beyond the 10-point claim, which comes from the paper's text. The ~10-point gain across three LLMs is the paper's own summary of §5.5.

No files were changed, so there is no commit message to suggest.
