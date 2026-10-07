# Task: retire `read: skim`

The first literature reviews read most papers as skims (abstract, introduction, conclusion and headline results), because their reading agents paid again for every paper already in their context. Since `paperlib read` reads every paper in full, one request each, no new skim is written. The concept stays only for the old notes, and it costs words in every session: the guide explains `read: skim`, `read-papers.py` has `--skims`, `review-status` counts skims, and the literature-review skill and its format have the "(skimmed)" mark.

On 7 Oct 2026 the author's library held 152 skim notes (llm/evaluation 70, llm/post-training 61, llm/foundation-models 21), and its five reviews 230 "(skimmed)" marks.

## Steps

1. Read the skimmed papers in full, an area at a time: `paperlib read --skims <scope>`. At about $0.36 a paper with Opus (the reading prompt's instructions and related list now come from the prompt cache after the first paper), the 152 papers come to about $55, roughly one and a half 5-hour windows.
2. `/literature-review update <scope>` for the three reviews: it drops the "(skimmed)" marks of papers now read in full, and the finding that leaned on a skim gets checked against the full note.
3. Check that no note says `read: skim` and no review has "(skimmed)".
4. Remove the concept from the engine: the `read: skim` paragraph of `guide/library-guide.md` (and `read:` from the note format, if `full` is then the only value), `--skims` and the depth in `read-papers.py`, the skim count in `review-status.py`, and the "(skimmed)" rules in `skills/literature-review/SKILL.md` and `format.md` (the paper-map example and the In practice provenance note).
5. Run `paperlib test` and `paperlib build-index` in `examples/library`.

Done when the library has no skim and the engine no longer mentions one.
