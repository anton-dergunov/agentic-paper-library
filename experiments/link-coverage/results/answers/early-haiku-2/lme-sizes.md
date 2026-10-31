**LongMemEval-S and -M differ only in how long the chat history is.** The questions and answers are the same. The paper says the history length is configurable, and it fixes two standard settings for comparison ([LongMemEval, p. 2](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=2)):

- **S** has about 115k tokens per question ([p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)). The evidence sessions are inserted into a much longer run of unrelated chats, which are drawn from simulated self-chats and from public ShareGPT and UltraChat data.
- **M** has 500 sessions, about 1.5M tokens ([p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)). It is about 13 times the length of S.

Both are built the same way: a "needle-in-a-haystack" design where the evidence sessions are placed in the middle of the history and given timestamps ([p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)).

**The "other versions" the paper mentions are not other datasets.** Two things can look like them:

- **Oracle setting.** This is a diagnostic, not a size. The model answers from only the evidence sessions. The paper uses it as the upper bound against which S and M are compared ([p. 6](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6)). For example, GPT-4o scores 0.870 with the oracle and 0.606 on S, a 30.3% drop.
- **Other lengths.** The paper says the length "is freely extensible" ([p. 2](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=2)), but it defines no other standard sizes. I didn't find an XS or other named variant in the text.

The paper's Table 8 results for S and M ([p. 13 or nearby](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=13)) use these same two settings. I didn't check the page number for that table closely, so confirm it before citing it.
