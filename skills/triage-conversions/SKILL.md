---
name: triage-conversions
description: File the library's new conversion problems (issues/ records of kind `new`) under the engine's tickets, one ticket per cause, refresh the tickets index, and propose batches of tickets for a fix session. Reads a PDF's text only at a cited place, to tell a paper's own slip from a conversion's. Use for "/triage-conversions", "triage the conversion issues", "what conversion bugs are there", "which tickets should I fix next".
model: opus
---

# /triage-conversions — one ticket per cause

The reader records every conversion problem it finds in `issues/<stem>.yaml`, one record
per problem, under the id of the engine ticket for its cause (`kind`), or as `kind: new`
with a `suggested` slug when none fits. A session records one with `paperlib issues add`.
This skill gives the `new` records a ticket and keeps the tickets' index current, so the
reader can choose what to fix. It is cheap: it reads records and tickets, and of the paper
only the cited place, in its three copies at most (`paperlib issues look`), never a whole
PDF.

## Steps

1. **See what is there.** `paperlib tickets` (the tickets, their folder, papers per ticket,
   and the untriaged count) and `paperlib issues --new` (the records to file).
2. **File each `new` record.**
   - **An existing ticket fits**: set `kind` to its id and drop `suggested` (edit the
     paper's `issues/<stem>.yaml`).
   - **The paper's own error**, not the conversion (two numbers the paper prints
     differently, its own typo): delete the record. A quick look at the paper's markdown
     around the cited place settles it; a doubt stays a record.
   - **A record that says a value changed** (a number, a sign, a unit, a symbol such as
     ±, ∈, "k", an exponent) needs more than the markdown, which looks the same whoever
     caused it. `paperlib issues look <paper> "<words at the place>"` prints the place in
     the markdown, in arXiv's cached HTML (each formula as the TeX LaTeXML kept) and in
     the PDF's text layer. Search for the words around the value, not the broken value.
     - The PDF prints the same: the paper's own slip; delete the record.
     - The HTML's TeX is the markdown's: the converter copied it faithfully, so a symbol
       missing from both was never typed (the author's) or was lost by LaTeXML; the PDF
       decides which.
     - The PDF has the character and the HTML lacks it: LaTeXML lost it; file it under
       the ticket for that loss.
     - The HTML has it and the markdown lacks it: the converter's; an engine ticket.
     The PDF's text layer often drops symbols (∈, √, a fraction's bar, a subscript's
     place), so a symbol it lacks proves nothing: a doubt stays a record. In the session
     of 23 Oct 2026, 24 of 28 such records were the papers' own slips.
   - **A new cause seen in several papers**: write a ticket `tickets/<id>.md` in the format
     of the others (frontmatter `id`, `title`, `converter`, `takes`, `status: open`, `cost`;
     then the labels line and **Broken**, **Fix**, **What it gives**, **Cost**,
     **Examples**), and file the records under it. One-off causes go under the nearest
     catch-all ticket rather than a ticket of their own.
   - **Cannot be fixed, or not worth it** (the PDF itself lacks it, arXiv's HTML leaves it
     out, a small isolated flaw both an agent and a person read past): file it, and add
     `wont-fix: <reason>` to the record, a reason that fits that one problem. A whole cause
     left as it is: `paperlib tickets move <id> wont-fix --reason "<why>"`, which moves the
     ticket to `tickets/wont-fix/`; its records then count as wont-fix too. Either way it is listed under "Won't fix" in the tickets index,
     and neither a new reading nor `paperlib issues add` records it again. A problem an open
     ticket will fix is not wont-fix.
3. **Catch-all tickets** (their Fix says "not known yet"): when one holds enough records
   to see sub-causes, split it: a ticket per sub-cause, its records moved over. Check the
   records that say a value changed as in step 2 first; the papers' own slips go.
4. **Status.** The active tickets sit at the top of `tickets/`, the closed ones in `done/`
   and `wont-fix/`; change one only with `paperlib tickets move <id> <status>`. A ticket with
   no open records left and nothing in the engine to do is `done`; a `fixed` one whose
   reconversion has run is closed with `paperlib issues close <id> --state <file>`, then
   moved to `done`.
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
