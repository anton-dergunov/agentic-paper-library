Agent memory systems fall into eight families, and the split that matters most is where the memory lives: as text outside the model, as cached hidden states, or in the weights ([Memory in the Age of AI Agents, p. 12](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?dest=section.3&page=12)). The family grouping is the one in `reviews/llm/memory.md`; I checked it against the paper notes and verified the numbers below in the papers.

Take one running example (mine, not from a paper): on Monday the user says "I moved to Berlin", and on Friday asks "where do I live?". Each family handles the Monday write and the Friday read differently.

## Text memory (most agent systems)

| Family | What happens on Monday | What happens on Friday | Main weakness |
|---|---|---|---|
| **Memory stream** (Generative Agents, MemoryBank) | The raw observation is appended; nothing is ever edited or deleted. | Entries are ranked by recency + importance + relevance. | The stream grows without bound, and "lives in London" stays alongside "Berlin". |
| **Extract-and-consolidate** (Mem0, A-MEM, LightMem, SeCom) | An LLM extracts the fact, then chooses add, update, delete or nothing against the 10 most similar stored facts. | The nearest facts by embedding are returned. | It costs LLM calls per message, and facts are lost at extraction. |
| **Graph** (Zep, HippoRAG) | The fact becomes an edge between entities; the London edge gets an end date instead of being deleted. | Keyword, embedding and graph search are combined, then reranked. | The store is large and slow to ingest, and targeted deletion is poor. |
| **Operating system** (MemGPT, MemoryOS, MemOS, MIRIX) | The context is treated as RAM; the model itself (MemGPT) or a usage score (MemoryOS) decides what to page out to storage. | The model issues its own searches, or tiers are read in order. | The paging decider is an extra component that no paper evaluates on its own. |
| **Learned write policy** (Memory-R1, Mem-α) | Same operations as Mem0, but chosen by a policy trained with RL on answer accuracy. | Similarity search, sometimes with a trained filter. | Training needs a benchmark with answers; evidence is thin. |
| **Experience** (ReasoningBank, ExpeL, Agent Workflow Memory) | Not facts but lessons: after each task, strategies and pitfalls are distilled from the trajectory. | Lessons from the most similar past task are injected. | Wrong lessons persist, and nothing is pruned. |

## Memory inside the model

- **Latent memory** (MemoryLLM, Cartridges, Memorizing Transformers): hidden states are kept and attended to later. Reads cost no prompt tokens, but no person can read the contents and you need the model's internals.
- **Weight memory** (MEMIT, Memory Layers, Titans): the fact is edited or trained into parameters. There is no context cost, but no single fact can be inspected or deleted, and edits don't propagate to what follows from them.

## What the differences cost in practice

- **Cost versus quality.** Mem0 answers with a p95 latency of 1.44 s against 17.12 s for full context, but full context still scores higher (72.90 against 66.88 on the LLM-judge metric) ([Mem0, p. 11, Table 2](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=table.2&page=11)).
- **Store size.** Mem0 keeps about 7k tokens per conversation and Zep's graph more than 600k; this is Mem0's own measurement of a competitor ([Mem0, p. 14](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=subsection.4.5&page=14)).
- **Where graphs help.** On long histories Zep beats full context, 71.2% against 60.2% on LongMemEval with 1.6k instead of 115k prompt tokens; this is vendor-run ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)).
- **Where graphs fail.** Abstracting text into entities loses the exact wording deletion needs: HippoRAG passes 9.5% of evaluable forgetting cases and Graphiti (Zep's engine) 7.0% ([ForgetEval, p. 6](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=section.5&page=6)). This is a single-author study whose own system is one of the subjects.
- **Independent runs are sobering.** On MemoryAgentBench a long-context GPT-5-mini scores 60.6 overall, while Mem0 scores 21.1, Zep 24.0 and MemGPT 28.3; plain BM25 reaches 41.5 ([MemoryAgentBench, p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)).
- **Writes are the bottleneck.** Every system except MemOS recalls under 60% of the facts it should have extracted ([HaluMem, p. 11](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?page=11)). The corresponding author is from the MemOS developer.
- **Experience memory does help agents.** ReasoningBank lifts WebArena success from 40.5 to 48.8 on Gemini-2.5-flash ([ReasoningBank, p. 6, Table 1](http://pdf.invalid/llm/memory/agent/ReasoningBank.%20Scaling%20Agent%20Self-Evolving%20with%20Reasoning%20Memory.pdf?dest=table.1&page=6)).

## What rests on thin ground

- HippoRAG, MIRIX, MemOS, ExpeL and Agent Workflow Memory have no note in `notes/`. Their one-line descriptions above come from the review only; I did not open those papers.
- The Mem0, Zep, MemoryOS and MemOS results are run by their own makers, and their LoCoMo numbers do not transfer between papers. The Mem0 and MemoryOS notes record that category labels are permuted or shifted between them.
