---
name: reapply-corrections
description: Put back the hand corrections a reconversion could not re-apply (listed by `paperlib corrections --stale`), merging each with what the new conversion changed there, or retire it when the converter now gets that part right. Use for "/reapply-corrections", after an overnight reconversion, or when a paper says a hand correction could not be re-applied.
model: opus
---

# /reapply-corrections — put back what a reconversion could not place

**Scope.** A paper or folder, or with none, every paper `paperlib corrections --stale` lists.

A correction in `corrections/<stem>.yaml` replaces the converter's text `was` with `now`.
`paperlib reconvert` applies it again by finding `was` in the new conversion, or a region
its landmarks place that is nearly the same. It is stale when the converter changed that
very text, so the new conversion may hold a fix of its own there, or something worse.

## Steps

For each stale correction:

1. **Read it and the place.** `where`, `why`, `was`, `now`, then the paper around its
   `section`, `prev` and `next`. Compare the new text with `was` (what the converter wrote
   then) and with `now` (what the edit made of it).
2. **Decide.**
   - **Retire** when the new conversion is as good as `now` for an agent reading the
     paper: `paperlib corrections retire <paper.md> "<where>"`.
   - **Merge** otherwise. Copy the paper aside first (`cp <paper.md> <scratch>/base.md`),
     since it is reconverted and not yet committed. Edit the paper so the place has both
     the correction and what the converter improved (`now`'s values with the new bold,
     say); check the PDF page only where the two disagree on content. Then retire the old
     correction and record the merged one:
     `paperlib corrections capture <paper.md> --base <scratch>/base.md --why "<why>"`.
3. **Take the pointer out**: delete the line "A hand correction of … could not be
   re-applied" under the paper's conversion note.

Then `paperlib corrections --stale` is empty for the scope and `paperlib check` passes.
Report per correction: retired or merged, and why, in a line. Suggest a commit message for
the library; do not commit.
