---
name: paper-info
description: A quick look at a paper the reader has come across, in the library or not: whether the library has it, its citations and venue, what it proposes and the nearest library papers. Use for "quick look at 2305.13514", "what is this paper", "do I have this paper", "how well cited is X". It reports; it does not say whether to add or read the paper.
model: sonnet
---

# /paper-info — a quick look at a paper

1. Run `paperlib info <arxiv-url-or-id> [...]`, all papers in one call. For a paper given by
   title, `paperlib info "<title words>"` finds it in the library; if it is not there, get
   its arXiv id with `paperlib lookup --title "<title>"` and run `info` on that.
2. Show the output as a table, unchanged: one row per line, the `Nearest` papers as links
   to their markdown. Add nothing of your own, and no advice on whether to add, read or
   skip the paper: that is the reader's decision, and they have reasons you cannot see.
3. If the reader then asks about the paper itself, answer from the abstract (`paperlib
   info <id> --json` has it) and say that only the abstract was read. For more, they add
   the paper (`paperlib add <id>`) and ask again.
