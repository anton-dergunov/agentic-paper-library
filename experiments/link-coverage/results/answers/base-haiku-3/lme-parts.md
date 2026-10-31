I'll read the paper's text and any existing note first.

The note has a digest, but I'll check the task list against the text on pages 2–5 before answering.

The task list matches the note. Next I'll check where the per-type question counts are given, and what the rest of the paper covers.

The text layer gives the question-type shares in Figure 9(a) but not which share belongs to which type. I'll look at that figure on PDF page 19.

The pie shows six shares, and the legend colours give the mapping. Next I'll get PDF locations for the passages I plan to cite.

**LongMemEval** is 500 hand-written questions, each asked after a long chat history that holds the answer somewhere in it. The questions fall into seven types, which the paper groups into five abilities. Page 2, where you are, is the motivation: earlier benchmarks have short histories and miss multi-session, temporal, update and assistant-side memory.

**The tasks**

| Type | Ability | What it asks | Share of questions* |
|---|---|---|---|
| single-session-user | IE (information extraction) | Recall a fact the user stated in one session | 14% |
| single-session-assistant | IE | Recall something the assistant said in one session | 27% |
| single-session-preference | none named | Use the user's stated preferences to personalise an answer | 6% |
| multi-session | MR (multi-session reasoning) | Aggregate or compare facts across 2+ sessions | 27% |
| knowledge-update | KU | Answer with the user's latest value after a change | 16% |
| temporal-reasoning | TR | Reason over timestamps and dates in the history | 11% |
| abstention (ABS) | ABS | Say "I don't know" to a false-premise question | 30 questions, built from the other types |

*The shares are from the pie in Fig. 9a. The text layer doesn't carry the labels, so I matched them by legend colour. The 11% for temporal-reasoning is the least certain match.

The histories are built from evidence sessions mixed into filler sessions. The short version (_S) is about 115k tokens, about 50 sessions. The long version (_M) is 500 sessions, about 1.5M tokens. Most questions need evidence from two or more sessions, up to six, and most evidence sits near the start of its session (Fig. 9b–c).

**What to read, in order**

1. **p. 3, Fig. 1 and Table 1.** The seven examples and how LongMemEval compares with LoCoMo, MemoryBank and others. [LongMemEval, p. 3, Fig. 1](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3&rect=108,230,505,514)
2. **p. 4, §3.2.** The definitions of the five abilities and the seven types, and how the abstention questions are made. [LongMemEval, p. 4, the five abilities](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=4&rect=311,379,461,389)
3. **p. 19, Fig. 9 and A.3.** The type shares and the evidence-spread statistics. [LongMemEval, p. 19, Fig. 9](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=19&rect=108,544,505,721)
4. **p. 21, Table 6.** How reliable the GPT-4o judge is, by type. It agrees with the experts on 97–100% of the sampled answers, against 30 per type.

Skip for now: the rest of the curation and history-building pipeline (pp. 4–5, Fig. 2, A.1–A.2), and the prompts in the appendix.

**Most useful overall**

- **p. 6, Fig. 3 (pilot study).** The headline gap: commercial assistants score 0.577 (ChatGPT) and 0.330 (Coze) on short histories, against 0.918 for GPT-4o with the full history. Long-context models lose 30–60% going to _S. [LongMemEval, p. 6, Fig. 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6&rect=108,73,504,271)
- **p. 21, Table 7.** Where the commercial systems fail: multi-session, knowledge-update and temporal questions drop sharply. Read it against the 97-question sample on p. 21, since it is small.
- **pp. 8–10 (Table 2, the design findings).** Read these only if you are designing a memory system. Rounds beat whole sessions, extracted user facts help recall, and chain-of-note helps reading.

**Caveats**

- The 97-question commercial study is small and was run by hand in August 2024. Treat its numbers as indicative.
- The paper doesn't give per-type question counts in the text, only the shares.
- The 30 abstention questions are rewritten from other types, so they are not a separate pool.
