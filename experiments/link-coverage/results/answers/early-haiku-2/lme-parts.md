**The seven question types** (the paper's five abilities are IE, MR, KU, TR, ABS):

| Type | Ability | What it tests |
|---|---|---|
| single-session-user | IE | A fact the user said in one session |
| single-session-assistant | IE | Something the assistant said in one session (e.g. a restaurant it recommended) |
| single-session-preference | none named | Whether a reply is personalised from what the user has said. The paper doesn't put this under one of the five abilities. |
| multi-session | MR | Aggregating or comparing facts across 2 or more sessions (counts, totals) |
| knowledge-update | KU | The newest value of a fact that changed over time (e.g. a new job, a new trip) |
| temporal-reasoning | TR | Dates and elapsed time, from timestamps and explicit time references |
| abstention | ABS | 30 false-premise questions where the right answer is "you didn't mention that" |

Examples for each are in [Figure 1, p. 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3). Page 2 is the intro, which summarises the same material and Table 1 (coverage against other benchmarks).

**What to read, in order:**

1. [Figure 1, p. 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3): one example per type. This is the quickest way to see the tasks.
2. [§3.2, p. 4](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=4): the exact definitions of the abilities and types.
3. [§3.3, p. 6](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6): how answers are scored (a GPT-4o judge, per-type prompts). Read this before trusting any number.
4. [Figure 9, p. 19](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=19) (appendix): the type mix, the number of evidence sessions (up to six) and where evidence sits in a session. The text layer doesn't tie the pie percentages to labels, so check that figure in the PDF.

**Most useful overall:**

- **[§5, pp. 8–10](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=8)**: the design lessons (rounds beat sessions, key expansion, time-aware query expansion, chain-of-note). This is the part most likely to change how you build a memory system.
- **[Table 2, p. 8](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=8)**: nine existing memory systems placed on the indexing/retrieval/reading framework.
- **[§3.4, p. 6](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6)**: the pilot showing that commercial assistants score well below offline reading.
- **Judge validation, Table 6 (p. 21)**: the evidence that the scorer agrees with experts, if you plan to rely on the scores.

**Can skip:** the related-work comparisons beyond Table 1, the §4 formalism unless you're building a memory system, the references, and most appendices. Appendix A (curation prompts and the ontology in Table 5) matters only if you want to rebuild the data.

Caveat: this is from the text layer and the note. I checked the table and figure text but did not look at the page images.
