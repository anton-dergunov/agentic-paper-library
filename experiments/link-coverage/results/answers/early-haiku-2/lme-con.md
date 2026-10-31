**Chain-of-Note (CoN)** is a reading strategy for retrieval-augmented LLMs. The model first writes a short note on each retrieved item, extracting the details that bear on the question, and only then answers from those notes. The paper's authors cite Yu et al., 2023 (arXiv:2311.09210) for it.

**How it is used in LongMemEval**

- **The problem it addresses (§5.5, p. 6):** even with perfect retrieval, the reader model can lose up to 10 absolute points of accuracy with a weak reading setup. Long retrieved contexts are hard to reason over directly.
- **What the paper does:** it splits the reading into two easier subtasks, copying the important details from each memory item, then reasoning over those shorter notes. It combines this with a JSON format for the memory items.
- **Where it is applied:** CoN is the default reader in §5.2–5.4 (the paper's own statement, around line 598 of the text layer). It is also a design choice in the paper's memory-design table (CP4, "Reading Strategy"): the recommended design uses CoN.
- **The prompt (Figure 13, appendix):** the CoN prompt asks the model to go through the chat history, extract the evidence step by step, and then answer. The non-CoN baseline asks for the answer directly.
- **Results:** in the oracle setting, CoN with JSON is the best of the four format/strategy combinations for GPT-4o, Llama 3.1 70B and Llama 3.1 8B. Across the reader LLMs, the paper reports gains of up to about 10 points. The gain is smaller for some models; for the 70B model, JSON without CoN is not consistently better than natural language.

This is not the same as the `notes/` folder in the library. There, a "note" is the agent's memory file for a paper, which is a different thing.
