Chain-of-Note (CoN, Yu et al., 2023) is a prompting strategy for the reader step. It makes the model write notes before it answers.

**The idea.** Without CoN, the model is given the retrieved memory items and the question, and it answers directly. With CoN, you tell it to go through each retrieved item, pull out whatever is relevant to the question, and only then reason from those notes to an answer. Suppose the question is "How many days between my trip to Rome and my dentist visit?" The model first writes "session 3: Rome trip on May 4" and "session 7: dentist on May 19", then does the subtraction. This splits long-context reading into two easier steps: extract, then reason. It also lets the model say an item is irrelevant instead of being pulled off by it.

**How LongMemEval uses it** (§5.5, p. 6):
- **Where it sits.** It is part of the reading stage, after retrieval. Retrieved items are sorted by timestamp and passed to the reader as JSON.
- **The prompt.** It is a small variation on the original (Appendix, Figure 13). The model traverses the items, extracts evidence, then answers. Decoding is greedy, with a 800-token generation limit.
- **Effect.** Even with perfect retrieval (the oracle setting), a poor reading strategy costs up to about 10 absolute points for GPT-4o. JSON plus CoN beat the other three combinations (Figure 6).
- **Interaction with JSON.** Without CoN, JSON does not reliably beat plain natural language. With CoN, JSON helps readers of every size.
- **Default.** Sections 5.2 to 5.4 use CoN and JSON throughout, so the indexing and retrieval comparisons are measured with a strong reader.
- **Table 2.** The authors' own design is listed with CoN as its reading strategy. CoN is also listed as a system in its own right, with its own indexing row.

The paper presents CoN as an existing technique that they adopted. The new part is showing how much reading strategy matters even when retrieval is perfect.

I read this from the text layer and didn't check the exact numbers in Figure 6 against the PDF. If you want a page-linked citation for a specific value, tell me which one.
