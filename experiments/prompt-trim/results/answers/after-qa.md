## How Zep invalidates outdated facts

Zep never deletes an outdated fact. It closes the fact's validity window instead ([Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)).

- **Facts are edges with two timelines.** Each fact-edge stores four timestamps:
  - **When it was true in the world:** `t_valid` and `t_invalid`. Relative dates like "two weeks ago" are converted to real dates using the message's timestamp.
  - **When Zep recorded and retired it:** `t'_created` and `t'_expired`.
- **Checking for contradictions.** When a new edge comes in, an LLM compares it with existing edges that are semantically related. If they contradict each other and their validity periods overlap, the old edge's `t_invalid` is set to the new edge's `t_valid`.
- **Newer always wins.** Ties are broken by ingestion order: the most recently ingested information takes precedence.
- **The history stays in the answer context.** At query time, each retrieved fact comes with its validity range ([p. 4, §3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=section.3&page=4)). The model sees "worked at A, until March" next to "works at B, since March", not just the latest fact.

A toy example (mine, not from the paper): "I live in Boston" arrives in January and "I just moved to Austin" arrives in June. The Boston edge gets `t_invalid` = June, and both facts stay in the graph.

The contradiction check is a single LLM judgement. The paper doesn't publish that prompt or measure how accurate the check is. The appendix covers extraction and deduplication prompts only.

## LongMemEval results

The test set is LongMemEval_s, whose conversations average about 115k tokens. **The only baseline is full context**: the whole history goes into the prompt, using the same model. MemGPT couldn't be run on it because it can't load an existing message history ([p. 7, §4.3.1](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.4.3.1&page=7)). From [p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7):

| Model | Full context | Zep | Latency | Context size |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | **63.8%** | 31.3 s → 3.2 s | 115k → 1.6k tokens |
| gpt-4o | 60.2% | **71.2%** | 28.9 s → 2.6 s | 115k → 1.6k tokens |

Things to watch when reading these numbers:

- **The headline gains are relative.** The paper's "+15.2% / +18.5%" means +8.4 and +11.0 percentage points. For gpt-4o the relative gain actually works out to 18.3%.
- **Knowledge updates, the category invalidation is meant for, don't clearly improve.** With gpt-4o they go up 78.2 → 83.3, but with gpt-4o-mini they go down 76.9 → 74.4 ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)). The authors say weaker models misread the temporal data. The biggest gains are elsewhere: preferences 20.0 → 56.7, temporal reasoning 45.1 → 62.4 and multi-session 44.3 → 57.9, all with gpt-4o. Questions about what the assistant said earlier in a session (single-session-assistant) drop 94.6 → 80.4.
- **One row looks like a copy error.** Single-session-user shows identical numbers for both models (81.4 → 92.9).
- **The evidence is thin.** Zep's own team ran it against their hosted service. There are no ablations, so nothing separates the effect of invalidation from that of retrieval, and no other memory system is compared. For an independent comparison, Mem0 tests against Zep: `library/llm/memory/agent/Mem0 Building Production-Ready AI Agents with Scalable Long-Term Memory.md`.

On the earlier MemGPT benchmark (DMR), Zep scored 94.8% vs MemGPT's 93.4% with gpt-4-turbo. The authors themselves call that benchmark too easy ([p. 6, Table 1](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.1&page=6)).

I added this to the Q&A section of the paper's note (`notes/Zep. A Temporal Knowledge Graph Architecture for Agent Memory.md`).

Suggested commit message:

```
Add Zep invalidation and LongMemEval Q&A to its note

- Explains how an outdated fact is closed (its end date set to the new fact's start date) rather than deleted, and that the model sees validity ranges when answering.
- Gives the LongMemEval_s scores against the full-context baseline in percentage points, and notes the paper's "18.5%" is relative and works out to 18.3%.
- Records that knowledge-update accuracy falls with gpt-4o-mini, and the identical single-session-user row that looks like a copy error.
```
