Every agent memory system runs the same loop: write something from the interaction, maintain the store, and read some of it back into the prompt. The library's 42 agent-memory papers fall into six families that differ mainly in what they store and what happens to an old fact when a new one contradicts it.

A running example (ours, not from a paper): the user says "I live in London", and three months later "I moved to Berlin".

| Family | What is stored | What happens to "London" | Examples in the library |
|---|---|---|---|
| Paged context | A small always-in-prompt block plus searchable archives | The model itself edits the block with a function call | MemGPT, MemoryOS, MemOS, MIRIX |
| Append-only stream | Raw records, plus summaries or reflections written on top | Nothing; both stay, and the newer one ranks higher at retrieval | Generative Agents, MemoryBank, SeCom, LightMem |
| Extracted fact store | Short facts an LLM pulls from each turn | An LLM picks ADD, UPDATE, DELETE or NOOP against similar facts | Mem0, Memory-R1, SAGE, Memanto |
| Graph | Linked notes, or entities with facts as edges | Zep gives the old edge an end date; A-MEM rewrites neighbouring notes and deletes nothing | Zep, A-MEM, HippoRAG, A-TMA |
| Experiential | Lessons, workflows and strategies from past tasks | Not applicable: it stores how to do things, not facts about the user | ExpeL, Agent Workflow Memory, ReasoningBank, Dynamic Cheatsheet, Memp |
| Parametric or latent | Weights, adapters or memory vectors inside the model | An edit or a gradient step | MemoryLLM, M+, Titans, MEMIT (in `llm/memory/parametric/`) |

A cross-cutting choice is who decides what to write: fixed rules, an LLM prompt, or a policy trained with reinforcement learning (Mem-α, Memory-R1, MemAgent).

## How the mechanisms differ

- **Paged context:** MemGPT treats the prompt as RAM and the archive as disk; under "memory pressure" the model saves what matters before messages are evicted ([MemGPT, p. 2–3](http://pdf.invalid/llm/memory/agent/MemGPT.%20Towards%20LLMs%20as%20Operating%20Systems.pdf?page=2)). MemoryOS replaces the model's judgement with fixed tiers and a heat score for eviction ([MemoryOS, p. 4–5](http://pdf.invalid/llm/memory/agent/Memory%20OS%20of%20AI%20Agent.pdf?page=4)).
- **Append-only stream:** Generative Agents scores each record by recency + importance + relevance and periodically writes "reflections" that cite their evidence ([Generative Agents, p. 8–9](http://pdf.invalid/llm/memory/agent/Generative%20Agents.%20Interactive%20Simulacra%20of%20Human%20Behavior.pdf?page=8)). Later work in this family mostly argues about the unit to store: SeCom finds topical segments beat turns, sessions and summaries ([SeCom, p. 6, Table 1](http://pdf.invalid/llm/memory/agent/On%20Memory%20Construction%20and%20Retrieval%20for%20Personalized%20Conversational%20Agents.pdf?dest=table.1&page=6)).
- **Fact store:** Mem0 retrieves the 10 most similar memories for each new fact and lets the LLM choose the operation ([Mem0, p. 3–4](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=3)). It is cheap to read but lossy, because whatever extraction misses is gone.
- **Graph:** Zep keeps two timelines per fact, when it was true and when it was learned, so it can answer both "where does she live" and "where did she live last year" ([Zep, p. 3, §2.2.3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)). Your own note on Zep covers this well.
- **Experiential:** ReasoningBank distils up to three strategy items per finished task, from failures as well as successes, and only ever appends ([ReasoningBank, p. 4](http://pdf.invalid/llm/memory/agent/ReasoningBank.%20Scaling%20Agent%20Self-Evolving%20with%20Reasoning%20Memory.pdf?page=4)).

## What the evidence says

- **No family wins everywhere.** An independent comparison of 12 systems found a different leader on each workload ([Are We Ready, p. 7](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?page=7)).
- **Full context often beats memory when the history fits.** Mem0's own paper has full context at 72.90 against its 66.88 ([Mem0, p. 11, Table 2](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=table.2&page=11)). On MemoryAgentBench plain BM25 scores 41.5 while Mem0, Zep and MemGPT score 21–28 ([MemoryAgentBench, p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)).
- **Raw text beats summaries.** Storing raw user turns scored 26.0 against 11.7 for summaries in one ablation ([Are We Ready, p. 11, Table 3](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.3&page=11)).
- **Updating is the weak spot, and it is not the same as forgetting.** Zep is best on knowledge-update questions (44.4), while Mem0 and Letta fall below plain long context ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)). Yet when asked to actually delete something, Zep's Graphiti engine passes 7.0% of the adversarial cases it could be scored on ([Control-Plane Placement, p. 8–9](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?page=8)).
- **Richer writes cost more.** Zep and Cognee reach the top utility only at 155 s and 117 s per query, against 3.7 s for LightMem ([Are We Ready, p. 10](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?page=10)).
- **Experiential memory is best on tool-use execution**, and the best family changes by domain ([EvoMemBench, p. 7–8](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?page=7)).

## How far to trust this

- **Vendor-run numbers:** most system papers are evaluated by their own authors, and re-runs by others come out much lower (A-MEM, Mem0).
- **LoCoMo category labels:** Mem0 and MemoryOS permute them, so per-category comparisons across papers do not transfer.
- **Conflicts of interest:** two of the independent studies have authors from the MemOS developer, and the forgetting study's single author evaluates their own system.
- **Coverage:** the six families are my grouping, not a taxonomy taken from one of the surveys. I worked from the library's notes on 17 of the 42 agent papers and 5 of the 10 benchmarks; the rest, including MemOS, MIRIX, HippoRAG, ExpeL and Agent Workflow Memory, are placed by their one-line index summaries only.
