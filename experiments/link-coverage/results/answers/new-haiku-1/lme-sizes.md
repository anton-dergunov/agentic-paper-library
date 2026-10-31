The paper defines only two standard lengths of the same benchmark, S and M. It names no other versions.

- **LongMemEval_S:** about 115k tokens of chat history per question. Each question's evidence sessions are inserted into a larger pile of unrelated sessions, which are self-simulated or drawn from ShareGPT and UltraChat ([p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)).
- **LongMemEval_M:** 500 sessions, about 1.5M tokens per question, built the same way ([p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)).

The 500 questions and their evidence are the same in both. Only the haystack length changes. The paper says the length is "freely extensible" and the two settings exist "for consistent comparison" ([p. 2](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=2)). The session count for S is not stated in the text I read.

Two other settings appear in the paper, but neither is a benchmark version:

- **Oracle:** the model sees only the evidence sessions, with no haystack. It is a diagnostic upper bound. In the §3.4 pilot, GPT-4o scores 0.870 with oracle and 0.606 on S, a 30% drop. The paper says the long-context models' drop on S was 30–60% ([p. 2](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=2)).
- **Commercial-system pilot:** ChatGPT and Coze were tested on 97 questions with a 3–6 session history, about 10x shorter than S. This was a manual pilot, not the standard S or M setting.
