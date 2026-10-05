The research agrees on the diagnosis and not on the cure: memory systems store facts well, but noticing that a fact has stopped being true is where they fail, and no approach handles it reliably yet. This comes from the library's memory review, with the numbers below checked against the papers or their notes.

**The problem, by example** (mine, not from a paper): a user says "I live in Paris", and three months later "I've moved to Berlin". Asked "where should the parcel go?", the system can go wrong at three layers:

1. **Store:** the Paris fact is still there and looks as valid as the Berlin one.
2. **Retrieval:** both come back, with nothing saying which is current.
3. **Answer:** the model has the right fact and still plans around Paris.

Most systems work on the first layer only.

## What systems do with an old fact

- **Delete it.** Mem0 has an LLM compare each new fact with its 10 nearest stored facts and choose add, update, delete or nothing ([Mem0, p. 3–4](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=3)). A contradiction with anything outside those 10 goes unnoticed.
- **Supersede and keep it.** Zep gives each fact two time ranges (when it was true, when the system learned it) and closes the old fact with an end date instead of deleting it ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)). This keeps "where did she live last year?" answerable.
- **Label its role.** A-TMA argues that end dates are not enough, because old, current and "what changed" facts still reach the model mixed together ("ghost memory"). It tags each fact as active, superseded or transition, and builds the retrieved evidence for the state the question asks about ([A-TMA, p. 1](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?page=1)).
- **Hold it as a probability.** Belief Memory keeps several candidate conclusions per attribute. A contradicting observation cuts the old one's probability to 0.25 and archives the previous version, and retrieval down-weights entries that have not been updated recently ([Belief Memory, p. 12, App. A.2](http://pdf.invalid/llm/memory/agent/Belief%20Memory.%20Agent%20Memory%20Under%20Partial%20Observability.pdf?dest=subsection.A.2&page=12)).
- **Let it decay.** MemoryBank's forgetting curve is hand-set, and the surveys list learned forgetting as open. I have this from the review only.

No paper in the library compares deleting with superseding on the same task.

## What the benchmarks find

- **Structure for time helps, but the best score is still low.** On LongMemEval's knowledge-update questions, Zep scores 44.4 against 20.0 for a plain long context ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
- **Revising across several hops is close to unsolved.** On MemoryAgentBench's conflicting-facts task, every agent is at or below 28% on multi-hop questions ([p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)). EvoMemBench reruns it on 15 memory methods and none exceeds 7% ([p. 6](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?dest=table.3&page=6)).
- **It gets worse with length.** o4-mini solves that task at 6K tokens (100 single-hop, 80 multi-hop) and drops to 61 and 14 at 32K ([p. 10, Table 5](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.5&page=10)).
- **Merging memories damages updates over time.** In DynamicMem every system handles a fresh preference change (70–89%). As history grows, the merging systems fall (A-Mem 89% → 39%, SimpleMem 89% → 47%), while append-only ones hold better (HippoRAG2 88% → 63%, plain RAG 85% → 59%) ([DynamicMem, p. 10–11](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?page=10)).
- **Many updates fail before the update step.** In HaluMem, update omission exceeds 50% for most systems because the original fact was never extracted ([HaluMem, p. 11](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?page=11)).
- **Graphs are poor at targeted removal.** In ForgetEval, plain deterministic stores pass 63–68% of adversarial deletion cases, and one extra LLM call at the moment of change lifts them to about 92–93%. Graphiti passes 7% and HippoRAG 9.5%, and Mem0 with LLM inference 43.6%, because it links new to old instead of removing the old ([ForgetEval, p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)).

## The answer layer

This part sits in `llm/personalization` and the memory review only touches it.

- **Models fail even with the full history in context.** In HorizonBench, all 25 models do worse on preferences that changed than on static ones, and on more than a third of errors they pick the old value, against 25% by chance ([HorizonBench, p. 8](http://pdf.invalid/llm/personalization/benchmarks/HorizonBench.%20Long-Horizon%20Personalization%20with%20Evolving%20Preferences.pdf?page=8)). The changes there are implied by a life event, not restated.
- **A stale dependency is usually unsaid.** *When Memory Updates but Behavior Does Not* audits a draft reply against verified old-to-new transitions and repairs it. That lifts its score on the Stale benchmark from .686 to .736 ([p. 5](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?page=5)).
- **Weight editing has the same gap.** In a testbed where the correct post-edit answers are known, the edited fact succeeds but accuracy on facts that should change with it falls from 0.97 to 0.01 ([Fundamental Problems With Model Editing, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)).

## How far to trust this

- **Every test is synthetic and different.** Each paper uses its own simulated users or planted facts, so the numbers do not compare across papers.
- **A-TMA's gains are mixed.** On its own conflict benchmark, accuracy with Zep rises from 0.480 to 0.720. On LoCoMo, temporal F1 rises only from 0.0295 to 0.1705, and the paper calls the effect host- and metric-dependent ([p. 11](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.3&page=11)).
- **ForgetEval has one author**, who built one of the tested systems. On cases from other benchmarks the gain from the extra LLM call shrinks to 12–18 points.
- **The review misuses one number.** It cites BEAM's contradiction score (at most 0.053) as evidence on stale facts. That task tests noticing that the user said two incompatible things and asking which holds; BEAM scores knowledge update separately.
- **Three of these papers have no note yet:** A-TMA, Belief Memory and DynamicMem. I read the cited passages, not the whole papers.

I tried to add the BEAM correction and the answer-layer point to the review's Q&A, but `reviews/llm/memory.md` is not writable in this checkout, so nothing was changed.
