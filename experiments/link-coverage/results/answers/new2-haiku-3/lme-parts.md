**The dataset in one paragraph:** 500 human-curated questions, each asked after a long chat history. The answer is buried in one or more earlier sessions. Seven question types cover five abilities (p. 4):

| Type | Ability | What it tests |
|---|---|---|
| single-session-user | IE | Recall of something the user said in one session |
| single-session-assistant | IE | Recall of something the assistant said |
| single-session-preference | IE | Using the user's stated preferences to personalise an answer (open-ended rubric) |
| multi-session | MR | Aggregating or comparing facts across 2+ sessions (counts, sums, comparisons) |
| knowledge-update | KU | The user's fact changed over time; the answer must be the latest value |
| temporal-reasoning | TR | Explicit dates or timestamp metadata, e.g. "how many days ago…" |
| abstention (30 questions) | ABS | False-premise questions; the right answer is "I don't know" |

Each question is a 4-tuple (history S, question q, question date, answer a) (p. 4). Histories come in two sizes: _S at about 115K tokens (around 50 sessions) and _M at 500 sessions (about 1.5M tokens) (p. 2).

**Read these, in order:**

1. **Figure 1, p. 3–4.** One concrete example per type. This is the fastest way to see what the tasks look like.
2. **§3.2, p. 4–5.** The five abilities and seven types, and how the data is built (attribute ontology, then background paragraphs, then evidence statements woven into task-oriented chats). Read this to know what the questions are.
3. **§3.3–3.4, p. 5–6, and Figure 3.** The GPT-4o judge and the pilot numbers (ChatGPT 0.577 vs. 0.918 for full-history GPT-4o; long-context drop from 0.870 to 0.606).
4. **Table 6 and Table 7, p. 21.** Judge agreement (>97%) and the human evaluation. Read these before trusting the judge for your own work.
5. **Figure 9, p. 19 (A.3).** Question-type shares, number of evidence sessions (up to six), and where evidence sits within sessions. The pie labels are not in the text layer, so check the figure in the PDF before quoting shares.

**Most useful overall:** §5 (p. 8–10), which has the design findings. Table 3 (key design, p. 9) and Figure 6 (reading strategy, p. 10) are the most reusable. §4 and Table 2 (p. 7–8) give the indexing/retrieval/reading framework that makes the comparisons possible.

**Skip on a first pass:** the related-work block (p. 2–3, except the LoCoMo and session-concatenation criticisms), the prompt figures (Figs 7, 8, 10–13), and the ablations in E.1–E.3 unless you're tuning a retriever.

The existing note at `notes/LongMemEval. Benchmarking Chat Assistants on Long-Term Interactive Memory.md` already covers the digest and related papers, so this reading guide is consistent with it.
