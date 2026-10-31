I'll start with the paper's text and any existing note on it.

The main text covers the task design. Now I'll pull the appendix statistics and the question-type breakdown.

## The tasks

LongMemEval has 500 questions. Each one is asked after a long chat history, and the assistant has to recall something from it. The questions cover five memory abilities, split into seven question types:

| Ability | Question type | What it tests |
|---|---|---|
| Information extraction | single-session-user | Recall something the user said in one session |
| | single-session-assistant | Recall something the assistant said |
| | single-session-preference | Give a reply personalised to the user's stated preferences |
| Multi-session reasoning | multi-session | Aggregate or compare facts spread over 2 or more sessions |
| Knowledge updates | knowledge-update | Track that a user fact changed (e.g. a new job or a new count) and answer with the latest value |
| Temporal reasoning | temporal-reasoning | Use timestamps and time words, e.g. "how many months since…" |
| Abstention | abstention | Say "I don't know" to a false-premise question (30 of the 500) |

Each question's evidence sits in one to six sessions inside a longer history. Two sizes are provided: LongMemEval-S (about 115k tokens, around 50 sessions) and LongMemEval-M (500 sessions, about 1.5M tokens). Answers are scored by a prompt-engineered GPT-4o judge.

## What to read

1. **[p. 1, abstract](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=1)**: the five abilities, the 500 questions, and the headline 30% drop.
2. **[p. 3, Table 1 and Figure 1](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3)**: one example per question type, and how the benchmark compares with MemoryBank, PerLTQA, LoCoMo and DialSim. This is the fastest way to see the tasks.
3. **[p. 4, §3.1–3.2](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=4)**: the formal definitions of each ability and the seven question types, with the abstention construction.
4. **[p. 5, Figure 2](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)**: how questions are built, with evidence sessions self-chatted and then hand-edited, and how histories are padded with ShareGPT and UltraChat sessions. This is what makes the data trustworthy and what you would need to extend it.
5. **[p. 6, Figure 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6)**: the pilot results. ChatGPT and Coze lose 37% and 64% against offline reading, and long-context models drop 30–60%.

If you only read further, read **[p. 19, Figure 9](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=19)** for the type distribution and evidence positions, and **[p. 21, Tables 6–7](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=21)** for how far to trust the judge and the human results.

## Most useful overall

- **Figure 1 and Table 1 (p. 3)** are the most useful for understanding the tasks.
- **§3.2 (p. 4–5)** explains the construction, which determines what the scores mean.
- **Figure 3 (p. 6)** is the result that motivates the benchmark.
- **§4–5 (p. 7 onward)** are about memory design. Read them only if you are building a memory system; they are outside the task question.
- **Table 5 (p. 17)** is the user-attribute ontology and **Appendix A.1** holds the simulation prompts. Read them only if you plan to generate new data.

I have not checked these page numbers against the PDF; the text layer's page breaks put Figure 9 on p. 19 and Table 6 on p. 21. The text layer does not say which percentage in Figure 9 belongs to which type, so read that figure in the PDF before quoting a split. The judge's reliability is measured on 30 samples per type (Table 6), so those numbers are noisy.

I did not write a note for this paper. Say if you want me to write `notes/` for it, to keep these answers.
