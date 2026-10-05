## How Zep invalidates outdated facts

Each fact is an edge in the graph, such as "Alice WORKS_FOR Acme". It carries two timelines ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)):

- **World time:** `t_valid` and `t_invalid`, meaning when the fact was true.
- **System time:** `t'_created` and `t'_expired`, meaning when the system learned or retired it.

Relative dates are resolved against the message's timestamp. "I started a new job two weeks ago" gets a real start date, not the arrival date of the message.

When a new fact is extracted, an LLM compares it with related existing edges. If the two contradict each other over an overlapping period, the old edge is not deleted. Its `t_invalid` is set to the new edge's `t_valid`, so the old edge now ends where the new one begins. The rule is that newer information always wins.

The memory can then answer both "where does she live now?" and "where did she live last year?". Candidates are compared only against edges between the same pair of entities, which keeps the check cheap.

Two weaknesses:
- The contradiction check is an LLM judgment, and the paper doesn't measure how often it wrongly expires a fact.
- There are no ablations, so the contribution of the temporal mechanism isn't isolated.

## LongMemEval result

The benchmark is LongMemEval_s, with about 115k tokens of history ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=7)). The baseline is full context, meaning the whole history pasted into the prompt.

| Model | Full context | Zep |
|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% |
| gpt-4o | 60.2% | 71.2% |

- **Context size and latency:** Zep's context is about 1.6k tokens against 115k. Latency drops from about 30 s to about 3 s, roughly 90% less.
- **By question type (gpt-4o, p. 7, Table 3):** Zep gains most on preference questions (20.0 → 56.7), temporal ones (45.1 → 62.4) and multi-session ones (44.3 → 57.9). Knowledge-update questions improve only slightly (78.2 → 83.3).
- **Where it loses:** single-session-assistant questions drop from 94.6 to 80.4.

Caveats:
- **Baseline:** full context is the only real baseline. MemGPT could not be run on LongMemEval because it can't ingest a history, and no other memory system is compared.
- **Source:** the numbers come from the vendor, run on its own hosted service.
- **Earlier benchmark:** on the older DMR benchmark, Zep scores 94.8% against MemGPT's 93.4% and full context's 94.4%. The authors themselves call DMR too easy.

This comes from `notes/Zep. A Temporal Knowledge Graph Architecture for Agent Memory.md`, whose digest rests on a full read. I didn't re-check the figures against the paper text.

Related papers in the library:
- LongMemEval, the benchmark itself.
- MemGPT, the DMR baseline.
- Mem0, a later system that compares itself against Zep.
