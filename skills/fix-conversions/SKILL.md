---
name: fix-conversions
description: Fix conversion tickets in the engine's converters (one ticket per cause of broken markdown: tables flattened or with values in the wrong cells, garbled equations, missing sections), each with a test and a check on the ticket's papers, then give the overnight command that reconverts the papers the tickets touch. Use for "/fix-conversions <ticket ids>", "fix these conversion tickets", "fix the bold in PDF tables", and after /triage-conversions has proposed a batch.
model: opus
---

# /fix-conversions — fix causes in the engine, not papers by hand

**Scope.** Ticket ids from `paperlib tickets` (the engine's `tickets/`), usually a batch
`/triage-conversions` proposed. With none, ask which, showing `paperlib tickets`.

The point is that one fix in the converter repairs every paper with the flaw, now and
for every paper added later. Do not fix papers by hand, read PDFs beyond the pages a fix
needs as evidence, or rewrite notes: the papers are reconverted overnight by the reader,
and only notes whose key content was broken are read again.

## Steps

1. **Read the tickets** and the engine's `AGENTS.md` (a fixture for every converter fix,
   changes measured on real papers). `paperlib issues --kind <id>` lists each ticket's
   papers and places; take three to five of them as the test set, those with key content
   broken first.
2. **Fix each ticket** in the engine's code:
   - Find the cause on the test papers: the place in the markdown, the source it came
     from (arXiv's HTML in the cache, the PDF's text layer), the converter step.
   - Change the converter. Add a fixture to `tests/test_conversion.py`.
   - Reconvert the test papers (`paperlib reconvert <paper.md>`; for PDF papers add
     `--pdf-text --inline-math`, minutes each) and look at the places again. Compare
     `paperlib symptoms --counts` and `paperlib symptoms --compare HEAD` on them with
     before, so the fix breaks nothing else. `paperlib test` must pass.
   - Close the test papers' records: `paperlib issues close <id> <paper.md> ...`.
   - `paperlib tickets move <id> fixed` (`done` if no other paper has its records), and
     update the ticket's Fix with what was done. A ticket that turns out to need a design decision
     or a new tool: write down what was found in the ticket and leave it `open`.
3. **By-hand tickets** (`takes: by-hand`) are done only when the reader asks, and the edit
   is marked `<!-- hand-edited: <what> -->`.
4. **Close the loop.** `paperlib tickets --write`; `paperlib check` must pass.
5. **Report.**
   - Per ticket: the cause, the fix, the papers it was checked on and what changed there.
   - The overnight command for the rest, one per fixed ticket:
     `caffeinate -i nice -n 19 paperlib reconvert --issue <id> --jobs 1 --state ~/.cache/papers/reconvert-<id>.jsonl`
     (`--list` instead of `--jobs` shows the papers), and after it
     `paperlib issues close <id> --state ~/.cache/papers/reconvert-<id>.jsonl`, which prints
     the `paperlib read --redo` command for the papers whose key content was broken.
   - Two commit messages, one per repository: the engine (converter, tests, tickets) and
     the library (the test papers, `issues/`). Never commit.
