**The dataset has 500 questions in seven types, covering five memory abilities.** Each question is asked after a long chat history with timestamped sessions, and the evidence sits somewhere inside it.

| Type | What it tests | Ability (paper's label) |
|---|---|---|
| single-session-user | Recall a detail the user mentioned in one session | IE |
| single-session-assistant | Recall something the assistant said | IE |
| single-session-preference | Use the user's stated preferences to personalise an answer; the answer is a rubric, not a fact | Not mapped to an ability in the text |
| multi-session | Aggregate or compare facts across two or more sessions | MR |
| knowledge-update | Notice that a user fact changed and answer with the latest value | KU |
| temporal-reasoning | Use timestamps and time phrases, such as "how many months since…" | TR |
| abstention | False-premise questions (30 of them) where the right answer is "I don't know" | ABS |

Two numbers matter for scale. The S setting is about 115K tokens (around 50 sessions), and the M setting is about 1.5M tokens (500 sessions). Most questions need evidence from several sessions, up to six, and evidence statements usually sit near the start of a session (p. 19, Fig. 9).

**What to read, in order** (PDF pages, from the `[page N]` markers):

1. **p. 3, Fig. 1 and Table 1.** One example per type, and how the benchmark compares with LoCoMo, MemoryBank and PerLTQA. This is the fastest way to see the tasks.
2. **p. 4, §3.2.** The formal definition of each ability and type. Read this once and you have the taxonomy.
3. **p. 6, Fig. 3.** The headline pilot. Commercial assistants score 0.577 (ChatGPT) against 0.918 for full-history GPT-4o. Long-context models drop 30–60% from oracle sessions to S.
4. **p. 8, Table 2 and Fig. 5.** The indexing → retrieval → reading view with four control points (value, key, query, reading). Then **pp. 9–10, Tables 3–4 and Fig. 6**: rounds beat whole sessions as values, extracted facts help the key, time-aware query expansion needs a strong LLM, and chain-of-note adds up to about 10 points.
5. **p. 21, Table 6 and the judge prompt.** Why the GPT-4o judge can be trusted: about 98% agreement with experts on 30 samples per type. Weakest on preference and abstention (0.90).

**Skip for now:** the ontology and generation pipeline (pp. 4–5, Fig. 2, Table 5), the appendix prompts (pp. 22–27) unless you are rebuilding the data, and Tables 8–11 unless you are choosing a reader model.

**Most useful overall for you:** p. 3 for the tasks, p. 8–10 for what actually moves memory-system scores, and p. 21 to judge whether the metric is trustworthy. The other pages are background.

The existing note already covers most of this in its digest. If you want, I can append a Q&A entry that maps the seven types to the five abilities, including the unmapped preference type.
