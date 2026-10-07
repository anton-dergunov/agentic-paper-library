Paper 2505.22101 (MemOS, short version) is added to `library/llm/memory/agent/`, and `build-index` rebuilt the indexes. `paperlib check` did not pass, but nothing it flagged is about this paper.

The check printed about 45,000 lines of errors. The ones I saw are missing PDFs and broken image links in other papers, and none mention MemOS. The cause is probably that this working copy (`lib-before`) doesn't hold the full PDF and image trees. Run the check in the real library to confirm.

**What the paper is**
- **Source:** the markdown came from `html`. The page map placed 17 headings and left none unplaced.
- **Summary set:** "MemOS (short version): a position-style proposal to manage parametric, activation and plaintext memory as one schedulable resource, via a standardized MemCube unit and interface, operation and infrastructure layers; no experiments."
- **Content:** the paper treats memory as a managed resource, built around MemCube, a standard memory unit with metadata, governance attributes and behavioural indicators. The design has three layers: interface (Memory API), operation (scheduling and lifecycle), and infrastructure (governance and store). It is a design proposal with no evaluation.
- **Related papers:**
  - The library already has the long version, [MemOS. A Memory OS for AI System](library/llm/memory/agent/MemOS.%20A%20Memory%20OS%20for%20AI%20System.md) (2507.03724), which supersedes this one.
  - It is also close to [MemGPT](library/llm/memory/agent/MemGPT.%20Towards%20LLMs%20as%20Operating%20Systems.md), which does OS-style paging of memory through the context window.
  - [Memory OS of AI Agent](library/llm/memory/agent/Memory%20OS%20of%20AI%20Agent.md) is the third OS-framed memory system there.
- **Review:** not yet in `reviews/llm/memory.md`; `/literature-review update llm/memory` adds it. The folder README already notes one paper there that the review doesn't cover.

Since the long version covers the same ground, keeping both is your call.

Suggested commit message:

```
Add MemOS (short version) to llm/memory/agent

- Adds the May 2025 short version of MemOS (2505.22101), a design proposal for treating parametric, activation and plaintext memory as one managed resource. The extended version (2507.03724) is already in the same folder.
- Rebuilt the indexes.
```
