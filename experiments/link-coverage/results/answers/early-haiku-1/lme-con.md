**Chain-of-Note (CoN)** is a prompting strategy from Yu et al. (2023): the model first goes through each retrieved document and writes out the evidence relevant to the question, then answers from those notes. It splits one hard reading task into two easier ones, copying the important details and then reasoning over the shorter notes.

**How this paper uses it:**

- **Page 6 (pilot study, Figure 3b):** CoN is one of the two conditions for long-context LLMs reading the full LongMemEval-S history (about 115k tokens). The text says performance drops 30–60% against oracle retrieval "regardless of whether the chain-of-note technique was applied." So on this page CoN does not rescue long-context reading. (p. 6, Figure 3b; lines 457–467 of the text layer)
- **Reading strategy in the design study (§5.5, p. 9-ish):** CoN, combined with a JSON-structured prompt, is the recommended reader. The paper reports that CoN with JSON beats the other combinations by a wide margin, and that it can be worth up to about 10 points of accuracy. Sections 5.2–5.4 use it by default.
- **Prompt:** Figure 13 (appendix) gives the CoN prompt, a small variant of the original, next to a non-CoN prompt.
- **Table 2:** CoN is listed as one of the nine systems compared, with a "CoN" reading strategy.

Note that page 6 shows CoN as a control, not as the paper's recommended design. The gain comes in §5.5, which I haven't re-read on its page. I also didn't check Anton's note for this paper, which may already cover it.
