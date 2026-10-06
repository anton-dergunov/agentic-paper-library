**Short answer:** in the papers in this library, obsolete facts are the weakest part of LLM memory. Systems store new facts well, but most keep serving the old one, and no update policy both replaces what changed and keeps what is still true.

Take a user who says "I live in Seattle" and later "setting up utilities in my new Austin apartment". Four things can go wrong, and each has its own evidence.

## Where it fails

- **The old fact is still retrieved.** After facts change, Zep scores 44.4 on LongMemEval's knowledge-update questions and plain long context 20.0. Mem0 (15.6) and Letta (17.8) fall below long context ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)). All scores are low and single-run.
- **Old and new are both retrieved, unlabelled.** A-TMA calls this "ghost memory": the answer model cannot tell which value is current ([p. 1](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?page=1&search=ghost%20memory)).
- **Merging destroys the update.** In DynamicMem, A-Mem's accuracy on changed preferences falls from 89% to 39% as history grows, while append-only RAG goes from 85% to 59% ([p. 11, Fig. 8](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?dest=figure.8&page=11)). The paper finds no design that wins on both retention and update.
- **The update is stored, but behaviour does not change.** A prototype resolves the current state 91% of the time, yet adapts its open-ended reply only 32% of the time ([When Memory Updates, p. 1](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?page=1)). In PersonaMem-v3, Mem0 uses an outdated stance in 51.4% of answers about changed preferences ([p. 17](http://pdf.invalid/llm/personalization/benchmarks/PersonaMem-v3.%20Toward%20Omni-Platform%20Personal%20Intelligence%20for%20Holistic%20User%20Understanding.pdf?page=17)).

Multi-hop consequences are close to unsolved: every agent scores at most 28% on MemoryAgentBench's multi-hop fact consolidation, and every memory method at most 7% on EvoMemBench.

## What the systems do about it

| Policy | Examples | Trade-off |
|---|---|---|
| Supersede and keep | Zep's validity intervals ([p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)), A-TMA's current/superseded/transition labels, Memanto | Can answer "where did she live before?"; the stale value stays retrievable |
| Delete | Mem0's DELETE operation, ForgetEval's purge | Clean prompt and real privacy deletion; a wrong update is unrecoverable |
| Keep several candidates with confidences | Belief Memory ([p. 5](http://pdf.invalid/llm/memory/agent/Belief%20Memory.%20Agent%20Memory%20Under%20Partial%20Observability.pdf?page=5)) | Recovers from noisy evidence; a contradicted value is only down-weighted to 0.25 |

No paper here compares these policies on the same task.

- **Deletion:** in ForgetEval, deterministic stores pass 63–68% of adversarial deletion cases, and one LLM call at the moment of change lifts that to about 92–93%. Graph memories pass under 10%, because they abstract away the exact wording.
- **Labelling:** adding A-TMA's labels to Graphiti/Zep raises conflict accuracy from 0.480 to 0.720 on the authors' own benchmark.
- **Decay:** MemoryBank's forgetting curve is hand-set and never says when a memory is actually dropped.

## In the weights

Model editing has the same problem. In a small testbed with known correct answers, an edit changes the target fact, but accuracy on facts that should follow from it falls from 0.97 to 0.01 ([Fundamental Problems, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)). MEMIT has no delete operation. Larimar can exactly remove a written fact, but from an external latent memory, not the model's weights ([p. 3](http://pdf.invalid/llm/memory/parametric/Larimar.%20Large%20Language%20Models%20with%20Episodic%20Memory%20Control.pdf?page=3)).

## How far to trust this

- Many 2026 papers point the same way, but each uses its own synthetic test.
- ForgetEval has one author, who built one of the systems tested; on cases from other benchmarks the gain shrinks to 12–18 points.
- A-TMA answers with a 3B model, and its LoCoMo F1 scores are tiny (temporal 0.03 to 0.17).
- Zep's own results are vendor-run.
- The ForgetEval, MemoryAgentBench, EvoMemBench and Fundamental Problems numbers come from the library's notes; I did not reopen those papers. The others I checked in the paper text.
