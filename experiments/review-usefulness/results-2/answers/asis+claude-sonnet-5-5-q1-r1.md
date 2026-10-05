The library's review of `llm/memory` (70 papers, last updated 2026-10-01) has a section on this. Obsolete facts are one of the weakest points of current memory systems, and no approach has been shown to solve them.

**Why it is hard.** Storing a fact is easy. Knowing it has stopped being true is hard. A-TMA calls the main failure "ghost memory": the old, current and in-between versions of a fact are all retrieved and blended into one answer. Facts that depend on the changed one also go stale. If "moved to Berlin" is stored, "nearest airport" should change too.

**The two camps on what an update should do:**
- **Supersede and keep.** Zep marks the old fact with a validity interval [(Zep, p. 3)](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3). A-TMA, Memanto, Belief Memory and Mem0's graph variant do something similar. The old fact stays available for questions like "where did she live last year?", and a wrong update can be undone.
- **Remove.** Mem0's DELETE and ForgetEval's purge take the old fact out. This is what a privacy deletion needs, and it keeps stale facts out of the prompt.
- No paper in the library compares the two on the same task.

**Results:**
- **Append-only stores keep returning old facts.** After facts change, Zep scores 44.4 and Cognee 37.8, against 15.6 for Mem0, 17.8 for Letta and 20.0 for plain long context ([Are We Ready…, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)). I guessed that file name from the stem, so the link may not resolve.
- **Labelling helps, with a cost.** A-TMA's current/historical/transitional labels raise Graphiti/Zep's temporal F1 on LoCoMo from 0.03 to 0.17 and conflict accuracy from 0.48 to 0.72. Accuracy on temporal questions falls from 0.37 to 0.32.
- **Updating and keeping pull against each other.** In DynamicMem, plain append-only retrieval tracks preference changes best. Systems that merge memories lose what they knew: A-Mem falls from 89% to 39%.
- **Resolving conflicts across several hops is close to unsolved.** MemoryAgentBench agents score at most 28%. EvoMemBench's memory methods score at most 7%. BEAM's contradiction resolution is at most 0.053 for every method.
- **Deletion depends on where the LLM sits.** In ForgetEval, deterministic stores pass 63–68% of adversarial deletion cases. One extra LLM call when the fact changes lifts that to 92–93%. Graph memories do worst (7–9.5%), because abstracting text into entities loses the wording that targeted deletion needs. The study has a single author who also built one of the systems tested, and on cases from other benchmarks the gain shrinks to 12–18 points.
- **Stale memory can mislead the model.** MemSyco-Bench finds Mem0 and LightMem raise the use of outdated memories from 16.3% to 41–49%.

**Forgetting by decay is barely developed.**
- MemoryBank's forgetting curve is hand-set, and the paper never says how a low retention score becomes a deletion.
- Titans learns a forget gate, but only because its memory is differentiable. Removing the gate raises perplexity from 27.0 to 29.0.
- The surveys all list learned forgetting as open.

**In the weights.** Editing knowledge in the model has the same problem. Fundamental Problems With Model Editing shows edits change the target fact but not its consequences: accuracy on downstream facts that should change drops from 0.97 to 0.01. MEMIT's edits also spill onto neighbouring facts. Larimar is the only in-model memory here that can forget a single fact exactly, because it keeps facts in an external latent matrix.

**Caveats:**
- **Review only.** I answered from the review and did not open the individual papers or their notes, so the numbers and what they mean are the review's, not independently checked. Several papers are marked as skimmed (A-TMA, Larimar, DeMem).
- **Evidence strength.** The review notes that many 2026 papers point the same way, but each uses its own synthetic test, and published comparisons between memory systems do not transfer well.
- **Library only.** I did not search the web, so anything newer than the library's papers is not covered.

If you want, I can read the A-TMA, ForgetEval and DynamicMem papers in full to check the numbers. The review's Q&A section is empty, so I can also add a short entry there once something is settled.
