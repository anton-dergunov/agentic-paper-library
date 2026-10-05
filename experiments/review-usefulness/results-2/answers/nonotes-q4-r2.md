The library holds 42 papers on external agent memory (`llm/memory/agent/`), and they differ along three axes: what is stored, who decides what gets written, and how old facts are retired. I read the surveys and comparison studies for this answer; the one-line descriptions of individual systems come from the library's index summaries, not a re-read of each paper.

**A concrete example.** A user says "I moved from Berlin to Lisbon in March." Each family remembers this differently:

| Family | What it stores | Examples in the library | Weak spot |
|---|---|---|---|
| Stream and reflection | The raw turn, timestamped, plus periodic higher-level summaries ("user relocates often") | Generative Agents, MemoryBank | Summaries blur detail; nothing is overwritten |
| Tiered ("OS-style") | A small always-in-context core ("lives in Lisbon") with the rest paged out to archive | MemGPT, MemoryOS, LightMem | Depends on the model promoting and evicting correctly |
| Extracted facts | An atomic fact, reconciled against existing ones with add/update/delete operations | Mem0, Memanto, Memory-R1 | Extraction discards context; targeted overwrites are unreliable |
| Knowledge graph | Entities and relations, with validity times: `lives_in(Berlin)` closed in March, `lives_in(Lisbon)` opened | Zep/Graphiti, HippoRAG, Mem0's graph variant | Expensive to build and query |
| Linked notes / hybrid | Notes that link to each other and get rewritten as new ones arrive | A-MEM, MIRIX, MemOS | Maintenance cost grows with the store |
| Experience / procedural | Not the fact at all, but how a task was solved: a workflow, strategy or lesson | ExpeL, Agent Workflow Memory, ReasoningBank, Memp, Dynamic Cheatsheet | Only helps when tasks recur |

The first five answer "what is true about the user or the world"; the last answers "how do I do this better next time". [Memory in the Age of AI Agents, p. 31, §4](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?dest=section.4&page=31) calls these factual and experiential memory, with working memory as a third function. All six are what it calls token-level memory; the alternatives are memory in weights or in hidden states ([p. 12, §3](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?dest=section.3&page=12)), which the library files under `llm/memory/parametric/` (MemoryLLM, Titans, Cartridges).

**Who decides what to write.** 
- **Fixed pipeline:** Mem0 and Zep run a set extract-then-reconcile procedure.
- **The agent itself:** MemGPT edits its own memory through tool calls.
- **A trained policy:** Memory-R1, Mem-α and MemAgent learn memory operations with RL.
- **Offline:** Sleep-time Compute and LightMem move consolidation out of the query path.

**What the comparison studies found.**
- **No architecture wins everywhere.** Graph and time-aware systems (Zep, Cognee) lead on cross-session reasoning, tiered hybrids on long coherent dialogue, and plain long context on stateful execution ([Are We Ready, p. 7, §4.1](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=subsection.4.1&page=7)). EvoMemBench's index summary reports the same across 15 methods, with long-context baselines staying competitive.
- **Structure is costly.** Zep and Cognee reach the top utility only at 116–155 s per operation, against 3.7 s for LightMem ([p. 10, §4.5](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=subsection.4.5&page=10)).
- **Every abstraction layer loses information.** Compression, summarisation and fact extraction each discard detail, and consolidation often destroys chronological cues, so raw long context still wins on time-dependent queries ([§1, findings 4 and 6](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=section.1&page=1)).
- **Updates separate the families most.** Graph systems handle knowledge updates most reliably; append-only and fact-extraction stores return stale facts (same section, finding 3).
- **Forgetting is a separate skill from recall.** ForgetEval shows a system can saturate recall and fail every deletion test, and that where the LLM sits (at write time or at mutation time) decides which failures are fixed ([Control-Plane Placement, p. 8, §5.7](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=subsection.5.7&page=8)).

**One weakly supported result.** AgentMemBench finds a flat embedding store beats graphs on every quality axis ([p. 10, Table 5](http://pdf.invalid/llm/memory/benchmarks/AgentMemBench.%20A%20Systematic%20Benchmark%20for%20Evaluating%20Long-Term%20Memory%20Management%20Strategies%20in.pdf?dest=table.5&page=10)). Its graph was built with spaCy rather than an LLM extractor, and it used a 7B generator. Treat it as evidence about cheap graphs, not about Zep-class systems.
