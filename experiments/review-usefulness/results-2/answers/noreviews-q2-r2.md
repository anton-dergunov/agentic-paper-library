**Invalidation: an outdated fact gets an end date and is never deleted.**

Take "Alice lives in London", followed months later by "Alice moved to Berlin in March" (my example, not the paper's). Zep keeps both facts and closes the London one at March, so it can answer both "where does she live" and "where did she live last year".

The mechanism ([p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)):

1. **Facts are edges with four timestamps.** `t_valid` and `t_invalid` record when the fact held in the world; `t'_created` and `t'_expired` record when the system learned or retired it.
2. **Dates are resolved at ingestion.** An LLM turns relative mentions ("two weeks ago") into absolute dates using the message's own timestamp.
3. **An LLM looks for contradictions.** Each new edge is compared against semantically related existing edges.
4. **The old edge is closed.** If the two contradict and overlap in time, the old edge's `t_invalid` is set to the new edge's `t_valid`.
5. **Newer information always wins.** Ties are broken by ingestion order.

Retrieval then hands the agent each fact with its validity range ([p. 4–5](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=4)).

**LongMemEval: the only baseline is full context, i.e. pasting the whole ~115k-token history into the prompt** ([p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Model | Full context | Zep | Latency (full context → Zep) | Context tokens |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s | 115k → 1.6k |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s | 115k → 1.6k |

- **The headline "18.5%" is relative.** In absolute terms the gain is 11.0 points with gpt-4o and 8.4 with gpt-4o-mini (the paper quotes 15.2% for the latter).
- **No other memory system is compared.** The authors tried MemGPT but could not get it to answer after loading the histories ([p. 7, §4.3.1](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.4.3.1&page=7)).
- **Invalidation itself is barely tested.** There are no ablations, and the knowledge-update question type moves little: 78.2% → 83.3% with gpt-4o and 76.9% → 74.4% with gpt-4o-mini ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)).
- **The larger gains are elsewhere.** With gpt-4o, preference questions go from 20.0% to 56.7%, temporal reasoning from 45.1% to 62.4% and multi-session from 44.3% to 57.9%. Questions about what the assistant said drop from 94.6% to 80.4%.
- **The evaluation is vendor-run.** The authors tested their own hosted service.

Nothing was changed in the library, so there is no commit to suggest.
