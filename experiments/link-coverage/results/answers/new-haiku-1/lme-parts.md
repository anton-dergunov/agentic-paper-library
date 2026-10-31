**The dataset: 500 questions in 7 types, covering 5 abilities** (p. 4, §3.2; examples in Figure 1, p. 3)

| Type | Ability | What it tests |
|---|---|---|
| single-session-user | IE | Recall a fact the user stated in one session |
| single-session-assistant | IE | Recall something the assistant said in one session |
| single-session-preference | (personalisation) | Use the user's stated preferences to tailor an answer, without a fact to recall |
| multi-session | MR | Aggregate or compare facts across two or more sessions (counts, totals, comparisons) |
| knowledge-update | KU | Answer with the user's latest value after a change (e.g. a new trip or a new job) |
| temporal-reasoning | TR | Use explicit dates or timestamp metadata (e.g. "how many months since…") |
| abstention | ABS | 30 false-premise questions built from the other types; the right answer is "I don't know" |

Each question is answered from a chat history of about 50 sessions (LongMemEval_S, ~115K tokens) or 500 sessions (LongMemEval_M, ~1.5M tokens). Evidence sits among filler sessions (p. 2, §1).

**What to read, in order**

1. **Figure 1, p. 3**: one example per type. This takes two minutes and makes the rest concrete.
2. **§3.2, p. 4**: the ability and type definitions. This is the core of the paper.
3. **§3.3 and Table 6, pp. 6 and 21**: the GPT-4o judge and its agreement with experts (97% overall). Read this before trusting any score.
4. **§3.4 and Figure 3, p. 6**: the pilot showing commercial systems and long-context models drop sharply at the _S length.
5. **Table 7, p. 21**: per-type results for ChatGPT and Coze on only 97 questions, which show where memory systems fail (multi-session and temporal are weak).
6. **Table 2, p. 8, and §5 (pp. 8–10)**: the design study (value, key, query, reading). Read this if you care about building a memory system; the summary in the note covers the numbers.

**Skim or skip**

- **Table 1, p. 3**: the comparison with other benchmarks. Useful for positioning, not for the tasks.
- **Figure 9, p. 19**: dataset statistics. Most questions need evidence from several sessions, up to six, and evidence tends to sit early in each session. The per-type counts are in the 9a pie chart, which the text layer doesn't read cleanly, so I haven't quoted them. Check the PDF page if you need them.
- **Appendix A.1 (question generation, around p. 16)**: read it only if you want to judge how valid the questions are. Yield for the harder types was about 5%.
- **Figures 8, 10–12 and the appendix ablations**: only if you plan to reproduce the pipeline or the judge.

**Most useful overall**: §3.2 and Figure 1 for the task definitions, Table 6 for trusting the metric, and Table 7 for the gap between commercial systems and the benchmark's hardest types. Those are the parts that change how you would read any result on this benchmark.
