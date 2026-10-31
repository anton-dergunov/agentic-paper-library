**To see the tasks quickly, read three things, about 3 pages in total:**

1. [Figure 1, p. 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3&rect=108,230,505,514) gives one worked example for each of the seven question types. It is the fastest way to get a feel for the tasks.
2. The list of five abilities and seven question types is on p. 4, in §3.2. The sentence that maps types to abilities starts at ["To thoroughly assess these…"](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=4&rect=399,548,505,558).
3. [Table 1, p. 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=3&rect=108,77,505,226) compares the benchmark with LoCoMo, PerLTQA and others. It shows what is new.

**The tasks.** Each question is asked after a long chat history made of timestamped user–assistant sessions.

| Type | What it asks | Example from Fig. 1 |
|---|---|---|
| single-session-user | Recall something the user said | "How long is my commute?" → 45 min |
| single-session-assistant | Recall something the assistant said | "Which restaurant in Rome did you recommend?" → Roscioli |
| single-session-preference | Use a stated preference to personalise an answer | Suggest accessories for a Sony camera user |
| multi-session | Aggregate across sessions | "How many instruments do I currently own?" |
| knowledge-update | Return the latest value after a change | "Where was my most recent family trip?" → Paris, not Hawaii |
| temporal-reasoning | Reason over timestamps and time mentions | "How many months since my last museum visit?" |
| abstention | Say "I don't know" when the question has a false premise | "How many fish in my 30-gallon tank?" The user never mentioned one. |

There are 500 questions in total, and the abstention ones are only 30 of them. They are rewrites of questions from the other types.

**Most useful parts overall, in order:**

1. **§5, pp. 8–10: what makes a memory system work.** This is the part that carries over to other work.
   - [Table 2, p. 8](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=8&rect=108,82,505,337) maps existing systems onto four design choices: value, key, query and reading strategy. It is a good lens for comparing memory systems.
   - [Table 3, p. 9](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=9&rect=107,82,505,316) shows that expanding keys with extracted user facts raises recall@k by 9.4% and QA accuracy by 5.4%.
   - [Fig. 6, p. 10](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=10&rect=108,219,505,321) shows that chain-of-note with JSON input adds up to 10 points even when retrieval is perfect.
2. **§3.4 and Fig. 3, p. 6: the pilot study.** [Fig. 3](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=6&rect=108,73,504,271) shows the headline difficulty.
   - ChatGPT scores 0.577 and Coze 0.330, against 0.918 for GPT-4o reading the whole history offline.
   - Long-context models lose 30–60% going from oracle sessions to the 115K-token version (_S).
3. **§3.3, pp. 4–5: how histories are built.** Read this if you plan to use or extend the dataset. Evidence sessions are hidden among filler sessions. The length is configurable, with _S at about 115K tokens and _M at about 1.5M.

**Skip on a first pass:**
- §2 related work (pp. 2–4).
- The appendices (pp. 11 onwards), apart from the judge-agreement table (Table 6, p. 21) if you doubt the metric. The judge agrees with experts more than 97% of the time.

**Caveats:**
- The numbers above come from the library note (`notes/LongMemEval…`), and I confirmed the p. 2–4 content against the text.
- I did not re-read the §5 and pilot-study pages myself. Check the pages before quoting those figures.
- The note says Memanto estimates about 5% label inconsistencies in LongMemEval and warns of saturation. Weigh that when treating scores as precise.
