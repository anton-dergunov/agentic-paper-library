---
name: triage-conversions
description: File the library's new conversion problems (issues/ records of kind `new`) under the engine's tickets, one ticket per cause, refresh the tickets index, and propose batches of tickets for a fix session. Reads no PDFs. Use for "/triage-conversions", "triage the conversion issues", "what conversion bugs are there", "which tickets should I fix next".
model: opus
---

# /triage-conversions — one ticket per cause

The reader records every conversion problem it finds in `issues/<stem>.yaml`, one record
per problem, under the id of the engine ticket for its cause (`kind`), or as `kind: new`
with a `suggested` slug when none fits. A session records one with `paperlib issues add`.
This skill gives the `new` records a ticket and keeps the tickets' index current, so the
reader can choose what to fix. It is cheap: it reads records and tickets, never PDFs or
paper text beyond a quick look at a cited place.

## Steps

1. **See what is there.** `paperlib tickets` (the tickets, their folder, papers per ticket,
   and the untriaged count) and `paperlib issues --new` (the records to file).
2. **File each `new` record.**
   - **An existing ticket fits**: set `kind` to its id and drop `suggested` (edit the
     paper's `issues/<stem>.yaml`).
   - **The paper's own error**, not the conversion (two numbers the paper prints
     differently, its own typo): delete the record. A quick look at the paper's markdown
     around the cited place settles it; a doubt stays a record.
   - **A new cause seen in several papers**: write a ticket `tickets/<id>.md` in the format
     of the others (frontmatter `id`, `title`, `converter`, `takes`, `status`, `cost`;
     then the labels line and **Broken**, **Fix**, **What it gives**, **Cost**,
     **Examples**), and file the records under it. One-off causes go under the nearest
     catch-all ticket rather than a ticket of their own.
   - **Cannot be fixed, or not worth it** (the PDF itself lacks it, arXiv's HTML leaves it
     out, a small isolated flaw both an agent and a person read past): file it, and add
     `wont-fix: <reason>` to the record, a reason that fits that one problem. A whole cause
     left as it is: the ticket's `status: wont-fix` with a one-line `reason`; its records then
     count as wont-fix too. Either way it is listed under "Won't fix" in the tickets index,
     and neither a new reading nor `paperlib issues add` records it again. A problem an open
     ticket will fix is not wont-fix.
3. **Catch-all tickets** (their Fix says "not known yet"): when one holds enough records
   to see sub-causes, split it: a ticket per sub-cause, its records moved over.
4. **Status.** A ticket with no open records left and nothing in the engine to do is
   `done`; a `fixed` one whose reconversion has run is closed with `paperlib issues close
   <id> --state <file>`, then `done`.
5. **Index.** `paperlib tickets --write` regenerates the engine's `tickets/README.md`;
   `paperlib check` must pass.
6. **Report and propose.**
   - The records filed, by ticket; the tickets created, split or closed; the records
     deleted as the paper's own errors.
   - Two or three **batches** for the next fix sessions, each a few tickets that touch the
     same code (PDF tables, PDF equations, the HTML converter, LaTeXML macros), ordered by
     key-content records first, then papers touched. For each: the tickets, what it gives,
     its cost, and the command to start it: `/fix-conversions <id> <id> ...`.
   - Two commit messages, one per repository: the library (`issues/`) and the engine
     (`tickets/`). Never commit.
