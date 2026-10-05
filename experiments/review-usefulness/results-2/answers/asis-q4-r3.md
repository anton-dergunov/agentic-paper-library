The library's memory review ([reviews/llm/memory.md](../reviews/llm/memory.md)) sorts its 70 papers into eight families. The numbers below are checked against the paper notes.

## The first split: where the memory lives

Take one fact, "the user moved to Berlin". It can be kept in three places:

- **Text outside the model**: a note, fact or graph edge pasted back into the prompt when relevant. A person can read it and delete it, and it works with any model, including a hosted API.
- **A cache inside the model**: hidden states the model attends to later. It is cheap to read, but unreadable to a person and tied to the model that wrote it.
- **The weights**: an edit, a fine-tune or a gradient step. It costs no prompt tokens, but a single fact cannot be inspected or removed.

Almost every agent memory system stores text, because only text can be shown to a user and deleted on request.

## The eight families

| Family | One memory is | Who decides what to write | Strength | Weakness |
|---|---|---|---|---|
| Extract-and-consolidate (Mem0) | a short extracted fact | an LLM, checking each fact against its 10 nearest stored facts | small store, fast reads | facts are lost at extraction |
| Graph (Zep, HippoRAG) | an entity or a fact edge | an LLM with entity resolution | history over time, multi-hop questions | large store, slow ingestion |
| Operating system (MemGPT, MemoryOS, MemOS, MIRIX) | pages, tiers or typed entries | the model itself, a usage score, a scheduler or agents | a policy for when the context is full | the deciding component is never evaluated alone |
| Stream with reflection (Generative Agents, MemoryBank) | every observation | nobody: everything is kept | simple | grows without bound, ignores contradictions |
| Learned write policy (Memory-R1, Mem-α, MemAgent) | a fact or a slot | a policy trained by reinforcement learning | writes tuned to what helps answers | needs a reward; evidence is thin |
| Experience (ExpeL, Agent Workflow Memory, ReasoningBank) | a lesson, workflow or pitfall | the success or failure of a task | agents improve without training | wrong lessons persist, nothing is pruned |
| Latent (MemoryLLM, Cartridges) | hidden states or a trained cache | a forward pass or offline training | cheap reads | needs model internals; short retention |
| Weights (MEMIT, Memory Layers, Titans) | a weight change | an edit or a gradient step | no context cost | edits do not propagate to what follows from them |

## Differences that matter in practice

- **When the work is done.** Mem0 and Zep pay at write time and read cheaply; a long context pays everything at read time. Mem0 answers at 1.44 s p95 against 17.12 s for full context ([Mem0, p. 11, Table 2](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=table.2&page=11)).
- **What an update does.** Mem0 deletes a contradicted fact. Zep gives the old edge an end date and keeps it, so it can still answer "where did she live last year?" ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)).
- **Store size.** Mem0 keeps about 7K tokens per conversation and Zep's graph more than 600K, by Mem0's own measurement ([Mem0, p. 14](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=14)).
- **Facts or experience.** For facts about a user, raw text tends to beat summaries. For an agent's own experience it is the reverse: distilled lessons help and raw trajectories hurt.

## How much to trust the system papers

- **Long context is often as good.** Mem0's own full-context baseline beats it, 72.90 against 66.88 (same table as above). On MemoryAgentBench, long-context GPT-5-mini scores 60.6 against 21.1 for Mem0, 24.0 for Zep and 28.3 for MemGPT ([p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)). That comparison is confounded: the memory systems all ran on the weaker GPT-4o-mini.
- **Memory wins when the history stops fitting.** On LongMemEval's 115K-token histories, Zep scores 71.2% against 60.2% for full context, with 1.6K prompt tokens instead of 115K ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)). Zep's own team ran this.
- **Rankings between systems do not transfer.** Mem0, Zep, MemOS and MIRIX were each evaluated by their vendor, and the same system moves by more than the claimed margins from one paper to the next.
- **Most loss happens at write time.** In HaluMem, every system except MemOS recalls under 60% of the facts it should have extracted ([p. 11, Table 3](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?dest=table.3&page=11)).

To read further, start with Generative Agents, MemGPT, Mem0 and Zep in that order, then LongMemEval for what a benchmark should test.
