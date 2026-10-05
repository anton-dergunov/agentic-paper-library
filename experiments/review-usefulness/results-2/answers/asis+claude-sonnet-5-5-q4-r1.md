Agent memory systems differ mostly in where the memory lives and who decides what to write. The library's review of the area (`reviews/llm/memory.md`, "Kinds of memory systems") groups them into eight families. I took this from the review alone and didn't open the individual papers, so treat the numbers as the review's.

## First split: where the memory lives

| | Text (token) | Cache (latent) | Weights (parametric) |
|---|---|---|---|
| What it is | facts, notes or summaries pasted into the prompt | hidden states or KV pairs the model attends to | knowledge trained or edited into parameters |
| Readable or deletable by a person | yes | mostly no | no |
| Works with a hosted API | yes | no, needs the model's internals | no, needs the weights |
| Read cost | prompt tokens on every request | a forward pass over the cache | none |

Almost all agent-memory systems store text, because only text can be shown to a user, deleted on request, and handed to any model.

## Second split: five design questions

1. What is one memory? It could be a turn, a segment, a fact, an entity, a lesson, a hidden state or a weight change.
2. Who decides what to write? Nobody, a fixed rule, an LLM prompt, a trained policy or a gradient step.
3. What shape is the store? A list, a graph, tiers, typed stores, a cache or the weights.
4. How is a read chosen? Embedding similarity, keywords, a graph walk, the model's own searches or attention.
5. When is the work done? At write time, at read time or in idle time.

## The eight families

| Family | Examples | One memory is | Main trade-off |
|---|---|---|---|
| Extract-and-consolidate | Mem0, A-MEM, LightMem, SeCom | an LLM-extracted fact | Small store and fast reads, and entries can be deleted. It costs LLM calls per message, and consistency is checked only against 10 neighbours. |
| Graph | Zep, HippoRAG | an entity or a fact edge | Gives history over time and multi-hop paths. The store is large, ingestion lags, and the accuracy gain is small. |
| OS-style (tiered) | MemGPT, MemoryOS, MemOS, MIRIX | pages, segments or typed entries | Gives an explicit policy for when memory is full. It adds a decision-maker that nobody evaluates alone. |
| Stream with reflection | Generative Agents, MemoryBank | every observation | Simple. It grows without bound and handles no contradictions. |
| Learned or principled write policy | Memory-R1, Mem-α, MemAgent, SAGE | a fact or slot | Write decisions are tuned to answers or cheaper. It needs a reward, and the evidence is thin. |
| Experience | ExpeL, Agent Workflow Memory, ReasoningBank, Memp | a lesson or workflow | Agents improve without training. Wrong lessons persist. |
| Latent | Memorizing Transformers, MemoryLLM, Cartridges | hidden states | Cheap reads. It is unreadable and needs model access. |
| Weights | MEMIT, Larimar, Memory Layers, Titans | a weight change | No context cost. Facts can't be audited or deleted, and edits don't propagate. |

Mem0 and Zep do the expensive work when writing. A long context does it all when reading. LightMem and Sleep-time Compute move work into idle time.

## What the review says about how they compare

- **A long context is the baseline to beat, and it often wins.** The 2026 benchmarks, run by other groups, show it often matches memory systems. What memory reliably buys is lower cost.
- **Published comparisons don't transfer.** Each paper reports the system as best, and storage, ingestion and read costs are separate budgets. Mem0 stores about 7K tokens per LoCoMo conversation and Zep over 600K. Both put 1–3K tokens in the prompt.
- **Graphs aren't a good default.** In AgentMemBench, graph memory recovers almost none of LoCoMo's distant turns. In ForgetEval, graphs pass only 7–9.5% of deletion cases. Zep did best on updating facts in one test (44.4 against 15.6 for Mem0).
- **Most loss happens at write time, and updating and forgetting are where systems fail.** HaluMem finds most systems recall under 60% of what they should have stored.

## Where to start

The review has a "Where to start reading" section. I'd read the surveys first: Memory in the Age of AI Agents for the token/latent/parametric split, and Rethinking Memory in LLM-based Agents for the write/manage/read loop.

I can read the Findings section and check the key numbers against the papers' notes. I could also go deeper on one family, such as Mem0 against Zep.
