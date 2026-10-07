Zep marks an old fact as no longer true instead of deleting it. On LongMemEval it beat a full-context baseline, which puts the whole conversation history in the prompt. I checked the numbers below against the paper, not only its note.

## How outdated facts are invalidated

In Zep's knowledge graph, each fact is stored as a link (an "edge") between two entities. Every fact carries two timelines ([p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)):

- **System time:** `t'_created` and `t'_expired` record when Zep learned the fact and when it retired it.
- **World time:** `t_valid` and `t_invalid` record when the fact was actually true. Relative dates like "two weeks ago" are converted to real dates using the message's timestamp (`t_ref`).

When a new fact arrives:

1. An LLM compares it with existing facts on related topics and looks for contradictions.
2. If a contradicting fact was true over an overlapping period, the old fact's `t_invalid` is set to the new fact's `t_valid`. The old fact stays in the graph, so its history can still be queried.
3. Newer information always wins, judged by when Zep received it.

**Example (ours, not from the paper):** "I work at Acme" (said in March) and later "I started at Globex two weeks ago" (said June 15). The Acme fact gets `t_invalid ≈ June 1`. Answers then use facts with their date ranges, so the answering model sees that Acme is past and Globex is current ([p. 4, §3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=section.3&page=4)).

## LongMemEval results

The baseline is **full context**: the whole conversation history, about 115k tokens, goes into the prompt ([p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)):

| Model | Full context | Zep | Context tokens | Latency |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | **63.8%** | 115k → 1.6k | 31.3 s → 3.2 s |
| gpt-4o | 60.2% | **71.2%** | 115k → 1.6k | 28.9 s → 2.6 s |

Caveats when reading these numbers:

- **The headline gains are relative.** The "15.2%" and "18.5%" in the text are +8.4 and +11.0 points. 71.2/60.2 actually works out to 18.3%.
- **There is no other memory system to compare against.** The authors couldn't get MemGPT to answer questions on LongMemEval ([p. 7, §4.3.1](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.4.3.1&page=7)). MemGPT was compared only on the easier DMR benchmark: Zep 94.8% vs MemGPT 93.4%.
- **No ablation tests the invalidation mechanism by itself.** The question type it should help most is knowledge-update. That improves only with gpt-4o (78.2 → 83.3) and *drops* with gpt-4o-mini (76.9 → 74.4) ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)). The biggest gains are on preference questions (20.0 → 56.7 with gpt-4o) and temporal reasoning. The authors say weaker models may not make good use of the date fields.
- **Zep's own team ran the evaluation**, on its hosted service.

Related papers in the library: [[LongMemEval]] defines the question types, and [[Mem0]] later compares itself against Zep.

I added this as a Q&A entry in `notes/Zep. A Temporal Knowledge Graph Architecture for Agent Memory.md`. Suggested commit message:

```
Add Zep Q&A on fact invalidation and LongMemEval results

- Records that invalidation sets t_invalid on the old fact instead of deleting it, and that an LLM decides what counts as a contradiction.
- Gives the LongMemEval gains in absolute points against the full-context baseline, and notes that knowledge-update drops with gpt-4o-mini.
```
