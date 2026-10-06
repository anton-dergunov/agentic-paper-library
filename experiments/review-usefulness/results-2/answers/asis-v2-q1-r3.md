The research in your library agrees on one thing: storing a fact is solved, but noticing that it has stopped being true is not. Every independent 2025–2026 benchmark that tests changed facts finds memory systems failing, and the proposed fixes are each tested only on their authors' own synthetic data.

## An example of the failure

A user says "I live in Seattle" in March and "setting up utilities in my new Austin apartment" in July. Asked where to ship a package, the system can go wrong at three stages:

1. **Write:** the Austin fact is stored but Seattle is never marked as replaced.
2. **Read:** both facts are retrieved because they look alike, and nothing says which is live.
3. **Use:** Austin is in the prompt, but the answer still plans around Seattle.

A-TMA calls the mixing of old, current and in-between versions "ghost memory" and is the one memory paper here built around all three stages ([A-TMA, p. 1](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?page=1)).

## How systems handle an update

| Approach | Papers | What happens to the old fact | Weak point |
|---|---|---|---|
| Delete | Mem0 (base) | An LLM compares each new fact with its 10 nearest neighbours and picks add, update, delete or nothing | A contradiction outside those 10 goes unnoticed; history is lost |
| Supersede and keep | Zep, Mem0's graph variant, Memanto, A-TMA | Marked as no longer valid and kept | The old fact can still be retrieved unless the reader filters on its status |
| Keep with a probability | Belief Memory | Its probability drops to 0.25 and the previous value is kept as a historical entry | Tested on LoCoMo and ALFWorld, not on an update benchmark |
| Defer to an offline pass | LightMem | Online writes only insert; updates run later in batch | The offline update can lower accuracy (67.78 to 65.39) |
| Decay | MemoryBank | Retention fades unless the fact is recalled | The paper never says how low retention becomes deletion |

- **Zep** is the reference design for superseding. Each fact carries when it was true in the world and when the system learned it, and a contradicted fact gets an end date ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)).
- **A-TMA** adds labels on top of an existing store: current, historical or transition. It expands retrieval along the "superseded by" links and shows the labels to the answering model.
- **Memanto** asks the agent to choose between supersede, retain or annotate when it detects a conflict.

## What the benchmarks find

- **Append-only stores return the old fact.** After facts change, Zep scores 44.4 and long context 20.0, while Mem0 (15.6) and Letta (17.8) fall below long context ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
- **Conflicting facts across several hops are close to unsolved.**
  - On MemoryAgentBench every agent scores at most 28% ([p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)).
  - On EvoMemBench every memory method scores 7% or less ([p. 6, Table 3](http://pdf.invalid/llm/memory/benchmarks/EvoMemBench.%20Benchmarking%20Agent%20Memory%20from%20a%20Self-Evolving%20Perspective.pdf?dest=table.3&page=6)).
  - On BEAM, contradiction resolution is at most 0.053 for every method at every length ([p. 8, Table 1](http://pdf.invalid/llm/memory/benchmarks/Beyond%20a%20Million%20Tokens.%20Benchmarking%20and%20Enhancing%20Long-Term%20Memory%20in%20LLMs.pdf?dest=table.1&page=8)).
- **Merging memories blurs old and new.** On DynamicMem, systems handle a fresh preference change well (70–89%), but as history grows A-Mem falls from 89% to 39%. Append-only HippoRAG2 (88% to 63%) and plain RAG (85% to 59%) hold up better ([DynamicMem, p. 10–11, Fig. 8](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?dest=figure.8&page=11)). The paper's conclusion is that no architecture wins on both retention and update.
- **Many updates never happen because the fact was never extracted.** In HaluMem, update omission exceeds 50% for most systems (p. 11).
- **Deletion depends on where the LLM sits.** In ForgetEval, deterministic stores pass 63–68% of adversarial deletion cases, and one LLM call at the moment of change lifts that to 92–93% ([p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)). Graph memories pass 7–9.5%, and Mem0 with LLM inference 43.6% because it links new to old instead of deleting.

## Retrieved but not applied

This part comes from `llm/personalization`, and the memory review does not cover it.

- **HorizonBench:** with the whole history in context and no memory system, all 25 models do worse on changed preferences than stable ones. They pick the old value on more than a third of errors, against 25% by chance ([p. 8](http://pdf.invalid/llm/personalization/benchmarks/HorizonBench.%20Long-Horizon%20Personalization%20with%20Evolving%20Preferences.pdf?page=8)).
- **When Memory Updates but Behavior Does Not:** it cites the Stale benchmark, where a write-side prototype resolves the current state 91% of the time but adapts open-ended behaviour only 32% of the time. The new evidence was visible in 67.8% of those failures ([p. 1](http://pdf.invalid/llm/personalization/methods/When%20Memory%20Updates%20but%20Behavior%20Does%20Not.%20Repairing%20Implicit%20Stale%20Dependencies%20in%20Personalized.pdf?page=1)). Its fix audits the drafted answer against changed state and gains 5.0 points (.736 against .686).
- **PersonaMem-v3:** on tracking preference changes, Mem0 answers with an outdated stance 51.4% of the time, against 25.7% for a self-rewritten text memory (p. 17).

Model editing shows the same gap in weights. An edit changes the target fact, but accuracy on downstream facts that should also change falls from 0.97 to 0.01 ([Fundamental Problems With Model Editing, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)).

## What is weakly supported

- **A-TMA's gains are on its own benchmark and a tiny answering model.** Conflict accuracy rises from 0.480 to 0.720 on the authors' LTP set. On LoCoMo, Zep's temporal F1 goes from 0.0295 to 0.1705 while its temporal accuracy falls from 0.3707 to 0.3178 ([p. 11, Table 3](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.3&page=11)). The answerer is qwen2.5:3b, which likely explains the very low baseline. The paper's own ablation on three profiles shows small, mixed effects per component (p. 20).
- **ForgetEval has one author**, who built one of the systems tested. On cases drawn from other benchmarks the LLM-hook gain shrinks to 12–18 points.
- **Zep and Mem0 results are vendor-run**, and neither ablates its update step.
- **"Are We Ready" reports very low absolute scores**, and its Mem0 numbers suggest a configuration problem.
- **Nobody compares supersede-and-keep with delete on the same task**, or a fix at one stage with a fix at another.
- **Learned forgetting is listed as open by every survey here.**

## How I checked

I opened the papers for the A-TMA, DynamicMem, BEAM, Belief Memory, Memanto and StateAuditor claims. The other numbers come from the full-read notes in `notes/`, not from reopening the papers. Memanto's conflict mechanism is described in its paper but I did not find an evaluation of it.

I tried to append the "retrieved but not applied" point to the Q&A of `reviews/llm/memory.md`, but the file is not writable in this session, so nothing was changed.
