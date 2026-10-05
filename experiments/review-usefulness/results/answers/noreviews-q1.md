**Scope:** this is a synthesis of the roughly 20 relevant papers in the library (`llm/memory/` and `llm/personalization/`), with no web search. Seven of them have no notes yet and were read only in part, as flagged in the last section.

## The short version

Take a user who said "I live in Seattle" and months later mentions "setting up utilities in my new Austin apartment". Research up to mid-2026 says three things about this case:

1. **Storing the update is the easy part.** Most systems now have some write-time mechanism for it.
2. **Revision is much weaker than retention.** On multi-hop conflict tests every memory system scores in single digits.
3. **The failure has moved downstream.** A system can hold the right current fact, even retrieve it, and still answer or plan from the old one.

## How systems handle a superseded fact

| Strategy | Example | What happens to the old fact |
|---|---|---|
| Time decay | MemoryBank, MemoryLLM | Fades regardless of whether it is still true. MemoryBank never says how decay becomes deletion ([p. 4](http://pdf.invalid/llm/memory/agent/MemoryBank.%20Enhancing%20Large%20Language%20Models%20with%20Long-Term%20Memory.pdf?page=4)). |
| LLM-chosen delete or update at write time | Mem0, Memory-R1 (the same operations, learned with RL) | Removed or overwritten ([Mem0, p. 3–4](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=3)). |
| Invalidate, don't delete | Zep/Graphiti, Mem0's graph variant | Kept with an end date; newer always wins ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)). |
| Explicit state roles | A-TMA | Kept and labelled active, superseded or transition; the labels are passed through retrieval to the answer prompt ([p. 6](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=subsection.4.3&page=6)). |
| Append-only log, regenerate the state | User as Code | Never overwritten; a typed current state is rebuilt from all facts ([p. 10](http://pdf.invalid/llm/personalization/methods/User%20as%20Code.%20Executable%20Memory%20for%20Personalized%20Agents.pdf?dest=subsection.3.2&page=10)). |
| Ask before persisting | Memanto | The agent chooses supersede, retain or annotate ([p. 5](http://pdf.invalid/llm/memory/agent/Memanto.%20Typed%20Semantic%20Memory%20with%20Information-Theoretic%20Retrieval%20for%20Long-Horizon%20Agents.pdf?page=5)). |
| Keep competing beliefs with probabilities | Belief Memory | A contradicted belief drops to 0.25 and stays as a historical version ([p. 12](http://pdf.invalid/llm/memory/agent/Belief%20Memory.%20Agent%20Memory%20Under%20Partial%20Observability.pdf?dest=subsection.A.2&page=12)). |
| Defer to offline | LightMem | Online inserts only; updates run later, on the argument that online updates wrongly delete non-conflicting facts ([p. 5](http://pdf.invalid/llm/memory/agent/LightMem.%20Lightweight%20and%20Efficient%20Memory-Augmented%20Generation.pdf?page=5)). |

The trend is away from deletion and towards keeping history with a status, because "where did she live before?" is a legitimate question.

## What the evaluations find

- **Conflict resolution:** on MemoryAgentBench's FactConsolidation multi-hop, every agent is at or below 28% ([p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)). EvoMemBench repeats it with 15 methods: all memory methods at 7% or less, while a long-context model reaches 96 on single-hop against 54 for the best memory method ([p. 6](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?dest=table.3&page=6)).
- **Memory can be worse than none:** Mem0, Letta and SimpleMem fall below plain long context on knowledge updates ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
- **Where the LLM sits matters:** in ForgetEval, an LLM at write time makes Mem0 worse (43.6% against 68.3% without it), because it links and keeps instead of deleting. An LLM hook at mutation time reaches about 92% ([p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)).
- **The verdict depends on the metric:** Zep is best on knowledge updates when the test is "is the new fact retrieved", but Graphiti scores 7% on ForgetEval, where the old fact must be gone from the top 10.
- **Many updates never happen:** in HaluMem, update omission exceeds 50% for most systems, because a fact that was never extracted cannot be updated ([p. 11](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?page=11)).
- **Retention and update trade off:** DynamicMem finds that no architecture wins both ([p. 10](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?page=10)).

## The failure moves downstream

- **Retrieval and answer:** A-TMA calls it "ghost memory". Graphiti had the right evidence in 0.812 of cases on one LTP profile but only 0.425 conflict accuracy; adding state labels raised that to 0.725 ([p. 2](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?page=2)).
- **Implicit change:** in HorizonBench, a life event changes a preference without restating it. All 25 models do worse on evolved items and pick the old value on over a third of errors, even with the full history in context ([p. 8](http://pdf.invalid/llm/personalization/benchmarks/HorizonBench.%20Long-Horizon%20Personalization%20with%20Evolving%20Preferences.pdf?page=8)).
- **Behaviour:** on the Stale benchmark, a prototype resolves the current state 91% of the time but adapts its open-ended plan only 32% of the time. StateAuditor audits from stored state to draft, since a weekend-plans answer never says "Seattle"; it gains 5 points (.686 to .736) ([p. 1](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?page=1), [p. 5](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?dest=subsection.6.1&page=5)).
- **In products:** on PersonaMem-v3, Mem0 gives an outdated stance in 51.4% of preference-change cases, against 25.7% for a self-rewritten text memory ([p. 17](http://pdf.invalid/llm/personalization/benchmarks/PersonaMem-v3.%20Toward%20Omni-Platform%20Personal%20Intelligence%20for%20Holistic%20User%20Understanding.pdf?page=17)).

## Facts in the weights

The same problem is worse in parametric memory. An edit changes the target fact but does not propagate: downstream accuracy fell from 0.97 to 0.01 on facts that should have changed ([Fundamental Problems, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)). MEMIT has no deletion operation, and MemoryLLM forgets by random dropping, so a fact cannot be removed on purpose.

## Weak spots

- **Evidence quality:** ForgetEval is single-author and its own system is a primary subject. A-TMA's gains depend on the host system, its LoCoMo scores are tiny (F1 0.08 to 0.16 with a 3B answer model), and its ablation shows small, mixed component effects ([p. 20](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=subsection.A.10&page=20)). StateAuditor shows no gain on a harder authored set.
- **Synthetic data:** almost all benchmarks here use generated users.
- **My reading:** A-TMA, the stale-dependency paper, User as Code, Memanto, Belief Memory and DynamicMem have no notes yet; I read their abstracts, method and results sections, not the full text. LightMem's update argument is from the existing digest, not the paper.
- **Not in these folders:** the Stale benchmark itself, plus Memora, MemConflict and MemTrace, which these papers cite for conflict diagnosis. They are candidates for `INBOX.txt`.
