The research agrees that a memory system finds it hard to know when a stored fact is no longer true. It is the weakest part of every system tested. Two designs compete. One marks the old fact as replaced and keeps it. The other deletes it. No paper compares them on the same task, and forgetting by decay barely exists. This is drawn from `reviews/llm/memory.md` (70 papers, current). I checked the main numbers against each paper's note or its text.

**An example (ours, not from the papers).** A user says "I live in Paris" in March and "I've moved to Berlin" in August. Later they ask "where should the package go?" A system that only adds facts finds both statements, because both match the question, and may answer Paris. A system that deletes the March fact can no longer answer "where did I live before?" A system that keeps both needs to tell the model which one is current. [A-TMA](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?page=1) calls this failure **"ghost memory"**: old, current and in-between versions of a fact are retrieved together and mixed in the answer.

## How systems fail

- **Systems that only add facts keep returning the old one.** On LongMemEval's questions about changed facts, Zep scores 44.4. Mem0 (15.6) and Letta (17.8) score below a plain long context (20.0) ([Are We Ready…, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
- **Merging old and new facts blurs which is current.** In [DynamicMem, p. 11, Fig. 8](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?dest=figure.8&page=11), A-Mem tracks a changed preference at 89% right after the change. It falls to 39% as more conversation accumulates. Systems that store each statement separately recover to about 60%.
  - So "consolidate" and "keep only the current value" pull against each other.
- **Many update failures start when the fact is first stored.** [HaluMem, p. 11, Table 3](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?dest=table.3&page=11) scores each step separately. More than half of failed updates fail because the original fact was never extracted, so there was nothing to update.
- **Chained updates are almost unsolved.** MemoryAgentBench gives the model a list of facts that override each other. o4-mini handles it at 6K tokens: 100 on single-step questions and 80 on two-step ones. At 32K tokens it falls to 61 and 14 ([p. 10, Table 5](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.5&page=10)). Every memory agent scores at most 28%.
- **Even a correctly retrieved fact can be misused.** In [MemSyco-Bench, p. 7, Table 1](http://pdf.invalid/llm/memory/benchmarks/MemSyco-Bench.%20Benchmarking%20Sycophancy%20in%20Agent%20Memory.pdf?dest=table.1&page=7), adding memory makes models follow the user's outdated or wrong beliefs over the facts. Most errors happen after the right memory was retrieved.

## The design choices

**1. Supersede and keep, or delete.**

| | Who | Gains | Loses |
|---|---|---|---|
| Mark old fact replaced, keep it | Zep: each fact records when it became true and when it stopped ([p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)); Mem0's graph variant, A-TMA, Memanto, Belief Memory | Answers questions about the past; a wrong update can be undone | The old fact still reaches the prompt unless it is labelled |
| Delete | Mem0's DELETE, ForgetEval's purge | Required for privacy deletion; keeps the prompt clean | History is gone |

A-TMA does not change how the store works. It labels each fact as current, historical or transitional. On Graphiti/Zep this raises temporal F1 on LoCoMo from 0.0295 to 0.1705, and accuracy on its own conflict benchmark from 0.48 to 0.72 ([p. 10–11](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.3&page=11)). Two caveats:
- The paper has no note in the library, so this rests on its abstract and the review.
- According to the review, accuracy on temporal questions falls (0.37 → 0.32).

**2. When the LLM gets involved.** [ForgetEval](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6) finds that what matters is when the LLM steps in, not whether there is one.
- Stores without an LLM pass 63–68% of adversarial deletion cases.
- One LLM call at the moment a fact changes lifts them to 92–93% (p. 6, Table 2).
- Mem0 with an LLM at write time falls to 43.6%, because it links the new fact to the old one and keeps both.
- Graph memories pass 7–9.5%: turning text into entities loses the exact wording a targeted deletion needs.
- The evidence is weak. The study has one author, who built one of the systems tested. On 77 cases written by outside contributors, the gain shrinks to 12–18 points.

**3. Learned update rules.** Mem0 asks an LLM to choose ADD, UPDATE, DELETE or nothing for each fact. Memory-R1 trains that choice with reinforcement learning: 62.7 against 45.7 for Mem0 on LoCoMo ([p. 5, Table 1](http://pdf.invalid/llm/memory/agent/Memory-R1.%20Enhancing%20Large%20Language%20Model%20Agents%20to%20Manage%20and%20Utilize%20Memories%20via%20Reinforcement.pdf?dest=table.1&page=5)). The gain on LongMemEval is small (55.4 vs 54.2, [p. 17](http://pdf.invalid/llm/memory/agent/Memory-R1.%20Enhancing%20Large%20Language%20Model%20Agents%20to%20Manage%20and%20Utilize%20Memories%20via%20Reinforcement.pdf?dest=table.5&page=17)), and the baselines run well below their published numbers.

**4. Forgetting over time.** This is barely developed.
- MemoryBank's forgetting curve has a hand-set shape, and the paper never says when a weak memory is actually deleted ([p. 4](http://pdf.invalid/llm/memory/agent/MemoryBank.%20Enhancing%20Large%20Language%20Models%20with%20Long-Term%20Memory.pdf?page=4)).
- The only learned forgetting is inside a model: Titans' forget gate ([p. 17, Table 5](http://pdf.invalid/llm/memory/parametric/Titans.%20Learning%20to%20Memorize%20at%20Test%20Time.pdf?dest=table.5&page=17)).
- Every survey lists learned forgetting as an open problem.

## The same problem when facts live in the weights

Model editing fails in the same way. [Fundamental Problems With Model Editing, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14) builds a small test where the right answers after an edit are known exactly.
- The edited fact itself changes correctly.
- Facts that follow from it should also change, and accuracy on them falls from 0.97 to 0.01.

Put simply, "moved to Berlin" should also change "nearest airport". No system here does that, whether the memory is text or weights. Belief Memory and DeMem are first attempts, and both were only skimmed for the review.

## How strong the evidence is

Many 2026 papers point the same way, but each uses its own synthetic test with single runs. Several are vendor-run or single-author. There is no shared benchmark for updates. Apart from A-TMA, the update numbers above come from the full-read notes.

## Where to start reading

1. **Are We Ready…:** the broadest comparison of update strategies.
2. **ForgetEval:** for deletion.
3. **A-TMA:** for the case for keeping old facts with labels.
4. **Zep:** for how validity intervals are implemented.

I can add this answer to the review's Q&A if you want to keep it.
