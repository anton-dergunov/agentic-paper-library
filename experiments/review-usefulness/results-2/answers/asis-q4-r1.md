I've read the library's review of `llm/memory` and checked its key numbers against the papers; here is the answer.

## The short version

The library's 70 memory papers describe dozens of named systems, but they fall into eight families. The first split is where the memory lives: as text outside the model, as cached hidden states, or in the weights. Nearly all agent memory systems are the text kind, because only text can be shown to a user, deleted on request and used with any model ([Memory in the Age of AI Agents, p. 12](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?page=12)).

## One example through each family

Take a user who says on Monday "I moved to Berlin", having earlier said they live in Munich.

| Family | What happens to "moved to Berlin" | Buys | Costs |
|---|---|---|---|
| **Memory stream** (Generative Agents, MemoryBank) | The sentence is appended to a timestamped log; reads rank by recency, importance and relevance. | Simple. | Munich is still there, and nothing reconciles the two. |
| **Extract-and-consolidate** (Mem0, A-MEM, LightMem) | An LLM extracts the fact, fetches the 10 most similar stored facts and chooses add, update, delete or nothing. | A small, readable, deletable store and fast reads. | LLM calls on every message; facts are lost at extraction. |
| **Graph** (Zep, HippoRAG) | Berlin becomes an edge between entities; the Munich edge gets an end date instead of being deleted. | "Where did she live last year?" and multi-hop paths. | A large store, slow ingestion and weak targeted deletion. |
| **Operating system** (MemGPT, MemoryOS, MemOS, MIRIX) | The context is RAM and a store is disk; the model, a usage score, a scheduler or agents decide what is paged out or promoted. | A policy for when memory is full. | An extra decision-maker that no paper evaluates on its own. |
| **Learned write policy** (Memory-R1, Mem-α, MemAgent, SAGE) | Same as the pipeline, but the add/update/delete choice is trained by RL or derived from a rule. | Write decisions tuned to answer quality, or cheaper ones. | Needs a reward; evidence is mostly LoCoMo with small models. |
| **Experience** (ExpeL, Agent Workflow Memory, ReasoningBank) | Not applicable: it stores lessons and workflows from past tasks, not facts about the user. | Agents improve across tasks without training. | A wrong lesson keeps being applied; nothing prunes. |
| **Latent** (MemoryLLM, Cartridges) | The text is absorbed into hidden states or a trained cache that the model attends to. | No prompt tokens on a read. | Needs the model's internals; unreadable by a person. |
| **Weights** (MEMIT, Titans, Memory Layers) | The fact is edited or trained into parameters. | No context cost. | Cannot be inspected or deleted; edits don't propagate to what follows from them. |

## What actually separates them

The review reduces the designs to five questions: 

1. **What is one memory?** A turn, a fact, an edge, a lesson, a hidden state or a weight change.
2. **Who decides what to write?** Nobody, a rule, an LLM prompt, a trained policy or a gradient step.
3. **What shape is the store?** A list, a graph, tiers, typed stores, a cache or the parameters.
4. **How is a read chosen?** By similarity, keywords, a graph walk, the model's own searches or attention.
5. **When is the work done?** At write time (Mem0, Zep), at read time (long context) or in idle time (LightMem, Sleep-time Compute).

The fifth explains why costs are hard to compare: storage, ingestion and reading are separate budgets. Mem0 reports storing about 7K tokens per LoCoMo conversation against more than 600K for Zep's graph, and says Zep's new memories became usable only after hours ([Mem0, p. 14](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=14)). That is Mem0's measurement of a competitor, so treat it as a vendor claim.

## What the evidence says about choosing

- **Long context is the real baseline.** Mem0's own full-context baseline beats it, 72.90 against 66.88, but at a p95 latency of 17.12 s against 1.44 s ([Mem0, p. 11, Table 2](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=table.2&page=11)).
- **Memory wins when the history is long.** On LongMemEval's 115K-token histories, Zep scores 71.2% against 60.2% for full context with gpt-4o, using 1.6K prompt tokens ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)). This is also vendor-run.
- **Graphs are not a general accuracy upgrade.** In AgentMemBench, only a plain embedding store of all turns recovers distant LoCoMo turns: Recall@5 of 0.573, against 0.001 for the graph and 0.005 for summaries ([AgentMemBench, p. 10](http://pdf.invalid/llm/memory/benchmarks/AgentMemBench.%20A%20Systematic%20Benchmark%20for%20Evaluating%20Long-Term%20Memory%20Management%20Strategies%20in.pdf?page=10)).
- **Rankings between systems don't transfer.** According to the review, the same Zep is 6 points below Mem0 in one paper and 17 above in another; I did not recheck those tables.
- **In-model memory is cheap to serve.** Cartridges matches in-context quality with 38.6× less memory ([Cartridges, p. 1](http://pdf.invalid/llm/memory/parametric/Cartridges.%20Lightweight%20and%20general-purpose%20long%20context%20representations%20via%20self-study.pdf?page=1)). No paper here compares latent or weight memory with a text system on the same conversational benchmark.

## One correction to the review

The review says MemoryLLM "mostly forgets a fact after about 30 updates" and cites Fig. 5. The paper's figure shows accuracy still above the no-context baseline after 20 updates ([MemoryLLM, p. 7, Fig. 5](http://pdf.invalid/llm/memory/parametric/MEMORYLLM.%20Towards%20Self-Updatable%20Large%20Language%20Models.pdf?dest=figure.5&page=7)). The 30 is the design's decay constant from p. 3 (about 1/e of a fact is left after N/K = 30 updates), not a measured result. I have not edited the review; say if you want it fixed.

Everything else above that carries no page link rests on the review alone. The fuller treatment is in `reviews/llm/memory.md`, under "Kinds of memory systems" and "Findings".
