**Chain-of-Note (CoN)** is a reading strategy for retrieval-augmented LLMs (Yu et al., 2023). The model first writes a short note on each retrieved item, pulling out the relevant facts, and then reasons over those notes to answer. The idea is to split a long-context reading task into two easier steps: copy the important details, then reason from the concise notes.

**How LongMemEval uses it**

- **Reader strategy (§5.5, p. 10).** After retrieval, the memory items are shown as JSON, and the reader is told to extract from each item before reasoning. The paper applies CoN and JSON by default in §5.2–5.4.
- **Prompt (Fig. 13, p. 25).** The CoN prompt asks for "first extract all the relevant information, and then reason over the information," and adds "Answer (step by step):". The non-CoN baseline drops that instruction. The text on p. 23 says the prompt is "a small variation of" CoN.
- **Result (Fig. 6, p. 10).** Under oracle retrieval, where only the evidence sessions are given, a weak reading setup costs up to 10 points for GPT-4o. CoN with JSON is best for every reader model tested. JSON alone does not reliably help without CoN.

**Here in the library**

- The paper's note (`notes/LongMemEval…md`, line 26) records the CoN + JSON result.
- Yu et al.'s CoN paper is not in the library, so the description above comes from LongMemEval's account of it.
- The reading-strategy point matters for this library's memory work: a retrieval gain can be cancelled by a poor reading step, so comparisons across memory systems should hold the reader prompt fixed.

I did not confirm that page 6 itself discusses CoN; the passages above are from pp. 10, 23 and 25.
