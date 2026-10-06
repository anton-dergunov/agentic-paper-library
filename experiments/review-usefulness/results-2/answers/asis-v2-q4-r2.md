Agent memory systems fall into eight families, and the split that matters most is where the memory lives: as text outside the model, as cached hidden states, or in the weights. Text can be read, corrected, deleted and used with any hosted model. The other two are cheaper to serve but opaque and need access to the model's internals.

A running example (ours, not from a paper): a user said "I live in Munich" in March and "I moved to Berlin" in May.

| Family | What it does with the example | Buys | Costs |
|---|---|---|---|
| **Extract-and-consolidate** (Mem0, A-MEM, LightMem) | An LLM extracts "lives in Berlin", compares it with the 10 most similar stored facts and updates or deletes "Munich" | Small store, fast reads, deletable entries | LLM calls on every message; facts are lost at extraction |
| **Graphs** (Zep, HippoRAG) | Keeps both as edges; the "lives in Munich" edge gets an end date instead of being deleted | History ("where did she live before?") and multi-hop paths | Large store, slow ingestion, poor targeted deletion |
| **Operating-system style** (MemGPT, MemoryOS, MemOS, MIRIX) | Treats the context as RAM and a store as disk; the model, a usage score, a scheduler or agents decide what is paged out or promoted | An explicit policy for when memory is full | An extra decision-maker that is not evaluated on its own |
| **Streams with reflection** (Generative Agents, MemoryBank) | Stores every observation, ranks by recency + importance + relevance, periodically writes higher-level "reflections" | Simplicity | Unbounded growth; both cities stay in the stream |
| **Learned write policies** (Memory-R1, Mem-α, SAGE) | Same add/update/delete choice as Mem0, but made by a trained policy or a derived rule instead of a prompt | Writes tuned to what helps answers, or cheaper | Needs a benchmark with answers as reward; thin evidence |
| **Experience memory** (ReasoningBank, ExpeL, Agent Workflow Memory) | Stores no facts about the user: it stores lessons from past tasks, such as strategies and pitfalls | Agents improve across tasks without training | A wrong lesson keeps being applied; nothing is pruned |
| **Latent** (MemoryLLM, Cartridges) | The move becomes hidden-state vectors the model attends to | No prompt tokens per read | Unreadable; needs model internals; can fade quickly |
| **Weights** (MEMIT, Titans, Memory Layers) | The fact is edited or trained into parameters | No context cost, large capacity | A single fact cannot be inspected or deleted |

## What the evidence says

- **Extraction pipelines trade accuracy for speed.** Mem0 scores 66.88 on LoCoMo against 72.90 for simply putting the whole conversation in context, but answers at a p95 of 1.44 s against 17.12 s ([Mem0, p. 11, Table 2](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=table.2&page=11)). This is the vendor's own run.
- **Most loss happens at write time.** Extraction recall is below 60% for every system but one ([HaluMem, p. 11](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?page=11)). Storing raw user turns beats storing summaries, 26.0 against 11.7 ([Are We Ready, p. 11, Table 3](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.3&page=11)). Both papers have an author from MemOS's developer.
- **Graphs help with change over time, not with general accuracy.**
  - Zep beats full context on LongMemEval, 71.2 against 60.2 with gpt-4o, vendor-run ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).
  - On questions after a fact changes, Zep scores 44.4 against 15.6 for Mem0, which falls below plain long context at 20.0 ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
  - Zep's store is over 600K tokens per conversation against about 7K for Mem0 ([Mem0, p. 14](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=14)).
  - Graph stores pass only 7–9.5% of deletion cases ([ForgetEval, p. 8](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?page=8)). This is a single-author study that includes the author's own system.
  - On distant LoCoMo turns a graph memory recalls almost nothing (Recall@5 0.001) where a plain vector store of all turns reaches 0.573 ([AgentMemBench, p. 10](http://pdf.invalid/llm/memory/benchmarks/AgentMemBench.%20A%20Systematic%20Benchmark%20for%20Evaluating%20Long-Term%20Memory%20Management%20Strategies%20in.pdf?page=10)).
- **Experience memory has the cleanest gains.** ReasoningBank lifts WebArena success from 40.5 to 48.8, against 44.1 for workflow memory ([ReasoningBank, p. 6, Table 1](http://pdf.invalid/llm/memory/agent/ReasoningBank.%20Scaling%20Agent%20Self-Evolving%20with%20Reasoning%20Memory.pdf?dest=table.1&page=6)). These are single runs with no variance reported.
- **In-model memory is cheap to serve but fragile or fixed.**
  - Cartridges matches in-context quality with 38.6× less memory, at about 30 minutes of training per corpus ([Cartridges, p. 1](http://pdf.invalid/llm/memory/parametric/Cartridges.%20Lightweight%20and%20general-purpose%20long%20context%20representations%20via%20self-study.pdf?page=1)).
  - MemoryLLM by design keeps about 1/e of a fact after 30 updates ([MemoryLLM, p. 3](http://pdf.invalid/llm/memory/parametric/MEMORYLLM.%20Towards%20Self-Updatable%20Large%20Language%20Models.pdf?page=3)).

The comparisons between systems are weak: most system papers are vendor-run on LoCoMo, which averages about 9K tokens and fits in context. The one independent stocktake finds that no architecture dominates ([Are We Ready, p. 7](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?page=7)).

## How this was checked

The family grouping follows the "Kinds of memory systems" section of `reviews/llm/memory.md`, which has a fuller write-up per family. The numbers above come from the papers' notes, or from the paper itself for AgentMemBench, which has no note. The table rows for HippoRAG, MIRIX, MemOS, Mem-α, SAGE, ExpeL and Agent Workflow Memory rest on the review alone.

One correction to the review: it gives graph memory's Recall@5 in AgentMemBench as "at most 0.005", but 0.005 is the summarisation strategy and the graph's figure is 0.001.
