Zep gives every fact two time ranges. When a new fact contradicts an old one, Zep sets an end date on the old fact rather than deleting it. On LongMemEval it beat a full-context baseline, meaning the model was given the entire chat history, not another memory system.

## How outdated facts are invalidated

[Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)

**The idea:** a fact is an edge between two entities, and the edge says when the fact was true. A toy example (ours, not from the paper):
- In March the user says "I work at Acme".
- In July they say "I started at Globex two weeks ago".
- The Acme edge is not deleted. It gets an end date of about late June, the start date of the Globex edge.

**How it works:**
- **Two timelines, four timestamps per edge.**
  - World time: `t_valid` and `t_invalid`, when the fact held.
  - System time: `t'_created` and `t'_expired`, when Zep learned the fact and when it retired it.
  - Relative dates such as "two weeks ago" are turned into real dates using the timestamp of the message they appear in (`t_ref`).
- **Finding contradictions.** When a new edge comes in, an LLM compares it with existing edges that have similar meaning. If they contradict each other and their time ranges overlap, the old edge's `t_invalid` is set to the new edge's `t_valid`.
- **Newer wins.** In a conflict, the information Zep received later always takes priority. Zep never weighs which source is more reliable.
- **History is kept.** Old edges stay in the graph. At query time, facts are returned with their date ranges, so the answering model can reason about what was true when ([p. 4, §3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=section.3&page=4)).

## LongMemEval result

[Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7). The test set is LongMemEval_s, with chat histories of about 115k tokens.

| Model | Full context | Zep | Context size | Latency |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | **63.8%** | 115k → 1.6k tokens | 31.3 s → 3.2 s |
| gpt-4o | 60.2% | **71.2%** | 115k → 1.6k tokens | 28.9 s → 2.6 s |

## Caveats

- **The gains are relative.** The paper's "+15.2%" and "+18.5%" are relative improvements. In absolute terms they are +8.4 and +11.0 points.
- **There is no comparison with another memory system on LongMemEval.** The authors tried MemGPT but could not get it to answer questions, because it can't load an existing chat history ([p. 7, §4.3.1](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=7&search=LongMemEval%20and%20MemGPT)). MemGPT was the baseline only on the easier DMR benchmark: 94.8% for Zep vs 93.4% for MemGPT.
- **Invalidation shows little benefit where it should matter most.** The knowledge-update question type is the one invalidation should help. There Zep scored 83.3% vs 78.2% with gpt-4o, and fell from 76.9% to 74.4% with gpt-4o-mini ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)). The biggest gains came on preference, temporal-reasoning and multi-session questions.
- **The evaluation is weak.** There are no ablations, so nothing shows how much invalidation itself adds. The vendor ran the evaluation on its own hosted service.

**Related papers in the library:**
- *Mem0*, a later memory system that compares itself against Zep.
- *LongMemEval*, the benchmark itself, which defines the question types.
- *HippoRAG*, a knowledge-graph memory with no notion of time.

I saved this answer to the Q&A in `notes/Zep. A Temporal Knowledge Graph Architecture for Agent Memory.md`. Suggested commit message:

```
Add Q&A to Zep note: fact invalidation and LongMemEval result

- Records how Zep sets end dates on contradicted facts and its LongMemEval_s scores against the full-context baseline, with absolute vs relative gains and the weak knowledge-update result.
```
