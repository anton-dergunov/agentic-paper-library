**Short answer:** the research in your library says obsolete facts are the weakest part of LLM memory today, and the problem has shifted from storing the update to using it. Systems can usually record the new fact, but the old one still gets retrieved alongside it, and even when the model knows which is current it often still acts on the old one.

This is from the library only (no web search). Six of the most recent papers have no notes yet, so I read their abstracts and the relevant passages, not the full text: A-TMA, MemSyco-Bench, DynamicMem, Belief Memory, Memanto and the StateAuditor paper.

## A running example

A user says "I live in Seattle", and months later "setting up utilities in my new Austin apartment". Nothing negates the first statement explicitly. Three things can go wrong:

| Stage | Failure | Evidence |
|---|---|---|
| Write | The update is never recorded | HaluMem: update omission exceeds 50% for most systems, mostly because the original fact was never extracted ([p. 11](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?page=11)) |
| Retrieve | Seattle and Austin both come back, unlabelled | MemSyco-Bench: Mem0 scores 53.06 when only the updated memory is retrieved, 26.38 when old and new appear together ([p. 9](http://pdf.invalid/llm/memory/benchmarks/MemSyco-Bench.%20Benchmarking%20Sycophancy%20in%20Agent%20Memory.pdf?dest=subsection.4.4&page=9)) |
| Use | The model knows about Austin but still recommends Seattle restaurants | The Stale benchmark's prototype resolves the current state 91% of the time but adapts open-ended behaviour only 32% ([p. 1](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?page=1)) |

## The approaches

- **Overwrite or delete at write time (Mem0, Memory-R1).** An LLM compares each new fact with similar memories and picks add, update, delete or no-op ([Mem0, p. 3](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=3)). Memory-R1 trains that choice with RL. The weakness is that the LLM tends to link and keep rather than delete: Mem0 with inference on drops to 43.6% on ForgetEval's adversarial cases ([p. 8](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?page=8)).
- **Keep the old fact but mark it invalid (Zep, Mem0's graph variant).** Each fact carries a validity interval, and a contradicting fact closes the old one's interval ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)). Zep is the best system on knowledge updates in the independent comparison, but at 155 s per query ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
- **Keep everything and label each record's role (A-TMA).** Records are tagged active, superseded or transition, and retrieval picks the view the question asks for, so "where did I live before?" still works ([p. 6](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=subsection.4.3&page=6)). On top of Zep it lifts conflict accuracy from 0.480 to 0.720, though gains depend on the host system.
- **Defer updates offline (LightMem).** Insert only while online, reconcile in a "sleep" pass, on the argument that online updates wrongly delete non-conflicting facts ([p. 5](http://pdf.invalid/llm/memory/agent/LightMem.%20Lightweight%20and%20Efficient%20Memory-Augmented%20Generation.pdf?page=5)). In its own table the offline pass sometimes lowers accuracy.
- **Decay (MemoryBank, MemoryOS, MemoryLLM).** Old or unused memories fade. This targets capacity, not correctness: a stale fact that is recalled often gets stronger.
- **Store probabilities instead of conclusions (Belief Memory).** Competing candidates are kept with probabilities updated as evidence arrives, so a wrong early conclusion can be revised.
- **Audit the response (StateAuditor).** Check the draft answer against verified old-to-new transitions and repair it. It gains 5 points on Stale, but a weaker auditor wrongly invalidates valid facts (LongMemEval knowledge-update falls from .816 to .579, [p. 7](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?dest=subsection.6.4&page=7)).

## What the benchmarks agree on

- **Revision is much harder than retention.** On FactConsolidation multi-hop, every memory agent is at or below 28% ([MemoryAgentBench, p. 8](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?page=8)), and at or below 7% in EvoMemBench's re-run ([p. 6](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?page=6)).
- **Memory systems can be worse than plain long context.** Mem0, Letta and SimpleMem fall below the long-context baseline on updates in "Are We Ready". In PersonaMem-v3, Mem0 takes an outdated stance 51.4% of the time against 25.7% for a self-rewritten text memory ([p. 17](http://pdf.invalid/llm/personalization/benchmarks/PersonaMem-v3.%20Toward%20Omni-Platform%20Personal%20Intelligence%20for%20Holistic%20User%20Understanding.pdf?page=17)).
- **No architecture both keeps stable facts and replaces changed ones.** DynamicMem finds the mechanism that helps one hurts the other ([p. 10](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?page=10)).
- **Long context does not solve it either.** With the full history in context, all 25 models in HorizonBench do worse on changed preferences than on static ones, and pick the old value in over a third of their errors ([p. 8](http://pdf.invalid/llm/personalization/benchmarks/HorizonBench.%20Long-Horizon%20Personalization%20with%20Evolving%20Preferences.pdf?page=8)).

## Facts stored in weights

Model editing (MEMIT) can rewrite thousands of facts but has no delete operation and no notion of time. The sharper problem is that edits do not propagate: in a controlled testbed the edited fact succeeds while accuracy on facts that should change with it falls from 0.97 to 0.01 ([Fundamental Problems, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)). That result is from one 83M model and one editor.

## What is contested or weakly supported

- **Delete versus keep-and-label is unresolved.** ForgetEval requires the old fact to be gone from recall; A-TMA requires it to stay for historical questions. The two are scored on different benchmarks, so no paper here compares them directly.
- **Much of the evidence is self-interested or synthetic.** Zep and Mem0 are vendor-run, ForgetEval's author evaluates their own system, and HaluMem and "Are We Ready" share authors with MemOS, which wins. FactConsolidation uses counterfactual edits, and Mem-α excluded it from training as too synthetic.
- **A-TMA's component evidence is thin.** It uses a 3B answer model, and its ablation on three profiles shows small, mixed effects.
- **The Stale benchmark is not in the library.** I know it only through the two papers that cite it; it would be the natural one to add.
