I'll check what page 6 says about chain-of-note, and whether the library has a note for this paper.

The library has a note for this paper. I'll check what it says about Chain-of-Note and read the paper's section 5.5 description.

**Chain-of-Note (CoN)** is a reading strategy from Yu et al. (2023). Given retrieved items, the model first writes a short note extracting the evidence from each item, then answers from those notes. The paper treats it as splitting long-context reading into two easier subtasks: copying the important details, then reasoning over concise notes.

**In this paper:** CoN is the fourth control point (reading strategy) in the paper's unified view of memory: indexing → retrieval → reading. The authors apply it by default in §5.2–5.4 and find that, even with perfect retrieval, a poor reading strategy can cost up to 10 points for GPT-4o. CoN with JSON-formatted input performs best ([p. 10, Fig. 6](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=10)).

**In this library:** the term appears in the paper's agent note, `notes/LongMemEval. Benchmarking Chat Assistants on Long-Term Interactive Memory.md`. Its digest records the CoN finding with its page, so later sessions don't need to re-read the paper for it. The note is one of the per-paper memory files described in `.claude/library-guide.md`. It is written by `paperlib read` or the `overview` skill, and sessions append settled points to its Q&A.
