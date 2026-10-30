# Task: every paper's type in its frontmatter, always filled

A paper's type (`method`, `survey`, `benchmark`, `study`, `system`, `position`, `theory`) tells a reader what kind of paper it is before they open it. Carrel shows it as an icon on every row of the library and filters by it, so it has to be in one place, and on every paper. Today it is in two places, and on four papers in five.

## The facts

Measured on 30 Oct 2026 on the author's library of 2,275 papers:

- **1,819 papers** have a type only as the `type:` line of their note (`notes/<stem>.md`, above `## Digest`). `paperlib read` writes it, in one Opus request that reads the whole paper. They are 985 method, 289 study, 188 benchmark, 144 system, 140 survey, 37 theory and 36 position. `paperlib.note_fields()` reads them.
- **5 papers** have it in their frontmatter, through `paperlib set-type`, which the overview skill runs.
- **456 papers** have no note, and so no type.
- **Filing** (`paperlib add`) makes one request, Sonnet by default, from the title and the abstract. It answers the folder, a reason and the summary, not the type.
- **`paperlib info`** already asks a model for a type, from the abstract (`guide/info-prompt.md`): a baseline.
- **The checks**: `check-library` rejects an unknown type but accepts none, and the guide calls the field optional.

## The experiment: `experiments/paper-type/`

**The question.** Can a cheap request at filing time, from the title, the summary and the abstract, find the type the whole-paper reading finds? If it can, every paper gets its type when it is filed, and the notes' types become a check on it rather than its source.

- **Gold**: the 1,819 notes' types. They come from reading the whole paper, but are one model's call: where a candidate disagrees, read a few by hand before blaming it. `method` against `system`, and `study` against `benchmark`, are the borders to expect.
- **Sample**: 30 papers a type, drawn at random (all of them where a type has fewer), about 210 papers. The whole 1,819 only if the sample leaves the choice open.
- **Candidates**:
  - the filing request with a `type` field added to its JSON (Sonnet; no extra request);
  - one Haiku request from the title, the summary and the abstract, as the backfill would make it;
  - `paperlib info`'s type, as the baseline.
- **Report**: accuracy, precision and recall by type, the confusion matrix, tokens and dollars a paper, and the disagreements read by hand. Write-up, apparatus and results in the format of [experiments/README.md](../../experiments/README.md), and a row in its table.
- **Decides**: which request types a paper at filing and in the backfill. If none agrees well enough (the disagreements read by hand decide what "well enough" is), the papers without a note get theirs from `paperlib read` instead, and filing leaves the type empty until then.

## The transition

1. **One place: the frontmatter's `type`.**
   - Filing writes it, through the request the experiment chooses.
   - `paperlib read` writes it too, from the note's `type:` line, since a whole-paper reading is the better evidence: it replaces the filing's type when they differ, and says so in its output.
   - The overview skill's `set-type` stays.
   - Whether the note keeps its `type:` line is decided here, after the experiment. Dropping it leaves one copy; keeping it records what the reading said when it differs from the filing.
2. **The backfill**, one command, run once on the library and safe to run again:
   - copy the type from the note where there is one (1,819 papers, no model);
   - classify the others (456) with one request each, from the title, the summary and the abstract;
   - leave a type already in the frontmatter alone, and print what it changed. `git diff` in the library shows the rest.
3. **The prompts**: the filing prompt and the reading prompt both always choose a type, told to pick the closest one when the paper is mixed or unclear.
4. **The checks**: `REQUIRED` gains `type`, so `check-library` requires it; the guide says it is required. The example library's papers get their types, and `paperlib test` passes.
5. **Afterwards**: carrel reads the frontmatter's type and falls back to `note_fields()` until this lands; then the fallback goes. `note_fields()` stays, for `family` and `evidence`.

Done when `check-library` passes on the author's library with `type` required; then record the decision in [design.md](../design.md#decisions-log) and delete this file.
