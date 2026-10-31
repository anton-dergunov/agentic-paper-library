**Short answer:** LongMemEval has 500 questions in seven types. They test five memory abilities against two history lengths. Page 2 only has the motivation and the start of related work. The task list is on p. 3 (Figure 1), which I also read.

**The seven question types (p. 3, Fig. 1)**

| Question type | Ability | What it tests |
|---|---|---|
| single-session-user | Information extraction | Recall a fact the user stated in one session (e.g. commute length) |
| single-session-assistant | Information extraction | Recall something the assistant said (e.g. a restaurant it recommended) |
| single-session-preference | Information extraction | Infer a preference from earlier chat and apply it (e.g. suggest Sony-compatible accessories) |
| multi-session | Multi-session reasoning | Combine facts from several sessions (e.g. count instruments the user owns) |
| knowledge-update | Knowledge updates | Give the latest value when the user changed it (e.g. most recent family trip) |
| temporal-reasoning | Temporal reasoning | Use dates in the chat to answer (e.g. months since the last museum visit) |
| abstention | Abstention | Say "you did not mention that" for a question the history cannot answer (30 questions) |

The mapping from types to abilities is my reading of the figure and Table 1, not a table in the paper.

**What to read, in order**

1. **p. 2, contributions (end of intro):** the four findings in one place. Quick, and it is the whole argument.
2. **p. 3, Table 1 and Fig. 1:** the comparison with LoCoMo, MemoryBank, PerLTQA and DialSim, and the seven types with examples. This is the task list.
3. **p. 4–6 (§3, construction and metric):** read this only if you need to trust the labels. It covers how the questions and histories are built, the GPT-4o judge (agrees with experts over 97%, p. 6; Table 6 on p. 21), and the pilot showing commercial assistants at 0.577 and 0.330 against 0.918 for full-history GPT-4o (p. 6, Fig. 3).
4. **p. 8–10 (§5, the design study):** this is the most useful part for memory-system work. Rounds beat sessions as the storage unit (p. 8, Fig. 5); adding extracted user facts to the keys gives +9.4% recall and +5.4% QA (p. 9, Table 3); time-aware query expansion helps temporal recall only with GPT-4o (p. 10, Table 4); chain-of-note with JSON input adds up to 10 points (p. 10, Fig. 6).

**Most useful overall:** the Figure 1 examples on p. 3 for the tasks, then the §5 findings on p. 8–10 for design choices. Skip the related-work survey on p. 2–3 unless you want the lineage.

The note in `notes/` has the digest but no Q&A yet. The seven-type breakdown and the mapping above are worth adding there if you want them kept.
