---
name: literature-review
description: Write or update the literature review of an area of the library — a narrative of what its papers find, how they relate and where the evidence is weak, kept in reviews/<scope>.md for Anton to read and for agents to start from. Use for "literature review of llm/memory", "/literature-review search-and-ranking", "update the review of X", "which reviews are stale", "what's the state of research in X" when no review exists yet. Not for single papers (that is overview).
---

# /literature-review — the state of an area, from the papers here

A review is the synthesis of one area of the library: Anton reads it to learn the state of
research, and agents read it before opening papers, so the same papers aren't re-read and
the same points re-derived. `format.md` in this folder defines the file; read it before
writing. Read `AGENTS.md` first if you have not.

**Scopes.** A review covers a folder in `catalog/topics.yaml` and everything under it: one
per top-level area, except `llm/`, which has one per subarea (`llm/memory`,
`llm/evaluation`, …). `curiosities` has none. The rollout order and its progress are in
`docs/tasks/literature-review.md` while the first pass is running.

**Modes.** `write <scope>` (there is no review yet), `update <scope>` (bring one up to
date) and `status`. With no mode, pick by whether `reviews/<scope>.md` exists.

## write

Reading an area takes many papers, so it is split into batches that can run in different
sessions or agents. Their results are kept in `reviews/.work/<scope>/` (ignored by git)
until the review is written.

1. **Scope and progress.** `scripts/review-status.py <scope>` lists the papers and which of
   them earlier batches have read. If some are read, say so in one line and continue from
   the remaining ones.
2. **Context.**
   - Read the scope's folder indexes (`library/<scope>/**/README.md`) for titles and
     summaries.
   - Read the existing `notes/<stem>.md` for papers in scope.
   - Find Anton's Obsidian notes for them, with one `find ~/obsidian -name '*.md' -not -path
     '*/.*'` matched against the stems, and read those.
   - Read the reviews of neighbouring areas, if any exist, for the Connections section.
3. **Triage.**
   - From the summaries, draft the themes the review will probably have.
   - Mark the papers to read in full, about a third: the surveys, the seminal papers, the
     main benchmarks, the papers a theme rests on, and the most recent strong results.
   - Split the remaining papers into batches of about 15, one subfolder per batch where
     possible.
4. **Read**, with one general-purpose subagent per batch, several in parallel. Give each
   the prompt in "Reading batches" below. Each writes `reviews/.work/<scope>/batch-NN.md`
   and the `notes/` digests of its full reads, paper by paper. If an agent or the session
   stops (a usage limit, for instance), the sections written so far are kept. Resume the
   agent if it is still reachable; otherwise the next run starts again at step 1 and reads
   only the papers that are left.
5. **Collect conversion problems.** Copy every `conversion:` problem from the batches into
   `catalog/conversion-issues.yaml` (`paper`: the stem, `problem`, `found`). Don't fix the
   papers; that is a separate pass.
6. **Write** `reviews/<scope>.md` as `format.md` describes, from the batch digests.
   - Open a paper again only to check a claim the review leans on.
   - Start the paper map from `scripts/review-status.py --links <scope>`.
   - Look up the exact page of each cited number in the digest; never guess one.
7. **Check.**
   - `scripts/review-status.py <scope>` must show every paper covered and no broken links.
   - Run `scripts/build-index.py` (the folder indexes now link the review), then
     `scripts/check-library.py`, which must pass.
   - Delete `reviews/.work/<scope>/`.
   - Mark the scope as written in `docs/tasks/literature-review.md`.
8. **Report.**
   - A link to the review and three or four lines on what the area looks like.
   - The number of conversion problems flagged, with the worst ones.
   - A commit message: the review, the new notes, the conversion issues. Never commit.

### Reading batches

The subagent prompt has these parts. Fill in the list of papers and the batch number.

> You are reading papers from Anton's research library for a literature review of
> `<scope>`. Read `AGENTS.md` (paper files, links) and `notes/README.md` (digest format).
>
> Papers: <paths, each marked full or skim>.
>
> - **Skim** papers: read the abstract, the introduction, the conclusion, and the
>   headline results table.
> - **Full** papers: read the main text up to the references; skip the appendix unless the
>   main results live there.
> - Promote a skim paper to full if it turns out to be central.
>
> For each full paper, write `notes/<stem>.md` in the `notes/README.md` format. If the file
> exists, merge into it and keep its Q&A.
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

1. `scripts/review-status.py --fix-links` (it lists links to renamed papers, which need a
   manual fix), then `scripts/review-status.py <scope>` for the uncovered papers.
2. Read the uncovered papers (their `notes/` digest first, if there is one), as reading
   batches when there are more than a few.
3. Add each paper to the paper map. Revise the findings, the comparison and the history
   where it changes them, and mark what it overturns.
4. Fold the lasting points from `## Q&A` into the narrative and remove them from there.
5. Bump `updated`, then check and report as in write (steps 5, 7 and 8).

## status

`scripts/review-status.py`: for each review, list the papers not yet covered and the broken
links. Also list the scopes in the rollout that have no review yet. Recommend `update` for
reviews with several uncovered papers.

## Iterating on this skill

Anton refines the format as he reads the reviews. When he corrects one, apply the
correction to the review and, if it is a general rule, to `format.md` or this file as well.
