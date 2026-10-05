**Invalidation.** Zep never deletes a fact; it gives a contradicted fact an end date ([p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)).

- **Facts are edges with four timestamps.** Two record when the fact was true in the world (`t_valid`, `t_invalid`). The other two record when the system created or expired it (`t'_created`, `t'_expired`).
- **Dates are resolved at ingestion.** Relative dates ("two weeks ago") are turned into real ones using the message's own timestamp.
- **An LLM checks for contradictions.** Each new edge is compared with semantically related existing edges.
- **The old fact is closed, not removed.** When a contradiction overlaps in time, the old edge's `t_invalid` is set to the new edge's `t_valid`.
- **Newer information always wins.** Priority follows ingestion order.

For example (mine, not the paper's): "lives in London" followed later by "moved to Berlin in March" leaves the London edge in place with `t_invalid` = March. The system can then answer both "where does she live" and "where did she live last year". Retrieval passes each fact to the agent with its validity range (p. 4–5).

**LongMemEval.** The only baseline is full context, meaning the whole ~115k-token history pasted into the prompt ([p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Model | Full context | Zep | Latency | Context tokens |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s | 115k → 1.6k |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s | 115k → 1.6k |

- **The headline "18.5%" is relative.** The absolute gains are 11.0 points for gpt-4o and 8.4 points for gpt-4o-mini (the paper's "15.2%").
- **No other memory system is compared.** The authors tried MemGPT but could not get it to answer on this benchmark (p. 7, §4.3.1). The evaluation is vendor-run against Zep's hosted service, with no ablations.
- **Invalidation itself is weakly supported.** Knowledge-update questions are the ones that test it most directly, and there Zep gains only with gpt-4o (78.2% → 83.3%) and slips with gpt-4o-mini (76.9% → 74.4%) (p. 7, Table 3).
- **One category gets clearly worse.** Questions about what the assistant said drop from 94.6% to 80.4% with gpt-4o (p. 7, Table 3).
