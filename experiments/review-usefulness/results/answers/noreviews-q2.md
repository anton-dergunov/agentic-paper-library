**Invalidation: old facts get an end date and are never deleted.**

Suppose the graph holds "Alice lives in London" and a new message says "Alice moved to Berlin in March". Zep stores the Berlin fact as a new edge valid from March, and closes the London edge by setting its end date to March. The London fact stays in the graph, so it can still answer "where did she live last year?".

The mechanics ([p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)):

1. **Each fact edge carries four timestamps on two timelines.** $t_{valid}$ and $t_{invalid}$ record when the fact held in the world; $t'_{created}$ and $t'_{expired}$ record when the system learned or retired it.
2. **Dates are resolved against the message's timestamp.** An LLM turns relative mentions such as "two weeks ago" into absolute dates using $t_{ref}$ (prompt on [p. 10, §6.1.5](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.6.1.5&page=10)).
3. **An LLM compares each new edge with semantically related existing edges** to find contradictions.
4. **On a temporally overlapping contradiction, the old edge's $t_{invalid}$ is set to the new edge's $t_{valid}$.** Newer information, by ingestion order, always wins.

At retrieval, facts are returned with their $t_{valid}$ and $t_{invalid}$ range, so the answering model sees which ones have expired (p. 4, §3).

**LongMemEval: the baseline is full context, not another memory system.**

The baseline pastes the whole ~115k-token history into the prompt ([p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)), on the LongMemEval_s split:

| Model | Full context | Zep | Latency (full context → Zep) | Context tokens |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 31.3 s → 3.20 s | 115k → 1.6k |
| gpt-4o | 60.2% | 71.2% | 28.9 s → 2.58 s | 115k → 1.6k |

The headline "15.2%" and "18.5%" improvements are relative; in absolute terms they are +8.4 and +11.0 points.

**Caveats**

- **No MemGPT comparison here.** The authors could not get MemGPT to run on LongMemEval (p. 7, §4.3.1), so MemGPT is the baseline only on the easier DMR benchmark (94.8% vs 93.4%, p. 6).
- **Invalidation is not isolated.** There are no ablations, so nothing shows how much of the gain comes from it.
- **Weak evidence on the category that tests it.** On knowledge-update questions Zep goes from 78.2% to 83.3% with gpt-4o, but drops from 76.9% to 74.4% with gpt-4o-mini ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)).
- **One category gets clearly worse.** Single-session-assistant questions fall from 94.6% to 80.4% with gpt-4o.
