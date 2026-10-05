**Invalidation.** Zep never deletes an outdated fact; it closes the fact's validity interval. Facts are edges in its knowledge graph (Graphiti), and each edge carries two pairs of timestamps:

- **Event time:** `t_valid` and `t_invalid` record when the fact was true in the world.
- **System time:** `t'_created` and `t'_expired` record when the system learned the fact or retired it.

When a new edge is extracted, an LLM compares it against semantically related existing edges, looking for contradictions. If one contradicts the new edge and their validity overlaps in time, the old edge's `t_invalid` is set to the new edge's `t_valid`. When the two conflict, the newer information always wins ([Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)).

For example, "I work at Acme" followed months later by "I started at Globex two weeks ago" leaves both edges in the graph. The Acme edge gets a `t_invalid` equal to the resolved Globex start date, which is worked out from the message's reference timestamp. Retrieval returns each fact with its `t_valid` and `t_invalid` fields, so the answering model can see the history.

**LongMemEval.** The only baseline is full-context: the whole conversation, about 115k tokens, put in the prompt of the same model. The benchmark is LongMemEval_s ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Model | Full-context | Zep | Latency (full-context → Zep) | Context tokens |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s | 115k → 1.6k |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s | 115k → 1.6k |

Three caveats on these numbers:

- **The headline gains are relative.** The paper's "15.2%" and "18.5%" improvements correspond to 8.4 and 11.0 percentage points. By my arithmetic the gpt-4o figure is 18.3%, not 18.5%.
- **There is no comparison with another memory system.** The authors tried to run MemGPT on LongMemEval and could not get it to answer the questions (p. 7, §4.3.1).
- **Invalidation is not clearly what drives the gain.** On knowledge-update questions, the type that most directly tests it, Zep goes from 78.2% to 83.3% with gpt-4o but drops from 76.9% to 74.4% with gpt-4o-mini. The large gains are on single-session-preference, temporal-reasoning and multi-session questions, and Zep loses on single-session-assistant questions (94.6% to 80.4% with gpt-4o) ([Zep, p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)).
