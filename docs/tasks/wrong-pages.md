# Task: correct the page numbers in notes and reviews

Most of the pages that notes and reviews cite for a table or a figure are wrong, usually by one. A reader who follows "p. 8, Table 1" lands a page before the table, and an agent that copies the citation passes the error on.

## What is known

**Agents' page numbers were wrong for 7 of 21 tables** in the citations measured for `paperlib locate` ([experiments/pdf-locations](../../experiments/pdf-locations/README.md)). They gave the page that mentions the table, not the one that prints it; the named destination had been hiding this. `locate` now searches the whole paper when the given page misses, and says "(on p. 8)".

The notes and reviews were checked on 30 Oct 2026. For each "p. N, Table M" or "p. N, Fig. M" in a note, and each review link with `dest=table.M` or `dest=figure.M`, the page was compared with the page whose text layer prints the caption ("Table M:" at a line's start or after a column gap).

| | Checkable | Right page | Wrong | Off by +1 | Off by +2 |
|---|--:|--:|--:|--:|--:|
| Notes' citations | 8,424 | 3,361 | **5,063** (in 1,519 notes) | 3,765 | 737 |
| Reviews' links | 519 | 218 | **301** | 251 | 32 |

- Another 1,068 citations in notes could not be checked: no caption was found, or more than one line looks like one.
- "+1" means the table is printed one page after the cited one.
- The shift is systematic, not random. The likely cause is the old markdown conversion: its page markers were probably placed where a page ends, or counted from 0. Check this on two or three notes before relying on it. Notes read from the text layer (since 26 Oct 2026) should be right; the 3,361 right citations are probably mostly theirs.
- Reviews' links still open the right place when the PDF has the named destination, since `dest` wins over `page`, which hid the error. The "p. N" in their text is wrong all the same.
- Prose citations ("(p. 8)") are probably shifted the same way, but nothing on the page can confirm them.

Example: the note on *Efficiently Scaling Transformer Inference* cites "p. 8, Table 1" and "p. 8, Fig. 8"; both are on p. 9. An Opus answer copied the first without running `locate`, and its link opened p. 8.

## Done already

- `paperlib locate` tries the page it is given, then the whole paper, and reports the right page.
- The guide's rule now says to run `locate` also for a citation taken from a note or review, so an answer corrects a wrong page instead of copying it.

## To do

1. **A deterministic checker.** For a note or review, list each table and figure citation with its page and the caption's page, using the text layer only (no model). It could be `paperlib check-pages [<scope>]`, or a mode of `paperlib check`. Report per note how its citations are shifted.
2. **Fix what the checker can prove.** Rewrite a table or figure citation's page when its caption is found on exactly one other page. In a review, fix the link's `page=` and its text.
3. **Prose citations in a note whose float citations are all shifted the same way.** Shift them by the same amount, and mark the note so its fixes can be reviewed (a diff in the library's git is enough). Leave notes with mixed shifts for `paperlib reread`.
4. **Measure, then decide**: on a sample of notes, count how many shifted prose citations are right after the shift, opening the PDF page for each, before applying step 3 to all of them.
5. Once the notes are right, consider whether reviews and notes should carry `rect` (design.md, Next).
