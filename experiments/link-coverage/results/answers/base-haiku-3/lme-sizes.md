**Short answer:** S and M are the same 500 questions with different amounts of chat history. Neither is a different benchmark. The paper also uses "oracle" as an evaluation setting, not a dataset size.

- **LongMemEval S** is the default setting, about 115k tokens of history per question ([p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)). The evidence sessions are hidden among unrelated user-AI sessions, drawn from simulated self-chats and public ShareGPT and UltraChat data.
- **LongMemEval M** keeps the same questions and evidence but buries them in 500 sessions, about 1.5M tokens ([p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)). It is the harder, more realistic stress test.
- **Oracle** is not a length. It means answering from only the evidence sessions, with no haystack. The paper uses it as an upper bound: GPT-4o scores 0.870 with oracle and 0.606 on S, a 30.3% drop ([Figure 3, p. 6](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6)).

The paper defines only these three, and says the pipeline can build histories of any length. So "other versions" means other lengths, not released variants. Whether the public release names its files `_oracle`, `_s` and `_m` is not in the paper, so I haven't checked it.

S and M also differ in results. In the appendix, with memory operations (K=V, round granularity), Mistral-Nemo scores 0.640 on S and 0.554 on M, and Qwen2.5-7B scores 0.452 and 0.390 ([Table 8, p. 19 or nearby](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=19)). I read these from the table text; I did not check the page number against the PDF.

Want me to add this to the paper's note Q&A so later sessions don't re-derive it?
