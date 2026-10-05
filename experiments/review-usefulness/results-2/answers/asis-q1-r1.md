The library's 70 memory papers agree on one thing: storing a fact is easy, and noticing that it has stopped being true is where every kind of memory system fails. Nothing tested so far handles it reliably. This answer follows the area review (`reviews/llm/memory.md`, "Updating and forgetting"), with the numbers checked against the notes or the papers; where I could not check, I say so.

## The problem, by example

A user says "I live in Paris" in March and "I've moved to Berlin" in June. A good memory then has to do three things:

1. Answer "where do I live?" with Berlin.
2. Still answer "where did I live in spring?" with Paris.
3. Update what follows from the move, such as the nearest airport.

Most systems do the first on short histories, few do the second, and almost none does the third.

## What systems do with the old fact

| Approach | Examples | What goes wrong |
|---|---|---|
| Keep everything, unlabelled | long context, plain RAG, Generative Agents | Old and new are retrieved together and nothing says which is live |
| Overwrite or merge | Mem0's UPDATE/DELETE, A-MEM's note rewriting | History is lost, and merging blurs old and new as the store grows |
| Supersede and keep | Zep, Mem0's graph variant, Memanto, Belief Memory, A-TMA | Needs an LLM to spot the contradiction; the old fact can still leak into answers |
| Hard delete | ForgetEval's purge | Needed for privacy, but graph stores can barely do it |
| Decay over time | MemoryBank, Belief Memory, Titans | Hand-set curves; learned only inside the model |

- **Supersede and keep is the current mainstream.** Zep gives each fact two time ranges (true in the world, known to the system), and a contradicted fact gets an end date instead of being deleted ([Zep, p. 3](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?page=3)).
- **Memanto and Belief Memory are variations.** Memanto marks an entry as superseded but keeps it, and can query current-only. Belief Memory stores each candidate fact with a probability, lowers it for a competing value, archives the old version and ranks stale entries lower.

## What the measurements show

- **"Ghost memory" (A-TMA, July 2026).** Old, current and transitional versions of a fact are retrieved together and mixed in the answer. Labelling each fact's state on top of Zep raises conflict accuracy from 0.480 to 0.720 on the paper's own benchmark ([A-TMA, p. 10, Table 2](http://pdf.invalid/llm/memory/agent/A-TMA.%20Decoupling%20State-Aware%20Memory%20Failures%20in%20Long-Term%20Agent%20Memory.pdf?dest=table.2&page=10)). On LoCoMo, temporal F1 rises from 0.0295 to 0.1705, which is still very low.
- **Validity-tracking stores do best on fact revision.** On LongMemEval's knowledge-update questions, Zep scores 44.4 and Cognee 37.8, against 20.0 for long context and 15.6 for Mem0 ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)).
- **Merging is worse than appending.** As history piles up behind a preference change, A-Mem falls from 89% to 39%, while plain RAG goes from 85% to 59% ([DynamicMem, p. 11](http://pdf.invalid/llm/memory/benchmarks/DynamicMem.%20A%20Long-Horizon%20Memory%20Benchmark%20in%20Real-World%20Settings.pdf?page=11&search=A-Mem)). The authors attribute this to merging blurring the boundary between old and new.
- **Changed facts that need a second reasoning step are close to unsolved.** On MemoryAgentBench's FactConsolidation, every agent scores at most 28% on multi-hop questions ([p. 8, Table 3](http://pdf.invalid/llm/memory/benchmarks/Evaluating%20Memory%20in%20LLM%20Agents%20via%20Incremental%20Multi-Turn%20Interactions.pdf?dest=table.3&page=8)).
  - It is a length problem, not only a memory problem: o4-mini scores 100 single-hop and 80 multi-hop at 6K tokens, but 61 and 14 at 32K (p. 10, Table 5).
  - EvoMemBench repeats the test with 15 memory methods, and none exceeds 7% (p. 6).
  - BEAM's best contradiction-resolution score is 0.053 (p. 8, Table 1).
- **Deletion fails for a different reason.** In ForgetEval, plain deterministic stores pass 63–68% of adversarial deletion cases, and one LLM call at the moment of the change lifts that to about 92–93% ([p. 6, Table 2](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?dest=table.2&page=6)).
  - Graph stores pass 7–9.5%, because turning text into entities discards the exact wording a targeted deletion needs.
  - Mem0 with LLM inference drops to 43.6%, because it links the new fact to the old one and keeps both.
- **Updates are often lost before they start.** In HaluMem, update omission exceeds 50% for most systems, because a fact that was never extracted cannot be updated (p. 11).

Putting the Zep and DynamicMem results together, my reading is: merging is worst, keeping both versions unlabelled is in the middle, and keeping both with a validity mark is best. No paper tests all three on one benchmark, so this is an inference.

## Memory in the weights

- **Edits don't propagate.** In a small model where the correct post-edit answers are known exactly, the edited fact itself succeeds, but accuracy on downstream facts that should change falls from 0.97 to 0.01 ([Fundamental Problems With Model Editing, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)). This is one tiny model and one editing method.
- **Single facts mostly cannot be removed.** The review names Larimar as the only in-model memory here that can delete one fact exactly. Its note is a skim and I did not check the paper.
- **The surveys' division of labour:** text memory for facts that change often and must be auditable, weights for stable general knowledge.

## What is weak or open

- **Each result uses its own synthetic benchmark.** The papers point the same way, but the numbers are not comparable across papers.
- **Two sources need caution.** ForgetEval has a single author who built one of the tested systems, and its gains shrink to 12–18 points on cases drawn from other benchmarks. A-TMA is only skimmed in the library, and its fix lowers some other scores.
- **Open questions:**
  - No paper compares supersede with delete on the same task.
  - No signal says when a memory should have been dropped; forgetting curves are hand-set.
  - Nothing propagates an update to its consequences in a text store. Belief Memory is a first attempt.

To read further, start with A-TMA for the failure, Zep for the standard mechanism, and MemoryAgentBench for the hardest test.

I tried to append the append-versus-merge point to the review's Q&A, but the file is not writable in this session, so nothing was changed and there is nothing to commit.
