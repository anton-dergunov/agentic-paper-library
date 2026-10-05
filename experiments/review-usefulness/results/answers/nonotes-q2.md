**Invalidation.** Zep never deletes an outdated fact; it closes the fact's validity interval when a newer fact contradicts it ([Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)).

For example (my illustration, not the paper's): in March the user says "I work at Acme", and in June "I started at Globex last week". The first fact is not removed. Its validity is ended at the moment the Globex job began, so the graph can still answer "where did they work in April?".

The mechanism has three steps:

1. **Timestamps on every fact.** Each fact is a graph edge carrying four timestamps on two timelines:
   - `t_valid` and `t_invalid` give the period when the fact was true in the world.
   - `t'_created` and `t'_expired` give when the system learned the fact and when it stopped treating it as current.
   - Relative dates such as "two weeks ago" are resolved against the message's reference timestamp.
2. **Contradiction check.** When a new edge arrives, an LLM compares it with semantically related existing edges and looks for contradictions.
3. **Invalidation.** If a contradicting edge overlaps in time, the old edge's `t_invalid` is set to the new edge's `t_valid`. When two facts conflict, the more recently ingested one wins.

**LongMemEval.** The baseline is full-context: the whole conversation of about 115k tokens is put in the prompt, with no memory system ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).

| Model | Full-context | Zep | Latency (full-context → Zep) | Context tokens |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s | 115k → 1.6k |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s | 115k → 1.6k |

Three caveats on these numbers:

- **The headline gains are relative.** The paper's "15.2%" and "18.5%" improvements are relative; in absolute terms they are 8.4 and 11.0 points.
- **There is no MemGPT comparison.** The authors tried to run MemGPT on LongMemEval and could not get it to answer (p. 7, §4.3.1), so the only baseline is their own full-context run.
- **Invalidation is only weakly supported by the results.** Knowledge-update is the question type that tests it most directly. Zep goes from 78.2% to 83.3% there with gpt-4o, but drops from 76.9% to 74.4% with gpt-4o-mini ([Zep, p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)). The large gains are in single-session-preference, temporal-reasoning and multi-session, and single-session-assistant gets worse with both models (94.6% to 80.4% with gpt-4o).
