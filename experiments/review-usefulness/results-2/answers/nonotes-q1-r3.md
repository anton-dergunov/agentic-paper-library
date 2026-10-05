This is drawn from the library only (I ran no web search), and I read the relevant sections of about fifteen papers rather than each in full.

**Short answer:** the research has moved from "delete or overwrite the old fact" to "keep it, but label it as superseded, and check that the answer actually uses the current one". Benchmarks agree this is still the weakest part of LLM memory.

Take "user lived in Seattle, now sets up utilities in Austin". Three things can go wrong, and current work treats them separately:

1. **The store still holds Seattle as live.**
   - Mem0 lets an LLM pick ADD / UPDATE / DELETE / NOOP per extracted fact ([Mem0, p. 3](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=subsection.2.1&page=3)).
   - Memory-R1 trains that choice with RL, because the untrained version misreads refinements as contradictions ([Memory-R1, p. 1, Figure 1](http://pdf.invalid/llm/memory/agent/Memory-R1.%20Enhancing%20Large%20Language%20Model%20Agents%20to%20Manage%20and%20Utilize%20Memories%20via%20Reinforcement.pdf?dest=figure.1&page=1)).
   - Zep never deletes: each fact carries a validity interval, and a contradicting fact closes the old one ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)).

2. **Retrieval returns both, unlabelled.** A-TMA calls this "ghost memory". Zep's temporal graph had the right evidence 81% of the time on one subset but answered conflict questions only 42.5% correctly. Passing explicit active / superseded / transition labels to the answer model raised that to 72.5% ([A-TMA, p. 1–2](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=section.1&page=1)).

3. **The model knows Austin but still plans around Seattle.** On the Stale benchmark a system resolved the current state 91% of the time but adapted open-ended behaviour only 32% of the time. StateAuditor checks from stored state to draft answer, not the reverse, for a 5-point gain ([StateAuditor, p. 1](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?dest=section.1&page=1)).

**What the benchmarks find**

- **Multi-hop forgetting:** every method scores at most 28% on reasoning over updated facts ([MemoryAgentBench, p. 8](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=subsection.4.2&page=8)).
- **Missed updates:** most systems miss over half of them, mainly because the original fact was never extracted ([HaluMem, p. 11](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?dest=subsubsection.6.2.1&page=11)).
- **Retain versus overwrite:** no system both keeps what stays true and overwrites what changes ([DynamicMem, p. 1](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?dest=section.1&page=1)).
- **Anchoring on the old value:** the best of 25 frontier models reaches 52.8%, and errors favour the pre-change value ([HorizonBench, p. 2](http://pdf.invalid/llm/personalization/benchmarks/HorizonBench.%20Long-Horizon%20Personalization%20with%20Evolving%20Preferences.pdf?dest=section.1&page=2)).
- **Architecture over model size:** graph-organised stores handle updates best, and a stronger LLM is not the fix ([Are We Ready, p. 9, Finding 3](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=subsection.4.3&page=9)).
- **Where the LLM sits:** ForgetEval finds an LLM call at mutation time reaches about 92% on adversarial forgetting, against 63–68% for deterministic stores ([ForgetEval, p. 8–9](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=subsection.5.7&page=8)).

**Facts held in weights**

This side is less settled. Hase et al. argue model editing is belief revision without a learned update mechanism: a few gradient steps on one sentence need not propagate to its consequences ([Fundamental Problems, p. 9](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=subsection.5.3&page=9)). MemoryLLM instead lets old knowledge decay exponentially from a fixed memory pool ([MemoryLLM, p. 2](http://pdf.invalid/llm/memory/parametric/MEMORYLLM.%20Towards%20Self-Updatable%20Large%20Language%20Models.pdf?dest=subsection.3.1&page=2)), which forgets by age rather than by whether the fact is still true.

**What is weakly supported**

- The 2026 results (A-TMA, ForgetEval, StateAuditor) are preprints evaluated largely on benchmarks their authors built.
- A-TMA's gains depend on the host system and are mixed on LoCoMo ([p. 12](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=section.6&page=12)).
- ForgetEval's trade-off picture rests on four systems.
- Time-decay forgetting (MemoryBank, MemoryOS) is outdated for this problem, since it removes what is old or unused, not what is false.

The Stale benchmark (Chao et al. 2026), which StateAuditor builds on, is not in the library; it would be the natural one to add.
