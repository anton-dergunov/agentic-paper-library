---
name: literature-pass
description: Find the papers missing from an area of the library, have Anton review the list, then add the approved ones in bulk with summaries. Use for "what am I missing in X", "literature pass on recommender-systems", "fill the gaps in llm/evaluation", "find the seminal papers on X", or to add a long list of papers at once.
---

# /literature-pass — fill the gaps in an area

Read `AGENTS.md` first if you have not: it has the layout, the rules and the topic tree.
For one or two papers use `add-paper`; this is for tens to hundreds.

**Propose first, add after approval.** Nothing is added before Anton has reviewed the list.

## Steps

1. **Scope.** Restate it in one line: which areas, and the depth (see
   [reading-list-guide.md](reading-list-guide.md)). A large area can be split into several
   lists, one per group of folders.
2. **Write the lists.** One subagent per list (Sonnet is enough; at most four at a time),
   each given [reading-list-guide.md](reading-list-guide.md) and its area. They write
   `docs/reading-lists/<area>.md` and `.tsv`. Read each list once: the folders exist, nothing
   is obviously already in the library, the reasons are concrete.
3. **Review.** Give Anton the list paths and the counts per folder, then wait. He strikes
   proposed papers by number and may move papers in from "Considered". Append those to the
   TSV with the next numbers and add them to the `.md` under "Added from Considered".
4. **Record the skips.** `scripts/reading-list-skips.py docs/reading-lists/<area>.md
   --strike <numbers> [--reason "..."]`, check the dry run, then rerun with `--write`. The
   struck and the considered papers go to `catalog/skipped.yaml`, so they are not proposed
   again.
5. **Add.** `scripts/add-batch.py docs/reading-lists/<area>.tsv`, in the background: about
   3–4 papers a minute, status saved per paper, so a rerun resumes and retries failures. Read
   only the failures and the closing counts. For `needs a PDF` rows, a subagent looks for an
   open PDF (author page, proceedings, institutional repository) and writes its local path
   into the row's `source` column; then rerun. ACM, Wiley, Springer, SSRN and OpenReview block
   scripts: ask Anton to download those in a browser. A paper that cannot be had is struck
   and recorded as in step 4, with that reason.
6. **Summaries.** `scripts/pending-summaries.py <scratchpad>/pending.md <folder> [...]`
   collects every paper without a summary under those folders, with its abstract. A subagent (Sonnet, about 150 papers each)
   reads only that file and the style of existing summaries in the folders, and writes
   `<number>\t<summary>` lines; then `scripts/apply-summaries.py <pending.md> <summaries.tsv>`.
   Check the numbers in a few summaries against the abstracts.
7. **Rebuild and check.** `scripts/build-index.py`, then `scripts/check-library.py`, which
   must pass. Spot-check two or three conversions, and list the papers that came from PDF
   text (`source: pdf-text`).
8. **Clean up.** Once every row of a list is `added`, `in library` or `struck`, delete its
   `.md` and `.tsv`: the papers carry their summaries and the skips are in the catalog.
9. **Report**: counts per area (added, struck, in library, from PDF text), anything left
   for Anton, and a suggested commit message. Never commit.

Work in one session at a time: two sessions running the same lists overwrite each other's
files.
