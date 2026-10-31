**LongMemEval_S and _M differ only in how much filler history surrounds the same questions.** The paper defines them on page 5 (§3.2):

- **LongMemEval_S**: about 115k tokens of chat history per question.
- **LongMemEval_M**: 500 sessions, about 1.5M tokens per question.

Both use the same 500 questions. Each question's evidence sessions are inserted at random among unrelated filler sessions (simulated self-chats, plus ShareGPT and UltraChat), and every session gets a plausible timestamp. The paper says the pipeline can build histories of any length, and these two are the standard settings for comparison.

**The other version in the paper is Oracle**, which is not a length setting. It gives the model only the evidence sessions, with no filler (p. 6). Oracle is an upper bound, and the gap from Oracle to _S measures how much the filler and the length hurt. For GPT-4o the paper reports 0.870 with Oracle and 0.606 on _S, a 30–60% drop across long-context models (p. 6, and the pilot results on p. 3–6).

I found no other named versions in this paper. Later releases of the dataset may add more, but this paper does not describe them.

**Correction to the existing note:** `notes/LongMemEval. Benchmarking Chat Assistants on Long-Term Interactive Memory.md` says _S has "~50 sessions". The paper gives only the token count for _S (p. 5), so that figure is not supported by the text. I can correct the note's digest and add this as a Q&A entry if you want.
