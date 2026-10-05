**Invalidation.** Zep never deletes a fact: it gives the old one an end date when a newer fact contradicts it.

- **Example (ours, not from the paper):** the graph holds "Alice lives in London" with a start date in 2023. A message then says "I moved to Berlin last month". Zep adds a Berlin edge whose start date is resolved from the message timestamp, and closes the London edge at that same date. Both "where does she live?" and "where did she live last year?" stay answerable.
- **Two timelines per fact:** each fact is an edge carrying four timestamps. $t_{valid}$ and $t_{invalid}$ record when the fact held in the world. $t'_{created}$ and $t'_{expired}$ record when the system learned and retired it.
- **Date resolution:** relative dates such as "two weeks ago" are resolved against the message's reference timestamp $t_{ref}$.
- **The check:** when a new edge arrives, an LLM compares it with semantically related existing edges. If it finds a contradiction that overlaps in time, it sets the old edge's $t_{invalid}$ to the new edge's $t_{valid}$.
- **Tie-break:** newer information always wins, following ingestion order.

All of this is in [Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3).

**LongMemEval.** The only baseline is full context: the whole conversation of about 115k tokens pasted into the prompt ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Model | Full context | Zep | Latency (full context → Zep) | Context tokens |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s | 115k → 1.6k |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s | 115k → 1.6k |

- **The headline "18.5%" is relative.** In absolute terms the gain is 11.0 points with gpt-4o and 8.4 points with gpt-4o-mini (15.2% relative).
- **No other memory system is compared.** The authors tried MemGPT but could not get it to answer on this benchmark ([p. 7, §4.3.1](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.4.3.1&page=7)). The evaluation is vendor-run on Zep's hosted service.

**Evidence that invalidation itself helps is thin.** The knowledge-update category is the one that tests it most directly, and there Zep goes from 78.2% to 83.3% with gpt-4o but drops from 76.9% to 74.4% with gpt-4o-mini ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)). The paper has no ablations, so nothing isolates what the timestamps contribute. The larger gains are elsewhere, with gpt-4o:

| Question type | Full context | Zep |
|---|---|---|
| single-session-preference | 20.0% | 56.7% |
| temporal-reasoning | 45.1% | 62.4% |
| multi-session | 44.3% | 57.9% |
| single-session-assistant | 94.6% | 80.4% |
