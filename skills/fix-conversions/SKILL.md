---
name: fix-conversions
description: Work through the library's known conversion problems — tables missing, flattened or with values in the wrong cells, missing sections, garbled equations — by fixing the converter for recurring ones, reconverting, or correcting a paper by hand from the PDF, and read again the papers whose notes were affected. Works through catalog/conversion-issues.yaml, filled from what the reader reported in the notes. Use for "/fix-conversions search-and-ranking", "fix the conversion issues", "fix this paper's table", "the conversion of X is broken", and between reading an area into notes and writing its review.
model: opus
---

# /fix-conversions — make the papers say what the PDFs say

When `paperlib read` writes a note, the reader reports on its `conversion:` line what is
broken in the paper's markdown. `paperlib conversion-issues` copies those reports into
`catalog/conversion-issues.yaml`, the one list of known conversion problems. This skill
works through that list. Read `AGENTS.md` (which imports `.claude/library-guide.md`) first
if you have not.

**Scope.** `<scope>` (a folder), `<paper.md>`, or nothing for the whole catalog. In the
pipeline of an area it sits between reading and writing:

```
paperlib read <scope>          notes; each reports its paper's conversion problems
/fix-conversions <scope>       this skill
/literature-review <scope>     the review, from notes of fixed papers
```

## Three kinds of problem

| Kind | Marked | Means | What is done |
|---|---|---|---|
| Key content broken | `key-content-broken: true` (set by the reader, or here) | A part the paper's findings rest on is missing or wrong: a results table missing or with values in the wrong cells, lost bold that marked the significant results, the main method's equation unreadable, a missing section. So the note may be wrong too. | Fix the paper, then read it again. First. |
| Worth fixing | no flag (the default) | The meaning survives, but the markdown is worse than it should be: a garbled equation explained in the prose, a table readable only by order. Most problems are this. | Fix the cause in the converter if it recurs, so new papers benefit; reconvert. The note stands; no new reading. |
| Won't fix | `wont-fix: <reason>` (set here) | Cannot be recovered by a program, or not worth it: the PDF itself lacks it (a formula that was never typeset, a scanned historical paper), arXiv's HTML leaves it out, or the flaw is small and isolated and both an agent and a person read past it. | Nothing. The entry stays, so the problem isn't looked at again. |

## Steps

1. **Collect.** Run `paperlib conversion-issues <scope>`. It adds the problems the notes
   report and the catalog lacks, then lists the open entries of the scope, those that
   have key content broken first. Say in one line how many there are of each kind.
2. **Look at each entry,** those with key content broken first. Open the markdown at the place
   it names, and the PDF at the same page (`Read` with `pages`, only the pages cited; the PDF
   is the paper's path under the PDF root, `.md` replaced by `.pdf`). Then classify it:
   - **Not a conversion problem**: the PDF has the same flaw (the paper's own typo or
     duplicated column), or the content is only a figure there too. Remove the entry and
     set the note's conversion line to `ok` (or to what remains).
   - **Key content broken**: whatever the reader marked, decide by the definition in the
     table; set or remove `key-content-broken: true` accordingly. Older notes never set it,
     so this is where they get it.
   - **Won't fix**: set `wont-fix: <reason>` in one line. A problem can break key content
     and still be unfixable (arXiv's HTML missing pages): mark both, so reviews know to check
     the PDF.
   - **Worth fixing**: everything else.
3. **Group the fixable ones by cause.** Several papers showing the same flaw (lost `±`,
   superscripts flattened in table cells, bold marking lost) point to one converter bug.
   - A converter bug is fixed in the engine, in a session there (its `AGENTS.md` applies:
     a regression test for the fix, the change measured on real papers). Record each bug
     once in the engine's `docs/tasks/conversion-follow-ups.md`, with these papers as
     examples, and leave their entries open until the fix is in and they are reconverted.
   - A flaw in one paper only: go to step 4.
4. **Fix one paper**, cheapest first, and look at the place again after each try:
   - **Reconvert.** `paperlib reconvert <paper.md>` for `source: html` (the converter may
     have improved since). For `source: pdf-text`, `paperlib reconvert --pdf-text
     --inline-math <paper.md>`, the thorough PDF conversion; most PDF papers had the quick
     one.
   - **By hand, from the PDF**, only for key content that is broken. Rewrite the
     broken part (the table, the equation, the paragraph) from the PDF page, with the
     paper's numbers exactly as printed; never fill in what the PDF does not show. Merged
     cells make an HTML `<table>`; equations are LaTeX, but a formula the PDF prints as
     plain text stays plain text. Put `<!-- hand-edited: <what was fixed> -->` next to it,
     so reconversion skips the paper.
5. **Read again the papers whose key content was broken** and is now fixed: `paperlib read
   --redo <paper.md> ...`. The note's Q&A is kept. Look at the new conversion line: if it
   still reports key content broken, return to step 2 for that paper. Papers fixed for any
   other problem keep their notes; set their conversion line to
   `ok` or to what remains, or the next `conversion-issues` run adds them back.
6. **Update the catalog.** Remove the entries that were fixed or were not conversion
   problems; keep the rest with their flags.
7. **Check.** `paperlib check` must pass.
8. **Report.**
   - A table: paper, the problem, its kind, what was done (reconverted, fixed by hand, read
     again, wont-fix and why, left for a converter fix).
   - The converter bugs recorded in the engine.
   - The entries still open in the scope.
   - A commit message: the fixed papers, the notes, the catalog. Never commit.
