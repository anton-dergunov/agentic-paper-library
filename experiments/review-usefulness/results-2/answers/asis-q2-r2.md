**Invalidation: old facts get an end date and are never deleted.**

Take "Alice lives in London" (stored as an edge between Alice and London), followed months later by "Alice moved to Berlin in March". Zep handles this in three steps:

1. **Date the new fact.** An LLM extracts when the fact became true, resolving relative dates ("two weeks ago") against the message's timestamp `t_ref`.
2. **Look for contradictions.** An LLM compares the new edge with semantically related existing edges.
3. **Close the old edge.** Where a contradiction overlaps in time, the old edge's `t_invalid` is set to the new edge's `t_valid`. London now reads "valid until March" and Berlin "valid from March".

Each edge carries four timestamps on two timelines:

- **World time (T):** `t_valid` and `t_invalid` record when the fact held true.
- **Ingestion time (T′):** `t'_created` and `t'_expired` record when the system learned the fact or retired it.

When facts conflict, the more recently ingested one always wins. Retrieval returns each fact with its validity range, so the model can answer both "where does she live" and "where did she live last year". See [Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3) and the extraction prompt at [p. 10, §6.1.5](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.6.1.5&page=10).

**LongMemEval: the baseline is full context, not another memory system.**

The baseline puts the whole ~115k-token conversation in the prompt. The dataset is LongMemEval_s, judged by GPT-4o ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Model | Full context | Zep | Latency | Context tokens |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s | 115k → 1.6k |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s | 115k → 1.6k |

**Caveats on the result:**

- **The headline gains are relative.** The paper's "15.2%" and "18.5%" improvements are relative; in absolute terms they are +8.4 and +11.0 points. By my arithmetic 60.2 → 71.2 is 18.3%, not 18.5%.
- **MemGPT is not compared here.** The authors could not get it to run on LongMemEval ([p. 7, §4.3.1](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.4.3.1&page=7)). MemGPT is the baseline only on the easier DMR benchmark (94.8% vs 93.4%, p. 6).
- **Invalidation itself is weakly supported.** There is no ablation of it. The knowledge-update question type, which tests it most directly, moves 78.2 → 83.3 with gpt-4o but drops 76.9 → 74.4 with gpt-4o-mini ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)). The big gains are in preference, temporal-reasoning and multi-session questions.
- **One category gets clearly worse.** Single-session-assistant falls 94.6 → 80.4 with gpt-4o.
- **The evaluation is vendor-run.** It ran on Zep's hosted service.

I changed nothing in the library, so there is nothing to commit.
