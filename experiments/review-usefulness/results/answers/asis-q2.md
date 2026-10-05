**Invalidation.** Zep never deletes a fact; it gives the old one an end date. Each fact is an edge between two entities, and when a new edge arrives, an LLM compares it with semantically related existing edges. If it finds a contradiction whose time ranges overlap, it sets the old edge's `t_invalid` to the new edge's `t_valid` ([p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)).

For example, "lives in London" followed later by "moved to Berlin in March" leaves the London edge in the graph with its validity ending in March. The agent can then answer both "where does she live" and "where did she live last year".

- **Two timelines per edge:** `t_valid`/`t_invalid` record when the fact held in the world, and `t'_created`/`t'_expired` record when the system learned or retired it. Relative dates ("two weeks ago") are resolved against the message's timestamp.
- **Newer wins:** when two facts conflict, the one ingested later always takes priority.
- **Shown at retrieval:** the context given to the agent includes each fact's validity range, so the model sees what is current.

**LongMemEval.** The only baseline is full-context: pasting the whole ~115k-token history into the prompt ([p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Model | Full-context | Zep | Latency (full → Zep) |
|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s |

Zep's context averages 1.6k tokens against 115k. The abstract's "up to 18.5%" improvement is relative; in absolute terms the gain is 11.0 points with gpt-4o and 8.4 with gpt-4o-mini.

Three caveats on how far this supports the invalidation mechanism:

- **Knowledge-update questions:** this is the category that tests invalidation most directly, and the gain is small with gpt-4o (78.2% → 83.3%) and negative with gpt-4o-mini (76.9% → 74.4%) ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)). The larger gains are in preference, temporal-reasoning and multi-session questions.
- **No ablation:** the paper never isolates invalidation, so the score cannot be attributed to it rather than to the shorter context or the graph search.
- **No other memory system:** the authors could not get MemGPT to run on LongMemEval ([p. 7, §4.3.1](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.4.3.1&page=7)), and this is a vendor paper tested on its own hosted service.
