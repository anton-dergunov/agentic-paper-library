**Invalidation.** Zep never deletes a fact: when a new fact contradicts an old one, the old one gets an end date.

- **Example:** the graph holds "Alice lives in London", and a new message says she moved to Berlin in March. The London edge is kept, but its validity now ends in March, where the Berlin edge begins.
- **Two timelines per fact:** each fact is an edge carrying four timestamps. `t_valid` and `t_invalid` record when it was true in the world; `t'_created` and `t'_expired` record when the system learned or retired it. Relative dates ("two weeks ago") are resolved against the message's own timestamp.
- **The check:** when a new edge is added, an LLM compares it with semantically related existing edges. If it finds a contradiction that overlaps in time, it sets the old edge's `t_invalid` to the new edge's `t_valid`.
- **Tie-break:** the more recently ingested information always wins.
- **At retrieval:** each fact is handed to the agent with its validity range, so it can answer both "where does she live" and "where did she live last year".

This is all in [Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3). The paper does not measure how often the LLM wrongly expires a fact, and has no ablation isolating what invalidation contributes.

**LongMemEval.** The only baseline is full context: the whole conversation of about 115k tokens pasted into the prompt ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Model | Full context | Zep | Latency (full context → Zep) | Context tokens |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s | 115k → 1.6k |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s | 115k → 1.6k |

- **The headline is relative:** the "up to 18.5%" improvement is 71.2 / 60.2. In absolute terms the gains are 11.0 points (gpt-4o) and 8.4 points (gpt-4o-mini).
- **No other memory system is compared:** the authors could not get MemGPT to answer questions on LongMemEval (p. 7, §4.3.1). The paper is also vendor-run against Zep's hosted service.
- **Knowledge-update is the weakest support for invalidation:** this is the question type that most directly tests it, and it moves least. With gpt-4o it goes from 78.2% to 83.3%; with gpt-4o-mini it falls from 76.9% to 74.4% ([Zep, p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)).
- **Where the gains are (gpt-4o):** preference questions go from 20.0% to 56.7%, temporal reasoning from 45.1% to 62.4%, and multi-session from 44.3% to 57.9%.
- **What gets worse:** questions about what the assistant itself said drop from 94.6% to 80.4% with gpt-4o.
