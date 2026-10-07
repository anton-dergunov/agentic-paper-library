Zep doesn't delete outdated facts. It marks them as no longer true and keeps them in the graph. On LongMemEval_s it scored 63.8% with gpt-4o-mini and 71.2% with gpt-4o. The only baseline was the same model reading the full ~115k-token conversation.

## Invalidating outdated facts

[Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)

Facts are stored as links (edges) between two entities, and each one carries timestamps on two timelines:
- **When the system learned it** (`t'_created`, `t'_expired`): the order in which messages were taken in.
- **When it was true in the world** (`t_valid`, `t_invalid`): relative dates like "two weeks ago" are turned into real dates using the timestamp of the message they came from.

When a new fact is added:
1. An LLM compares it with existing facts that have similar meaning, looking for contradictions.
2. If a contradiction overlaps in time, the old fact gets an end date: its `t_invalid` is set to the new fact's `t_valid`. It stays in the graph as history.
3. The newer information always wins, judged by when the system received it.

For example (ours, not from the paper): "I work at Acme" in March and "I started at Globex two weeks ago" in June gives the Acme fact an end date of about late May.

When Zep answers a question, it passes each fact to the model together with its valid and invalid dates (p. 4). So the model reading the context still has to work out which facts are current.

## LongMemEval results

[Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)

| Answering model | Full context | Zep | Context size (full → Zep) | Latency (full → Zep) |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | **63.8%** | 115k → 1.6k tokens | 31.3 s → 3.2 s |
| gpt-4o | 60.2% | **71.2%** | 115k → 1.6k tokens | 28.9 s → 2.6 s |

- **The headline gains are relative.** The paper's "+15.2% / +18.5%" are relative improvements; in absolute terms the gains are +8.4 and +11.0 points.
- **No other memory system was compared.** MemGPT is the baseline on the easier DMR benchmark, but the authors couldn't get it to answer on LongMemEval because it can't load an existing chat history ([p. 7, §4.3.1](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.4.3.1&page=7)).
- **Invalidation shows little benefit in the numbers.** Knowledge-update is the question type closest to it. It rose only from 78.2 to 83.3 with gpt-4o, and fell from 76.9 to 74.4 with gpt-4o-mini ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.3&page=7)). The authors think weaker models misread the date fields. The biggest gains are elsewhere: preference questions (20.0 → 56.7) and temporal reasoning (45.1 → 62.4). Single-session-assistant questions get worse (94.6 → 80.4).
- **The evidence is weak.** The vendor ran the evaluation on its own hosted service, and there is no experiment that turns invalidation off. So the paper doesn't show how much invalidation itself contributes.

The library's Mem0 paper later compares itself against Zep, which gives a second, non-Zep measurement.

I added this to the Q&A in `notes/Zep. A Temporal Knowledge Graph Architecture for Agent Memory.md`. You don't have an overview note for this paper.

Suggested commit message:

```
Add Q&A on Zep edge invalidation and LongMemEval results

- Records how Zep marks contradicted facts as no longer true, and that its LongMemEval gains are relative (+8.4 / +11.0 points absolute).
- Notes that knowledge-update, the question type closest to invalidation, barely improves and drops with gpt-4o-mini.
```
