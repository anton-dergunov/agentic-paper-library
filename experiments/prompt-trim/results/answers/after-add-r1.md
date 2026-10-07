Added MemOS (2505.22101) to `llm/memory/agent/`. `paperlib check` does not pass, but the failures don't involve this paper.

- **Check failures:** It reports about 45,000 problems, mostly missing PDFs and broken image links across the whole library. Nothing in its output names MemOS. I did not look into the cause. This copy of the library (`copies/lib-after`) looks like it lacks the PDFs and images.
- **Filing:** The markdown came from `html`. The page map placed 17 headings and left none unplaced.
- **Summary:** "Proposes MemOS, a memory operating system for LLMs that manages parametric, activation and plaintext memory through a standardized MemCube abstraction with lifecycle control, fusion and migration."

**How it relates:** MemOS treats memory as an operating-system resource. It manages parametric, activation and plaintext memory under one abstraction (the MemCube). The folder's other agent-memory papers (e.g. the note-network and survey papers) are mostly about plaintext retrieval or consolidation. This is the original May 2025 paper. The library already holds its follow-up, [MemOS. A Memory OS for AI System](library/llm/memory/agent/MemOS.%20A%20Memory%20OS%20for%20AI%20System.md) (2507.03724), which adds a scheduler and a metadata schema for provenance and governance.

Not yet in `reviews/llm/memory.md`; `/literature-review update llm/memory` adds it.

Suggested commit message:

```
Add MemOS (2505.22101) to llm/memory/agent

Adds the original MemOS paper, a memory operating system for LLMs that manages parametric, activation and plaintext memory through a MemCube abstraction. It sits next to the later MemOS follow-up already in the folder. The indexes are rebuilt.

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
```
