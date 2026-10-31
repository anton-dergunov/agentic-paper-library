**LongMemEval_S and _M differ only in how much chat history sits around the evidence.** The questions, the answers and the evidence sessions are the same in both. The paper defines them on [p. 5, §3.2](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5):

- **S (short):** about 115k tokens per question, roughly 50 sessions. Each question's evidence sessions are placed in the middle of unrelated chat sessions.
- **M (medium):** 500 sessions, about 1.5M tokens per question.

The paper says the pipeline can build histories "of arbitrary length" and that these are two standard settings ([p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)). The filler sessions come from simulated self-chats and from ShareGPT and UltraChat.

The other setting the paper uses is **Oracle**, which is not a size. It gives the model only the evidence sessions, so it is an upper bound on what retrieval could achieve. On S, long-context LLMs drop 30–60% against Oracle ([p. 6, Figure 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6)). The paper's Table 8 in the appendix (p. 16 or so, not checked) reports S and M results alongside Oracle for five more models. In that table M is lower than S for every model.

The paper names no other versions. Its results cover only S, M and Oracle. I checked only this paper in the library, so if you mean a later release, such as a cleaned or newer dataset, I can't confirm it from here.
