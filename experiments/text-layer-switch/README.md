# Experiment · moving the library from markdown to text layers

**Question.** [`reading-formats`](../reading-formats/README.md) decided that each paper is read from its PDF's text layer, with the PDF beside it, instead of a markdown conversion. What does that change do to a real library of 2,275 papers? Its notes and reviews were written from the markdown and are kept. And what did the experiment leave unmeasured that shows up only in use?

**Status.** Done 26 Oct 2026 on the author's library, with [`migrate.py`](migrate.py).
- **The move.**
  - 2,256 papers became text layers, in 100 seconds on 6 cores.
  - The 19 web articles were converted again by [Defuddle](../web-articles/README.md).
  - 94 figure folders (2.6 GB), 422 files of conversion records and 15 of hand corrections went.
  - The library's tree went from 2.7 GB to 300 MB.
  - `paperlib check` passes, and every review covers the papers it covered before, with 574 links repointed.
- **Four fixes to the engine came out of it:**
  - the reading view's search for the reference list, which missed or misplaced 667 papers' and took 5 minutes over the library (now 108, in 5 s);
  - two failures of the web converter on transformer-circuits.pub;
  - a race in `paperlib read`.
- **Afterwards, the pages notes and reviews cite** were corrected without reading again ([below](#afterwards-the-pages-notes-and-reviews-cite-30-oct-2026)): 6,840 table and figure pages and 5,817 prose pages in notes, 595 in reviews, $2.80 of Haiku. A second round fixed 279 more table and figure pages, and settled what the first left: 315 prose pages moved, and 1,189 citations now cite a range of two to four pages, which holds the page nine times in ten by the measurement, for $2.76 more.
- **One finding needs the author's decision.** Agents did open the PDF's page when the text lacked a value, as in the experiment, but Claude Code refused to read it: the PDFs are outside the library, behind the `pdf/` link.

**Serves.** [`docs/design.md`](../../docs/design.md#decisions-log), [`docs/text-layer.md`](../../docs/text-layer.md).

## Method

`PAPER_LIBRARY=<library> uv run python migrate.py [step ...]`, its steps in order, each safe to repeat:

| Step | What it did in the author's library |
|---|---|
| `text` | 2,256 `html` and `pdf-text` papers became `<stem>.txt`: the frontmatter (`source: pdf`), then `pdftotext -layout` with `[page N]` lines; the `.md` went. One PDF whose name the synced folder stores in another Unicode form was found by its NFC name. |
| `broken` | The two papers whose issue records said the text layer itself is broken (LSTM, a PostScript conversion; *The Anatomy of a Large-Scale Hypertextual Web Search Engine*, an OCR layer) were marked `text-layer: broken`. |
| `web` | The 19 web articles were rendered in Chrome and converted with Defuddle, keeping their file names, frontmatter and PDFs (where the reader's highlights are). |
| `clean` | 94 `images/` folders, `issues/` (799 records) and `corrections/` (26) removed. |
| `notes` | The `- Conversion: …` line removed from the 26 notes that had one; nothing else in the 1,816 notes changed, and their 16 `reread:` marks stay. |
| `reviews` | 3 figures embedded from `images/` removed (their captions already carried page links to the figure); `review-status --fix-links` repointed 574 links from `.md` to `.txt`, by stem, none left over. |
| `vscode` | `**/images` left the search excludes. |
| `stats` | What the reading view keeps of each text layer: [`results/stats.json`](results/stats.json). |

Outside the library: the 239 links to library papers in the author's career notes were repointed by stem (231 to `.txt`; 8 link web articles, still `.md`), and the PDF folder's `README.md` reworded.

The checks the reading-formats experiment left open, about $1.40:
- `paperlib read` on three unread papers (LightGBM, DBSCAN Revisited Revisited, Scikit-learn), read by hand against the text layer;
- three sessions in the library (`claude -p` with Read, Grep, Glob and Bash, project settings, $2 cap each):
  - GPT-1's RACE accuracies, which are drawn in Figure 2;
  - RULER's against NoLiMa's effective length for Llama 3.1 70B, across papers;
  - *The Anatomy*'s Table 1, on its OCR layer, which prints 147.8 GB as "117.8 GB".

## Results

### Text layers

- **61,068 pages, 303 million characters** (the markdown was 245 MB; `-layout` pads with spaces).
- **Unreadable text layers:**
  - None of the 2,256 PDFs lacks a text layer. The fewest letters on a page, averaged over a paper, are 719.
  - The most `�` (unmapped glyphs) in any paper is 1.3%, in *Billion-scale similarity search with GPUs*, in clumps of figure labels beside clean prose. The first threshold, 1%, marked it broken. It was raised to 5%, and the mark removed by hand.
  - The two broken text layers the issue records knew of are garbled but mapped, so no automatic check sees them. They stay marked by hand, and a program never takes a mark off.

### The reading view's cut

The first version, ported from the experiment's `notes.py`, cut at a "References" heading past the first third of the text. Over the library it cut 1,589 papers and left 667 whole, and it took over 5 minutes: its pattern backtracked on the long runs of spaces two columns leave. What was wrong, found by sampling the uncut and the most-cut papers:

| Cause | Papers | Now |
|---|---|---|
| Small capitals spaced out by the text layer: "R EFERENCES" | 292 | matched |
| A heading at the left margin with the other column's text beside it, on the paper's last page: "after the page" cut nothing | most of 233 | cut at the heading, since everything after it on the page is references |
| A heading alone on its line before a third of the text, in papers whose appendix is longer than the paper (*Why Do We Need Weight Decay*, 33%) | part of 142 | counts from a tenth of the text |
| The word as a figure's label at the left margin (WebGPT's example answers, a diagram in *Uncertainty Distillation*, cut at p. 4 and p. 2) | a few, found by the earliest cuts | a heading counts only when five or more years follow it, as in any reference list |
| A heading in the right column with nothing after it (a table column headed "References") | a few | treated as beside text |

Now:
- The view cuts 2,146 papers: 1,798 at a heading at the left margin, 348 after the page of one in the right column.
- It sends 110 whole: a right-column heading on the last page, or "References" run into a line with one space.
- It keeps a median 69% of a paper's text (10th percentile 37%).
- It takes 5 seconds over the library, and `paperlib reading` 1.4 s.
- The 12 papers under 40 pages whose view keeps less than a quarter were read at the cut: each is cut where its main text ends (page 9 or 10 of a conference paper; page 5 of a 37-page paper whose appendix is the rest).

### Web articles

The first conversion lost most of *Circuit Tracing* (18% of the old markdown's sentences) and left the section titles of two transformer-circuits.pub papers as bare "§ 2". The causes and fixes are in [`web-articles`](../web-articles/README.md#afterwards-the-librarys-19-articles).

After them:
- 18 of the 19 articles keep 82–99% of the old markdown's sentences. The misses are mostly the old converter's note, share buttons and bylines.
- *Circuit Tracing* keeps 67%: its page has been revised since it was first converted.
- Every article has at least as many headings as before, except LazyGraphRAG (23 → 6: the old count held the blog's navigation).

### Notes from the text layer

Three notes, $0.65 (estimated $0.83 by the refitted cost line).
- Pages match the text layer's `[page N]`.
  - One float is cited a page late: LightGBM's Algorithms 3–4 are printed on p. 5 and cited at p. 6, where the text discusses them.
  - The tables are quoted with their values.
- The LightGBM note flags Theorem 3.2's equation as garbled in the text layer and does not quote it, as the reading prompt now asks.
- No note mentions a conversion.

### Sessions in the library

| Question | Cost | What the agent did | Answer |
|---|---|---|---|
| GPT-1, RACE accuracy with 0 and 12 layers (Figure 2) | $0.16 | `paperlib info`, the note, a grep of the text layer, then `Read` of the PDF with `pages=7` | Refused: the PDF is outside the allowed folders. It named the figure and page, gave what the text says, and gave no number. |
| RULER vs NoLiMa for Llama 3.1 70B | $0.39 | notes, then grep and reads of both text layers; no review (its question names the papers) | Correct, 64K against 2K, with pages; it also found that NoLiMa quotes RULER as 32K and traced that to RULER's appendix (p. 26, Table 15) |
| *The Anatomy*, Table 1 sizes (OCR layer) | $0.18 | the note, a grep, then `Read` of the PDF with `pages=9` (refused), then the text layer | 147.8 GB, 53.5 GB and 293 MB, each flagged: two worked out from the table's own totals, and 147.8 from the note, against the scan's 117.8 |

- **The agent opens the page when the text lacks a value**, in a real library as in tier F, and for the paper marked `text-layer: broken`.
- **In the library the PDF cannot be read.** The PDFs live in a synced folder outside the library, reached through `pdf/`. Claude Code resolves the link and treats the file as outside the session's folders: refused in a headless session, a permission prompt in an interactive one. Tier F's copies held the PDFs inside the session's folder, so it did not show there.
- **The fix is a setting, which this session was not allowed to write** (it changes what an agent may do), so it is left to the author: the PDF folder in `permissions.additionalDirectories` of the library's `.claude/settings.local.json`. `paperlib init` could write it for every library; see [`docs/text-layer.md`](../../docs/text-layer.md#setup).

## Afterwards: the pages notes and reviews cite (30 Oct 2026)

**Question.** The switch kept the notes and reviews, but 60% of their table and figure citations gave the wrong page ([`pdf-locations`](../pdf-locations/README.md)). Can they be corrected without reading the papers again, about $600 at $0.35 a note?

**The cause.** The markdown marked pages on headings only: `page-map.py` wrote the page a section starts on, `### 4.3 Title (p. 6)`. A note's "p. 6" is the first page of the section its claim came from, and the claim is printed there or later. In 300 notes, 97.6% of the prose citations name a page where one of the PDF's sections starts. So the error is not one shift per note: it depends on where in its section each claim sits.

**The old markdown was still there.** `git filter-repo` had left the commits from before the switch in the library's pack (132 of 135 readable); the ref `refs/archive/markdown` now keeps them from `git gc`. Each note is matched against the version it was read from, found through the filter's commit map. The 11 notes read from text layers are left alone.

### Method

Cheapest first; a citation's page changes only when a step settles it.

| Step | What settles a page | Apparatus |
|---|---|---|
| Tables and figures | The page whose text layer prints the caption, or `locate`'s PDF finder when the text layer prints none or several. A range grows to hold the caption's page. A caption more than 5 pages away is left (since the second round, also one 2 or more pages before): the citation gives the page of the text that discusses the float. 32 sampled fixes all agree with `locate`. | `paperlib check-pages --fix` |
| Quote | A quote of three or more words in the claim, printed on one page | [`fix-pages.py`](fix-pages.py) `apply` |
| Section | Every passage under the cited heading is placed on one page | |
| Words | The old markdown cut into passages (sentences, merged to 12 words), each placed on the pages that print its word 4-grams. The passage under the cited heading sharing the claim's rarest words wins, by a margin of 4. A table, or a passage not placed, that wins leaves the page unknown. | |
| Haiku | Given the claim and the numbered passages under its heading, it names the passage that states the claim; the claim takes that passage's page when it is placed on one page | `fix-pages.py apply-model` |

The claim is the text between the previous citation on its line and this one; for a review, the link's sentence. Page ranges ("p. 8–9") are left alone.

### Measured

On 2,496 prose citations in notes whose quote settles the page, with the quote taken out of the claim ([`results/pages-measure.txt`](results/pages-measure.txt)). 64% are right as written.

| Step | Moves that fix | Moves that break a right page | Moves still wrong |
|---|--:|--:|--:|
| Words, margin 2 | 307 | 48 | 34 |
| **Words, margin 4** | **250** | **31** | **28** |
| Words, margin 6 | 185 | 15 | 20 |
| **Haiku**, on the 201 citations words leave open at margin 6 ($0.04) | **30** | **6** | **4** |
| Sonnet, the same 201 ($1.42) | 33 | 8 | 5 |
| Haiku, moving only where words' best guess agrees | 15 | 4 | 1 |

- "Break" overcounts: read by hand, several are claims of two facts on adjacent pages, where the new page prints the other one.
- Before tables and unplaced passages counted as "unknown", words at margin 3 fixed 317 and broke 47.
- The section rule kept 175 right and missed 22 fixes; it never moves a page wrongly once it requires every passage to be placed.
- Haiku decides 70% of what it is given. Sonnet is no better at 35 times the price, and agreement halves the fixes without improving the ratio.

### Applied to the author's library

| | Citations | Moved | Kept by a step | Left as written |
|---|--:|--:|--:|--:|
| Notes, tables and figures | 14,180 | 6,840 | 6,554 | 786 (189 far, 597 no caption found) |
| Notes, prose, single pages | 23,853 | 5,817 | 15,958 | 2,078 |
| Reviews, tables and figures | 913 | 453 | 404 | 56 |
| Reviews, prose | 609 | 142 | 374 | 93 |

- The notes' prose moves: quote 901, section 14, words 3,609, Haiku 1,293. By the measurement, about four in five fix a page.
- What is left is thin: 2 notes have more than 20 citations left, 50 more than 10; none is worth reading again for this. Per note in [`results/pages-left.tsv`](results/pages-left.tsv).
- Haiku: 1,635 requests for the notes, $2.76; the reviews' 254 citations a few cents more. Measuring cost $1.56.
- The library's diff changes page numbers only (checked by a script that blanks every page reference), in 1,769 files; `review-status` finds no broken link.
- Every decision is in [`results/pages.tsv`](results/pages.tsv), [`pages-model.tsv`](results/pages-model.tsv) and [`pages-reviews.tsv`](results/pages-reviews.tsv).

### Second round (31 Oct 2026)

**Tables and figures.**
- Two caption forms the finders missed, in `locate` and `check-pages` alike:
  - a bold label running into its caption with no colon ("Table 6 DNA…", in Meta's papers: OLMo 2, SAM 3, Movie Gen, DyT);
  - Roman numbers against Arabic ("Table III" finds "TABLE 3").
- `locate` cuts a table box that the PDF's table finder merged with a paragraph and another table.
- A caption two or more pages *before* the cited page is now "far" and left alone. There the citation gives the page of the text that discusses the float, as with a teaser figure cited from the results. The first round had moved 112 such citations back (84 notes, 1 review); they were restored.
- `check-pages --fix` then fixed 279 more pages in notes and 35 in reviews.
- Notes now: 13,757 right, 0 wrong, 314 far, 109 unprovable. Reviews: 901 right, 0 wrong, 6 far, 6 unprovable.

**Prose.** What the first round left, and a second opinion on the words rule's moves, by [`fix-pages.py`](fix-pages.py) `apply-leftovers`, in order:

| Step | What settles the citation |
|---|---|
| Filled | An unplaced passage that is not a table (a display equation) takes the page of the placed passages before and after it, when both are on one page; the rules run again |
| Haiku, one claim | The claim asked alone; Haiku's first pick placed on one page gives that page, a pick across a page break the two-page range |
| Section span | The run of pages N, N+1, … printing the section's placed passages, at most four: "p. N–M" |
| Second opinion | Haiku is asked about each move of the words rule; when it names another page, the citation cites the range over both |

Measured on the known answers that the first round would leave: 392 citations ([`results/pages-measure-leftovers.txt`](results/pages-measure-leftovers.txt), $0.78):

| Step | Single pages right | Single pages wrong | Ranges holding the page | Ranges missing it | Left |
|---|--:|--:|--:|--:|--:|
| Filled | 2 | 2 | | | |
| Haiku, one claim | 50 | 20 | 36 | 2 | |
| Section span | 8 | | 207 | 13 | |
| No passages | | | | | 52 |

- A range always starts at the cited page, so a section span never loses a right page; it widens it.
- Haiku asked twice about the same claims varies: a first run gave 48 right and 5 wrong.
- A step by a table or figure named in the claim (its caption's page, within N−1 to N+5) fixed 9 and gave 7 wrong pages of 21, so it was dropped: prose about a table is often printed away from its caption ([`results/pages-measure-leftovers-captions.txt`](results/pages-measure-leftovers-captions.txt)).

The second opinion, on the 309 known moves of the words rule ([`results/pages-measure-second.txt`](results/pages-measure-second.txt), $0.16):
- Haiku agrees with 277 (241 fix, 15 break a right page, 21 still wrong) and is unsure of 5.
- It disagrees with 27, which become ranges: 23 hold the page.
- Wrong single pages fall from 59 to 37, for 27 ranges.

**Applied** ([`results/pages-leftovers.tsv`](results/pages-leftovers.tsv), [`pages-leftovers-reviews.tsv`](results/pages-leftovers-reviews.tsv)), $2.76 of Haiku:

| | Notes | Reviews |
|---|--:|--:|
| Left by the first round | 2,077 | 93 |
| Filled: kept / moved | 158 / 25 | 5 / 0 |
| Haiku, one claim: kept / moved / range | 555 / 287 / 301 | 10 / 3 / 6 |
| Section span: kept / range | 40 / 492 | 3 / 54 |
| Still left (no passage placed) | 219 | 12 |
| Words' moves: agreed or unsure / range | 3,278 / 327 | 64 / 9 |

- One note (*Sigmoid Loss*) was skipped: a hand fix had added a citation, so its first-round log no longer lines up.
- The library's diff changes page numbers only, in 928 files. `paperlib check` passes, and `review-status` finds no broken link.

**Left:** 4,836 prose page ranges in notes keep their headings' pages. 220 single prose citations in notes and 12 in reviews keep their section's first page: no passage under the heading could be placed. Tables and figures that `check-pages` cannot place stay as written (423 in notes, 12 in reviews). The guide's rule to run `locate` on a page taken from a note covers them in answers.

## Not measured

- A literature review written from notes read off the text layer. The kept reviews were written from markdown notes.
- What reading a whole area costs. The cost line is fitted on four papers until 20 readings are logged with their length.
- How often a plausible wrong digit in a text layer misleads an answer when nobody opens the page.
