Checking the exact citation links, then I'll answer.

The two versions differ only in how much unrelated chat history is wrapped around the evidence. The questions and the evidence sessions are the same in both ([p. 5, history compilation](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5&rect=367,654,505,664)).

**How a history is built.** For each of the 500 questions, the benchmark takes the few evidence sessions (up to six). It adds unrelated sessions and shuffles the evidence into the middle, like a needle in a haystack. It then assigns timestamps. The filler is a fixed mix of 25% ShareGPT, 25% UltraChat and 50% simulated sessions about other attributes of the same user (Appendix A.2). The pipeline can make a history of any length, and S and M are the two standard sizes.

| Setting | History per question | Use |
|---|---|---|
| **LongMemEval_S** | about 115k tokens (roughly 50 sessions) | Fits a 128k-context LLM, so you can feed the whole history to the model ("long-context reading"). |
| **LongMemEval_M** | 500 sessions, about 1.5M tokens | Fits no LLM, so you need a memory system or retrieval. |
| **Oracle** | Only the evidence sessions | Not a released size. The paper uses it as an upper bound that isolates reading from finding. |

The "roughly 50 sessions" for S is my estimate. The text I read gives only the token count for S.

**Oracle versus S.** Oracle is the same questions with no haystack. The drop from oracle to S is the cost of long context alone. GPT-4o goes from 0.870 to 0.606, and Llama 3.1 70B from 0.744 to 0.334 ([p. 6, Figure 3b](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6&rect=108,73,504,271)). The appendix tables (Table 8 for five more models, and later ones) report oracle, S and M side by side.

**M is for retrieval.** The paper's retrieval pipeline works on both S and M. It indexes each round or session as a value, with a key such as the value plus extracted facts, and a retriever fetches from the index. Table 8 shows M scoring a few points lower than S for the same method. For example, Mistral-Nemo with `K = V+fact` gets 0.666 on S and 0.598 on M.

The paper (p. 5) says the history length is freely configurable, so other "versions" are just other lengths from the same pipeline. The public release is just S and M. I haven't checked whether the authors released other variants, such as an oracle file.

I changed no files, so there's nothing to commit.
