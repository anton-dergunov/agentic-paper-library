**Invalidation.** Zep never deletes an outdated fact: it closes the fact's validity interval, and the newer fact always wins.

- **Two timelines per fact.** Each fact is an edge between two entities carrying four timestamps: `t_valid` / `t_invalid` say when the fact held in the world, and `t'_created` / `t'_expired` say when the system learned or retired it. Relative dates ("two weeks ago") are resolved against the message's timestamp.
- **Contradiction check.** When a new edge is extracted, an LLM compares it with semantically related existing edges. If one contradicts it and their validity periods overlap, the old edge's `t_invalid` is set to the new edge's `t_valid`.
- **What retrieval sees.** The old edge stays in the graph, and retrieved facts are handed to the model with their date ranges, so it can tell what used to be true from what is true now.

A toy example (ours, not from the paper): "I work at Acme" creates `user —works_at→ Acme`, valid from 2023. A later "I joined Globex in March 2025" creates a new edge valid from 2025-03, and the Acme edge gets `t_invalid = 2025-03`.

See [Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3).

**LongMemEval.** The only baseline is full context: the whole ~115k-token conversation placed in the prompt, on the LongMemEval_s set ([p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Answering model | Full context | Zep | Context tokens | Latency |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 115k → 1.6k | 31.3 s → 3.20 s |
| gpt-4o | 60.2% | 71.2% | 115k → 1.6k | 28.9 s → 2.58 s |

- **The headline gains are relative.** The paper's "15.2%" and "18.5%" improvements are relative, not percentage points; the absolute gains are 8.4 and 11.0 points. The gpt-4o figure actually works out to about 18.3% from the table's own numbers.
- **Invalidation shows only a small effect.** On knowledge-update questions, the category that exercises it most directly, Zep goes 78.2 → 83.3% with gpt-4o but drops 76.9 → 74.4% with gpt-4o-mini ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)). The larger gains are on preference, temporal-reasoning and multi-session questions.
- **One category gets worse.** Single-session-assistant questions fall 94.6 → 80.4% with gpt-4o.
- **The evidence is weak.** No other memory system is compared: the authors could not get MemGPT to run on LongMemEval ([p. 7, §4.3.1](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.4.3.1&page=7)). There are no ablations, so nothing isolates what invalidation contributes, and the vendor ran the evaluation on its own hosted service.
