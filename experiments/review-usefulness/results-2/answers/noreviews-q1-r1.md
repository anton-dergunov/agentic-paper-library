**Short answer:** the 2025–26 work in your library has stopped treating this as a storage problem. Recording that a fact was superseded is largely solved; the open failure is that the old value still gets retrieved next to the new one and the answer model picks it, or keeps planning around it. This is from about 25 papers in `llm/memory/` and `llm/personalization/`; I did not search the web.

## A running example

The user said "I live in Seattle", and later "setting up utilities in my new Austin apartment". Nothing negates the first statement explicitly. A system can fail in three places:

- **Bank:** both facts are stored as equally live.
- **Retrieval:** "where should I ship this?" pulls both, or only Seattle.
- **Answer:** both are in context, correctly dated, and the model still plans around Seattle.

A-TMA names this "ghost memory" and argues that the three levels must be scored separately ([A-TMA, p. 1](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=section.1&page=1)).

## What systems do with the old fact

| Strategy | Papers | What goes wrong |
|---|---|---|
| Overwrite or delete | Mem0 (LLM picks ADD/UPDATE/DELETE/NOOP), Memory-R1 (same operations, learned by RL) | Loses history; online LLM updates also delete facts that did not conflict, which is LightMem's argument for deferring updates offline |
| Keep and invalidate | Zep/Graphiti (bitemporal edges; the old edge gets an end date), Mem0's graph variant, Memanto (non-destructive supersede) | The validity metadata exists but does not reliably reach the answer |
| Merge or rewrite notes | A-MEM, SimpleMem, MemoryOS | Blurs old and new as history grows |
| Time decay | MemoryBank, MemoryOS heat score | Age is not obsolescence; MemoryBank never tests whether forgetting helps |
| Keep, label by role | A-TMA (current / historical / transition labels passed to the answer model) | Gains depend heavily on the host system |

## What the evidence says

- **Timestamps alone are not enough.** On A-TMA's conflict-heavy benchmark, Graphiti/Zep retrieves supporting evidence 71% of the time but gets only 48% of conflict questions right; adding explicit state labels lifts that to 72% ([A-TMA, p. 10, Table 2](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.2&page=10)). The component ablation is small and mixed, so treat the mechanism as plausible rather than proven (p. 20).
- **Retrieving both versions is the dangerous case.** In MemSyco-Bench, A-MEM retrieves old and new memories together in 98.6% of update cases and scores 24% accuracy. Mem0 scores 53% when only the new memory is retrieved and 26% when both appear ([MemSyco-Bench, p. 9](http://pdf.invalid/llm/memory/benchmarks/MemSyco-Bench.%20Benchmarking%20Sycophancy%20in%20Agent%20Memory.pdf?page=9&search=Update%20cases%20fail)). Memory systems often raise outdated-memory use compared with simply giving the model the full dialogue (p. 7).
- **Retention and update trade off.** In DynamicMem, no architecture wins both. Accuracy on a changed preference falls from 89% to 39% for A-MEM as history grows, while append-only RAG and HippoRAG2 hold near 60% ([DynamicMem, p. 10, Finding 3](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?page=10&search=Retention%20and%20update)).
- **Where the LLM sits matters more than whether there is one.** ForgetEval finds that an LLM at write time hurts deletion (Mem0 with inference on: 43.6%), while an LLM hook at mutation time reaches about 92% on adversarial cases ([Control-Plane, p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)). This is a single-author paper whose own system is a subject.
- **Knowing the update does not change behaviour.** On the Stale benchmark, a prototype resolves the current state 91% of the time but adapts open-ended behaviour only 32% of the time ([StateAuditor, p. 1](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?dest=section.1&page=1)). HorizonBench shows the same with no memory system at all: all 25 models pick the pre-change value on over a third of their errors ([HorizonBench, p. 8](http://pdf.invalid/llm/personalization/benchmarks/HorizonBench.%20Long-Horizon%20Personalization%20with%20Evolving%20Preferences.pdf?page=8)).
- **Benchmarks agree it is unsolved.** Every agent is at or below 28% on MemoryAgentBench's multi-hop selective forgetting, and contradiction resolution is the weakest ability in BEAM, at 0.05 or below for every model and method (Table 1).

## Facts held in weights

The picture is worse there. MEMIT can write 10,000 facts at once but has no delete operation (p. 9). Hase et al. show that an edit succeeds on the fact itself while accuracy on facts that should change downstream falls from 0.97 to 0.01 ([Fundamental Problems, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)), though on one tiny model. MemoryLLM forgets by random decay, not by obsolescence. Larimar is the exception with an explicit forget operation (p. 3).

## How far to trust this

- Most system numbers are vendor-run and conflict across papers: Zep is best on knowledge updates in one study and scores 5.0 on selective forgetting in MemoryAgentBench.
- Nearly all the update benchmarks are synthetic, and HorizonBench's human annotators reach only 56–64% on its items.
- LongMemEval's knowledge-update questions check that the new fact is found, not that the old one is gone, so high scores there say little about this problem.
