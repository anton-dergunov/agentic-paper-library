I added 2505.22101 to `llm/memory/agent`, but `paperlib check` does not pass. It reports 45,680 problems across the library. They are missing PDFs and broken image links in other papers and in `reviews/`, and none of them mention the new paper. I didn't dig into them, since the skill says to do only its steps.

- **Filing:** the markdown came from `html`. The page map placed 17 headings and left 0 unplaced.
- **What it is:** this is the short version of MemOS. It treats parametric, activation and plaintext memory as managed resources. A standard unit, the MemCube, carries metadata, governance attributes and usage indicators. A three-layer architecture handles the API, scheduling and lifecycle, and storage and governance. It is a design proposal with no experiments.
- **Related papers:**
  - The library already has the longer follow-up, [MemOS: A Memory OS for AI System](library/llm/memory/agent/MemOS.%20A%20Memory%20OS%20for%20AI%20System.md) (2507.03724). That one is a separate arXiv id, so it didn't register as a duplicate.
  - It sits in the same OS-style memory line as [MemGPT](library/llm/memory/agent/MemGPT.%20Towards%20LLMs%20as%20Operating%20Systems.md) and [Memory OS of AI Agent](library/llm/memory/agent/Memory%20OS%20of%20AI%20Agent.md).
  - It is broader than both, because it also covers activation and parameter memory.
- **Review:** it is not yet in `reviews/llm/memory.md`. `/literature-review update llm/memory` adds it.

Suggested commit message:

```
Add MemOS short version (2505.22101) to llm/memory/agent

- Adds the May 2025 short version of MemOS, a design proposal for a memory operating system with the MemCube abstraction; the longer follow-up (2507.03724) is already in the same folder.
- Regenerated the indexes.
```
