This is drawn from the library's copies (about 20 papers in `llm/memory/` and `llm/personalization/`), not a web search. The short version: the field has moved from "overwrite the old fact" to "keep it, but mark it as no longer current", and the benchmarks say neither works reliably yet.

**The problem, by example.** A user said "I live in Seattle", then later "setting up utilities in my new Austin apartment". Both memories are true as written and both match "where should I ship this?". The distractor is a true fact from the wrong time, so relevance ranking cannot separate them.

**Three ways systems handle it**
- **Overwrite or delete.** Mem0 has an LLM choose ADD, UPDATE, DELETE or NOOP for each new fact; Memory-R1 trains that choice with RL. It loses history, and a wrong call destroys a valid fact.
- **Invalidate, don't delete.** Zep stores when each fact was true and when it was learned; a contradicting fact closes the old one's validity interval ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)).
- **Label the state for the answer model.** A-TMA argues timestamps alone are not enough: Graphiti retrieved supporting evidence 81% of the time but answered conflict questions 42.5% correctly on one profile. Tagging evidence as current, historical or transition raised conflict accuracy from 0.48 to 0.72 on the full benchmark ([A-TMA, p. 1](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=section.1&page=1)).

**What the benchmarks find**
- **Forgetting is barely tested.** ForgetEval finds recall scores say nothing about it: one store does respectably on recall and passes 0 of 385 forgetting cases. One LLM call at update time lifts pass rates from about 70% to about 93% ([ForgetEval, p. 8](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=subsection.5.7&page=8)).
- **Multi-hop over updated facts fails.** In MemoryAgentBench no method exceeds 28% ([p. 8](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=subsection.4.2&page=8)).
- **Updates are mostly missed, not botched.** HaluMem finds most systems miss over half the required updates, because the old fact was never extracted ([p. 11](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?dest=subsubsection.6.2.1&page=11)).
- **Structure helps.** A 2026 systems comparison finds graph-organised stores handle updates best and append-only stores return stale facts; Zep leads its knowledge-update slice with only 44.4 exact match ([Are We Ready, p. 9](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=subsection.4.3&page=9)).
- **Knowing is not acting.** A prototype resolved the user's current state 91% of the time but adapted its open-ended behaviour only 32% of the time ([StateAuditor, p. 1](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?dest=section.1&page=1)).

**In the weights.** Editing facts in parameters is in worse shape. Hase et al. argue it is belief revision and list 12 open problems, such as working out an edit's downstream consequences ([p. 1](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?page=1)). MemoryLLM-style latent pools forget by age, not by whether a fact was superseded ([p. 3](http://pdf.invalid/llm/memory/parametric/MEMORYLLM.%20Towards%20Self-Updatable%20Large%20Language%20Models.pdf?dest=subsubsection.3.1.3&page=3)).

**Weakly supported**
- **A-TMA:** it uses a 3B answer model, its LoCoMo F1 scores are very low in absolute terms (0.08 to 0.16), and its own ablation shows small, mixed component effects (p. 20).
- **ForgetEval:** the authors benchmark their own store, 30% of audited failures were scorer artifacts, and the gain depends on the LLM (+8 points with Qwen, none with Llama) (p. 9).

**Gaps in the library.** The Stale and Memora benchmarks are cited by these papers but not held here. Say if you want them queued in `INBOX.txt`.
