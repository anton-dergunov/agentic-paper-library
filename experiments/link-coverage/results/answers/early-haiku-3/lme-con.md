**Chain-of-Note (CoN)** is a reading technique from Yu et al. (2023). The model first goes through each retrieved item and writes a short note extracting the evidence relevant to the question. Only then does it reason over those notes to answer. The point is to split one hard long-context reading task into two easier ones: copying the important details, then reasoning over a shorter, cleaner text.

**How LongMemEval uses it** (§5.5, with Figure 6 on p. 6):

- **Input format:** retrieved memory items are presented as structured JSON, not free text. The paper treats JSON and CoN as two separate levers.
- **Reading prompt:** the prompt in Figure 13 (Appendix) is a small variant of CoN. It asks the reader to traverse the documents and extract evidence before answering. Decoding is greedy, with a maximum of 800 generated tokens.
- **Default:** CoN and JSON are applied throughout §5.2–5.4 unless stated otherwise.
- **Result (oracle retrieval, p. 6):** a poor reading strategy costs up to about 10 points for GPT-4o, even with perfect retrieval. Without CoN, JSON does not consistently beat plain natural language. With CoN, JSON helps readers of all capability levels.

I read this as the paper's use of CoN, since the page names it as a reading strategy. If you meant something else by "chain of note" here, such as the library's `notes/` files, tell me and I'll answer that instead.
