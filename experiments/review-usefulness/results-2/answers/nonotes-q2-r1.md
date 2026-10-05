**Invalidation.** Zep never deletes an outdated fact; it closes the fact's validity interval when a newer one contradicts it.

For example, "Alice works at Acme" is stored as an edge between two entities. When a later message says "I started at Initech two weeks ago", the old edge stays in the graph but is marked as no longer true from that start date.

The mechanism ([Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)):

1. **Temporal extraction.** Each message has a reference timestamp `t_ref`, which an LLM uses to resolve absolute and relative dates ("two weeks ago") into datetimes for each fact.
2. **Four timestamps per edge, on two timelines.** `t_valid` and `t_invalid` record when the fact held in the world. `t'_created` and `t'_expired` record when the system learned it and retired it.
3. **Contradiction check.** An LLM compares each new edge with semantically related existing edges.
4. **Invalidation.** Where a contradiction overlaps in time, the old edge's `t_invalid` is set to the new edge's `t_valid`. New information always wins, following ingestion order.

At retrieval, each fact is returned to the model with its `t_valid` and `t_invalid` fields, so it can tell current facts from superseded ones (p. 4, §3).

**LongMemEval.** The baseline is full context: the whole conversation of about 115k tokens placed in the prompt, on the LongMemEval_s set ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Model | Full context | Zep | Latency (full context → Zep) | Context tokens |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s | 115k → 1.6k |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s | 115k → 1.6k |

The paper's headline "15.2%" and "18.5%" improvements are relative; in absolute terms the gains are 8.4 and 11.0 points.

- **No memory-system baseline.** The authors tried to run MemGPT on LongMemEval but could not get it to answer questions (p. 7, §4.3.1), so the only comparison is full context.
- **Knowledge-update questions barely move.** This is the category invalidation should help most, yet it goes 76.9% → 74.4% with gpt-4o-mini and 78.2% → 83.3% with gpt-4o ([Zep, p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)).
- **Where the gains come from.** The largest improvements are in single-session-preference and temporal-reasoning questions; single-session-assistant gets worse (94.6% → 80.4% with gpt-4o).
- **No ablation.** Nothing in the paper isolates the effect of edge invalidation itself.
