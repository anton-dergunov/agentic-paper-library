Agent memory systems in the library fall into six kinds, and they differ mainly in what they store, who decides what gets written, and what happens when a fact changes. This rests on the library's notes for about 25 of the 70 memory papers; for the rest (marked * below) I used only the index summaries, not the papers.

A running example makes the differences concrete: the user says "I live in London", and three months later "I moved to Berlin".

| Kind | What is stored | What happens on "moved to Berlin" | Examples |
|---|---|---|---|
| Append-only stream | Raw turns or segments, plus LLM reflections | Both stay; retrieval ranking has to prefer the newer one | Generative Agents, MemoryBank, SeCom |
| Tiered context (OS-style) | A small always-in-prompt block, with older content paged out to searchable storage | The agent itself edits the in-prompt block through a function call | MemGPT, MemoryOS, LightMem |
| Extracted fact store | Atomic facts pulled out by an LLM | An LLM picks ADD / UPDATE / DELETE / NOOP against similar facts | Mem0; Memory-R1 and Mem-α learn this policy with RL |
| Graph | Entities and fact edges, or linked notes | Old edge gets an end date instead of being deleted (Zep); A-MEM rewrites neighbouring notes and deletes nothing | Zep, Mem0's graph variant, A-MEM, HippoRAG* |
| Experience (procedural) | Strategies, workflows and pitfalls distilled from past tasks | Not about user facts; the bank mostly just grows | ReasoningBank, ExpeL*, Agent Workflow Memory*, Dynamic Cheatsheet* |
| Latent or parametric | Vectors or weights inside the model | Overwritten or decayed; a single fact cannot be inspected or deleted | MemoryLLM, Titans, Cartridges, MEMIT |

## How they differ

- **Unit of storage:** raw text keeps detail but costs tokens, while summaries and extracted facts are compact but lose information. Topical segments beat turns, sessions and summaries in SeCom.
- **Who controls writes:** this can be a fixed pipeline (Mem0), the agent itself via tool calls (MemGPT), or a trained policy (Memory-R1, Mem-α). In Mem-α the training is what helps, not the memory design: the same framework scores 0.389 with the untrained model and 0.642 trained.
- **Update and forgetting:** the options are never deleting (Generative Agents, A-MEM), decay or eviction by a score (MemoryBank, MemoryOS), LLM-decided deletion (Mem0), and time-stamped invalidation (Zep).
- **What the memory is for:** facts about the user and the world, or experience on how to do tasks. The survey [Memory in the Age of AI Agents, p. 31](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?dest=section.4&page=31) adds working memory as a third function.
- **Write cost:** this scales with how far each write propagates. Zep and Cognee reach the top utility only at 155 s and 117 s per query, against 3.7 s for LightMem ([Are We Ready, p. 10, Fig. 11](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=figure.11&page=10)).

## What the evidence says

- **No kind wins everywhere.** Zep leads LongMemEval, MemOS leads LoCoMo, and plain long context leads the database workload ([Are We Ready, p. 7, Fig. 7](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=figure.7&page=7)). On tool-use execution, procedural memory is best ([EvoMemBench, p. 7](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?page=7)).
- **Full context is often still the strongest baseline when the history fits.** In Mem0's own paper it scores 72.90 against Mem0's 66.88, at 17 s versus 1.4 s p95 latency ([Mem0, p. 11, Table 2](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=table.2&page=11)). In EvoMemBench, Gemini-3-Flash on raw context scores 83.0 on a LongMemEval subset, against at most 52.0 for any memory method ([p. 6, Table 3](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?dest=table.3&page=6)).
- **Raw text beats summaries as the stored value.** [LongMemEval, p. 8, Fig. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?dest=figure.5&page=8) finds this, and LoCoMo, SeCom and the Are We Ready ablations agree.
- **Revising is much weaker than retaining.** On multi-hop questions over updated facts, every memory method scores 7% or less in EvoMemBench (p. 6). In a forgetting test, the two graph systems fail almost entirely (Graphiti 7.0%, HippoRAG 9.5%), and Mem0 with LLM extraction falls to 43.6% ([Control-Plane Placement, p. 8–9](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?page=8)).

## Caveats

- Most system papers are vendor-run, with few ablations.
- LoCoMo category labels are permuted between papers (Mem0 and MemoryOS against A-MEM), so per-category comparisons across papers do not transfer.
- Two of the comparison studies have ties to a system they rank well: Are We Ready and HaluMem to MemOS, and the forgetting study to its author's own Lethe.
