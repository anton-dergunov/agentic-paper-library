Four of the six written reviews are fully up to date. Two have broken links, but probably only in this copy of the library.

| Review | Updated | Papers covered | Broken links |
|---|---|---|---|
| `llm/context` | 2026-10-06 | 20 of 20 | 2 |
| `llm/evaluation` | 2026-10-04 | 109 of 109 | 0 |
| `llm/foundation-models` | 2026-10-05 | 39 of 39 | 1 |
| `llm/memory` | 2026-10-01 | 70 of 70 | 0 |
| `llm/personalization` | 2026-10-01 | 70 of 70 | 0 |
| `llm/post-training` | 2026-10-05 | 111 of 111 | 0 |

No review has papers it doesn't cover yet, so none needs an `update`.

**Broken links.** All three are embedded figures:
- `Lost in the Middle-fig01.svg` and `Recursive Language Models-fig02.webp` in the `llm/context` review.
- `DeepSeek-V2-fig04.webp` in the `llm/foundation-models` review.

This copy has no `images/` folders under `library/` at all, so the figures weren't copied over and the reviews themselves are probably fine. If the links also break in the main library, those figure files need to be regenerated.

**Memory and personalization notes.** The `llm/memory` and `llm/personalization` reviews were written before every paper got a note. The plan says 42 and 35 of their papers have none. Reading them, about 4M tokens, would make later questions and updates cheaper: `paperlib read llm/memory llm/personalization`

**Scopes without a review yet:**
- **`search-and-ranking` (127), being read:** 91 papers read and 36 left (the rest of `neural-ranking/` and all of `search-systems/`). After that come `/fix-conversions search-and-ranking` and then the review. The 91 notes report conversion problems in 46 papers; Shallow pooling has its key content broken.
- **Primary areas not started:** `recommender-systems` (97) and `experimentation-and-metrics` (71).
- **Rest of `llm/`:** `uncertainty-and-hallucination`, `safety-and-privacy`, `behaviour`, `agents`, `retrieval-augmented`, `reasoning`, `prompting-and-in-context`, `pretraining`, `architecture`, `efficiency`, `routing`, `text-analytics`.
- **Other areas:** `ml-systems` and all 15 other top-level areas (`data-centric-ml` through `research-practice`).

None of the six reviews is marked `checked` in the plan yet. Next is finishing the reading of `search-and-ranking`:
```
paperlib read search-and-ranking --focus reviews/.work/search-and-ranking/focus.md
```

Nothing changed, so there's nothing to commit.
