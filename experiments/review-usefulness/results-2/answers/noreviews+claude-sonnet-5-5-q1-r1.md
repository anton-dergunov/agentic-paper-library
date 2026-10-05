I've been reading the library's memory folders and paper notes, and I have enough to answer. Everything below comes from the library, not a web search. I only read the abstract and introduction of A-TMA, DynamicMem and Belief Memory, because they have no notes yet.

## Short answer

Papers handle obsolete facts in four ways, from the oldest to the newest:

1. Overwrite or delete the old fact.
2. Keep the old fact but mark when it stopped being true.
3. Keep the old fact with an explicit current, historical or transition role.
4. Edit the model's weights.

The recent work says the first two are not enough. Most of the papers also show the problem is poorly measured.

## The approaches

**1. Write-time overwrite (Mem0 and similar).** For each new fact, the system retrieves the 10 most similar memories. An LLM then picks ADD, UPDATE, DELETE or NOOP ([Mem0, p. 3](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=3)). It is cheap and simple. The weakness is that a fact never extracted can never be updated. HaluMem finds more than 50% omission on the update step for most systems ([p. 11](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?page=11)).

**2. Bitemporal invalidation (Zep/Graphiti).** Each fact edge has both a world-time validity interval and an ingestion time. When a new edge contradicts an old one, the old edge's `t_invalid` is set to the new edge's `t_valid`, and newer information always wins ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)). This is the reference design, and Mem0's graph variant copies it by marking edges invalid instead of deleting them. On LongMemEval knowledge-update questions Zep goes from 78.2 to 83.3 with gpt-4o ([p. 7](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=7)). That result is vendor-run, with no ablations.

**3. State roles at retrieval and answer time (A-TMA, 2026).** The paper names the failure "ghost memory". Old, current and transition facts sit together in the store, get mixed during retrieval, and the answer model can't tell which one the query wants ([A-TMA, p. 1](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?page=1)).
- Their example: a former address should answer "where did the user live before?" but not "where should the package ship?".
- Their fix keeps superseded records and labels them current, historical or transition.
- On their own benchmark, an overlay on Graphiti/Zep raises conflict accuracy by 0.24 absolute. Temporal KG evidence alone had 0.812 evidence support but only 0.425 conflict accuracy.
- The gains depend on the host system, and the benchmark is the authors' own.

**4. Weight editing and continual learning.** Knowledge editing is the parametric version of the same problem, and the library's main caution is [Fundamental Problems With Model Editing](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?page=14). It argues editing is belief revision. In its small testbed the edited fact itself succeeds, but downstream accuracy on facts that should change falls from 0.97 to 0.01 (p. 14). That is one tiny model and one editor, so treat it as a warning, not a general result. [Sparse Memory Finetuning](http://pdf.invalid/llm/memory/parametric/Continual%20Learning%20via%20Sparse%20Memory%20Finetuning.pdf) and [Titans](http://pdf.invalid/llm/memory/parametric/Titans.%20Learning%20to%20Memorize%20at%20Test%20Time.pdf) address the same issue from the forgetting side.

## Where the evidence disagrees

**Keep history or delete it?** A-TMA argues that deleting loses history, so the old value should be kept and labelled. [Control-Plane Placement Shapes Forgetting](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?page=6) takes the opposite stance. Its ForgetEval requires superseded facts to be absent from the top-10 recall.
- Mem0 with LLM inference on falls to 43.6% overall, because it prefers to link and keep the old fact over deleting it (p. 8).
- Graphiti scores only 7.0% of evaluable cases, and HippoRAG 9.5%.
- Deterministic stores sit at 63–68% on the adversarial cases. A mutation-time LLM hook lifts them to about 92%.
- The paper's main finding is that *where* the LLM sits (write time, mutation time, or nowhere) matters more than whether there is one.
- Caveat: it is a single author, and their own system is a main subject.

**Existing benchmarks mostly test the wrong thing.** LongMemEval's knowledge-update questions check that the new fact is retrieved, not that the old one is gone. [MemoryAgentBench](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?page=10) has a FactConsolidation task, built from counterfactual edit pairs where "newer facts have larger serial numbers". o4-mini scores 100 and 80 (single-hop and multi-hop) at 6K tokens. At 32K it scores 61 and 14 (p. 10). So even a plain "newer wins" rule collapses with length.

**Append-only memory returns stale facts.** [Are We Ready For An Agent-Native Memory System?](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?page=9) finds Zep best on knowledge update (44.4 EM). Mem0 (15.6), Letta (17.8) and SimpleMem (6.7) fall below plain long context (20.0), which the paper calls "hallucinations of the past" (p. 9).

**Implicit change is the harder case.** HorizonBench and DynamicMem target preferences that change without being restated, such as a life event that shifts a preference, or drift across 16 apps over 15 months. HorizonBench argues the "most recent statement wins" rule would return exactly the stale value. It evaluates no actual memory system. I haven't read DynamicMem's results.

**Forgetting policies are weakly supported.** MemoryBank's Ebbinghaus-style decay never says how retention becomes deletion, and it has no ablation of forgetting. The survey [Memory in the Age of AI Agents](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?page=59) notes that LRU-style forgetting drops rare but vital long-tail facts (p. 59). Time-decay is not the same as supersession.

## What is new compared with older work

The older view (Zep, Mem0) treated obsolescence as a storage problem you could solve with validity intervals. The 2026 papers (A-TMA, ForgetEval, HorizonBench) say it spans three levels, and a single QA score hides which one failed:
- bank maintenance
- retrieval
- answer-time resolution

[Belief Memory](http://pdf.invalid/llm/memory/agent/Belief%20Memory.%20Agent%20Memory%20Under%20Partial%20Observability.pdf) is a different design. It keeps several candidate conclusions with Noisy-OR probabilities, so one wrong update can't lock in.

## Gaps in the evidence

- Most numbers are from the authors' own systems or benchmarks (Zep, Mem0, A-TMA, ForgetEval).
- No paper in the library compares the main approaches on one shared benchmark that tests both "new fact present" and "old fact absent or correctly labelled".
- Mem0's per-category labels on LoCoMo are permuted, so its category claims don't transfer to other papers.

If useful, I can write a Q&A entry into the notes for Zep, A-TMA and Control-Plane, or read A-TMA, DynamicMem and Belief Memory in full with `paperlib read`. The entry would hold the comparison above, so the next session doesn't re-derive it. I haven't changed any files, so there's no commit to suggest.
