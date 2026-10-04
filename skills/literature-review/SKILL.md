---
name: literature-review
description: Write or update the literature review of an area of the library — a narrative of the kinds of approaches, what the papers find, how they relate and where the evidence is weak, kept in reviews/<scope>.md for the reader to read and for agents to start from. Use for "literature review of llm/memory", "/literature-review search-and-ranking", "update the review of X", "I've added papers to X, update the review", "a year has passed, what's new in X", "which reviews are stale", "what's the state of research in X". Not for single papers (that is overview).
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

**Modes.** `write <scope>` (there is no review yet), `update <scope>` (bring one up to
date: new papers were added, or time has passed) and `status`. With no mode, pick by
whether `reviews/<scope>.md` exists.

## write

Reading an area takes many papers, so it is split into batches that can run in different
sessions or agents. Their results are kept in `reviews/.work/<scope>/` (ignored by git)
until the review is written.

1. **Scope and progress.** `paperlib review-status <scope>` lists the papers and which of
   them earlier batches have read. If some are read, say so in one line and continue from
   the remaining ones.
2. **Context.**
   - Read the scope's folder indexes (`library/<scope>/**/README.md`) for titles and
     summaries.
   - Read the existing `notes/<stem>.md` for papers in scope.
   - If `overview_dir` is configured (see `.claude/library-guide.md`), find the reader's own
     notes for them, with one `find <overview_dir> -name '*.md' -not -path '*/.*'` matched
     against the stems, and read those.
   - Read the reviews of neighbouring areas, if any exist, for the Connections section.
3. **Triage.**
   - From the summaries, draft the themes the review will probably have.
   - Mark the papers to read in full, about a third: the surveys, the seminal papers, the
     main benchmarks, the papers a theme rests on, and the most recent strong results.
   - Split the remaining papers into batches of about 15, one subfolder per batch where
     possible.
4. **Read**, with one general-purpose subagent per batch, several in parallel. Give each
   the prompt in "Reading batches" below. Each writes `reviews/.work/<scope>/batch-NN.md`
   and a `notes/` digest for every paper it reads, full or skim, paper by paper. The
   batch files are deleted at the end; the notes are what later sessions keep. If an agent or the session
   stops (a usage limit, for instance), the sections written so far are kept. Resume the
   agent if it is still reachable; otherwise the next run starts again at step 1 and reads
   only the papers that are left.
5. **Collect conversion problems.** Copy every `conversion:` problem from the batches into
   `catalog/conversion-issues.yaml` (`paper`: the stem, `problem`, `found`). Don't fix the
   papers; that is a separate pass.
6. **Write** `reviews/<scope>.md` as `format.md` describes, from the batch digests.
   - Build the "Kinds of …" taxonomy from the digests' `family` and `mechanism` lines:
     find the few questions on which the approaches differ, then group the papers into
     families by their answers.
   - Open a paper again only to check a claim the review leans on.
   - Start the paper map from `paperlib review-status --links <scope>`, and mark the
     skimmed papers "(skimmed)" from the digests' `read:` lines.
   - Collect the disagreements between papers as you write the findings, for "Where the
     papers disagree".
   - Look up the exact page of each cited number in the digest; never guess one.
   - Choose each diagram's type for what it shows, and use a paper's own figure where it
     explains better (`format.md`, "Diagrams and figures").
   - **Write the "In practice" section last**, when everything else is done: decide which
     one or two topics a practitioner relying on these papers would want recommendations
     on, derive them from the findings, and open with the provenance note (`format.md`,
     "The In practice section"). Skip it if the area has none.
7. **Check.**
   - `paperlib review-refs <scope>` turns the links into reference-style links.
   - `paperlib review-status <scope>` must show every paper covered and no broken links.
   - Run `paperlib build-index` (the folder indexes now link the review), then
     `paperlib check`, which must pass.
   - Delete `reviews/.work/<scope>/`.
   - If the library keeps a review plan (e.g. `docs/tasks/literature-review.md`), mark the
     scope as written there.
8. **Report.**
   - A link to the review and three or four lines on what the area looks like.
   - The number of conversion problems flagged, with the worst ones.
   - A commit message: the review, the new notes, the conversion issues. Never commit.

### Reading batches

The subagent prompt has these parts. Fill in the list of papers and the batch number.

> You are reading papers from a research-paper library for a literature review of
> `<scope>`. Read `AGENTS.md` and the `.claude/library-guide.md` it imports (paper files,
> links, and the notes format for digests).
>
> Papers: <paths, each marked full or skim>.
>
> - **Skim** papers: read the abstract, the introduction, the conclusion, and the
>   headline results table.
> - **Full** papers: read the main text up to the references; skip the appendix unless the
>   main results live there.
> - Promote a skim paper to full if it turns out to be central.
>
> For every paper, write `notes/<stem>.md` in the notes format from
> `.claude/library-guide.md`, with `read: full` or `read: skim`. A skim's digest is
> shorter: the claim, the mechanism, the evidence and its strength, and the numbers with
> pages. If the file exists, merge into it and keep its Q&A; never replace a `read: full`
> digest with a skim.
>
> Write `reviews/.work/<scope>/batch-NN.md`. It starts with `# Batch NN` and has one
> section per paper, headed `## <stem>` (the filename without `.md`, exactly). **Append
> each paper's section (and write its notes file) as soon as you have read that paper**,
> not at the end, so that work survives if you are stopped. If the file already has a
> section for a paper, that paper is done; skip it.
>
> ```
> ## <stem>
> - read: full | skim
> - pdf: <the pdf.invalid base for this paper>
> - kind: method | survey | benchmark | study | system | position | theory
> - claim: <what it does or finds, one sentence>
> - family: <the kind of approach it belongs to, in a few words (e.g. "extract-and-
>   consolidate pipeline", "graph memory"); name a new one if none fits>
> - mechanism: <how, in two plain sentences>
> - evidence: <what it was tested on, against what>; strength: <replicated / one benchmark /
>   vendor-run / no ablations / …>
> - numbers: <the 1–3 results that matter, each with its baseline and (p. N, Table M)>
> - relates: <other papers here it builds on, compares with or contradicts, with how>
> - conversion: ok | <what is broken, where (p. N)>
> ```
>
> **Check the conversion as you read.** Flag garbled or missing equations, tables flattened
> into text, missing figures or sections, a truncated body, page markers that don't match
> the text, and numbers in a `source: pdf-text` paper that look wrong. When numbers are
> affected, say so under `numbers`. Don't edit the paper.
>
> Reply with one line per paper: its stem, full or skim, and conversion ok or the
> problem.

## update

Two situations lead here, and the steps are the same:

- **The reader added papers** ("I've added some papers to X, update the review").
  `paperlib review-status` lists them as not covered.
- **Time has passed** ("a year has passed, what's going on in X"). The review only covers
  papers in the library, so first check how current the library is for the area. Look at
  the newest `published` dates in scope and at how many papers were added since the
  review's `updated` date. If few were, offer `/literature-pass <scope>` to find the recent
  work first. Continue once the approved papers are added, or straight away if they
  decline.

Steps:

1. **Links and coverage.** Run `paperlib review-status --fix-links`; it lists links to
   renamed papers, which need a manual fix. Then run `paperlib review-status <scope>`,
   which lists the uncovered papers and, if a reading pass is under way, which of them are
   still unread.
2. **Format.** Compare the review with `format.md`. A review written under an older format
   gets what it lacks in this update: missing sections ("Where the papers disagree", "In
   practice"), evidence labels, source links in the comparison tables.
3. **Read** the uncovered papers. Read their `notes/` digest first, if there is one. For
   more than a few papers, use reading batches with the prompt above, kept in
   `reviews/.work/<scope>/`.
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
6. **Check** as in write: steps 5 and 7.
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
