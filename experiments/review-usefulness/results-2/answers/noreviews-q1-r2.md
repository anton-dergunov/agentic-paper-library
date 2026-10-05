Short version: research has converged on **mark an obsolete fact as superseded rather than deleting it or letting it decay**, but the evaluations show this fixes only the storage step. Stale facts still leak through retrieval, through the answering model, and through behaviour that silently depends on the old value. This is drawn from the library's memory folders only; I did not search the web.

## An example

A user said "I live in Seattle" in March and "setting up utilities in my new Austin apartment" in June. A memory system can fail in four places:

1. **Store:** both facts sit there as equally true.
2. **Retrieval:** "where should I ship this?" pulls up Seattle because it matches just as well.
3. **Answer:** both are retrieved, and the model picks the wrong one.
4. **Behaviour:** the model knows about Austin but still recommends a Seattle dentist.

## What systems do at the store

| Strategy | Examples | Weakness |
|---|---|---|
| Overwrite or delete | Mem0: an LLM picks ADD/UPDATE/DELETE/NOOP per fact ([p. 3](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=3)); Memory-R1 learns that choice with RL | Loses history; a wrong delete is unrecoverable |
| Time decay | MemoryBank's forgetting curve ([p. 4](http://pdf.invalid/llm/memory/agent/MemoryBank.%20Enhancing%20Large%20Language%20Models%20with%20Long-Term%20Memory.pdf?page=4)), MemoryOS heat score | Age is not obsolescence; MemoryBank never ablates forgetting |
| Invalidate but keep | Zep: each fact has a validity interval, and a contradiction closes the old one ([p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)); Memanto: supersede / retain / annotate ([p. 5–6](http://pdf.invalid/llm/memory/agent/Memanto.%20Typed%20Semantic%20Memory%20with%20Information-Theoretic%20Retrieval%20for%20Long-Horizon%20Agents.pdf?page=5)) | The old fact is still retrievable |
| Defer updates offline | LightMem's "sleep-time" pass, argued on the grounds that online updates wrongly delete non-conflicting facts ([p. 5](http://pdf.invalid/llm/memory/agent/LightMem.%20Lightweight%20and%20Efficient%20Memory-Augmented%20Generation.pdf?page=5)) | Its own table shows the update can lower accuracy, 67.78 → 65.39 ([p. 6, Table 2](http://pdf.invalid/llm/memory/agent/LightMem.%20Lightweight%20and%20Efficient%20Memory-Augmented%20Generation.pdf?dest=table.2&page=6)) |

## What the evaluations find

- **Revision is much harder than retention.** On EvoMemBench's multi-hop fact-consolidation task every memory method scores 7% or less, while a long-context model reading the raw history scores 96 on the single-hop version against at most 54 for memory methods ([p. 6](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?page=6)).
- **Some memory systems are worse than no memory system.** On knowledge updates, Mem0 (15.6) and Letta (17.8) fall below plain long context (20.0); Zep leads at 44.4 ([p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
- **No design both keeps stable facts and replaces changed ones.** In DynamicMem, systems that merge updates into existing notes degrade as history grows (A-Mem 89% → 39% on changed preferences), while append-only ones hold up better ([p. 10](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?page=10)).
- **Many updates fail before the update step.** In HaluMem, update omission exceeds 50% for most systems because the new fact was never extracted ([p. 11](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?page=11)).
- **Where the LLM sits matters for deletion.** ForgetEval finds an LLM at write time hurts (Mem0 with inference 43.6%, Graphiti 7.0%), while an LLM hook at mutation time reaches about 92% ([p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)).

## Past the store

- **Retrieval and answering:** A-TMA names the problem "ghost memory". On its benchmark, Zep's graph retrieves supporting evidence 71% of the time but gets only 48% of conflict questions right. Labelling each retrieved item as current, historical or transition lifts that to 72% ([p. 10, Table 2](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.2&page=10)).
- **Behaviour:** the stale-dependencies paper cites a benchmark where a system resolves the current state 91% of the time but adapts its open-ended advice only 32% of the time, with the updated evidence visible in 67.8% of those failures ([p. 1](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?page=1)). Its fix audits the draft against each changed fact and gains 5 points ([p. 5, Table 1](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?dest=table.1&page=5)).

## Facts held in weights

Editing methods rewrite the target fact but not what follows from it. In a controlled testbed the edited fact reaches 1.00 accuracy while facts that should change as a consequence fall from 0.97 to 0.01 ([p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)); that is one small model and one editor. MEMIT has no deletion operation ([p. 9](http://pdf.invalid/llm/memory/parametric/Mass-Editing%20Memory%20in%20a%20Transformer.pdf?page=9)), and MemoryLLM forgets by randomly dropping memory tokens, so old facts fade whether or not they are obsolete ([p. 3](http://pdf.invalid/llm/memory/parametric/MEMORYLLM.%20Towards%20Self-Updatable%20Large%20Language%20Models.pdf?page=3)).

## How far to trust this

- **Conflicting requirements:** ForgetEval scores a system as correct only if the old fact is gone from recall; A-TMA wants it kept and labelled. Both are right for different cases (privacy purge versus a changed preference), and no paper here handles both.
- **Thin evidence:** ForgetEval is single-author, with the author's own system as a subject, and its gains shrink on an external subset ([p. 9](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?page=9)). A-TMA's gains depend on the host system, and it answers with a 3B model. Memanto's conflict resolution is not tested at all; the paper says its benchmarks do not cover contradictions ([p. 11](http://pdf.invalid/llm/memory/agent/Memanto.%20Typed%20Semantic%20Memory%20with%20Information-Theoretic%20Retrieval%20for%20Long-Horizon%20Agents.pdf?page=11)).
- **Not in the library:** the Stale benchmark (Chao et al. 2026), MemTrace and AriadneMem, which these papers lean on, and the retrieval-side literature on conflicts between retrieved and memorised knowledge.

A-TMA, Memanto, DynamicMem and the stale-dependencies paper have no notes yet; I read them directly, and `paperlib read` would give them digests.
