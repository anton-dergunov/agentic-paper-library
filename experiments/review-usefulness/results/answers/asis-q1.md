Research agrees that obsolete facts are where LLM memory fails most, and no approach handles them reliably yet. This comes from the library's two reviews (`reviews/llm/memory.md`, `reviews/llm/personalization.md`); I did not reopen the papers, and several of them (A-TMA, Belief Memory, BEAM, DynamicMem, Larimar) were only skimmed for those reviews.

Take one example: a user said "I live in Munich" in March and "I've moved to Berlin" in May. A memory system can go wrong in three ways.

**1. The old fact is still retrieved and mixed into the answer**

- **Ghost memory.** A-TMA names the failure: old, current and in-between versions of a fact come back together. Labelling each fact as current, historical or transitional lifts accuracy on its own conflict benchmark from 0.480 to 0.720 ([p. 10, Table 2](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.2&page=10)). On LoCoMo the gain is mixed: temporal F1 rises but accuracy on temporal questions falls ([p. 11, Table 3](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.3&page=11)).
- **Append-only stores do worst.** In an independent test after facts change, Zep scores 44.4 and Cognee 37.8, against 20.0 for long context, 17.8 for Letta and 15.6 for Mem0 ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
- **Mem0's consistency check is local.** It compares a new fact only with its ten nearest stored facts, so a contradiction further away goes unnoticed ([p. 3–4](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=3)). In PersonaMem-v3 it takes an outdated stance in 51.4% of answers about changed preferences, against 25.7% for a plain textual memory ([p. 17](http://pdf.invalid/llm/personalization/benchmarks/PersonaMem-v3.%20Toward%20Omni-Platform%20Personal%20Intelligence%20for%20Holistic%20User%20Understanding.pdf?page=17)).
- **Multi-hop conflicts are close to unsolved.** Every agent scores at most 28% on MemoryAgentBench ([p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)). Memory methods reach at most 7% on EvoMemBench ([p. 6, Table 3](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?dest=table.3&page=6)), and at most 0.053 on BEAM's contradiction resolution ([p. 8, Table 1](http://pdf.invalid/llm/memory/benchmarks/Beyond%20a%20Million%20Tokens.%20Benchmarking%20and%20Enhancing%20Long-Term%20Memory%20in%20LLMs.pdf?dest=table.1&page=8)).

**2. The update is never stored**

- HaluMem scores extraction, updating and answering separately. More than half of failed updates fail because the original fact was never extracted ([p. 11, Table 3](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?dest=table.3&page=11)).
- Merging memories to stay current destroys what was still true. In DynamicMem, A-Mem falls from 89% to 39%, and append-only retrieval tracks preference changes best ([p. 11, Fig. 8](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?dest=figure.8&page=11)).

**3. The update is stored, but behaviour does not change**

- **Anchoring.** In HorizonBench, all 25 models keep answering from the old preference. Shortening the history to about 95K tokens makes it worse (47.7% outdated answers), so the failure is in revising a belief, not in finding the evidence ([p. 8, Table 2](http://pdf.invalid/llm/personalization/benchmarks/HorizonBench.%20Long-Horizon%20Personalization%20with%20Evolving%20Preferences.pdf?dest=table.2&page=8)).
- **Stale dependencies.** A system can hold "Berlin" and still plan around Munich's airport, because the stale assumption is never written down. An audit-and-regenerate step repairs only part of this, adding 5 points ([When Memory Updates but Behavior Does Not, p. 5, Table 1](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?dest=table.1&page=5)).
- **Same problem in the weights.** After a model edit, accuracy on downstream facts that should change falls from 0.97 to 0.01 ([Fundamental Problems With Model Editing, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)). MEMIT's edits also damage neighbouring facts ([p. 8, Table 2](http://pdf.invalid/llm/memory/parametric/Mass-Editing%20Memory%20in%20a%20Transformer.pdf?dest=table.2&page=8)).

**What the proposed fixes are**

| Approach | Papers | What it does with the old fact | Known weakness |
|---|---|---|---|
| Supersede and keep | Zep ([p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)), A-TMA, Memanto | Gives it an end date or a "historical" label | Large stores; graphs pass only 7–9.5% of targeted deletions |
| Remove | Mem0's DELETE, ForgetEval's purge | Takes it out of the store | No history, and no recovery from a wrong update |
| Hedge | Belief Memory | Keeps several candidates with probabilities | Tested on LoCoMo and ALFWorld only |
| Decay | MemoryBank, Titans' forget gate | Lets it fade | The curve is hand-set; learned only where memory is differentiable |
| Exact forgetting in the model | Larimar ([p. 7, Table 4](http://pdf.invalid/llm/memory/parametric/Larimar.%20Large%20Language%20Models%20with%20Episodic%20Memory%20Control.pdf?dest=table.4&page=7)) | Erases one fact from a latent matrix | The only in-model memory here that can do it |

On deletion, ForgetEval finds that one extra LLM call at the moment of change lifts deterministic stores from 63–68% to 92–93% of adversarial cases ([p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)). Treat that with caution: the single author built one of the tested systems, and the gain shrinks to 12–18 points on cases from other benchmarks.

**What is weak or open**

- No paper in the library compares supersede-and-keep with deletion on the same task.
- Every result rests on its own synthetic benchmark, so the numbers above do not compare across papers.
- Learned forgetting — deciding what to drop and when — is listed as open by every survey.
- Propagating an update to what follows from it is barely started; Belief Memory and DeMem are first attempts.

The practical reading is that facts which change often belong in text memory, where they can be inspected and replaced, and weights suit stable knowledge. Within text memory, keeping the old fact with validity labels has the best independent evidence so far, from the Zep result above.
