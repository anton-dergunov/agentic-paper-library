Answer drawn from the library only (papers up to August 2026); I did not search the web.

**Short version:** the field has moved from "delete or overwrite the old fact" to "keep it, mark it superseded, and make sure the answer uses the right state". The 2026 papers agree that storing the update is the easier part, and that the failures sit in retrieval, in answering, and in behaviour that silently depends on the old value.

Take "lives in Seattle", then later "setting up utilities in my new Austin apartment". Three things can go wrong, and they map onto three lines of work.

**1. The store: overwrite, invalidate or decay**
- **Overwrite:** Mem0 has an LLM choose ADD/UPDATE/DELETE/NOOP per extracted fact. Memory-R1 shows this misfires (a second adopted dog is read as a contradiction of the first) and trains the choice with RL instead.
- **Invalidate, don't delete:** Zep/Graphiti stamps each fact with when it was true and when it was learned, and a contradicting fact closes the old one's validity window ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)). Memanto instead surfaces the conflict to the agent to supersede, retain or annotate ([Memanto, p. 5](http://pdf.invalid/llm/memory/agent/Memanto.%20Typed%20Semantic%20Memory%20with%20Information-Theoretic%20Retrieval%20for%20Long-Horizon%20Agents.pdf?page=5)).
- **Decay:** MemoryBank and MemoryLLM forget by time or usage. This is older and does not target obsolete facts: an old fact can still be true.
- **Comparison:** a 12-system study finds graph stores handle updates most reliably, while append-only and fact-extraction stores return stale facts ([Are We Ready, p. 1](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?page=1)). It also finds that consolidation destroys chronological cues, so raw long context still wins on time-dependent queries.

**2. Retrieval and answering: the right state for the question**
- **Ghost memory:** A-TMA's term for old, current and transition facts reaching the answer model unlabelled. On its benchmark Graphiti retrieves supporting evidence 81% of the time on one profile but resolves only 42.5% of conflicts; explicit current/historical labels raise that to 72.5% ([A-TMA, p. 2](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=section.1&page=2)).
- **Multi-hop:** in MemoryAgentBench every method scores at most 28% when the updated fact must be used in a multi-hop inference ([MemoryAgentBench, p. 8](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?page=8)).
- **Missed updates:** in HaluMem most systems miss over 50% of updates, mainly because the original fact was never extracted ([HaluMem, p. 11](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?page=11)).
- **Commanded forgetting:** ForgetEval tests supersede, purge and expiry directly. Deterministic stores pass 63–68% of adversarial cases; one LLM call at mutation time lifts this to about 92% ([ForgetEval, p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)).

**3. Behaviour: the model knows, but still plans around the old value**
- **Implicit dependence:** the Stale benchmark's own prototype resolves the current state 91% of the time but adapts open-ended advice only 32% of the time. StateAuditor checks the draft against each changed attribute and gains 5 points ([StateAuditor, p. 5](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?dest=subsection.6.1&page=5)).
- **Reverting to the original:** in HorizonBench the best of 25 models reaches 52.8%, and over a third of errors on changed preferences pick the originally stated value ([HorizonBench, p. 1](http://pdf.invalid/llm/personalization/benchmarks/HorizonBench.%20Long-Horizon%20Personalization%20with%20Evolving%20Preferences.pdf?page=1)).

**In the weights**

Model editing (MEMIT and successors) changes the target fact but not its consequences. In a controlled testbed, edits reach 1% accuracy on downstream facts that should have changed ([Fundamental Problems, p. 13](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=subsection.6.5&page=13)). The paper argues that next-token training never taught models belief revision. This is the parametric version of the multi-hop failure above.

**What is weakly supported**
- **Zep:** its own LongMemEval results show knowledge-update accuracy falling with gpt-4o-mini (76.9% to 74.4%) and rising only with gpt-4o (p. 7).
- **A-TMA:** it uses a 3B answer model, its LoCoMo F1 scores are very low in absolute terms, and its ablation is mixed.
- **ForgetEval:** it scores by substring match, and the authors' audit found 30% of sampled failures of their deterministic store were scorer artefacts. The mutation-time hook gave no gain on MemoryAgentBench's fact-update task.
- **StateAuditor:** no gain on a harder authored set; an earlier version over-corrected on conflict-free questions.

**Gaps in the library**

Several works these papers lean on are not here: the Stale benchmark (Chao et al. 2026), Memora/FAMA (Uddin et al. 2026), MQuAKE and MemConflict. I can queue them in `INBOX.txt` if you want them.
