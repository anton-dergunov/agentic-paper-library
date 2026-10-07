## Short answer

Recognising that a stored fact has stopped being true is the weakest part of current memory systems. The library's papers (mostly 2025–2026) agree on four things:

1. **Old facts keep coming back.**
2. **The failure usually starts when facts are written, not when they are retrieved.**
3. **The field hasn't settled whether an outdated fact should be marked as replaced or deleted.**
4. **Updating one fact rarely updates the facts that depend on it.**

Every result comes from a synthetic benchmark the authors built themselves, so the direction is clear but the sizes of the effects are not.

## The problem, with an example

*(The example is mine, not from a paper.)* A user says in March "I live in Moscow" and in July "I just moved to Berlin." Most memory stores only ever add text, so both facts stay in the store. A question like "what's a good weekend trip?" retrieves both, and the model mixes them up or picks the wrong one. [A-TMA, p. 1](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?page=1) calls this **"ghost memory"**: old, current and in-between versions of a fact are all retrieved and blended into one answer.

## What the evidence shows

**Old facts keep coming back.**
- [Are We Ready For An Agent-Native Memory System?, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9) measures questions where a fact has changed:
  - Zep, which gives each fact a validity interval, scores 44.4 and Cognee 37.8.
  - Mem0 (15.6), Letta (17.8) and SimpleMem (6.7) score below simply putting the whole history in the context (20.0).
  - The authors call this "hallucinations of the past."
  - The run isn't neutral: two of its authors build MemOS, and Mem0's very low scores suggest it may have been misconfigured.

**Reconciling conflicting facts across several steps is close to unsolved.**
- MemoryAgentBench's selective-forgetting task gives the model counterfactual edits with serial numbers, where the newer fact wins.
- Every memory agent scores at most 28% on the multi-hop version ([p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)).
- o4-mini solves it at 6K tokens (100 single-hop, 80 multi-hop) but drops to 61 and 14 at 32K ([p. 10, Table 5](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.5&page=10)). The difficulty is finding the right fact in a long history, not the reasoning.

**Most failed updates fail because the fact was never stored.**
- HaluMem scores extraction, updating and answering separately. For most systems, more than half of the facts that should have been updated were simply missed, mainly because the original fact was never extracted ([p. 11, Table 3](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?dest=table.3&page=11)).
- So many "update failures" actually happen when facts are written.

**Merging old and new memories causes a different kind of loss.**
- In DynamicMem, every system handles a fresh preference change well.
- As more history piles up after the change, systems that merge memories lose track of it: A-Mem falls from 89% to 39%, SimpleMem from 89% to 47%.
- Plain RAG and HippoRAG2 recover to 59–63% ([p. 11, Fig. 8](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?dest=figure.8&page=11)).

## Two approaches: mark it replaced, or delete it

**Mark the old fact as replaced and keep it.**
- Used by Zep's validity intervals ([p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)), Mem0's graph variant, Memanto, Belief Memory and A-TMA.
- A-TMA is a layer added on top of an existing memory store. It labels each fact as current, historical or transitional, retrieves the version the question asks about, and shows the labels to the answering model.
- On Graphiti/Zep, accuracy on A-TMA's own conflict benchmark rises from 0.480 to 0.720 ([p. 10, Table 2](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.2&page=10)).
- On LoCoMo, temporal F1 rises from 0.0295 to 0.1705, but temporal accuracy *falls* from 0.3707 to 0.3178 ([p. 11, Table 3](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.3&page=11)). The authors themselves say the gains depend on the store it runs on.
- The benefit: the system can still answer "where did she live last year?" and can recover from a wrong update.

**Delete the old fact.**
- Mem0's DELETE operation and ForgetEval's purge work this way. A privacy deletion requires it, and it keeps outdated facts out of the prompt.
- ForgetEval tests 13 store configurations ([p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)):
  - Stores that delete by fixed rules, with no LLM call, pass 63–68% of the adversarial deletion cases.
  - One extra LLM call at the moment a fact changes lifts them to 92–93%.
  - Graph memories pass only 7–9.5%, because turning text into entities throws away the exact wording that a targeted deletion needs.
  - Mem0 with its LLM making the update decisions passes only 43.6%, because it links the new fact to the old one and keeps both.
- Treat ForgetEval with caution:
  - It has one author, who also built one of the systems tested.
  - Most adversarial cases were drafted by the same family of models used for the extra LLM call.
  - On cases written by outside contributors, the stores without the extra call drop to 29–34%, and the gain from the call shrinks to 12–18 points ([p. 21, Table 17](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.17&page=21)).

**No paper in the library compares the two approaches on the same task.** That is the clearest open question.

## Forgetting over time and in the weights

- **Gradual forgetting (decay) is barely developed.**
  - MemoryBank's forgetting curve is set by hand, and the paper never says when a low score actually leads to deletion.
  - A learned "forget gate" exists only in memory built into the model's architecture, as in Titans.
  - The surveys all list learned forgetting as an open problem.
- **Updates don't carry through to related facts.**
  - Fundamental Problems With Model Editing builds a small model where the correct result of an edit is known exactly.
  - The edited fact itself changes, but accuracy on downstream facts that should change with it falls from 0.97 to 0.01 ([p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)).
  - The same problem applies to text memory: "moved to Berlin" should also change "nearest airport." Only Belief Memory and DeMem make first attempts at this.
  - That test uses one tiny model and one editing method, so it shows the problem exists more than it measures how big it is.

## What looks reliable, and what doesn't

- **Reliable:** several independent groups find that stores which only append (and also systems that merge memories) return outdated facts, and that a memory has to know which version of a fact is current. Zep-style validity intervals do best on update questions in the one comparison run by an outside group.
- **Weak:**
  - Every benchmark is synthetic and built by the paper's own authors.
  - Most results are single runs.
  - A-TMA has a note in the library only from a skim.
  - Nothing tests these systems on real users.
- **From the review only:** MemSyco-Bench reports that adding Mem0 or LightMem raises how often the model relies on outdated memories from 16.3% to 41–49%. I didn't check that number in the paper.

For the full picture, start with [reviews/llm/memory.md](reviews/llm/memory.md) at the section "Updating and forgetting are where memory systems fail" (around line 417). One correction to it: it says that in DynamicMem "append-only retrieval tracks preference changes best." The paper actually says HippoRAG2 stands out, and plain RAG only recovers to a similar level (p. 11). I can fix that line and add this answer to the review's Q&A if you want.
