Locate failed on the path I gave it, so I'm retrying with just the file name.

**S and M are the same 500 questions with the same evidence sessions. They differ only in how much unrelated chat history surrounds the evidence.**

The paper builds each question's history like a needle-in-a-haystack test. It samples unrelated user–AI sessions, inserts the evidence sessions among them, and assigns timestamps. The filler comes from simulated self-chats and from ShareGPT and UltraChat. The history length can be set freely, and the paper fixes two standard sizes ([LongMemEval, p. 5](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5&rect=367,654,505,664)):

| Version | History per question | Intended use |
|---|---|---|
| **LongMemEval_S** ("short") | about 115k tokens, roughly 50 sessions (the session count is from the library note, not the quoted passage) | Fits in a long-context window, so you can feed the whole history to a model. |
| **LongMemEval_M** ("medium") | 500 sessions, about 1.5M tokens | Too big for any context window, so a memory or retrieval system is required. |
| **Oracle** | Only the evidence sessions | Not a third size. It is an upper-bound setting that separates reading ability from retrieval ability (p. 6). |

- **Difficulty:** Long-context models drop 30–60% going from oracle to S. GPT-4o goes from 0.870 to 0.606 and Llama-3.1-70B from 0.744 to 0.334 (p. 6, from the library note).
- **Where each is used:** The paper runs its retrieval and indexing design experiments on M, with the Stella-V5 retriever. Later systems usually report on S. For example, the Zep paper compares against full context on S (71.2% vs 60.2% with gpt-4o).
- **Same questions:** An S score and an M score are therefore comparable question for question. The gap shows how much the extra haystack hurts.
- **Other variants:** Besides S and M and the oracle setting, I found none in the paper's text. The page 26 table compares oracle, S and M. The note does not mention other releases. If you've seen a newer variant, such as a cleaned-up release, it isn't in this library.

The "other versions" part rests on a keyword search of the paper and its note, not a full read. I did not read the page 26 table. I also didn't get a precise link for the oracle sentence on page 6, because the phrase matched twice there.

I changed nothing in the repository, so there is no commit message to suggest. If you want this kept, I can append it to the paper's note under Q&A.
