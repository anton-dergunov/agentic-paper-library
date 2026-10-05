Agent memory systems differ on four things: where the memory lives, what it is for, what unit and structure it is stored in, and who decides what gets written, changed or forgotten. This is drawn from the 70 papers in `llm/memory/`; about 30 have notes with page-level digests, and systems I cite without a page come from the index one-liners only.

A running example (ours, not from a paper): the user says "my boyfriend James" in March and "James and I broke up" in June, then asks in July "who should I bring to the wedding?". Each kind of system handles the June message differently.

## 1. Where the memory lives

The broadest survey here splits memory by carrier ([Memory in the Age of AI Agents, p. 12–31](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?dest=section.3&page=12)):

| Form | What it is | Examples in the library | Trade-off |
|---|---|---|---|
| **Token-level (external)** | Text, graphs or tables outside the model, retrieved into the prompt | MemGPT, Mem0, Zep, A-MEM | Inspectable and editable, but costs retrieval and context |
| **Latent** | Hidden states or KV caches kept between calls | MEMORYLLM, M+, Cartridges, Memorizing Transformers | Compact, but a fact cannot be inspected or deleted |
| **Parametric** | The weights themselves | MEMIT, Titans, sparse memory finetuning, Text-to-LoRA | No retrieval step, but edits don't propagate to consequences |

The survey's own guidance is token-level for auditable, high-churn facts, parametric for persona and style, and latent for edge or privacy-sensitive settings (p. 29–31). The James fact is high-churn, so it belongs in the first row, as does everything below.

## 2. What the memory is for

The same survey separates three functions ([p. 31–45](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?dest=section.4&page=31)):

- **Factual memory** holds facts about the user and the world. Most "memory layer" products are this: Mem0, Zep, MemoryBank, MemoryOS.
- **Experiential memory** holds what the agent learned from doing tasks. It ranges from raw trajectories, to distilled strategies (ExpeL, ReasoningBank, Dynamic Cheatsheet), to reusable workflows and skills (Agent Workflow Memory, Memp).
- **Working memory** manages the context within one task (MemAgent, MemGPT's working context).

## 3. How external stores are structured

This is where the named systems actually differ:

- **Flat stream with scored retrieval.** Generative Agents stores every observation and ranks by recency + importance + relevance; nothing is ever deleted ([p. 8](http://pdf.invalid/llm/memory/agent/Generative%20Agents.%20Interactive%20Simulacra%20of%20Human%20Behavior.pdf?page=8)). Both James records survive, and the newer one merely ranks higher.
- **Tiers with paging.** MemGPT keeps a small editable working context plus searchable recall and archival storage ([p. 2–3](http://pdf.invalid/llm/memory/agent/MemGPT.%20Towards%20LLMs%20as%20Operating%20Systems.pdf?page=2)). MemoryOS promotes and evicts between short, mid and long-term tiers by a heat score ([p. 4–5](http://pdf.invalid/llm/memory/agent/Memory%20OS%20of%20AI%20Agent.pdf?page=4)).
- **Extracted facts with CRUD.** Mem0 has an LLM extract facts, then choose ADD, UPDATE, DELETE or NOOP against similar existing memories ([p. 3–4](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=3)). The March fact is overwritten or deleted.
- **Temporal knowledge graph.** Zep stores facts as edges with validity intervals; a contradiction closes the old edge rather than deleting it ([p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)). It can answer both "who is her partner now?" and "who was it in April?".
- **Linked notes.** A-MEM writes notes, links them to neighbours, and rewrites the neighbours' descriptions when a new note arrives ([p. 4](http://pdf.invalid/llm/memory/agent/A-MEM.%20Agentic%20Memory%20for%20LLM%20Agents.pdf?page=4)).
- **Typed stores.** MIRIX (six stores, one agent each) and Memanto (thirteen categories, explicitly no graph) route by memory type.

A separate question is the unit stored. SeCom finds topical segments beat turns, sessions and summaries ([p. 6, Table 1](http://pdf.invalid/llm/memory/agent/On%20Memory%20Construction%20and%20Retrieval%20for%20Personalized%20Conversational%20Agents.pdf?dest=table.1&page=6)), and LongMemEval finds summaries or extracted facts as stored values lose information ([p. 8](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=8)).

## 4. Who controls writes and forgetting

- **Fixed rules:** FIFO eviction, heat scores, or MemoryBank's Ebbinghaus decay, which the paper itself never turns into an actual deletion rule ([p. 4](http://pdf.invalid/llm/memory/agent/MemoryBank.%20Enhancing%20Large%20Language%20Models%20with%20Long-Term%20Memory.pdf?page=4)).
- **The LLM, by prompt:** MemGPT's self-directed edits, Mem0's tool calls.
- **A trained policy:** Memory-R1 and Mem-α learn the write operations with RL. In Mem-α the training, not the memory design, gives the gain: 0.389 untrained vs 0.642 trained in the same framework ([p. 7, Table 3](http://pdf.invalid/llm/memory/agent/Mem-%CE%B1.%20Learning%20Memory%20Construction%20via%20Reinforcement%20Learning.pdf?dest=table.3&page=7)).
- **Offline consolidation:** LightMem only inserts online and reconciles in a "sleep-time" pass, arguing online updates wrongly delete non-conflicting facts ([p. 5](http://pdf.invalid/llm/memory/agent/LightMem.%20Lightweight%20and%20Efficient%20Memory-Augmented%20Generation.pdf?page=5)).

Maintenance splits the same way into timestamp versioning, capacity eviction and LLM consolidation ([Are We Ready, p. 3, Table 1](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.1&page=3)).

## What the independent comparisons say

- **No structure wins everywhere.** Across 12 systems, Zep leads LongMemEval, MemOS leads LoCoMo and plain long context leads the database workload ([Are We Ready, p. 7](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?page=7)). EvoMemBench finds the best family depends on the domain ([p. 8, Table 6](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?dest=table.6&page=8)).
- **Simple baselines are hard to beat.** On MemoryAgentBench, BM25 (41.5) matches the best memory agent, and Mem0, Zep and MemGPT score 21–28 ([p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)). In Mem0's own paper, full context (72.9) beats Mem0 (66.9); the win is latency.
- **Memory is better at retention than revision.** On multi-hop fact-update questions, every memory method scores 7% or less ([EvoMemBench, p. 6](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?page=6)).
- **Recall and forgetting are separate axes.** Graph abstraction, which helps temporal recall, nearly fails a deletion test: Graphiti passes 7% of the cases it could be scored on ([Control-Plane Placement, p. 8](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?page=8)). That study has one author, and their own system is a main subject.

Most headline numbers in the system papers are vendor-run. LoCoMo per-category figures also do not transfer between papers, because Mem0 and MemoryOS permute the category labels.
