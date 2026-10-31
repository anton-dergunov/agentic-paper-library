**Chain-of-Note (CoN)** is a reading strategy for retrieval-augmented QA. Before answering, the reader model goes through each retrieved item and writes a short note on what it says about the question, then answers from those notes. The point is robustness: irrelevant or noisy retrievals get noted as such rather than silently shaping the answer. It comes from Yu et al. 2023, which the paper cites but the library doesn't hold.

**How LongMemEval uses it**

- It is the **reading** stage of the paper's indexing → retrieval → reading framework. Reading is one of the four control points, alongside value, key and query (p. 8, Table 2).
- It is the default for every experiment in §5.2–5.4: "we apply Chain-of-Note and json format … by default" (§5.1, p. 7).
- The prompt (Fig. 13, appendix p. 23) is a small variant of CoN. The model traverses the retrieved memory items, extracts evidence, then answers. Decoding is greedy, with an 800-token cap.
- The finding is that CoN with JSON-formatted input is worth up to about +10 points even with oracle retrieval (§5.5, p. 10, Fig. 6). Long-context readers also gain from it, so the gain isn't only a retrieval effect. JSON alone doesn't reliably help without CoN.
- Retrieved items are sorted by timestamp before reading, which helps the reader keep temporal order.

**In the library:** the note (`notes/LongMemEval…md`) records this as "chain-of-note with JSON input is worth up to +10 points even with oracle retrieval (p. 10, Fig. 6)". The paper's own pilot and design results are in its digest; the CoN detail itself is not in any review or other note.

I checked the CoN mentions by search and read the §5.1, §5.5 and appendix passages. I didn't confirm that the text on page 6 of the PDF itself mentions CoN. Its mentions are on the intro page, p. 7, p. 10 and p. 23. If you meant something on page 6, tell me which passage and I'll check it.
