**Invalidation** ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3))

Zep never deletes a fact. It gives it an end date. Facts are edges in the graph, such as "Alice LIVES_IN London", and each edge carries two timelines:

- **World time:** `t_valid` and `t_invalid`, meaning when the fact was true.
- **System time:** `t'_created` and `t'_expired`, meaning when Zep learned the fact and when it retired it.

Relative dates like "two weeks ago" are resolved against the message's reference timestamp.

When a new edge is added, an LLM compares it with existing edges between the same pair of entities. If they contradict and their validity periods overlap, the old edge gets `t_invalid` equal to the new edge's `t_valid`. Newer information always wins. So "moved to Berlin" closes "lives in London" without erasing it. The agent can still answer "where did she live last year?".

Comparing edges only within one entity pair keeps the check cheap. It also avoids merging similar-looking facts about different entities.

**LongMemEval_s** (about 115k-token histories; [Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7))

The baseline is the full conversation pasted into the prompt, not another memory system:

| Model | Full context | Zep |
|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% |
| gpt-4o | 60.2% | 71.2% |

Zep's context is about 1.6k tokens against 115k. Latency drops from about 30 s to about 3 s, roughly 90% less.

By question type with gpt-4o (Table 3, same page), the gains are:

- Preference: 20.0 → 56.7
- Temporal: 45.1 → 62.4
- Multi-session: 44.3 → 57.9
- Knowledge-update: 78.2 → 83.3

Single-session-assistant questions get worse: 94.6 → 80.4.

**Caveats**

- MemGPT could not be run on LongMemEval because it can't ingest a history, so full context is the only baseline there. On DMR, Zep scores 94.8% against MemGPT's 93.4%, a margin the authors call too small to mean much.
- The paper has no ablations and no other memory systems. It is vendor-run on Zep's hosted service.
- [Mem0](library/llm/memory/agent) is a later paper that compares against Zep directly.

I took these numbers from the library's digest note for the paper and did not re-read the converted markdown. The note records no conversion problems.
