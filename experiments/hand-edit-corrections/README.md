# Experiment · Hand edits kept apart from the paper and applied again on reconversion

**Question.** A paper edited by hand was skipped by every reconversion (`<!-- hand-edited -->`), so it never got a later converter's fixes. Can the edits be stored apart from the paper and applied again, by a program, to a fresh conversion: how often, and how big are they?

**Status.** Run 19 Oct 2026 on the author's library (2,274 papers). **The library's hand edits are small: 25 markers in 17 papers (0.7%), 26 corrections once stored, 25K characters (0.01% of the library's markdown). Applied to today's conversion, the edits as captured when they were made are placed by the program in 27 of 29 cases: 17 by their text exactly, 1 by its landmarks among repeats, 7 by their landmarks where the converter had changed the text a little (all 7 the right place on inspection), 2 retired because the converter now makes the fix. The other 2 needed a session, both where the converter now rewrites the very text the edit fixed. No edit failed because of how its place was recorded.** Shipped: `paperlib corrections`, applied by `paperlib reconvert`; the 16 papers migrated.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md) (reconversion), ticket [`hand-edited-stale`](../../tickets/done/hand-edited-stale.md).

## The edits

17 papers carried 25 `hand-edited` markers (10 converted from PDF, 7 from arXiv's HTML). One, Confident Learning, is not an edit but a whole conversion from the paper's LaTeX source, made because arXiv's HTML lacks pages; it stays marked and skipped (ticket `html-incomplete`). The other 16 papers' edits, captured against their fresh conversion and reviewed, are 26 corrections in 15 papers:

| | Count |
|---|---|
| Replace converter text | 19 (15 of them a table, or rows of one) |
| Insert (the title moved to the top, a figure transcription, a caption) | 3 |
| Delete (a garbled second copy of a table, a duplicate caption) | 4 |
| Characters of corrected text | 25,621 (median 374, largest 5,724: PersonaMem's Figure 3 transcribed) |
| Share of the library's 241 MB of markdown | 0.01% |

Review dropped 7 runs the capture had taken beside a marker that were the converter's own later change, not the edit: captions the converter now writes better (bold titles, mathematics), Yahoo's Eq. (3), which the number-only fix of the same day now reads itself, and the crop that stood in for Figure 1 of "Memory in the Age of AI Agents", which the converter now downloads from arXiv whole. They are listed, with why, in `migrate.py`. That paper has no correction left.

## Where a correction applies

A correction stores the converter's text it replaces (`was`) and the corrected text (`now`), plus landmarks: the heading above, the first 80 characters of the lines before and after (`prev`, `next`), and its table, figure or equation label. Text is compared line by line after normalising whitespace, table-cell padding (a column the table writer right-aligns included), `(p. N)` markers and image alt text; landmarks also ignore emphasis. In order:

1. `was` found once: applied. Found several times: the occurrence whose landmarks agree.
2. `was` gone and `now` there: retired (the converter makes the fix).
3. Landmarks place a region at least 0.9 like `was`, or one bounded by both `prev` and `next` at least 0.5 like it: applied, recorded as drifted.
4. Otherwise stale: kept, and the paper says so under its conversion note.

Capture stores the smallest span: the changed lines of a block, joined when two rows apart at most (three lines; eight in an HTML table, whose row takes four), or a whole table when half its lines changed.

## Results

Two sets of corrections, each applied to a conversion it was not taken from:

- **then → fresh**: the edits as made (every commit that added a marker, diffed against the paper before it), applied to today's conversion. This is the situation a correction meets at its next reconversion.
- **fresh → older**: the edits captured against today's conversion, applied to the paper as converted before its first edit.

| Outcome | then → fresh | fresh → older |
|---|---|---|
| exact | 17 | 14 |
| landmarks (among repeats) | 1 | 3 |
| drifted (placed by landmarks) | 7 | 9 |
| obsolete (retired) | 2 | 5 |
| stale (needs a session) | 2 | 1 |
| all | 29 | 32 |

The 7 drifted matches of then → fresh, read one by one against the region they replaced: AdaGReS's algorithm (0.975; the converter now bolds its keywords), Command A's Tables 7 and 12 (0.901, 0.974; new bold), Continual Learning's Table 1 (0.998), Unbiased LambdaMART's Table 3 (0.847, bounded: the converter dropped an empty header row and still misaligns the values), Shallow Pooling's paragraph before Table 3 (0.953), Toward Activity Discovery's Table 4 (0.988). All 7 replaced the right text. Where the converter had improved that text (bold), the drifted correction puts the hand version back over it, which `paperlib corrections --drifted` lists for a look.

The 2 stale: "Memory in the Age of AI Agents" Figure 1, where the converter now has arXiv's image and the edit a crop from the PDF; Yahoo's Eq. (3), which was only its number when edited and which the converter now reads. Both are the case `/reapply-corrections` exists for: the converter and the edit both changed the same text. The one stale in fresh → older is that same Figure 1.

What the run found and fixed in the matching before these numbers: indentation inside a one-column table (AdaGReS's loop bodies) was lost by collapsing whitespace, while a right-aligned numeric column's padding (Interleaved Table II, headers included) looked like indentation, so leading space is kept only in one-column tables; image alt text changed ("Refer to caption" → ""); a caption's new bold title moved the landmark; a table's changed rows were split into 18 corrections (Continual Learning) until rows two apart were joined. An emphasis-only change beside a marked block was briefly dropped as drift, and the rule removed: Command A's hand edit bolds one of two values in a cell, which the converter cannot.

## Apparatus

`reapply.py` (the two sets and their outcomes; `results.txt`, `results.json`), `migrate.py` (the migration, with the review's drops). The fresh conversions were made in a scratch copy of the 16 papers, with the library's config, so the PDFs and the download cache were the library's:

```bash
paperlib reconvert --force --pdf-text --inline-math library --jobs 1 --state run.jsonl   # in the scratch copy, 33 min
PAPER_LIBRARY=~/papers uv run python reapply.py <scratch copy> --json results.json
PAPER_LIBRARY=~/papers uv run python migrate.py <scratch copy> --write
```

Paper text is not committed here (most of these papers are not openly licensed); the results hold paper names, places and outcomes.
