# Experiment · what did fixing the 22 conversion problems one literature review flagged change across the library?

**Question.** The review of `llm/evaluation` (4 Oct 2026) logged 22 conversion problems in the papers it read: wrong numbers in tables, table and figure numbers that differ from the PDF's, a title split in two, references with nothing in them. Which of them are the converter's, and what do the fixes change in the other 1,900 arXiv-HTML papers?

**Status.** Run 4–5 Oct 2026 on the author's library: every arXiv-HTML paper reconverted in 7 h 13 min with three jobs (1,890 converted, 16 with figures arXiv does not serve, 296 skipped, none failed). **Papers showing a symptom fell from 761 to 379. An invisible padding digit had been printed in 1,052 table cells of 29 papers, and changed the value in 256 cells of five. 608 captions in 114 papers took the PDF's number.** Written up on 9 Oct from the run's state file, the library's git history and the task file; the symptom counts were recomputed that day over the commits before and after the run.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#table-and-figure-numbers).

## Method

- **The 22 entries** came from `catalog/conversion-issues.yaml` of the library. Each was traced to arXiv's HTML and fixed in `scripts/html-to-markdown.py`, in the new `scripts/caption-numbers.py`, or by hand where the HTML itself lacks the content.
- **The run.** `paperlib reconvert --all --jobs 3 --state <file>`, 18:33 on 4 Oct to 01:46 on 5 Oct. The 296 skipped are 277 PDF-only papers, 16 not from arXiv HTML and 3 edited by hand. Three papers failed on the first pass with no message and converted on the retry.
- **Symptoms.** `paperlib symptoms` over the library at the commit before the run and the commit of the run → [`symptoms-before.tsv`](symptoms-before.tsv), [`symptoms-after.tsv`](symptoms-after.tsv). Both listings use the checks of 9 Oct, which include two added later (`double-mark`, `macro-name`); the counts below leave those two out, and then match the 761 counted before the run.
- **Padding digits.** In the run's diff, a table row whose numbers differ only by a leading digit removed → [`padding-digits.tsv`](padding-digits.tsv).
- **Captions.** Papers whose state line reports captions renumbered, with the changes the diff shows → [`captions-renumbered.tsv`](captions-renumbered.tsv).

## Results

### The 22 entries

| Outcome | Papers |
|---|---|
| Fixed in the converter (15) | SWE-bench, The Leaderboard Illusion, Cheating Automatic LLM Benchmarks, MT-Bench, MATH, τ-bench, τ²-bench, Terminal-Bench, LiveCodeBench, QASC, MuSiQue, Length-Controlled AlpacaEval, Agent-as-a-Judge, Decomposing Physician Disagreement, Med-PaLM (title and the A.7 page) |
| Fixed by hand (3) | Measuring what Matters (introduction, background and Figure 1 from the LaTeX source; sections renumbered), Self-Taught Evaluators (five table references), Text-to-SQL Benchmarks are Broken (frontmatter, title block, a caption) |
| Not a conversion defect: the markdown matches the PDF (4) | HELMET, When the Judge Changes, Med-PaLM Table A.3, Terminal-Bench Table 1 |
| Left in the catalog (2) | Trust or Escalate (two algorithm lines joined in arXiv's HTML), Establishing Best Practices (its table of 17 benchmarks is not in arXiv's HTML) |

Med-PaLM and Terminal-Bench each appear twice, with one entry fixed and one that was no defect.

### Symptoms, papers

| Symptom | Before | After |
|---|---|---|
| Any of those below | 761 | 379 |
| `split-title` | 473 | 1 |
| `empty-header` | 337 | 336 |
| `flat-table` | 21 | 22 |
| `tex-box` | 20 | 9 |
| `figure-link` | 16 | 16 |
| `empty-ref` | 16 | 9 |
| `year-citation` | 13 | 4 |
| `true-digits` | 5 | 0 |
| `raw-citations` | 3 | 3 |
| `captionof` | 2 | 1 |
| `pt-residue`, `forest`, `input-path` | 2, 1, 1 | 2, 1, 1 |

- The one `split-title` left is a paper edited by hand, which the run skips.
- `empty-header` is a table whose header row arXiv's HTML does not mark and no rule gives away; the cells are intact.

### Numbers that were wrong

- **1,052 cells in 29 papers** had a `\phantom` digit printed as part of the number. In 796 of them the digit was a zero ("08.3" for 8.3), which reads right.
- **In 256 cells of five papers the value was wrong:** PaliGemma 2 ("23.0" for 3.0, 183 values), MuSiQue ("53.4" for 3.4, 9 values), Toolformer ("199.3" for 99.3), Gated Graph Sequence Neural Networks ("171.1" for 71.1) and 8-bit Optimizers ("211.9" for 11.9).
- **No note or review had quoted a wrong value.** Of the five papers only MuSiQue had a note; it says which tables were affected.

### Captions

- **608 captions in 114 papers** were renumbered to the PDF's numbers, and 3 `\captionof` captions were given one. The reason is nearly always one float early in the paper: a plot set beside a table and captioned as a table, or a float arXiv counts and the PDF does not, after which every number is off by one (Spider 2.0: 45 captions; MT-Bench: 28).
- **22 of the 114 papers had a note.** Fifteen notes were written before the run; one cited tables by their old numbers (Spider 2.0, Tables 4 and 5 for the PDF's 5 and 6), and so did one line of the `llm/evaluation` review. Both are corrected. MT-Bench, Cheating and Measuring what Matters had been corrected during the run.

## What the numbers do not say

The padding count finds a cell only when its row changed in nothing but leading digits, so a row that changed in other ways as well is missed. The caption changes were read from the diff by a caption's first 25 characters; two captions that open alike are counted once. Nobody compared all 608 new numbers with the PDFs: the captions of two papers were (Spider 2.0, Cheating Automatic LLM Benchmarks), and the pass renames a caption only when the PDF caption opens with the same words.

## Findings

- A hidden span is dropped with its text, so a number padded with `\phantom` is the number the PDF prints.
- `scripts/caption-numbers.py` runs on every arXiv-HTML conversion and gives captions, and the links to them, the PDF's numbers.
- `paperlib symptoms` gained `split-title`, `tex-box`, `empty-ref`, `year-citation`, `true-digits`, `captionof` and `input-path`.
- A note or review written before 5 Oct 2026 that cites a table or figure of one of the 114 papers by number may use arXiv's number; the two found are fixed.
