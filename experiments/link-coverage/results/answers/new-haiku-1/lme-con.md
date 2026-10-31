**Chain-of-Note (CoN)** is a reading strategy for retrieval-augmented LLMs (Yu et al., 2023). Instead of answering straight from retrieved text, the model first goes through each retrieved item and writes a short note on what it says about the question, then answers from those notes. The idea is to split one long-context reading job into two easier steps: copy the relevant details, then reason over the concise notes.

**How LongMemEval uses it:**

- **Baseline in the pilot study** ([p. 6, Figure 3b](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6)): the table reports the S-setting accuracy with and without CoN. Only GPT-4o improves (0.606 → 0.640). The Llama 3.1 70B, Llama 3.1 8B and Phi-3 models all get worse. The paper's text says long-context reading drops 30–60% "regardless of whether" CoN is applied.
- **Reading design in §5.5** (the paper's own method): the retrieved memory items are presented as structured JSON, and the reader is instructed to extract from each item first, then reason. In the oracle-retrieval setting, CoN is what makes JSON consistently beat plain natural language. Without CoN, JSON does not reliably win. Picking the best reading strategy alone is worth up to about 10 points for GPT-4o.
- **Reading prompt in the appendix** (Figure 13): a small variant of CoN. It asks the model to traverse the documents and extract evidence before answering. Decoding is greedy with an 800-token limit.
- **Defaults:** §5.2–5.4 apply CoN and JSON by default.

So CoN is a prompting device in the benchmark's reader, not part of the memory system itself. Its gains depend on the reader model: it helps GPT-4o on the full history and, with JSON, on oracle retrieval, but not the open models on the full history.

This library doesn't use CoN anywhere. The per-paper notes in `notes/` are digests and Q&A for agents, not a reasoning technique.
