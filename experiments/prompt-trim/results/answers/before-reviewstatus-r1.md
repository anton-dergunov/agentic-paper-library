All six reviews cover every paper in their scope. The only problems are three broken figure links, which most likely come from this copy of the library rather than the reviews, and notes that are still missing in two areas.

## Reviews

| Review | Updated | Covered | Broken links | Missing notes |
|---|---|---|---|---|
| `llm/context` | 2026-10-06 | 20 / 20 | 2 | — |
| `llm/evaluation` | 2026-10-04 | 109 / 109 | 0 | — |
| `llm/foundation-models` | 2026-10-05 | 39 / 39 | 1 | — |
| `llm/memory` | 2026-10-01 | 70 / 70 | 0 | 42 papers |
| `llm/personalization` | 2026-10-01 | 70 / 70 | 0 | 35 papers |
| `llm/post-training` | 2026-10-05 | 111 / 111 | 0 | — |

None of the reviews needs an `update` for new papers.

- **Broken links:** they point to figures from *Lost in the Middle*, *Recursive Language Models* and *DeepSeek-V2*. They are the only figure links in any review, and this copy has no `images/` folders under `library/` at all. So the links are probably fine in the real library; run `paperlib review-status` there to confirm.
- **Missing notes:** `llm/memory` and `llm/personalization` were written before every paper got a note. `paperlib read llm/memory llm/personalization` would fill in the 77 notes, at roughly 4M tokens. That isn't urgent, but later updates and questions in these areas would rely on the notes. `llm/memory` also has 5 open conversion problems, none affecting key content.

## Scopes in the rollout with no review yet

- **`search-and-ranking` (127 papers): partly read.** 91 papers are read and 36 are left: the rest of `neural-ranking/` and all of `search-systems/`. The notes report 52 conversion problems that aren't in the catalog yet, and one catalogued problem (*Shallow pooling*) affects key content. Next steps:
  1. Read the remaining papers: `paperlib read search-and-ranking --focus reviews/.work/search-and-ranking/focus.md`
  2. Run `/fix-conversions search-and-ranking`
  3. Run `/literature-review search-and-ranking`
- **Not started:** `recommender-systems` and `experimentation-and-metrics` are next by priority. After them come `ml-systems`, the other 13 `llm/` subareas and the 15 other areas.

The plan in `docs/tasks/literature-review.md` matches all of this, and no review there is marked `checked` yet. I haven't changed any files, so there's no commit message.
