---
name: literature-review
description: Write or update the literature review of an area of the library — a narrative of the kinds of approaches, what the papers find, how they relate and where the evidence is weak, kept in reviews/<scope>.md for the reader to read and for agents to start from. Use for "literature review of llm/memory", "/literature-review search-and-ranking", "update the review of X", "I've added papers to X, update the review", "a year has passed, what's new in X", "which reviews are stale", "what's the state of research in X", and for reading an area into notes ahead of its review ("read llm/agents", "read 30 papers of X"). Not for single papers (that is overview).
model: opus
---

# /literature-review — the state of an area, from the papers here

A review is the synthesis of one area of the library: the reader reads it to learn the
state of research, and agents read it before opening papers, so the same papers aren't
re-read and the same points re-derived. `format.md` in this folder defines the file; read
it before writing. Read `AGENTS.md` (which imports `.claude/library-guide.md`) first if you
have not. Paths below are the defaults; `.claude/library-guide.md` has this library's.

**Scopes.** A review covers a folder in `catalog/topics.yaml` and everything under it:
usually one per top-level area, except an area too large for one review, which has one per
subarea (e.g. `llm/memory`, `llm/evaluation`, … under `llm/`). An area kept outside the
reader's interests (papers kept for fun, say) may have none. If the library keeps a review
plan (e.g. `docs/tasks/literature-review.md`), it holds the rollout order and its progress
while the first pass is running.

**Modes.** `read <scope> [N]` (read papers into notes, and stop), `write <scope>` (there is
no review yet), `update <scope>` (bring one up to date: new papers were added, or time has
passed) and `status`. With no mode, pick `write` or `update` by whether
`reviews/<scope>.md` exists.

**The pipeline.** A review is the last of three steps, and each step can run on its own:

```
paperlib read <scope>          notes, one request per paper; runs from a terminal too
/fix-conversions <scope>       fix the conversion problems the notes report; read again the
                               papers whose key content was broken
/literature-review <scope>     the review; reads what is missing, offers the fix first
```

**What it costs.** Reading is most of the work. `paperlib read` gives each paper to the
reading model in one request, about 35K tokens for a paper of ordinary length, so 100
papers come to a few million tokens and can use up a usage window. Reading is resumable
and its results are the notes, so it can be spread over several sessions (`read <scope>
30`), and the review written when `paperlib review-status <scope>` shows nothing left.
The measurements are in the engine's `experiments/review-token-cost` and
`experiments/reading-models`. Do not read papers with subagents: an agent keeps every
paper it has read in its context and pays for all of them again on each request.

## read

1. **Scope and progress.** `paperlib review-status <scope>` lists the papers that have no
   note yet. Say in one line how many are read and how many are left.
2. **Focus.** If `reviews/.work/<scope>/focus.md` does not exist, read the scope's folder
   indexes (`library/<scope>/**/README.md`) for titles and summaries, draft the themes the
   review will probably have and the questions it will ask of each paper (five to ten
   lines), and save them there. `reviews/.work/` is ignored by git.
3. **Read.** Run `paperlib read <scope> --focus reviews/.work/<scope>/focus.md`, with
   `--limit N` when a number of papers was asked for. Run it in the background and wait
   for it; it prints a line per paper.
   - Every paper is read in full: there is no skimming.
   - Exit code 3 means the account's usage limit was reached; the script prints the
     message with its reset time. The notes written so far are kept. Don't assume the
     limit still holds: the reader may switch accounts or pay with API credits. Say how
     many papers are left and when the limit resets, and ask whether to run the same
     command again now or later.
   - A paper that failed for another reason is reported with the error; try it once more
     alone (`paperlib read <paper.md>`).
4. **Papers whose results are in the appendix.** A note whose `evidence` line or digest
   says the main numbers are in an appendix was read without them. Read those again:
   `paperlib read --redo --appendix <paper.md> ...`.
5. **Report**: how many notes were written, how many papers are left, and the conversion
   problems the notes report (`paperlib review-status <scope>` counts them). If any have
   key content broken, suggest `/fix-conversions <scope>` before the review. In `read`
   mode, stop here.

## write

1. **Read** every paper of the scope, as above, until `paperlib review-status <scope>`
   lists none as not read.
2. **Conversion problems.** Run `paperlib conversion-issues <scope>`: it copies the
   problems the notes report into `catalog/conversion-issues.yaml` and lists the open ones.
   If any in the scope have key content broken (or have not been looked at yet: older
   notes never mark it), say how many and which matter most, and offer `/fix-conversions <scope>`
   before writing. Write once they are fixed or the reader says to go ahead; then,
   wherever the review leans on a paper whose key content is broken, say so.
3. **Context.**
   - Read the notes of every paper in scope (`notes/<stem>.md`): these are what the
     review is written from.
   - If `overview_dir` is configured (see `.claude/library-guide.md`), find the reader's own
     notes for them, with one `find <overview_dir> -name '*.md' -not -path '*/.*'` matched
     against the stems, and read those.
   - Read the reviews of neighbouring areas, if any exist, for the Connections section:
     their abstract, "Kinds of …" headings and Connections, not the whole file.
4. **Write** `reviews/<scope>.md` as `format.md` describes, from the notes.
   - Build the "Kinds of …" taxonomy from the notes' `family` lines and digests: find the
     few questions on which the approaches differ, then group the papers into families by
     their answers.
   - Take each finding's strength from the notes' `evidence` lines.
   - Open a paper again to check any claim the review leans on, and always before
     stating what a result means beyond what its note says: a note gives numbers
     faithfully, and their interpretation is where reviews go wrong.
   - Start the paper map from `paperlib review-status --links <scope>`. Mark a paper
     "(skimmed)" only if its note says `read: skim` (notes from before `paperlib read`).
   - Collect the disagreements between papers as you write the findings, for "Where the
     papers disagree".
   - Look up the exact page of each cited number in the note; never guess one.
   - Choose each diagram's type for what it shows, and use a paper's own figure where it
     explains better (`format.md`, "Diagrams and figures").
   - **Write the "In practice" section last**, when everything else is done: decide which
     one or two topics a practitioner relying on these papers would want recommendations
     on, derive them from the findings, and open with the provenance note (`format.md`,
     "The In practice section"). Skip it if the area has none.
5. **Check.**
   - `paperlib review-refs <scope>` turns the links into reference-style links.
   - `paperlib review-status <scope>` must show every paper covered and no broken links.
   - Run `paperlib build-index` (the folder indexes now link the review), then
     `paperlib check`, which must pass.
   - Delete `reviews/.work/<scope>/`.
   - If the library keeps a review plan (e.g. `docs/tasks/literature-review.md`), mark the
     scope as written there.
6. **Report.**
   - A link to the review and three or four lines on what the area looks like.
   - The number of conversion problems flagged, with the worst ones.
   - A commit message: the review, the new notes, the conversion issues. Never commit.
   - One line advising to discuss or correct the review in a new session: this one's
     context holds every note, and each later turn pays for it again.

## update

Two situations lead here, and the steps are the same:

- **The reader added papers** ("I've added some papers to X, update the review").
  `paperlib review-status` lists them as not covered.
- **Time has passed** ("a year has passed, what's going on in X"). The review only covers
  papers in the library, so first check how current the library is for the area. Look at
  the newest `published` dates in scope and at how many papers were added since the
  review's `updated` date. If few were, offer `/expand-library <scope>` to find the recent
  work first. Continue once the approved papers are added, or straight away if they
  decline.

Steps:

1. **Links and coverage.** Run `paperlib review-status --fix-links`; it lists links to
   renamed papers, which need a manual fix. Then run `paperlib review-status <scope>`,
   which lists the uncovered papers and which of them have no note yet. It also lists
   covered papers that have no note (reviews written before every paper got one): offer
   to read them, so that later questions and updates can use them.
2. **Format.** Compare the review with `format.md`. A review written under an older format
   gets what it lacks in this update: missing sections ("Where the papers disagree", "In
   practice"), evidence labels, source links in the comparison tables.
3. **Read** the uncovered papers: `paperlib read <scope>` reads the ones without a note
   (steps 3–4 of `read`). Then deal with conversion problems as in step 2 of `write`, and
   read the new notes.
4. **Revise** the review:
   - Place each paper in the map and in its family under "Kinds of …". When a paper that
     was skimmed has since been read in full (its note says `read: full`), drop its
     "(skimmed)" mark. A new family gets
     its own subsection and a row in the side-by-side table.
   - History: add a period for the new papers; don't rewrite the old ones.
   - Findings: when new evidence changes a finding, rewrite it and say in place what
     changed ("until 2026 …; the 2027 papers show …"). Add new findings, and update each
     **How strong the evidence is** line and its labels.
   - "Where the papers disagree": add new disagreements, and mark the ones the new papers
     settle.
   - Comparison tables, open questions (mark what is now resolved), where to start
     reading (swap in a newer paper if it is now the better entry point) and connections.
   - The "In practice" section, last: re-derive the recommendations from the revised
     findings, update the date in its provenance note, and add the section if the review
     predates it.
   - The abstract, if the state of the area has changed.
   - Fold the lasting points from `## Q&A` into the narrative, and remove them there.
5. **Log.** Add a line to `## Updates` saying what came in and what changed, and bump
   `updated`.
6. **Check** as in write, step 5.
7. **Report.**
   - A link to the review.
   - **What changed since <previous updated date>**, a few lines for the reader: new kinds of
     approaches, findings overturned or strengthened, and the two or three new papers to
     read first.
   - Any conversion problems flagged.
   - A commit message. Never commit.

## status

`paperlib review-status`: for each review, list the papers not yet covered and the broken
links. Also list the scopes in the rollout (the review plan, if the library keeps one) that
have no review yet. Recommend `update` for reviews with several uncovered papers.

## Iterating on this skill

The reader refines the format as they read the reviews. When they correct one, apply the
correction to the review and, if it is a general rule, to `format.md` or this file as well.
