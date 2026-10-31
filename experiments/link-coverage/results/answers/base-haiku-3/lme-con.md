**Chain-of-Note (CoN)** is a reading strategy for retrieval-augmented LLMs. Instead of answering straight from a long pile of retrieved text, the model first writes a short note on each item, pulling out what is relevant, and then reasons over those notes to answer. The paper's own summary (p. 10): it "decomposes long-context reading into two simpler subtasks: copying important details and reasoning with more concise notes." The original Yu et al. (2023) paper is cited but not filed in this library.

**How LongMemEval uses it**

- **Default reader.** Sections 5.2–5.4 apply CoN with JSON input by default. Memory items are sorted by timestamp and presented as JSON, then the reader writes notes and answers (§5.1, §4.2). The prompt (Fig. 13, appendix) is "a small variation of" CoN: traverse the documents, extract evidence, then answer, with greedy decoding and an 800-token cap.
- **Main result (p. 10, Fig. 6).** With oracle retrieval, a poor reading strategy costs GPT-4o up to 10 points. CoN with JSON is the best setup and is the only format that consistently helps across reader models; without CoN, JSON does not reliably beat plain text.
- **Pilot on full histories (p. 6, Fig. 3b).** The table shows CoN does not rescue long-context reading. On LongMemEval_S, GPT-4o goes from 0.606 to 0.640, while Llama 3.1 70B drops from 0.334 to 0.286, Llama 3.1 8B from 0.454 to 0.420, and the Phi-3 models also fall. The "% Drop" column matches these numbers. The p. 6 text attributes the 30–60% gap to the full history itself, "regardless of whether" CoN is applied.

**Reading the two results together:** CoN helps when the right evidence is already retrieved (oracle), and it does little for, or hurts, weaker readers that must sift through the whole ~115K-token history. The p. 6 table is the one to check against the PDF, because the two-column layout makes the row alignment easy to misread.

The note in `notes/` covers the p. 10 result in its Digest but not the p. 6 pilot, so the p. 6 point is not yet recorded there.
