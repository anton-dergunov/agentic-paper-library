I'll check the note and the paper's section structure first.

The tasks are all on page 3–4, so you need very little of the paper for them.

**To see the tasks (about 5 minutes):**
- [Fig. 1, p. 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3&rect=108,230,505,514) shows one worked example per question type, each with its evidence statements and the answer. Start here.
- §3.2 on p. 4 gives the five abilities and the seven question types in prose. It sits just after [Table 1, p. 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3&rect=108,77,505,226), which compares the benchmark with LoCoMo and others.

**The tasks.** Each question is asked after a long, timestamped chat history between a user and an assistant. The 500 questions fall into five abilities and seven types:

| Ability | Question type | Example from Fig. 1 |
|---|---|---|
| Information extraction | single-session-user | "How long is my commute?" The user said 45 minutes. |
| Information extraction | single-session-assistant | "Remind me of the restaurant you recommended in Rome." (Roscioli) |
| Information extraction | single-session-preference | The user owns a Sony camera. Recommend accessories that fit it. |
| Multi-session reasoning | multi-session | "How many instruments do I own?" Counts across several chats. |
| Knowledge updates | knowledge-update | "Where was my most recent family trip?" Hawaii was later replaced by Paris. |
| Temporal reasoning | temporal-reasoning | "Months since my last museum visit?" Needs the session timestamps. |
| Abstention | false-premise (30 questions) | "How many fish in my 30-gallon tank?" The user never mentioned one. |

Single-session-preference is the odd one out. It has no short answer. It is graded against a rubric describing the preferred response.

**How the histories are built (skim p. 5).** The evidence sessions are hidden among filler chats. LongMemEval_S has about 115K tokens per question, and LongMemEval_M has about 1.5M. That length is the main difficulty of the benchmark.

**Most useful overall, in order:**
1. **Fig. 1 and §3.2 (pp. 3–4).** This is the task definition.
2. **Pilot study, Fig. 3 (p. 6).** Long-context models drop 30–60% going from oracle sessions to _S, and ChatGPT scores 0.577 on a much easier version. It shows why the benchmark is hard.
3. **Unified framework, Fig. 4 and Table 2 (p. 8).** It splits a memory system into indexing, retrieval and reading, with four design knobs. It is the paper's most reusable idea.
4. **Design findings, §5 (pp. 8–10).** These are the practical results:
   - Index rounds rather than whole sessions.
   - Add extracted user facts to the retrieval key.
   - Expand queries with a time range for temporal questions.
   - Use chain-of-note reading with JSON input.
5. **Appendix A.3, Fig. 9 (p. 19).** It gives the question-type distribution and shows that most questions need 2–6 evidence sessions.

**Skip on a first pass:**
- The §2 related-work background.
- Appendices C–D (prompts and per-system mappings), unless you are re-implementing something.
- Appendix E.5 (error analysis), unless you care about retrieval versus reading failures. MemSyco-Bench in the library reports that retrieval failures dominate.

The library also has [[notes/LongMemEval...]] with a 20-line digest of the numbers. Its Q&A section is empty. I read the note and pp. 3–4 directly, and have not checked the page numbers for §5 and the appendix against the PDF. Run `paperlib locate` on the numbers before you rely on them.

**Suggested commit message:** none needed, since I changed no files.
