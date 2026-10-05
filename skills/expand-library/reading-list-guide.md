# Writing a reading list

For one area of the library, find the papers that should be in it and are not, so that the
reader can strike what they do not want and the rest can be added. One list per area, kept
in the library: `docs/reading-lists/<area>.md` for reading and `<area>.tsv` next to it for
`paperlib add-batch`. Paths below are the defaults; `.claude/library-guide.md` has this
library's.

## What to look for

- **Seminal papers**: the ones a practitioner in the area is expected to know, that the rest of
  the field builds on or measures against.
- **Important recent work** from the last two years: papers that changed practice, set a new
  standard, or are widely used as baselines and benchmarks. Search the web; don't rely on memory
  for recent work.
- **Surveys** that map a folder well, at most one or two per folder, the best and most recent.
- **Industry papers** where they are the reference for how a thing is done at scale (e.g. YouTube,
  Pinterest, LinkedIn, Microsoft, Netflix, Spotify, Meta, Google papers on search, ranking,
  recommendation and experimentation).

Depth: for the reader's primary areas (see `AGENTS.md` for their focus) aim for 30–60 papers
per area; for the others, 5–15 per area. Fewer strong papers beat a padded list.

## What to leave out

- Anything already in the library. Read the area's indexes (`library/<area>/README.md` and the
  README of every folder below it) first, and check each candidate with
  `paperlib lookup <id>`, which prints `already in library`.
- Anything in `catalog/skipped.yaml`; `paperlib lookup` prints `skipped earlier`.
- Outdated or superseded work, incremental variants, and papers with little uptake. List the
  notable ones you considered and rejected, with the reason, in the "Considered, not proposed"
  section, so they are recorded and not proposed again.
- Books, courses and talks. A paper published only as a web article (Distill,
  transformer-circuits.pub) is fine, and so is an engineering blog post when it is the
  reference write-up of a method or system that has no paper (Netflix's recommendation
  foundation model, Meta's GEM); give its URL. Ordinary blog commentary is left out.

## Verifying

- Every arXiv candidate must be checked with `paperlib lookup --no-abstract <id> [...]`,
  about 20 ids per call (longer calls can stop after the first entry). Use the id and title it
  prints. A paper not on arXiv gets its best stable URL (publisher DOI, ACL Anthology, PMLR,
  author PDF).
- The target folder must be a folder in `catalog/topics.yaml`; read its scope line. If a
  candidate fits no folder, say so in the list rather than inventing a folder.

## Output

`docs/reading-lists/<area>.md`:

```markdown
# Reading list: <area>

<one paragraph: what the area already has, what the list adds, and the gaps it fills>

## Proposed

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | Title | 2024 | 2401.12345 | <folder> | one line: what it is and why it belongs |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
```

Number the proposed papers continuously; group them by folder.

`docs/reading-lists/<area>.tsv`, one line per proposed paper, no header, tab-separated:
`number, arxiv id (or empty), url (or empty), title, year, folder, source`. `source` is `web`
for a web article or blog post, and empty otherwise.

Do not add papers to the library, edit the catalog, or touch any other file.
