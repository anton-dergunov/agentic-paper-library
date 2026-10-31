**The dataset has 500 questions in seven types, covering five memory abilities.** Each question sits on a chat history of sessions where the answer is buried. Two lengths are provided: _S (~115k tokens, ~50 sessions) and _M (500 sessions, ~1.5M tokens).

| Type | Ability | What it tests |
|---|---|---|
| single-session-user | IE | Recall something the user said in one session |
| single-session-assistant | IE | Recall something the assistant said |
| single-session-preference | (personalization) | Tailor an answer to the user's stated preferences, without asking for them |
| multi-session | MR | Aggregate or compare facts across 2–6 sessions |
| knowledge-update | KU | Answer with the user's newest value after a change |
| temporal-reasoning | TR | Use timestamps and time references ("how many months ago") |
| abstention (30 questions) | ABS | Say "I don't know" to false-premise questions |

The paper's Figure 1 (p. 3) gives one example per type, and the type breakdown is p. 19. The text layer loses the pie chart's labels, so I haven't stated per-type counts. Check the figure if you need them.

**What to read, in order:**

1. **p. 3, Figure 1 and Table 1.** The fastest way to see what the tasks look like, and how this benchmark differs from LoCoMo and MemoryBank.
2. **p. 4, §3.1–3.2.** The formal setup (history of timestamped sessions, question, answer) and the definitions of the five abilities and seven types.
3. **p. 5, Figure 2 and "History Compilation".** How questions are built: evidence is stated indirectly, then buried among filler sessions. Read this if you want to judge whether the benchmark is realistic.
4. **p. 6, §3.3–3.4.** The GPT-4o judge (>97% agreement with experts; prompts and agreement in Table 6, p. 21) and the pilot results. Those results are the headline numbers: ChatGPT 0.577 and Coze 0.330, against 0.918 for offline reading.
5. **p. 19, Figure 9.** Type distribution, number of evidence sessions (most need several, up to six), and where evidence sits within a session.

**Skip for a task overview:** §4 (the unified indexing/retrieval/reading view, pp. 7–8) and §5 (design experiments, pp. 8–10). Those matter if you're building a memory system, not for understanding the data. Appendix A.1 (pp. 17–18, the ontology in Table 5 and the generation prompts) only matters if you plan to build variants.

**Most useful overall:** p. 4–5 for what the tasks are and how they're made, p. 3 Figure 1 for examples, and p. 6 for how answers are scored.

Links to the pages:
- [p. 3, Figure 1](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3)
- [p. 4, §3.1–3.2](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=4)
- [p. 5, Figure 2](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)
- [p. 6, §3.3–3.4](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6)
- [p. 19, Figure 9](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=19)

The existing note (`notes/LongMemEval. Benchmarking Chat Assistants on Long-Term Interactive Memory.md`) already covers these numbers, so I didn't change it.
