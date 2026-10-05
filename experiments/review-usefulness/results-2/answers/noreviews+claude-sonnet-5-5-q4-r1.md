The library has 70 papers on this under `llm/memory/`. Below, "what's stored" and "how it's managed" are the axes that separate the systems. I'm working from the index summaries, not from full reads of the papers. The surveys (below) give the formal taxonomies.

## 1. Where the memory lives

| Kind | What's stored | Library papers |
|---|---|---|
| **In-context / tiered** | A small window plus an external store the model pages in and out. | MemGPT, Memory OS of AI Agent (MemoryOS: short, mid and long-term tiers, promoted by a heat score), LightMem |
| **External text or notes** | Extracted facts or notes in a vector store. | Mem0, A-MEM, MemoryBank, MIRIX, O-Mem |
| **External graph** | Entities and relations, often with time. | Zep/Graphiti (bitemporal: when a fact was true vs. when it was learned), HippoRAG, Mem0's graph variant |
| **Experience or procedural** | Workflows, strategies and insights distilled from past trajectories. | Agent Workflow Memory, ExpeL, Memp, ReasoningBank, Dynamic Cheatsheet |
| **Parametric** | Knowledge in weights or activations: editing, memorizing transformers, test-time training. | The 18 papers in `llm/memory/parametric/` |
| **Unified** | Several kinds under one scheduler. | MemOS (plaintext, activation and parameter memory) |

## 2. How memory is managed

- **Hand-designed pipeline.** A fixed extract, consolidate, retrieve flow, as in Mem0, Zep and MemoryBank. MemoryBank forgets by Ebbinghaus-style decay, strengthened on each recall.
- **The LLM manages it as an agent.** In MemGPT, A-MEM and MIRIX the model decides what to write and link. MIRIX gives each of six typed stores its own agent. MemMA runs the whole cycle with cooperating agents.
- **Learned with RL.** Memory-R1 learns ADD/UPDATE/DELETE/NOOP from 152 training pairs. Mem-α learns memory construction, and MemAgent learns to overwrite a fixed-size memory while reading long text.
- **Gated writes.** SAGE uses a novelty gate so only ambiguous writes reach an LLM, which saves cost.
- **Offline or "sleep" processing.** Sleep-time Compute, and LightMem's offline update stage.

## 3. Where they differ most

- **Unit of storage.** SeCom (On Memory Construction and Retrieval for Personalized Conversational Agents) finds topical segments beat turns, sessions and summaries. xMemory (Beyond RAG for Agent Memory) argues flat top-k over a self-similar stream returns redundancy, so it decouples before aggregating.
- **Structure vs. simplicity.** Graph systems (Zep, HippoRAG) sit against Memanto, which argues graphs are unnecessary and uses 13 typed categories with conflict resolution instead.
- **Time and updates.** Zep's bitemporal model targets stale facts. A-TMA names "ghost memory", where old, current and transitional facts mix at retrieval.
- **Forgetting.** Control-Plane Placement Shapes Forgetting (ForgetEval) tests 13 systems. It finds that where the LLM sits decides which forgetting failures get fixed. DeMem frames forgetting as rate–distortion.
- **Uncertainty.** Belief Memory keeps several candidate conclusions with Noisy-OR probabilities instead of committing to one.
- **Personalisation, security and governance.** O-Mem builds user profiles, MIRIX has a sensitivity-level vault, and A Survey on Long-Term Memory Security covers attacks and defences.

## 4. Where to start

- **Taxonomies:** Memory in the Age of AI Agents, Rethinking Memory in LLM based Agents (parametric vs. contextual forms, six atomic operations including consolidation and forgetting), and Memory for Autonomous LLM Agents (mechanisms and evaluation gaps).
- **Evaluation caveat:** Are We Ready For An Agent-Native Memory System? argues end-to-end F1 hides cost, per-module trade-offs and robustness to updates. The ten papers in `llm/memory/benchmarks/` (LongMemEval, LoCoMo and others) are where to check the numbers.
- **Origin of the ideas:** Generative Agents introduced reflection and retrieval scored by recency, importance and relevance. Most later systems build on that.

I haven't opened the per-paper notes or the PDFs, so I have no page numbers to cite. I can read a few of these in full and write a comparison with pages and links. Mem0, Zep, A-MEM and MemGPT would be the natural set for comparing the main designs.
