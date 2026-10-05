**Invalidation.** Zep does not delete an outdated fact; it closes its validity interval, so the old fact stays in the graph as history.

For example, if the graph holds "Alice works at Acme" and a new message says "I started at Initech two weeks ago", the Acme edge is kept but marked as ending when the Initech edge begins.

The mechanism ([Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)):

1. **Four timestamps per fact (edge).** `t_valid` and `t_invalid` record when the fact was true in the world. `t'_created` and `t'_expired` record when the system learned it and when it stopped believing it.
2. **Temporal extraction.** An LLM dates each new fact, resolving relative expressions ("two weeks ago") against the message's reference timestamp.
3. **Contradiction check.** An LLM compares the new edge with semantically related existing edges.
4. **Invalidation.** Where a contradiction overlaps in time, the old edge's `t_invalid` is set to the new edge's `t_valid`. New information always wins.

Retrieval returns each fact with its `t_valid` and `t_invalid`, so the answering model sees the dates and has to reason over them itself.

**LongMemEval.** The baseline is full-context: the whole conversation (about 115k tokens) put in the prompt, with no memory system. The dataset is LongMemEval_s, judged by GPT-4o ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Model | Full-context | Zep | Latency (full-context → Zep) | Context tokens |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s | 115k → 1.6k |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s | 115k → 1.6k |

Caveats on these numbers:

- **The headline gains are relative.** The "15.2%" and "18.5%" improvements are relative; in absolute terms they are +8.4 and +11.0 points. The gpt-4o figure works out to 18.3% from the table's own numbers, not 18.5%.
- **No memory-system baseline.** The authors tried to run MemGPT on LongMemEval and could not get it to answer (p. 7, §4.3.1), so the only comparison is against full-context.
- **Invalidation is weakly supported by the breakdown.** On knowledge-update questions, the category that tests it most directly, Zep is slightly worse with gpt-4o-mini (76.9% → 74.4%) and modestly better with gpt-4o (78.2% → 83.3%) ([Zep, p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)).
- **Where the gains and losses are.** The large gains are in single-session-preference, temporal-reasoning and multi-session. Single-session-assistant gets worse with both models (94.6% → 80.4% with gpt-4o).
