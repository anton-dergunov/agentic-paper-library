**Short answer:** S and M are two sizes of the same 500 questions. They differ only in how much filler chat history surrounds the evidence. The paper doesn't define any other numbered versions, but it does use an oracle setting that is not a size.

**The two standard settings** (the paper says these are "two standard settings for consistent comparison", p. 1 and p. 5):

- **LongMemEval_S:** about 115k tokens of history per question. The evidence sessions are mixed into unrelated filler sessions.
- **LongMemEval_M:** 500 sessions, about 1.5M tokens per question.

The filler comes from three sources (p. 5, App. A.2): 50% simulated self-chat sessions on other user attributes, 25% ShareGPT, and 25% UltraChat. Each evidence session is inserted at a random position, and timestamps are assigned to all sessions. The questions and evidence are identical across both settings, so the only variable is the haystack size. That is what makes S and M comparable.

**The oracle setting (not a size):** the model is given only the evidence sessions. The paper uses it as an upper bound. Long-context models drop 30–60% going from oracle to S, for example GPT-4o goes from 0.870 to 0.606 and Llama-3.1-70B from 0.744 to 0.334 (p. 6, Fig. 3). Most of the paper's reading-strategy experiments use this setting (p. 10, Fig. 6).

**Other versions in the library:** the LoCoMo-style predecessors in the note are different benchmarks, not versions of this one. The incremental-interaction paper in the library repackages LongMemEval as "LME(S*)", with 5 histories of about 355K tokens and 300 questions, so it is a third configuration of the data. Check that paper's note before quoting its numbers next to S or M.

**Caveat on the note:** the existing note says S has "~50 sessions". The passages I checked give only the 115k token figure, not a session count, so I'd treat "~50" as unverified until someone checks it against the paper or the released data.

Citation: [LongMemEval, p. 5, the S and M definitions](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=5)
