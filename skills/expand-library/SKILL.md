---
name: expand-library
description: Find the papers missing from an area, have the reader review the list, then add the approved ones in bulk with summaries. Use for "what am I missing in X", "expand the library on X", "fill the gaps in X", "literature pass on X", "find the seminal papers on X", or to add a long list of papers at once.
model: sonnet
---

# /expand-library — fill the gaps in an area

For one or two papers use `add-paper`; this is for tens to hundreds. Paths below are the
defaults; `.claude/library-guide.md` has this library's.

**Propose first, add after approval.** Nothing is added before the reader has reviewed the
list.

## Steps

1. **Scope.** Restate it in one line: which areas, and the depth (see
   [reading-list-guide.md](reading-list-guide.md)). A large area can be split into several
   lists, one per group of folders.
2. **Write the lists.** One subagent per list (Sonnet is enough; at most four at a time),
   each given [reading-list-guide.md](reading-list-guide.md) and its area. They write
   `docs/reading-lists/<area>.md` and `.tsv` in the library (create the folder if it is
   missing). Read each list once: the folders exist, nothing is obviously already in the
   library, the reasons are concrete.
3. **Review.** Give the reader the list paths and the counts per folder, then wait. They
   strike proposed papers by number and may move papers in from "Considered". Append those
   to the TSV with the next numbers and add them to the `.md` under "Added from Considered".
4. **Record the skips.** `paperlib skips docs/reading-lists/<area>.md
   --strike <numbers> [--reason "..."]`, check the dry run, then rerun with `--write`. The
   struck and the considered papers go to `catalog/skipped.yaml`, so they are not proposed
   again.
5. **Add.** `paperlib add-batch docs/reading-lists/<area>.tsv`, in the background: about
   3–4 papers a minute, status saved per paper, so a rerun resumes and retries failures. Read
   only the failures and the closing counts. For `needs a PDF` rows, a subagent looks for an
   open PDF (author page, proceedings, institutional repository) and writes its local path
   into the row's `source` column; then rerun. ACM, Wiley, Springer, SSRN and OpenReview block
   scripts: ask the reader to download those in a browser. A paper that cannot be had is
   struck and recorded as in step 4, with that reason.
6. **Summaries.** `paperlib pending-summaries <scratchpad>/pending.md <folder> [...]`
   collects every paper without a summary under those folders, with its abstract. A subagent (Sonnet, about 150 papers each)
   reads only that file and the style of existing summaries in the folders, and writes
   `<number>\t<summary>` lines; then `paperlib apply-summaries <pending.md> <summaries.tsv>`.
   Check the numbers in a few summaries against the abstracts.
7. **Rebuild and check.** `paperlib build-index`, then `paperlib check`, which
   must pass. Spot-check two or three conversions, and list the papers that came from PDF
   text (`source: pdf-text`).
8. **Clean up.** Once every row of a list is `added`, `in library` or `struck`, delete its
   `.md` and `.tsv`: the papers carry their summaries and the skips are in the catalog.
9. **Report**: counts per area (added, struck, in library, from PDF text), anything left
   for the reader, and a suggested commit message. Never commit.

Work in one session at a time: two sessions running the same lists overwrite each other's
files.
