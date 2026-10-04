# Experiment · can the whole library be regenerated with the current converter without losing text?

**Question.** When the converters improve, every existing paper can be converted again from its
cached sources. Doing that to about 2,200 papers at once: how long does it take, does it fix what
the old conversions got wrong, does it lose anything, and what checks are needed to trust the result?

**Status.** Run 1–2 Oct 2026, numbers re-derived from git and the run logs 3 Oct 2026: **1,904
arXiv-HTML papers in 2 hours with 3 jobs and 277 PDF-only papers in 6.9 hours one at a time; papers
showing a conversion symptom fell from 1,370 to 362; one paper actually lost text (SCULPT, 2,318
words, fixed the same morning); 80 papers lack 3 or more PDF pages because arXiv's HTML lacks
them, and the 27 worst were catalogued; 6 of 9 spot-checked PDF equations were right.** The
word-shrink check flagged 7 papers, but 6 of the 7 flags were errors in the check itself (fixed 4 Oct).

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#reconversion)

## Method

- **Corpus.** The whole library as it stood on `main` before the run (commit `4b0e0bc5` in the
  private library repository): 2,200 papers, of which 1,905 were converted from arXiv's HTML, 279
  were PDF-only and 16 were web articles. Pilots had already been run on `main`: the 25 papers then
  in `catalog/conversion-issues.yaml` and the 71 papers of `llm/personalization`.
- **What changed in the converters** (1 Oct): the arXiv-HTML converter learned to keep boxed text
  and prompt templates as quotes, to keep scaled tables and header rows, and to handle `forest`
  trees, figure links, siunitx numbers and citations rebuilt from the `.bib`. The PDF converter was
  replaced: docling's layout analysis for headings, tables and figures, and marker's model for
  display equations, in place of the PDF's plain text layer.
- **The run.** It ran overnight in a separate git worktree, so other sessions could keep working
  on `main`, with `scripts/reconvert.py`. Downloads were cached under `~/.cache/papers/`, so a rerun
  needs no network:

  ```sh
  caffeinate -i sh -c '
    python3 scripts/reconvert.py --all --jobs 3 --state ~/.cache/papers/reconvert-pass2.jsonl;
    python3 scripts/reconvert.py --all --jobs 3 --state ~/.cache/papers/reconvert-pass2.jsonl;
    python3 scripts/reconvert.py --all --pdf-text --state ~/.cache/papers/reconvert-pdf.jsonl'
  ```

  The second line retries what the first left `failed` or `partial`. The third converts the
  PDF-only papers the quick way: structure, tables, figures and display equations, but not inline
  mathematics. An earlier pass the same evening, with the converter from before the evening's
  fixes, was stopped by hand once those fixes landed. Its state file is kept for its throughput
  only.
- **Validation.** A session the next morning followed a written checklist: the run's outcomes, the
  converter tests, the symptom counts (`scripts/conversion-symptoms.py --counts`), the papers whose
  text shrank (`scripts/conversion-symptoms.py --compare main`, 5% threshold), and spot checks
  against the PDFs. It also added checks of its own: words that disappeared at any threshold,
  coverage of each PDF page, and coverage of arXiv's HTML. The bugs it found were fixed, with a
  test for each, and the papers they affected were converted again. The result was committed as
  `f8056ad3`.
- **Re-derivation** (3 Oct, this folder). The markdown and SVG files at `4b0e0bc5` (before),
  `1b6f6dbe` (the nightly result) and `f8056ad3` (after the fixes) were extracted with
  `git archive`, and the final symptom checker was run over each copy. [`before_after.py`](before_after.py)
  and [`pdf_words.py`](pdf_words.py) compare the copies, and [`runs.py`](runs.py) summarises the
  state files. No conversion was run again.

  ```sh
  # in each extracted copy <c>/, with the checker from f8056ad3
  LIBRARY_DIR=<c>/library python3 scripts/conversion-symptoms.py > symptoms-<c>.tsv
  python3 before_after.py 4b0e0bc5/library f8056ad3/library symptoms-before.tsv symptoms-after.tsv > before-after.json
  python3 pdf_words.py 4b0e0bc5/library f8056ad3/library > pdf-words.txt
  python3 runs.py state/reconvert-pass2.jsonl --split 2026-10-02T02:05:05 > runs-pass2.json
  python3 runs.py state/reconvert-pdf.jsonl --split 2026-10-02T09:16:50 2026-10-02T09:19:41 > runs-pdf.json
  python3 runs.py state/reconvert-2026-10-01.jsonl --split 2026-10-01T20:53:11 > runs-pass1.json
  ```

  The validation's own scripts are run from the root of a library checkout, with the engine's
  scripts in `scripts/`. For example: `python3 pages.py pages.json`,
  `python3 incomplete.py pages.json incomplete.json`,
  `python3 htmlcov.py pages.json <state.jsonl>`, `python3 pdfcov.py`,
  `python3 spot.py spot-html.txt`.

Caveats:

- Times are local (BST) and come from the state files. Each line records when a paper finished,
  not when it started, so the time of an invocation runs from its first record to its last and
  leaves out the first paper.
- Symptoms are regular expressions over the markdown. They count papers that show a known
  failure, not every failure. `empty-header` cannot tell a broken header from a table whose
  source has no header rule.
- The spot checks cover ten HTML papers and ten PDF papers, drawn with `random.seed(20261002)`,
  and nine equations. They indicate rates; they do not measure them.

## Results

### The run

| Pass | Records | Converted | Other outcomes | Wall clock | Rate |
|---|---|---|---|---|---|
| pilot, `llm/personalization` (1 Oct) | 71 | 67 | 4 skipped | 3 min | — |
| first pass, previous converter, `--jobs 3` (stopped) | 1,337 | 1,180 | 157 skipped | 127.5 min | 555 papers/h |
| **arXiv HTML, `--jobs 3`** | **2,200** | **1,904** (16 `partial`) | 296 skipped | **119 min** | **960 papers/h** |
| retry of failures | 16 | 16, still `partial` | — | 4.1 min | — |
| **PDF-only, one at a time** | **277** | **276** | 1 failed | **414 min** | **40 papers/h** |
| retry of the failed paper (morning) | 2 | 1 | 1 failed | — | — |

- **arXiv HTML.** That is 3.75 s of wall clock per paper with three workers. Most of the time
  goes to re-encoding figures; downloads were needed only for papers not yet cached, about 840
  by the task's estimate (not measured). The 296 papers skipped were 277 PDF-only papers, 16 web
  articles and 3 papers edited by hand. Two papers that had been PDF-only now had an arXiv
  rendering and became HTML papers.
- **Partial.** All 16 `partial` papers have figures that arXiv does not serve: between 1 and 127
  per paper, and a retry does not help. They still link to arXiv and make up the 16 `figure-link`
  symptoms below.
- **PDF-only.** Per paper: median 52 s, mean 90 s, 90th percentile 178 s. The slowest was the
  International AI Safety Report 2026 (32 min, 111,213 words), where the equation model failed,
  so text with lost symbols was kept as it was. Next came The Algorithmic Foundations of
  Differential Privacy (14.5 min, 98,916 words). The run wrote 3.2 million words, median 9,516
  per paper.
- **The one failure** was "Canaries in the Coal Mine". OpenCV's resize segfaults inside docling's
  OCR stage, on some attempts only. Three of five attempts crashed (crash reports at 02:10, 09:12
  and 09:16); a direct run at 09:13 and a retry at 09:19 succeeded. The installed OpenCV was
  already the newest release.

### Symptoms before and after

Papers converted from arXiv HTML that show each symptom, counted with the final checker:

| Symptom | Before (`4b0e0bc5`) | Nightly (`1b6f6dbe`) | After fixes (`f8056ad3`) |
|---|---|---|---|
| **papers with any symptom** | **1,370** | 362 (365 with that day's checker) | **362** |
| `empty-header`: pipe table with an empty header row | 1,213 | 336 | 336 |
| `box`: a boxed text left as an image | 283 | 1 (7) | 1 |
| `figure-link`: a figure still linked to arXiv | 192 | 16 | 16 |
| `flat-table`: a line of 25+ numbers | 113 | 21 | 20 |
| `badge` | 43 | 0 | 0 |
| `pt-residue`: a TeX length left in an equation | 33 | 2 | 2 |
| `forest`: an empty tree | 29 | 1 | 1 |
| `raw-citations` | 5 | 3 | 3 |
| `digit-groups` | 4 | 0 | 0 |
| `macro` | 1 | 0 | 0 |

Of the 1,905 papers present as HTML papers in both copies, 1,012 went from a symptom to none, 358
kept one, 533 had none before or after, and 2 gained one. Both of those gained an `empty-header`:
Chain of Thought Monitorability, and Neural Collaborative Filtering vs. Matrix Factorization
Revisited. Six papers show a symptom they did not show before, and in the other four it came
with the fix of an older one: in two, a flattened table became a table with an empty header; in
Geometric Deep Learning, a box and a TeX length gave way to an empty-header table; in Visual
Instruction Tuning, a box became quoted text that the `flat-table` rule now matches.

- **The 6 `box` flags that the final checker drops on the nightly copy** (7 → 1, taking 3 papers
  off the list, 365 → 362) were the checker's error. It flagged a diagram that already carried its text as a quote beneath it.
- **Remaining `empty-header`** tables are expected: when a table has no rule under its header,
  the source gives no cue for one.
- **The 20 `flat-table` lines** were read one by one. Most are prose dense with numbers, or
  coordinates in a prompt, and not tables. One is TikZ source that arXiv's HTML shows as text
  ("Real numbers, data science and chaos"), and it was catalogued. The validation fixed the
  scaled-table bug.

The "1,618 papers" in the task file is a different number. It was counted on 1 Oct, before the
pilots, by an earlier detector that had an extra `no-thead` rule (1,071 papers) and looser
patterns. Its counts are not comparable with these.

### Did any text go missing?

`conversion-symptoms.py --compare main` lists HTML papers whose prose shrank by more than 5%. It
flagged 7 papers after the nightly run and 6 after the fixes ([`compare.txt`](compare.txt)). The
re-derivation reproduces both numbers, and then shows that 6 of the 7 flags were errors in the
check:

| Paper | As flagged | Cause | Body against body, tags on one line |
|---|---|---|---|
| Gemini 2.5 | −16.8% | old copy counted with its frontmatter (7,037 words of authors) | 0.0% |
| NVIDIA Nemotron 3 | −15.7% | frontmatter, 795 words | 0.0% |
| Humanity's Last Exam | −11.4% | frontmatter, 2,524 words | +0.3% |
| Group Sequence Policy Optimization | −8.9% | frontmatter, 65 words, in a 667-word paper | 0.0% |
| Open X-Embodiment | −6.1% | frontmatter, 663 words | +0.3% |
| Large Language Diffusion Models | −13.4% | a `<` in an equation taken for the start of a tag, which removed 2,371 words up to the next `>` | +0.3% |
| **SCULPT** | **−10.6%** | **real: three tables holding only a code listing were dropped (2,318 words)** | fixed: 0 papers shrank |

The check reads the old copy with `git show`, frontmatter included, but the new copy without it.
A long author list therefore looks like lost text. Its tag pattern `<[^>]+>` also spans lines.
Counting body against body, with a tag confined to one line, SCULPT is the only paper that lost
more than 5%, and after the fix no paper does ([`before-after.json`](before-after.json)). Over
all 1,905 papers, the median change in prose words is 0.0%, the 5th percentile −0.1% and the
95th +10.7%. 145 papers grew by more than 5%, from recovered boxes and tables. Both errors in the
check are still in `scripts/conversion-symptoms.py`.

**Fixed 4 Oct 2026.** `--compare` now counts body against body, takes the mathematics out before it
strips tags, and matches only real tags. Against the commit before the nightly pass, where it had
flagged 7, it flags none; against the commit before the whole reconversion it flags one paper,
Stress Detection (−6.6%), which lost no word: its siunitx numbers were written with digit groups,
five tokens each, and are now one ([`compare-fixed.txt`](compare-fixed.txt)).

The validation also ran a stricter check that ignores the threshold ([`lostall.py`](lostall.py),
[`lostall.txt`](lostall.txt)): it counts words that occur in the old copy and no longer occur in
the new one. 13 papers lost 60 or more such words. In xLSTM and others, the lost "words" are
LaTeX macro names (`textrm`, `operatorname`). Two papers had been PDF-only before and grew
overall. Confident Learning lost 89 words, but at 2,200 words for a 39-page paper it pointed to
the next finding.

**Bugs found and fixed during the validation:**

- **A table holding only a code listing was dropped.** SCULPT was the only paper affected
  ([`scan.py`](scan.py)).
- **A scaled table with full-width group rows was treated as layout and flattened.** Five papers
  were affected ([`scan2.py`](scan2.py)): ReAct, Movie Gen, Large Language Diffusion Models, LLM
  Hacking, and Privacy-Preserving Instructions.
- **PDF text starting with `#` became a heading.** Long Short-Term Memory and Ad Click Prediction
  were affected.

The converter tests went from 41 checks to 44.

### arXiv's HTML is incomplete for some papers

No symptom catches this. A paper whose HTML rendering stops partway converts cleanly, and its
markdown ends where the rendering ends. It was found in three steps.

1. **Words per paper.** [`truncated.py`](truncated.py) divides the markdown's word count by the
   PDF's ([`truncated.txt`](truncated.txt)). The median ratio is 0.97. The worst is "Studying
   Large Language Model Generalization with Influence Functions", at 0.08. This finds the worst
   cases but cannot say where the text is missing.
2. **Words per PDF page.** [`pages.py`](pages.py) checks every PDF page with 120 or more words.
   A page counts as missing when under 25% of its three-word sequences occur in the markdown
   ([`pages.json`](pages.json), [`pages.txt`](pages.txt)). Of 1,907 HTML papers, **223 have a
   missing page and 80 have three or more**.
3. **Converter or source?** For those 80, [`htmlcov.py`](htmlcov.py) measures how much of
   arXiv's cached HTML text the markdown holds: between 81% and 99%, median 94%
   ([`htmlcov.txt`](htmlcov.txt)). The missing pages are missing from arXiv's HTML. The
   converter did not drop them.

[`incomplete.py`](incomplete.py) then sets aside pages that look like references: 12 or more
years and a venue word. It keeps the papers missing 8 or more pages, or 4 or more pages that make
up a quarter of the paper. That leaves **27 papers**, missing between 4 and 121 pages
([`incomplete.json`](incomplete.json), [`incomplete.txt`](incomplete.txt)).
[`catalog_entries.py`](catalog_entries.py) wrote their entries in the issues catalog
([`catalog-entries.yaml`](catalog-entries.yaml)). For example:

- "Studying Large Language Model Generalization with Influence Functions" ends at §2.1.
- The GPT-4 Technical Report has no System Card.
- Confident Learning stops at "Assumptions" (p. 3).

The fix is to convert these papers from the PDF, which `reconvert.py` could not do for an HTML
paper at the time.

### PDF-only papers

- **Length.** The median new/old word ratio is 1.048 ([`pdf-words.txt`](pdf-words.txt)). Four
  papers came out more than 15% shorter: Long Short-Term Memory 0.69, The Power of Two Random
  Choices 0.76, Canaries 0.78 and ROUGE 0.81.
- **Coverage.** [`pdfcov.py`](pdfcov.py) applies the page check above with a 60% bar
  ([`pdfcov.txt`](pdfcov.txt); the rerun on 3 Oct matches the validation's output). It shows that
  every page of LSTM and of Power of Two is only 19–39% covered. Their PDFs have a broken text
  layer (lost ligatures, letters split by spaces), which also inflated the old copies' word
  counts. The fix is a cleaner PDF. ROUGE has no page under 60%, and its drop was not
  investigated. 22 of the 277 papers have a page under 60%: most have just one, and the
  International AI Safety Report has two.
- **Equations.** Eight papers have one or two display equations left as the PDF's raw text.

### Spot checks against the PDFs

[`spot.py`](spot.py) checks the sampled papers ([`spot-html.txt`](spot-html.txt),
[`spot-pdf.txt`](spot-pdf.txt), [`spot_sample.py`](spot_sample.py)); its output is in
[`spot-check.txt`](spot-check.txt).

| Check | HTML (10 papers) | PDF-only (10 papers) |
|---|---|---|
| headings found on their stated page | 308 of 310 (one a page early, one not found in the PDF text) | 322 of 323 (one not found) |
| figures | 117, all local files | 112, all local files |
| tables | 46 pipe tables, none with an empty header; 29 HTML tables, 27 with a header | numeric cells found in the PDF text: 2,296 of 2,296, plus 161 of 298 in TabPFN ([`spot-tables.txt`](spot-tables.txt)) |
| display equations, checked symbol by symbol against the page image | — | **6 of 9 right** |

- **TabPFN.** Its Extended Data tables are images, so their numbers come from OCR. The
  paper's conversion note says the numbers are the PDF's own, which is wrong for these tables.
- **The three wrong equations:**
  - LambdaLoss, NDCG-Loss2 (p. 6): an exponent written as a factor.
  - DSSM, eq. 16 (p. 7): the left-hand sides dropped and a subscript swapped.
  - Adam (p. 6): a figure legend taken for an equation.

  The two-in-three rate matched the bar the task had set for merging, so the run was merged and
  the error rate is recorded as a known limit.
- **The validation session's own summary** reports "289 of 290 headings" for the HTML sample,
  which does not match its script's output. The table above follows the output.

### Files

| File | Holds |
|---|---|
| [`state/`](state/) | the three `--state` files as the run left them: one line per paper with status, message and time |
| [`runs.py`](runs.py), `runs-*.json` | outcome and throughput per invocation |
| `symptoms-before.tsv`, `symptoms-nightly.tsv`, `symptoms-after.tsv` | `conversion-symptoms.py` listings: symptoms and path per paper |
| [`before_after.py`](before_after.py), `before-after*.json` | symptom moves and the three word counts, before against nightly and before against after |
| `compare.txt` | `--compare main` as run during the validation |
| `compare-fixed.txt` | `--compare` with the check fixed on 4 Oct, against three commits of the library |
| [`lost.py`](lost.py), [`lost2.py`](lost2.py), [`lostall.py`](lostall.py), `lostall.txt` | per-paper diagnosis of shrinkage against `main` |
| [`scan.py`](scan.py), [`scan2.py`](scan2.py) | which papers each of the two table bugs affected, from the cached arXiv HTML |
| [`truncated.py`](truncated.py), [`pages.py`](pages.py), [`htmlcov.py`](htmlcov.py), [`incomplete.py`](incomplete.py), [`catalog_entries.py`](catalog_entries.py) and their outputs | detection of incomplete arXiv renderings |
| [`pdf_words.py`](pdf_words.py), [`pdfcov.py`](pdfcov.py) and outputs | PDF-only papers |
| [`spot_sample.py`](spot_sample.py), [`spot.py`](spot.py), [`spot_tables.py`](spot_tables.py), `spot-*.txt` | spot checks; `spot-equations.txt` lists the twelve sampled equations by paper and page |

**Changes from the scripts as run.** Hard-coded paths to the state file and the arXiv cache in
`htmlcov.py`, `scan.py` and `scan2.py` became an argument and paperlib's `CACHE_DIR`. Four
scripts were inline in the session: `spot_sample.py`, `spot_tables.py` and `catalog_entries.py`
are saved unchanged, except that `spot_tables.py` lost its last part, which rendered a page for
a look by eye; `pdf_words.py` reads two checked-out copies in place of `git show`. Converted
paper text was removed from the outputs: one table in `spot-tables.txt` and the equations in
`spot-equations.txt`. Not kept: the page images the equations were judged on, the per-equation
verdicts beyond the three errors, and three exploratory scripts (`lost3.py`, `trunc2.py`,
`where.py`).
