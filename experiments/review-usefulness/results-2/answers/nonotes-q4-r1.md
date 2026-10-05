The systems in `llm/memory/` differ on four things: where the memory lives, what unit is stored, when the LLM does its work (at write, at read, or in between), and how outdated facts are handled.

A running example: a user says "I work at Acme" in March and "I moved to Initech" in June, then asks in September where they work.

## Where memory lives

The broadest split, from [Memory in the Age of AI Agents, p. 12, §3](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?dest=section.3&page=12), is by carrier:

- **Token-level:** text or structured records in an external store, retrieved into the prompt. Almost everything in `agent/` is this.
- **Parametric:** the fact is written into weights, as in MEMIT or sparse memory finetuning (`parametric/`).
- **Latent:** vectors or KV caches the model attends to, as in MemoryLLM, M+ or Cartridges.

The same survey separates what memory is for: facts about the user and world, experience of how to do tasks, and working memory within a task (p. 31, §4).

## Families of external memory

- **Memory stream with reflection:** append every observation, score retrieval by recency, importance and relevance, and periodically write higher-level reflections. In the example both facts stay and recency has to favour Initech. See [Generative Agents, p. 8, §4.1](http://pdf.invalid/llm/memory/agent/Generative%20Agents.%20Interactive%20Simulacra%20of%20Human%20Behavior.pdf?dest=subsection.4.1&page=8).
- **Tiered, OS-style paging:** a small in-context block plus recall and archival stores, with the model moving data between them by function calls. The model itself would rewrite "employer" in its working context. See [MemGPT, p. 2, §2](http://pdf.invalid/llm/memory/agent/MemGPT.%20Towards%20LLMs%20as%20Operating%20Systems.pdf?dest=section.2&page=2); [MemoryOS, p. 4, §3.3](http://pdf.invalid/llm/memory/agent/Memory%20OS%20of%20AI%20Agent.pdf?dest=subsection.3.3&page=4) automates promotion and eviction with a heat score.
- **Extracted fact stores:** an LLM distils each exchange into short facts, then decides to add, update or delete against similar existing ones. Acme is overwritten at write time. This is [Mem0, p. 3, §2.1](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=subsection.2.1&page=3); Memory-R1 learns those operations with RL.
- **Graphs:** entities and relations rather than flat facts. [Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3) keeps both employment edges and marks Acme as invalid from June, so "where did I work in April?" is still answerable. [A-MEM, p. 3, §3](http://pdf.invalid/llm/memory/agent/A-MEM.%20Agentic%20Memory%20for%20LLM%20Agents.pdf?dest=section.3&page=3) links notes and rewrites old ones instead; HippoRAG uses the graph for associative retrieval.
- **Typed stores:** separate stores per memory type with their own schemas. [MIRIX, p. 6, §3.1](http://pdf.invalid/llm/memory/agent/MIRIX.%20Multi-Agent%20Memory%20System%20for%20LLM-Based%20Agents.pdf?dest=subsection.3.1&page=6) has six, each run by an agent. [Memanto, p. 5, §III-D](http://pdf.invalid/llm/memory/agent/Memanto.%20Typed%20Semantic%20Memory%20with%20Information-Theoretic%20Retrieval%20for%20Long-Horizon%20Agents.pdf?page=5) has thirteen categories over plain vector search and argues graphs are unnecessary.
- **Experience memory:** stores how to do things, not facts about the user. [Agent Workflow Memory, p. 2, §2](http://pdf.invalid/llm/memory/agent/Agent%20Workflow%20Memory.pdf?dest=section.2&page=2) induces reusable workflows, and [ReasoningBank, p. 4, §3.2](http://pdf.invalid/llm/memory/agent/ReasoningBank.%20Scaling%20Agent%20Self-Evolving%20with%20Reasoning%20Memory.pdf?dest=subsection.3.2&page=4) distils strategies from successes and failures. ExpeL, Memp and Dynamic Cheatsheet sit here too.

## What the comparisons show

- **No architecture wins everywhere.** A study of 12 systems finds graph methods strong on single-hop recall but weak on temporal reasoning, and local maintenance cheaper than global reorganisation: [Are We Ready, p. 7, §4.1](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=subsection.4.1&page=7).
- **Long context is still a strong baseline.** [EvoMemBench, p. 6, §5.2](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?dest=subsection.5.2&page=6) finds it competitive across 15 methods. Mem0's own paper has full context ahead on LoCoMo (about 73% against 67% judge score), and Mem0's advantage is p95 latency, about 1.4 s against 17 s: [Mem0, p. 13, §4.3](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=subsection.4.3&page=13).
- **Forgetting is under-tested.** Most benchmarks score recall only; [Control-Plane Placement, p. 8, §5.7](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=subsection.5.7&page=8) finds that an LLM at write time fixes different deletion failures than one at mutation time.

Treat the headline numbers with care: Mem0, Zep and Memanto are written by the vendors of those systems, and the forgetting study is a single-author paper from a company in the same space.

I read the sections linked above; Memory-R1, HippoRAG, ExpeL, Memp, Dynamic Cheatsheet and the parametric and latent papers are characterised from their index summaries only.
