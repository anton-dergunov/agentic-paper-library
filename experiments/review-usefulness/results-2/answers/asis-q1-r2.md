**Short answer:** current research treats stale facts as the weakest part of LLM memory. Systems now mark old facts as replaced, but benchmarks show this mostly fails once the history is long or the change has knock-on effects. This comes from the library's memory review and the papers it cites; I checked the figures below against the papers or their notes.

Take "I moved from Paris to Berlin". A memory can go wrong in three ways: it returns Paris, it returns both and the model blends them, or it returns Berlin but still answers "nearest airport" from Paris.

**What systems do**

- **Supersede and keep.** Zep gives each fact a validity interval, and a contradicted fact gets an end date instead of being deleted ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=section.2&page=3)). Memanto and Belief Memory also keep the old version ([Memanto, p. 5–6](http://pdf.invalid/llm/memory/agent/Memanto.%20Typed%20Semantic%20Memory%20with%20Information-Theoretic%20Retrieval%20for%20Long-Horizon%20Agents.pdf?page=5); [Belief Memory, p. 12](http://pdf.invalid/llm/memory/agent/Belief%20Memory.%20Agent%20Memory%20Under%20Partial%20Observability.pdf?dest=subsection.A.2&page=12)).
- **Remove.** Mem0 has an LLM choose add, update, delete or nothing for each new fact against its 10 nearest stored facts ([Mem0, p. 3–4](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=3)). Memory-R1 and Mem-α train that decision with reinforcement learning.
- **Label at read time.** A-TMA tags each fact as current, superseded or transitional, so retrieval and the answer model know which is which. On its own conflict benchmark this lifts Zep from 0.480 to 0.720 ([A-TMA, p. 10, Table 2](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.2&page=10)).

No paper in the library compares superseding with deleting on the same task.

**What the benchmarks find**

- **Stores that only append return the old fact.** After facts change, Zep scores 44.4, while Mem0 (15.6) and Letta (17.8) fall below plain long context at 20.0 ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
- **Multi-hop updates are close to unsolved.** On MemoryAgentBench every agent scores at most 28% ([p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)). EvoMemBench's memory methods reach at most 7% ([p. 6, Table 3](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?dest=table.3&page=6)).
- **Retaining and updating pull against each other.** In DynamicMem, A-Mem, which merges notes, falls from 89% to 39% on changed preferences as history grows. Append-only HippoRAG2 holds at 63% ([p. 11, Fig. 8](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?dest=figure.8&page=11)).
- **Deletion often fails.** In ForgetEval, graph memories pass 7–9.5% of adversarial deletion cases and Mem0 with LLM inference 43.6%. One LLM call at the moment of change lifts plain stores from 63–68% to about 92–93% ([p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)).
- **Weights have the same problem.** A model edit changes the target fact but not what follows from it: accuracy on facts that should change falls from 0.97 to 0.01 ([Fundamental Problems With Model Editing, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)).

**How far to trust it**

The direction is consistent across many 2026 papers, but each uses its own synthetic test, so the numbers don't compare across papers.

- **ForgetEval** has a single author who built one of the tested systems, and its gains shrink to 12–18 points on external cases.
- **A-TMA**'s LoCoMo gain is mixed: temporal F1 rises from 0.0295 to 0.1705, but temporal accuracy falls from 0.3707 to 0.3178 (p. 11, Table 3).
- **The model-editing result** comes from one 83M-parameter model and one editing method.

**Still open:** when to forget at all (decay curves are hand-set), and making an update propagate to its consequences.
