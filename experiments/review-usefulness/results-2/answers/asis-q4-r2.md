I've read the library's memory review and checked the numbers below against the paper notes. The review sorts the 70 papers in `llm/memory` into eight families.

To see the differences, take one message, "I moved to Berlin in May" (my example, not from a paper), and follow what each family does with it:

| Family | What it does with the message | Buys | Costs |
|---|---|---|---|
| **Extract-and-consolidate** (Mem0, LightMem, A-MEM) | An LLM extracts the fact, compares it with similar stored facts, then adds, updates or deletes. | Small store, fast reads, entries a person can read and delete | LLM calls per message; facts lost at extraction |
| **Graph** (Zep, HippoRAG) | Stores an edge `user –lives in→ Berlin` with validity dates; the old "lives in Paris" edge gets an end date rather than being deleted. | History over time, multi-hop paths | Large store, ingestion lag, poor targeted deletion |
| **Operating system** (MemGPT, MemoryOS, MemOS, MIRIX) | Treats the context as RAM and a store as disk; the model, a usage score, a scheduler or agents decide what is paged out or promoted. | A policy for when memory is full | An extra decision-maker that no paper evaluates alone |
| **Stream with reflection** (Generative Agents, MemoryBank) | Appends the raw message with a timestamp; ranks by recency, importance and relevance; periodically writes summaries back. | Simplicity | Unbounded growth, contradictions unhandled |
| **Learned or derived write policy** (Memory-R1, Mem-α, SAGE) | Same operations as Mem0, but the write decision is trained by RL or replaced by a novelty rule. | Decisions tuned to answers, or cheaper writes | Needs a reward; evidence is thin |
| **Experience** (ExpeL, Agent Workflow Memory, ReasoningBank) | Ignores the fact; stores lessons and workflows from finished tasks. | Agents improve across tasks without training | Wrong lessons persist; nothing is pruned |
| **Latent** (MemoryLLM, Cartridges) | Keeps hidden states or a trained cache that the model attends to. | No prompt tokens on a read | Needs model internals; unreadable |
| **Weights** (MEMIT, Titans, Memory Layers) | Edits or trains the fact into parameters. | No context cost | No audit or deletion; edits don't propagate |

The first six store text and the last two store inside the model. That split matters most: only text can be shown to a user, deleted on request, and used with a hosted API ([Memory in the Age of AI Agents, p. 29–31](http://pdf.invalid/llm/memory/agent/Memory%20in%20the%20Age%20of%20AI%20Agents.pdf?page=29)).

Where the differences show up in the evidence:

- **Cost moves between write time and read time.** Mem0 keeps about 7K tokens per LoCoMo conversation and Zep more than 600K, and Zep's memories became usable only hours after ingestion ([Mem0, p. 14](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?page=14)). This is Mem0's own measurement of a competitor.
- **Memory buys latency, not accuracy, on short histories.** In Mem0's own table, full context scores 72.90 against 66.88 for Mem0, but with a p95 latency of 17.12 s against 1.44 s ([Mem0, p. 11, Table 2](http://pdf.invalid/llm/memory/agent/Mem0.%20Building%20Production-Ready%20AI%20Agents%20with%20Scalable%20Long-Term%20Memory.pdf?dest=table.2&page=11)).
- **Memory wins on accuracy once the history is long.** At about 115K tokens, Zep scores 71.2% against 60.2% for full context with GPT-4o ([Zep, p. 7, Table 2](http://pdf.invalid/llm/memory/agent/Zep.%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf?dest=table.2&page=7)). This is a vendor-run result.
- **Graphs are best at updates and worst at deletion.** After facts change, Zep scores 44.4 against 15.6 for Mem0 and 20.0 for long context ([Are We Ready, p. 9, Table 2](http://pdf.invalid/llm/memory/agent/Are%20We%20Ready%20For%20An%20Agent-Native%20Memory%20System.pdf?dest=table.2&page=9)). In ForgetEval, Graphiti (Zep's engine) passes only 7% of deletion cases and HippoRAG 9.5% ([ForgetEval, p. 8–9](http://pdf.invalid/llm/memory/agent/Control-Plane%20Placement%20Shapes%20Forgetting.%20An%20Architectural%20Study%20of%20Agent%20Memory%20Across%20Thirteen.pdf?page=8)). ForgetEval is a single-author study by the builder of one tested system.
- **Extraction is the weak step in pipelines.** Every system except MemOS recalls under 60% of the facts it should have stored ([HaluMem, p. 11, Table 3](http://pdf.invalid/llm/memory/benchmarks/HaluMem.%20Evaluating%20Hallucinations%20in%20Memory%20Systems%20of%20Agents.pdf?dest=table.3&page=11)). The corresponding author works for the company behind MemOS.
- **Weight edits don't propagate.** After an edit, accuracy on downstream facts that should change falls from 0.97 to 0.01 ([Fundamental Problems With Model Editing, p. 14, Table 4](http://pdf.invalid/llm/memory/parametric/Fundamental%20Problems%20With%20Model%20Editing.%20How%20Should%20Rational%20Belief%20Revision%20Work%20in%20LLMs.pdf?dest=table.4&page=14)).

Rankings between named systems should not be trusted. The same Zep is 6 points below Mem0 in MemOS's LoCoMo table and 17 points above it in MIRIX's; that comparison rests on the review only, since I did not open those two tables.

The full treatment is in `reviews/llm/memory.md`, under "Kinds of memory systems" and "Findings".
