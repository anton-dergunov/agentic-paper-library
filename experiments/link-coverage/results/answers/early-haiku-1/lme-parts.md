**What the dataset is:** 500 human-curated questions. Each one is answered from a long chat history of timestamped sessions, where the evidence is buried among filler sessions. There are two sizes: `_S` (about 115K tokens, roughly 50 sessions) and `_M` (500 sessions, about 1.5M tokens) ([Table 1, p. 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3); [§3.2, p. 4](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=4)).

**The seven question types** (five abilities, plus two types that test them in other ways):

| Type | Ability | What it asks |
|---|---|---|
| single-session-user | IE | Recall something the user said in one session (e.g. commute length) |
| single-session-assistant | IE | Recall something the assistant said (e.g. a restaurant it recommended) |
| single-session-preference | personalisation | Give a response that uses the user's stated preferences; graded against a rubric |
| multi-session | MR | Aggregate or compare facts spread over 2+ sessions (e.g. count instruments owned) |
| knowledge-update | KU | Give the latest value after the user changed it (e.g. a trip, a tank size) |
| temporal-reasoning | TR | Date arithmetic from timestamps and explicit dates (e.g. "how many months since…") |
| abstention (30 questions) | ABS | Answer "I don't know" to a false-premise question built from the other types |

These are shown in [Figure 1, p. 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3).

**What to read, in order:**
1. **Figure 1 (p. 3)**: the fastest way to see every task type.
2. **§3.2 (p. 4)**: the five abilities and type definitions in precise terms. This is the section to read if you only read one.
3. **Appendix A.2 (p. 19)**: how histories are built. Evidence sessions are mixed 50/25/25 with simulated sessions, ShareGPT and UltraChat. This determines what the scores actually measure.
4. **Appendix A.4, Table 6 (p. 21)** with **Figure 10 (p. 20)**: how the GPT-4o judge is checked. Accuracy is 90% or higher per type, and the lowest scores are on preference and abstention.
5. **Figure 3 (p. 6)**: the headline pilot. Long-context models drop 30–60% from oracle sessions to `_S`, for example GPT-4o going from 0.870 to 0.606.

**Skip unless you're building a memory system:** §4 (the indexing/retrieval/reading framework) and §5 (design experiments, pp. 8–10). Read those when you want the design findings, such as rounds beating whole sessions as the storage unit.

**Caveats:**
- The per-type question counts are not in the text layer. The pie chart in [Figure 9a, p. 19](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=19) gives the percentages (14%, 27%, 11%, 6%, 16%, 27%), but the text layer doesn't say which label goes with which. Check the figure in the PDF before quoting a split.
- Most sessions are human-edited (about 70%) and most questions need several sessions (up to six). That is the part of the design that's hardest to reproduce.

The existing note at `notes/LongMemEval. Benchmarking Chat Assistants on Long-Term Interactive Memory.md` already covers the digest and the related papers, so it is a good companion to these sections.
