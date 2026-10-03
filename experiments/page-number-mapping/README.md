# Experiment · can every heading carry the PDF page it starts on?

**Question.** The markdown an agent reads is converted from arXiv's HTML, which has no pages; the
reader holds the PDF. Can each heading be given the page it starts on, `### 4.3 LongMemEval (p. 6)`,
from what the PDF itself records (named destinations, the bookmark outline) or by finding the
heading in the page text, without ever putting a wrong page on a heading?

**Status.** Measured 30 Sep 2026 over the 240 papers then in the library: **the shipped mapper adds
a page to 591 more headings in 100 papers and changes none**; afterwards **10,067 of 12,149 headings
(82.9%) carry a page: 99.6% of numbered headings (7,476 of 7,508) and 55.8% of unnumbered ones**.
Counted again 3 Oct 2026 over 2,202 papers: 83.0% overall, 99.1% of numbered headings. Five
iterations before the shipped one were each rejected on the regression below.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#page-numbers).

## Method

- **Corpus.** The 240 papers in the private library on 30 Sep 2026 (233 converted from arXiv HTML,
  7 from PDF text), each with its PDF. The papers and PDFs are not committed; the paper titles in
  the result files are.
- **The mapper.** [`page-map-49be320b.py`](page-map-49be320b.py) is `scripts/page-map.py` as
  measured and shipped (private-repo commit `49be320b`). It places a heading by, in order:
  1. **named destinations** — LaTeX with hyperref writes `section.4`, `subsection.4.3`,
     `appendix.A`; exact when present;
  2. **the PDF outline** (bookmarks) — added in this experiment, numbered headings only, matched
     in reading order to the next bookmark with the same section number;
  3. **text search** — from the previous placed page onward, skipping table-of-contents pages
     (five or more dot-leader lines), with unnumbered headings bounded by the next exactly placed
     heading.

  The current [`scripts/page-map.py`](../../scripts/page-map.py) has since added IEEE Roman
  numbering; the logic measured here is unchanged in it.
- **The defect that started it.** *Beyond Recall* (a report of more than 60 pages whose PDF
  has no LaTeX section anchors) had 24 headings stamped with p. 2, its table of contents, because the text
  search found each numbered title there first. Its PDF has a 132-entry outline with exact pages.
- **Regression harness.** [`pagemap_regress.py`](pagemap_regress.py) runs a candidate
  `page-map.py` over a copy of every paper and compares page numbers with the library's current
  ones: *gained* (a heading had none, now has one), *lost*, *moved*. A change ships only with
  nothing lost or moved, since a wrong page is worse than none.

  ```bash
  python3 experiments/page-number-mapping/pagemap_regress.py <dir with candidate page-map.py and paperlib.py>
  ```

  It needs the PDFs; it writes nothing to the library.
- **Coverage counter.** [`coverage.py`](coverage.py) counts headings with and without `(p. N)` in a
  library's markdown, numbered and unnumbered by `page-map.py`'s own rule, optionally by
  `source`. It reads markdown only, so it was run on 3 Oct 2026 over library snapshots taken from
  git at each commit:

  ```bash
  python3 experiments/page-number-mapping/coverage.py <library dir> --by-source --unplaced
  ```

- **What was changed when copying.** `pagemap_regress.py` took the private repo's `scripts/`
  directory as a hard-coded path and ran from inside it; it now takes that directory as its
  argument. Otherwise it is as run. The six runs' outputs are recovered from the session
  transcript, not from saved files (only run 1's output had been saved).

## Results

### The iterations

Each row is a cumulative change to the mapper, run over all 240 papers. The baseline is
destinations plus text search, as set up on 29 Sep.

| Run | Change | Gained | Lost | Moved | Papers changed | Outline used in |
|---|---|---|---|---|---|---|
| 1 | Outline for every heading (unnumbered matched by words); contents pages skipped | 64 | 18 | 29 | 35 | 49 papers |
| 2 | + a bookmark may not point before the last exactly placed heading | 59 | 11 | 19 | 28 | 39 |
| 3 | Outline for numbered headings only | 6 | 3 | 0 | 3 | 3 |
| 4 | + an unnumbered heading of five or more words may match anywhere in the page text | 579 | 3 | 0 | 101 | 3 |
| 5 | Long headings must start a line, and may wrap over the next three lines | 533 | 3 | 0 | 95 | 3 |
| **6** | **+ long headings searched up to the next exactly placed heading; hyphenated line breaks rejoined** | **591** | **0** | **0** | **100** | **3** |

What each rejection showed:

- **Runs 1–2: an unnumbered heading must not take a bookmark's page.** A paragraph heading shares
  its words with a bookmark for a different, later section. WildChat's "User Consent" occurs as a
  line on p. 2 and as a bookmark on p. 13; "Language." in HELM matches bookmarks on p. 35 and
  p. 141 and lines on eight pages. The moves inspected (WildChat, FollowBench, Reflexion, HELM,
  MemGuard) were all the outline overriding a correct text match; the full list is in
  [`regress-runs.txt`](regress-runs.txt).
- **Run 3: the outline is rarely needed.** Restricted to numbered headings it applies in 3 papers,
  but there it is the only source: it is what fixed *Beyond Recall* (134 headings placed, 0
  numbered unplaced, contents pages 2–5 skipped).
- **Run 4: matching anywhere is too loose.** Of its 579 gains, 528 matched at the start of a line
  and 51 elsewhere: inside figure text ("1st 5th 10th position of document with the answer…" for a
  *Lost in the Middle* finding heading) or mid-sentence where the heading's words are quoted.
- **Runs 5–6: the gain is long paragraph headings that wrap.** Bold run-in headings such as
  "Extended-context models are not necessarily better at using input context." span two or three
  PDF lines; requiring a line start and allowing the wrap kept the gains and dropped the false ones.
  The three "lost" in runs 3–5 were *Beyond Recall*'s own long appendix headings, which run 6
  recovered by searching further than two pages ahead and by rejoining a word hyphenated across
  lines ("Ab-" / "stention").

After run 6, no paper has a heading whose page is lower than the previous heading's (0 before, 0
after).

### Coverage

| Library | Papers | Headings with a page | Numbered | Unnumbered |
|---|---|---|---|---|
| 29 Sep, setup (`0cb6b27e`) | 238 | 9,293 of 11,943 (77.8%) | 7,302 of 7,340 (99.5%) | 1,991 of 4,603 (43.3%) |
| 30 Sep, before (`a60fa99`) | 240 | 9,442 of 12,149 (77.7%) | 7,441 of 7,508 (99.1%) | 2,001 of 4,641 (43.1%) |
| **30 Sep, after (`8a25d07a`)** | **240** | **10,067 of 12,149 (82.9%)** | **7,476 of 7,508 (99.6%)** | **2,591 of 4,641 (55.8%)** |
| 3 Oct (`23947512`) | 2,202 | 78,920 of 95,058 (83.0%) | 55,905 of 56,389 (99.1%) | 23,015 of 38,669 (59.5%) |

Between "before" and "after", 625 headings gained a page: 591 from run 6 and 34 in *Beyond Recall*,
remapped with the outline in commit `52b848cb` (which also corrected its 24 headings on p. 2). Per source on 3 Oct ([`coverage-23947512.txt`](coverage-23947512.txt)):

| Source | Papers | With a page | Numbered |
|---|---|---|---|
| `html` (page-map.py) | 1,909 | 81.6% | 99.1% |
| `pdf-text` (converter writes the page) | 277 | 100% | 100% |
| `web` (page-map.py on the printed page) | 16 | 68.9% | 0 of 6 |

So: **every numbered heading can be placed, bar a handful per thousand; an unnumbered one only
about half the time.** The unplaced unnumbered headings are mostly short ones ("Results",
"Dataset") that occur in running text too and are searched only two pages ahead, so the mapper
leaves them without a page rather than guess. Papers converted from the PDF have every page,
because the layout converter knows where each heading is.

The 32 numbered headings still unplaced on 30 Sep were in 5 papers, 21 of them in *Larimar*; on 3
Oct, 484 in 45 papers, concentrated in books and long tutorials (*Deep Reinforcement Learning, a
textbook* 148, *Introduction to Multi-Armed Bandits* 96). Why those fail was not investigated.

## Files

| File | Holds |
|---|---|
| [`page-map-49be320b.py`](page-map-49be320b.py) | the mapper as measured (run 6) |
| [`pagemap_regress.py`](pagemap_regress.py) | the regression harness |
| [`regress-runs.txt`](regress-runs.txt) | the six runs' summaries and lost/moved lists, plus the line-start and reading-order checks |
| [`coverage.py`](coverage.py) | the heading coverage counter |
| `coverage-<commit>.txt` | its output at the four commits in the table |

## Limits

- The regression compares against the library's previous page numbers, not against pages checked
  by hand. "Changed none" means the new mapper agrees with the old one wherever both place a
  heading; a page wrong in both would not show.
- The 591 gains were checked by rule (line start, reading order) and by reading the samples in
  `regress-runs.txt`, not one by one.
- One library, mostly recent ML papers built with LaTeX and hyperref, where destinations do most
  of the work.
