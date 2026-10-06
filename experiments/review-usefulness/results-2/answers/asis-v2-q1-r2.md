The research in the library agrees on one thing: storing a new fact is easy, but stopping the old one from being used is largely unsolved. Every system tested fails some version of the task, and no approach wins across benchmarks.

This comes from the `llm/memory` and `llm/personalization` papers. I checked the numbers below in the papers, except EvoMemBench's, which comes from its note.

## What goes wrong

Take "lives in London", then later "moved to Berlin". The failure can happen at three stages, which [A-TMA, p. 6–9](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=subsection.4.3&page=6) separates and calls "ghost memory":

- **Store:** both facts sit in memory with nothing marking which one is live.
- **Retrieval:** "where should I ship this?" and "where did she live before?" use nearly the same words, so relevance search returns both.
- **Answer:** the model sees both as plain text and blends them.

## Three ways to handle an update

| Approach | Examples | Strength | Weakness |
|---|---|---|---|
| Delete or overwrite | Mem0's DELETE, A-MEM's note rewriting | Keeps the prompt clean | Loses history, and a wrong LLM judgement destroys a fact for good |
| Supersede and keep | Zep's validity intervals, A-TMA's labels, Belief Memory's probabilities | Can answer "what was true last year" and recover from a bad update | The old fact is still retrievable and can still leak into answers |
| Append only | Plain RAG, HippoRAG | Nothing is lost or blurred | Nothing says which value is current |

- **Zep** gives each fact a validity period. A contradicting fact sets the old one's end date, and newer information always wins ([p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=subsubsection.2.2.3&page=3)).
- **A-TMA** marks records as active, superseded or transitional, links them, and passes those labels to the answer model.
- **LightMem** argues against deleting during the conversation: an LLM may read two related facts as a conflict and delete one, which cannot be undone ([p. 9](http://pdf.invalid/llm/memory/agent/LightMem.%20Lightweight%20and%20Efficient%20Memory-Augmented%20Generation.pdf?dest=subsection.5.6&page=9)). It defers updates to an offline pass.

No paper here compares delete against supersede on the same task.

## What the measurements show

- **Systems that track time do best on simple updates.** In an independent study of a dozen systems, Zep scores 44.4 on knowledge-update questions and Cognee 37.8. Long context scores 20.0, Letta 17.8 and Mem0 15.6 ([p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
- **Chained updates are close to unsolved.** If "moved to Berlin" should also change "nearest airport", every agent on MemoryAgentBench scores at most 28% ([p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)). EvoMemBench's memory methods score at most 7% on the same task.
- **Length makes it worse.** o4-mini scores 100 single-hop and 80 multi-hop at 6K tokens, but 61 and 14 at 32K ([p. 10, Table 5](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.5&page=10)). BEAM's contradiction-resolution scores are at most 0.053 for every method ([p. 8, Table 1](http://pdf.invalid/llm/memory/benchmarks/Beyond%20a%20Million%20Tokens.%20Benchmarking%20and%20Enhancing%20Long-Term%20Memory%20in%20LLMs.pdf?dest=table.1&page=8)).
- **Merging blurs old and new.** In DynamicMem, A-Mem's accuracy on a changed preference falls from 89% to 39% as history grows behind the change, while append-only RAG and HippoRAG2 end at 59% and 63% ([p. 11](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?page=11&search=On%20update%2C%20HippoRAG2%20stands%20out)).
- **Labelling helps, partly.** A-TMA on top of Graphiti/Zep raises accuracy on its own conflict benchmark from 0.480 to 0.720 ([p. 10, Table 2](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.2&page=10)). On LoCoMo, temporal F1 rises from 0.0295 to 0.1705 but temporal QA accuracy falls from 0.3707 to 0.3178 ([p. 11, Table 3](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.3&page=11)).
- **Getting the old fact out of retrieval is a separate skill.** ForgetEval checks that the old value is absent from the top-10 results. Plain deterministic stores pass 63–68% of adversarial cases, and one LLM call at the moment of change lifts them to 92–93%. Mem0 with its LLM router passes 43.6% and Graphiti 7.0% ([p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)).

Zep shows why rankings do not transfer. It is best on the simple update slice above, yet scores 7.0 and 3.0 on MemoryAgentBench's single- and multi-hop update tasks, and its engine nearly fails ForgetEval. The three tests ask for different things: answer with the new value, reason through changed facts, and keep the old value out of retrieval.

## A correct store is not enough

- **Models anchor on the old value even with the full history in context.** In HorizonBench, shortening the history to about 95K tokens raises the share of errors that pick the pre-change value to 47.7% ([p. 8, Table 2](http://pdf.invalid/llm/personalization/benchmarks/HorizonBench.%20Long-Horizon%20Personalization%20with%20Evolving%20Preferences.pdf?dest=table.2&page=8)). So this is a belief-update failure, not a retrieval one. No memory system is tested there.
- **Retrieved facts are "sticky".** In PersonaMem-v3, Mem0 answers from an expired preference 51.4% of the time, against 25.7% for a plain self-updating text memory. Agentic search sits at 37–40%: it finds the evidence but does not judge whether it still applies ([p. 17](http://pdf.invalid/llm/personalization/benchmarks/PersonaMem-v3.%20Toward%20Omni-Platform%20Personal%20Intelligence%20for%20Holistic%20User%20Understanding.pdf?page=17&search=tracking%20preference%20changes)).
- **Memory systems can increase use of outdated memories.** In MemSyco-Bench with DeepSeek-V4-Flash, the rate rises from 16.3 with the full dialogue to 41.4 with Mem0 and 48.6 with LightMem ([p. 7, Table 1](http://pdf.invalid/llm/memory/benchmarks/MemSyco-Bench.%20Benchmarking%20Sycophancy%20in%20Agent%20Memory.pdf?dest=table.1&page=7)). With Qwen3-8B the full dialogue is already at 56.2.
- **One repair is to audit the draft reply against the stored state.** "When Memory Updates but Behavior Does Not" does this and gains 5 points on the Stale benchmark, but its two human annotators barely agree with each other (κ = 0.126) ([p. 5](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?page=5)).

## Memory in the weights has the same problem

Model editing changes the target fact but not what follows from it. In a small model with exactly known correct answers, accuracy on downstream facts that should change falls from 0.97 to 0.01 after an edit ([p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)). That is one tiny model and one editing method.

## How far to trust this

- **Each paper uses its own, mostly synthetic, test.** The agreement is in direction, not in comparable numbers.
- **ForgetEval** has a single author who built one of the tested systems. On externally written cases the pass band drops to 28–51%.
- **Zep's and Mem0's own results** are vendor-run. The independent study has two authors from the MemOS vendor and very low absolute scores.
- **Forgetting by time decay is barely tested.** MemoryBank's forgetting curve is hand-set, and the paper never says how a low retention score becomes a deletion (p. 4, per its note).

I tried to append the cross-paper points to the Q&A of `reviews/llm/memory.md`, as the library conventions ask, but the file is read-only here, so nothing was changed.
