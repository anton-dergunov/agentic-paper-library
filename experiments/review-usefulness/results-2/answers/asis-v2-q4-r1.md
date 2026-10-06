The library's 70 memory papers describe dozens of named systems, but they fall into eight families. Six keep memory as text outside the model, and two keep it inside the model.

Take a user who says "I moved to Berlin in May" after earlier saying they live in London. Each family handles that sentence differently:

| Family | What it does with "moved to Berlin" | Buys | Costs |
|---|---|---|---|
| **Memory stream** (Generative Agents, MemoryBank) | Appends it as a timestamped record and ranks reads by recency + importance + relevance. | Simplicity. | London stays in the stream; nothing resolves the contradiction, and the store grows without bound. |
| **Extract-and-consolidate** (Mem0, A-MEM, LightMem) | An LLM extracts the fact, fetches the 10 most similar stored facts, and picks add, update, delete or no-op. | A small, readable, deletable store and fast reads. | LLM calls on every message, and consistency is checked only against those 10 neighbours. |
| **Graph** (Zep, HippoRAG) | Stores it as an edge between entities; the London edge gets an end date instead of being deleted. | History ("where did she live last year?") and multi-hop paths. | A large store, slow ingestion, and poor targeted deletion. |
| **Operating-system tiers** (MemGPT, MemoryOS, MemOS, MIRIX) | Treats the context as RAM and a store as disk; a model, a usage score, a scheduler or agents decide what is paged in and out. | An explicit policy for when memory is full. | An extra decision-maker that no paper evaluates on its own. |
| **Learned or derived write policy** (Memory-R1, Mem-α, SAGE) | Makes the same add/update/delete choice, but with a policy trained by reinforcement learning on answer accuracy, or a statistical rule. | Write decisions tuned to answers, or cheaper ones. | Needs a benchmark with answers as reward; evidence is mostly LoCoMo with small models. |
| **Experience memory** (ExpeL, Agent Workflow Memory, ReasoningBank) | Does not store user facts; stores lessons, workflows or pitfalls from finished tasks. | Agents improve across tasks without training. | A wrong lesson keeps being applied; ReasoningBank's store is append-only. |
| **Latent** (MemoryLLM, Cartridges) | Keeps hidden states or a trained cache that the model attends to. | Reads cost no prompt tokens. | Needs model internals; a person cannot read it. |
| **Weights** (MEMIT, Titans) | Edits or trains the fact into parameters. | No context cost at all. | A single fact cannot be inspected or deleted. |

## What separates them

- **Where the memory lives.** Text can be shown to a user, deleted on request and used with any hosted model; cache and weight memory win only on serving cost. Almost every agent system in the library therefore stores text ([Memory in the Age of AI Agents, p. 29–31](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?dest=subsection.3.4&page=29)).
- **When the work is done.** Mem0 and Zep pay at write time, and a long context pays on every read. Mem0 stores about 7k tokens per LoCoMo conversation and answers at p95 1.44 s, against 17.12 s for full context ([Mem0, p. 11, Table 2](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=table.2&page=11)).
- **Who decides what to write.** Nobody (streams), a prompt (Mem0, Zep), the model itself through function calls (MemGPT), a usage score (MemoryOS), or a trained policy (Memory-R1). In Mem-α the training is what helps, not the memory layout: the same design scores 0.389 with the untrained model and 0.642 trained ([Mem-α, p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Mem-%CE%B1.%20Learning%20Memory%20Construction%20via%20Reinforcement%20Learning.pdf?dest=table.3&page=7)).
- **How updates and forgetting work.** Streams only lower an entry's rank, Mem0 deletes, and Zep keeps the old fact with an end date.

## What the evidence says

- **Full context is still the quality ceiling on short histories.** In Mem0's own paper, full context scores 72.90 against Mem0's 66.88 on LoCoMo, where conversations are about 26k tokens (same table). On the 115k-token LongMemEval, Zep beats full context 71.2% to 60.2% ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)). Both results are vendor-run.
- **Graphs help updates, not recall or deletion.**
  - After facts change, Zep scores best: 44.4 against 15.6 for Mem0 ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
  - On deletion tests, graph systems pass only 7.0% (Graphiti) and 9.5% (HippoRAG) of cases ([ForgetEval, p. 9](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?page=9&search=7.0)).
  - On distant LoCoMo turns, an entity graph recovers almost nothing: Recall@5 of 0.001 against 0.573 for a plain dense store of all turns ([AgentMemBench, p. 10](http://pdf.invalid/llm/memory/benchmarks/AgentMemBench.%20A%20Systematic%20Benchmark%20for%20Evaluating%20Long-Term%20Memory%20Management%20Strategies%20in.pdf?page=10&search=0.573)).
- **Experience memory works best as distilled lessons.** ReasoningBank lifts WebArena success from 40.5 to 48.8 on Gemini-2.5-flash, ahead of Agent Workflow Memory at 44.1 ([ReasoningBank, p. 6, Table 1](http://pdf.invalid/llm/memory/agent/ReasoningBank.%20Scaling%20Agent%20Self-Evolving%20with%20Reasoning%20Memory.pdf?dest=table.1&page=6)).
- **No system dominates, and published comparisons do not transfer.** The independent testbed finds a different leader per workload. Per-category LoCoMo numbers are also unreliable across papers: Mem0 and MemoryOS print them under permuted or shifted column labels.

## How far to trust this

The family grouping is the review's (`reviews/llm/memory.md`, "Kinds of memory systems"). I checked every number above against the paper's text or its note. Sixteen of the papers in these folders have no note yet, including HippoRAG, MemOS, MIRIX, SAGE, ExpeL and Agent Workflow Memory; for those, the mechanism descriptions rest on the review and the abstracts only. `paperlib read llm/memory` would fill them in.

I changed no files.
