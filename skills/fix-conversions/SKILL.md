---
name: fix-conversions
description: Fix the papers whose markdown conversion is damaged — tables missing or flattened, values in the wrong cells, missing sections, unreadable main equations — by reconverting them or correcting them by hand from the PDF, then read them again so their notes are right. Works through catalog/conversion-issues.yaml and the problems the reader graded `damaged` in the notes. Use for "/fix-conversions search-and-ranking", "fix the conversion issues", "fix this paper's table", "the conversion of X is broken", and between reading an area into notes and writing its review.
model: opus
---

# /fix-conversions — repair damaged papers before they are relied on

When `paperlib read` writes a note, the reader grades the paper's markdown on the note's
`conversion:` line: `ok`, `minor: <what>` (the meaning is still recoverable) or `damaged:
<what>` (something a note or a review needs is missing or unreliable). This skill fixes the
damaged ones, so that the notes and the reviews written from them rest on the paper's real
content. Read `AGENTS.md` (which imports `.claude/library-guide.md`) first if you have not.

**Scope.** `<scope>` (a folder), `<paper.md>`, or nothing for every entry in the catalog.
In the pipeline of an area it sits between reading and writing:

```
paperlib read <scope>          notes, with a conversion grade each
/fix-conversions <scope>       this skill
/literature-review <scope>     the review, from notes of fixed papers
```

**Only `damaged`.** Papers graded `minor` are left alone: their notes already say which
detail not to trust. A converter fix or a thorough reconversion may clean them up later.

## Steps

1. **Collect.** Run `paperlib conversion-issues <scope>`. It grades the notes written
   before grades existed (one model request over their conversion lines), adds every
   damaged paper to `catalog/conversion-issues.yaml`, and lists the catalog's entries in the
   scope: the work list. Say in one line how many there are.
2. **Look at each entry.** Open the markdown at the place the problem names, and the PDF at
   the same page (`Read` with `pages`, only the pages cited; the PDF path is the paper's
   path under the PDF root, `.md` replaced by `.pdf`). Then sort it:
   - **The paper's own error**: the PDF shows the same thing (a duplicated column, a
     typo in a number). Nothing to fix; remove the entry, and say so in the report.
   - **Not in the text at all**: a result shown only as a figure, a table that is an
     image in the PDF too. Not a conversion problem; remove the entry.
   - **Missing because arXiv's HTML is incomplete**: whole pages or sections absent. The
     converter cannot fix this yet (the engine's `docs/tasks/conversion-follow-ups.md`
     tracks it); leave the entry.
   - **Broken by the conversion**: fix it (step 3). If the same flaw is likely in other
     papers (lost `±`, superscripts flattened in table cells, bold marking lost), it is a
     converter bug: also record it once, with this paper as an example, in the engine's
     `docs/tasks/conversion-follow-ups.md`, so it is fixed for every paper rather than
     paper by paper.
3. **Fix**, cheapest first, and look at the place again after each try:
   - **Reconvert.** `paperlib reconvert <paper.md>` for `source: html` (the converter may
     have improved since). For `source: pdf-text`, `paperlib reconvert --pdf-text
     --inline-math <paper.md>`: the thorough PDF conversion, with every paragraph that has
     mathematics read by the model; most of the library's PDF papers had the quick one.
   - **By hand, from the PDF.** Rewrite only the broken part (the table, the equation, the
     paragraph) from the PDF page, with the paper's numbers exactly as printed; never fill
     in what the PDF does not show. Merged cells make an HTML `<table>`; equations are
     LaTeX. Put `<!-- hand-edited: <what was fixed> -->` next to it, so reconversion skips
     the paper. A long table or a missing section is worth this; a cosmetic slip is not.
4. **Read the fixed papers again.** `paperlib read --stale <scope>` re-reads every paper
   changed since its note was written, keeping the note's Q&A. The new note's conversion
   line should be `ok` or `minor`; if it still says `damaged`, look at what it names.
5. **Update the catalog.** Remove the entries that were fixed, and those that were not
   conversion problems. Keep the others, with the problem line updated if it changed.
6. **Check.** `paperlib check` must pass.
7. **Report.**
   - A table: paper, what was wrong, what was done (reconverted, fixed by hand, the paper's
     own error, left and why).
   - The converter bugs recorded in the engine, if any.
   - The entries still open in the scope.
   - A commit message: the fixed papers, the re-read notes, the catalog. Never commit.
