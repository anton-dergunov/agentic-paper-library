I'll check for an existing note first, then find the section headings in the paper's text.

The grep matched only figures and tables, so I'll search for section headings and read the abstract and introduction.

The introduction gives the five abilities and Figure 1 lists seven question types. Next I'll read Section 3 (dataset) and the basic statistics appendix.

The text layer gives the seven question types, but the Figure 9 pie labels aren't tied to slices. I'll check that page in the PDF and read the experiment setup.

The dataset has **500 questions** that test **five memory abilities**, split into **seven question types**. Each question is asked after a long chat history with the assistant, and the answer is spread across one or more earlier sessions.

| Type | What it tests | Share of questions (Fig. 9) |
|---|---|---|
| single-session-user | recall something the user said in one session | 14% (~70) |
| single-session-assistant | recall something the assistant said in one session | 11% (~56) |
| single-session-preference | use the user's stated preferences to personalise an answer (open-ended) | 6% (~30) |
| multi-session | aggregate or compare facts across 2+ sessions | 27% (~133) |
| knowledge-update | answer with the user's latest value after a change | 16% (~78) |
| temporal-reasoning | use timestamps and time references | 27% (~133) |

The five abilities are information extraction, multi-session reasoning, knowledge update, temporal reasoning and abstention. Abstention is not a separate type: 30 questions are false-premise versions of questions from the other types, so they fall within those shares. The percentages come from the pie chart on p. 19; the counts are my conversion of them to 500.

**Which parts to read, in order**

1. **Table 1 and Figure 1, p. 3** ([link](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3)): one example per type, and how this benchmark compares with LoCoMo, MemoryBank and others.
2. **§3.2, p. 4** ([link](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=4)): the precise definition of each ability and type. This is the section to quote from.
3. **§3.3, p. 5**: the GPT-4o judge and its 97% agreement with humans. Read it if you plan to reuse the evaluation.
4. **Figure 9 and A.3, p. 19**: the type distribution, and that most questions need up to six sessions.

Skim or skip §3.2's construction pipeline (p. 5, Fig. 2) unless you plan to build similar data. §3.4 (p. 6) has the headline gap: commercial systems and long-context LLMs drop 30–60%.

**Most useful overall**

- **§4, p. 7: the unified view.** It splits a memory system into indexing, retrieval and reading, with four control points: value, key, query and reading strategy. This is the framework to compare other memory systems against, and Table 2 maps nine of them onto it.
- **§5.2, p. 8 and Fig. 5:** storing rounds (one user message plus the reply) works better than whole sessions. Summaries and extracted facts lose information, but facts help multi-session questions.
- **Table 3, p. 9:** adding extracted user facts to the index key gives about 9.4% better recall and 5.4% better accuracy.
- **Table 4 and Fig. 6, p. 10:** time-aware query expansion helps temporal questions, but only with a strong model doing the time extraction. Chain-of-Note with JSON input gains up to 10 points, even with perfect retrieval.

Skip for now: the question-construction detail in A.1 (pp. 17–19), the evaluation prompts in A.4 (pp. 20–21), and the ablations in Appendix E (pp. 25–27) unless you need a specific number.

The results use GPT-4o, Llama 3.1 and Phi-3, so the absolute numbers are dated. The design findings are the part most likely to transfer.
