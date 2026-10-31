**Notes** are per-paper agent memory: one markdown file for each paper, kept so later sessions don't re-read and re-derive the same paper.

- **Where:** `notes/<stem>.md`, where `<stem>` is the paper's filename without `.txt`. The folder is flat, so moving a paper doesn't touch its note.
- **What's in it:** a header (`type`, `family`, `evidence`, `strength`), a Digest of at most 20 lines with page cites, a Related in library list of links to other papers, and a Q&A section.
- **Who writes it:** `paperlib read <scope or paper.txt>` writes or merges notes (one model request per paper, resumable). The `overview` skill also writes them. Any session can append to the Q&A when it settles something worth keeping.
- **Rule:** merge into an existing note and never drop its Q&A.

**Here:** the LongMemEval paper (`library/llm/memory/benchmarks/`) has no note yet. `ls notes/` finds nothing for it, so a question about it would start from the text layer, and an answer worth keeping should be appended to a new note's Q&A. Its page 6 is the one you're reading, so cite that page when you do.

I took "chain of note" to mean the notes system. If you meant something else, such as the chain-of-note technique from the paper, tell me and I'll look at page 6 for that.
