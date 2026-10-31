**What the dataset tasks are:** 500 hand-written questions, each asked after a long user–assistant chat history. The assistant must recall or reason over facts the user revealed in one or more earlier sessions. There are five abilities, covered by seven question types:

- **Information extraction (IE):** single-session-user, single-session-assistant, and single-session-preference (use a remembered user preference to personalise an answer).
- **Multi-session reasoning (MR):** aggregate facts across two or more sessions (up to six).
- **Knowledge update (KU):** the user's situation changed, so the answer must use the newer fact.
- **Temporal reasoning (TR):** use dates in the timestamps and times stated in the text.
- **Abstention (ABS):** 30 "false premise" questions where the right answer is "I don't know".

The history is either LongMemEval-S (about 115k tokens, roughly 50 sessions) or LongMemEval-M (500 sessions, about 1.5M tokens).

**Which parts to read, in order:**

1. **p. 3, Table 1 and Figure 1.** Fastest overview: how the benchmark compares with MemoryBank, PerLTQA, LoCoMo and DialSim, and one concrete example per question type.
2. **p. 4, §3.2 (the definitions).** The five abilities and seven types, each defined in a sentence. This is the reference for the task list.
3. **p. 6, §3.4 and Figure 3.** The headline result: long-context LLMs drop 30–60% against oracle evidence, and ChatGPT and Coze drop 37% and 64% against offline reading with GPT-4o. This tells you whether the benchmark is hard in practice.
4. **p. 5, Figure 2 and "History Compilation".** How questions and evidence sessions are built, and how the haystack is padded. Read it only if you plan to build on the data.
5. **p. 19, Figure 9 (Appendix A.3).** Question-type distribution, number of evidence sessions, and where the evidence sits in each session. The percentages for the question types are in the figure, not the text layer, so read the page itself for the per-type counts.

**Most useful overall:** Figure 1 (p. 3) plus the §3.2 definitions (p. 4) cover what the tasks are. Figure 3 (p. 6) is the result that justifies the benchmark. Skip §4 onward unless you care about the memory designs; they are the paper's second contribution, not part of the task definition. The appendix judge validation (Table 6, Appendix A.4) is worth a look only if you plan to use GPT-4o as the grader.

Caveats: I read pp. 1–6 and the Appendix A.3 caption from the text layer. I did not check the per-type counts or the judge's per-type numbers. This paper has no note or review yet in `notes/` or `reviews/`, so nothing else in the library is cross-referenced. I can write its `notes/` entry on request.
