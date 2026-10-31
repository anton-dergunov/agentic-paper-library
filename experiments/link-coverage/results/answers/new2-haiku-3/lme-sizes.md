The path I used was wrong; I'll locate the file.

**LongMemEval S and M are two sizes of the same benchmark: the same 500 questions, with different amounts of chat history around the evidence.** The paper names no other versions, though it does use an "oracle" setting for comparison.

- **S** ("standard"): each question's history is about 115k tokens. The evidence sessions are mixed into unrelated chat sessions. ([p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5))
- **M**: 500 sessions, about 1.5M tokens per question, so the evidence is buried in a much longer haystack. ([p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5))
- **Oracle**: not a dataset size. The model sees only the evidence sessions, with no distractors, so it measures reading ability alone. The gap between Oracle and S is the cost of finding the evidence in a long history. ([p. 6, Figure 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6))

The paper's own results show the effect of size. Its Table 8 (appendix, [p. 26](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=26)) reports, for example, Mistral-Nemo with direct long-context reading at 0.688 on Oracle, 0.162 on S, and a memory-based setup at 0.640 on S and 0.554 on M. Since the paper gives only S and M as its standard settings, anything you have seen labelled differently is likely a later release or a third-party variant, not something defined in this paper.
