# Experiment · what the library's markdown buys over the PDF

**Question.** The library rests on two claims that had never been measured. One is that an agent answers questions about papers better, or as well and more cheaply, from the library's markdown than from the PDF. The other is that the conversion work (tickets, fixes, reconversions) changes the answers, and not only how the markdown looks. Which form of a paper should an agent read: the PDF (text layer plus page images), the PDF's text layer, arXiv's HTML, or the markdown? Alone, or as an agent with files to search? And what does each cost?

**Status.** Run 24–26 Oct 2026 on 37 papers: 118 questions (103 distinct), 581 answers, and 24 notes. About $110 of requests (Opus 5.5 through `claude -p` on the subscription, about three five-hour windows with the sessions' own work). **The markdown buys nothing measured.**
- **Single papers, whole paper in one request.** PDF 51 of 51 questions, text layer 43, markdown 43; the eight the text forms lose are values drawn in a plot.
- **Across papers.** An agent in the library, in a folder of PDFs and in a folder of text layers answer the same 13 questions alike; the text layers are the cheapest.
- **With the PDF beside the text layer**, an agent opens the page exactly when a value is drawn (9 of 9, and 0 of 6 otherwise) and when the text layer looks broken (5 of 9 broken passages, 0 of 5 clean ones), unprompted, at about $0.10 a question.
- **Notes** written from the text layer were preferred by a blind judge with the PDF in 9 of 12 pairs (markdown 2, equal 1); they had no wrong page against the markdown's 17, and no wrong number in either.
- **Where the forms differ**, the text layer is ahead: it keeps the numbers inside vector figures, its page markers are exact, and it has none of the converter's errors (E4).
- **Recommended:** the text layer with `[page N]` markers, beside the PDF, as the agent's copy of a paper ([decision](#decision)).

**Serves.** [`docs/design.md`](../../docs/design.md#decisions-log). Plan, written before the runs: [`plan.md`](plan.md); run log, with every finding as it was made: [`PROGRESS.md`](PROGRESS.md).

## Method

- **Conditions.** One request with the whole paper (`run.py`, `claude -p` without tools): **c0** (closed book), **pdf** (a document block: text layer and page images), **txt** (`pdftotext -layout`), **html** (arXiv's `<article>`), **md** (the library's markdown). Page forms for small print: one page as PDF, as a 1,255 px or 2,576 px image. Agent sessions (`claude -p` with Read, Grep, Glob, Bash, no web, no edits, read-only copies built by `copies.py`): **x-lib** in a copy of the library (guide, catalog, notes, reviews, markdown); **x-pdf** in a copy of its 2,275 PDFs; **x-txt** in a copy of their text layers with a line `[page N]` at each page; **f-plain** in a copy holding each paper's PDF beside its text layer, whose `CLAUDE.md` says only what the files are; **f-hint**, the same plus "a value drawn in a figure is not in the text: read that page of the PDF". **x-att**: the PDFs a cross-paper question rests on, attached to one request.
- **Questions** ([`questions.yaml`](questions.yaml), golds checked against the PDF pages by eye and with `inputs.py check`). E1: six per paper on nine papers (a table, a second table, an equation, an appendix or setup detail, a value only in a figure, an unanswerable trap); four of the papers were published after the model's training cutoff, drafted by `draft.py` and checked by hand. E3: 13 across papers, five of them mined from the library's reviews and two library-wide aggregations. E4: six places where a converter fix changed the markdown, with the markdown before the fix. E5: small print and plot values on single pages. E6: ten questions on the structure of equations. E7 (tier F): fifteen E1 and E5 questions reworded to name their paper. E8 (tier G): fourteen questions aimed at the passages of seven papers whose issue records call the text layer broken or flawed (`draft.py --weak`).
- **Grading** (`judge.py`): one request per question holds all its answers, shuffled and unlabelled, against the gold and a tolerance for plot readings. A question whose first answers differ between conditions (closed book aside) was asked twice more in each, while the paper was still in the cache; a difference counts when it holds in two runs of three. Every disagreement and ten agreements were read by hand.
- **Notes** (`notes.py`, tier H): for four papers published after the cutoff, a note from the markdown's reading view and one from the text layer, both with today's `guide/reading-prompt.md` and Opus 5.5, three times each. A blind judge with the PDF got each pair in shuffled order, the `## Conversion` sections left out, and listed each note's errors and what each has that the other lacks; every listed error was then checked by hand.

```bash
PAPER_LIBRARY=<library> uv run python copies.py                    # the agents' copies, in the cache
PAPER_LIBRARY=<library> uv run python run.py <tier> --budget 20    # A B B2 C C2 D F G; stops at 80% of the five-hour window
PAPER_LIBRARY=<library> uv run python run.py canary                # on each new Claude Code release
PAPER_LIBRARY=<library> uv run python notes.py write [r]; uv run python notes.py compare [r]
PAPER_LIBRARY=<library> uv run python report.py                    # results/summary.md
```

## Results

All tables are in [`results/summary.md`](results/summary.md); every answer is in `results/runs/`, every grade in `results/judge/`.

### One paper, the whole paper in one request (E1, E5, E6)

| Questions | c0 | pdf | txt | md |
|---|---|---|---|---|
| E1, five papers the model may know (27) | 20.5 | 27 | 23 | 23 |
| E1, four papers after the cutoff (24) | 2 | 24 | 20 | 20 |
| E6, equation structure (10) | | 10 | 10 | 10 |
| E5, small print in tables (6) | | 6 | 6 | 6 |
| E5, numbers printed inside vector figures (2) | | 2 | 2 | 0 |

- **The forms differ only where a value is drawn.** Tables (15), equations (7), appendix and setup details, a citation, prose and traps: PDF, text layer and markdown all correct. The eight values only in a plot or a diagram label: the PDF 3 of 3 runs on each, the text forms declined 3 of 3 and never guessed.
- **The LaTeX buys nothing at answer time.** On 17 equation questions, including a fraction no prior gives whose text layer spreads it over three lines with its bar lost, the text layer answered every one the markdown did.
- **Text inside vector figures** (a p-value on a bar, heatmap cells) is in the text layer and not in the markdown, which keeps a figure as a picture ([ticket `figure-text-lost`](../../tickets/figure-text-lost.md)).
- **Small print in a dense table is read from a 1,255 px page image** (2,250 tokens), the cheapest form that answers a question about one known page.
- **HTML** (DPO only) costs 2.5× the PDF and cannot cite pages; dropped after the pilot.
- **Closed book** answers DPO and InstructGPT from memory, which is why four papers after the training cutoff were added: there it scored 2 of 24, both traps.

### What the conversion's errors do (E4)

On six places where a converter fix changed the markdown, the old markdown gave a confident wrong answer where it printed a plausible wrong value (MuSiQue's padding digit, 3 of 3 runs) and declined where the value was missing (3 questions). The fixed markdown and the PDF were right. The text layer had none of these errors (3 of 3), including a Qwen3-VL table both markdown versions broke: the converter's errors are its own, not the PDF's.

### Across papers (E3)

| | x-lib | x-pdf | x-txt | x-att |
|---|---|---|---|---|
| Score (13 questions; x-att 9) | 13 | 12 | 12 | 9 |
| By hand | 13 | 13 | 13 | 9 |
| Cost a question | $0.42 | $0.36 | $0.30 | $1.72 |

- **Every condition answers every question**, the library-wide aggregations included, where all three agents found eight papers the gold's own search had missed. The two partial grades of x-pdf and x-txt are on golds copied from a library review; read by hand, those answers are correct.
- **The library is the dearest agent condition**, not the cheapest: its session starts at 12.4K tokens against 7.4K, and it reads notes and whole markdown files where x-txt greps the text layer for the line it needs. Notes and reviews shortened the path but did not change an answer.
- **x-pdf ran `pdftotext` itself in 13 of 13 sessions** and never looked at a page, since no question needed one.
- **The library cites a page per heading**, so its reviews cite tables one page early in three papers (ticket `page-markers-within-sections`).

### Figures with the PDF at hand (E7, tier F)

Fifteen questions: nine values drawn in a figure, two printed inside vector figures (in the text layer), four answered by the text.

| | f-plain | f-hint |
|---|---|---|
| Correct | 15 of 15 | 15 of 15 |
| Page looked at, drawn values | 9 of 9 | 9 of 9 |
| Page looked at, text in vector figures | 0 of 2 | 2 of 2 |
| Page looked at, text questions | 0 of 4 | 0 of 4 |
| Cost a question | $0.11 | $0.10 |

- **Unprompted, the agent reads the text first and opens the page when the value is not there**: with Claude Code's `Read` of the PDF with `pages` (7), or by rendering the page with `pdftoppm` and cropping the plot (2). Each answer says it read the value off the plot.
- **The hint adds nothing**: it opened pages for figure text the text layer already had, and rendered and cropped more often.
- **A canary** (`run.py canary`: three drawn values, two text questions, one vector-figure text) repeats this on each Claude Code release, since the behaviour belongs to Claude Code. Its first run on 2.1.301 matched tier F exactly.

### Where the text layer is weak (E8, tier G)

Seven papers: LSTM (a PostScript conversion), The Anatomy of a Large-Scale Hypertextual Web Search Engine (an OCR layer), a 2025 cold-start meta-learning paper, EDM, DiskANN, GPT-2, a MIDI-to-score paper. At 9 of the 14 passages the text layer is broken (LSTM's minus signs and fraction bars, a mangled PageRank formula and table, "�" for mathematical letters, "6=" for ≠, ✓/✗ as 3/7, 1/10⁸ as "1018"); the other 5 are clean, their issue records describing the converter's errors, not the text layer's.

| | c0 | txt | md | f-plain |
|---|---|---|---|---|
| Correct, broken passages (9) | 7 | 8 | 9 | 9 |
| Correct, clean passages (5) | 3 | 5 | 5 | 5 |

- **The model reads through a broken text layer**, and says what it repaired: minus signs from the stated ranges, "1018" as 1/10⁸ because a rate cannot exceed 1, the 7s as crosses.
- **The one thing it cannot repair is a plausible wrong digit**: the OCR layer's "117.8 GB" for 147.8 GB (txt wrong 3 of 3, hedged), the same failure as the old markdown's padding digit in E4.
- **The agent opened the page for 5 of the 9 broken passages and none of the clean ones**, the OCR table in 3 of 3 runs, after the grep showed garbled neighbouring cells.
- Closed book knows the old famous papers; on the 2025 paper it declined both questions where every document form was right.

### Notes from the text layer (tier H)

Four papers published after the cutoff (SOAP, Muon, and Beyond; Scaling and Stabilizing Large-Scale Embedding-Based Retrieval; A-TMA; When the Judge Changes, So Does the Measurement), three notes from each form, compared pair by pair.

| | text layer | markdown |
|---|---|---|
| Preferred (12 pairs; 1 equal) | 9 | 2 |
| Wrong statements | 9 | 16 |
| Wrong pages (more than a page off) | 0 | 17 |
| Wrong numbers, garbled equations | 0 | 0 |
| Cost a note | $0.08–0.37 | $0.08–0.37 |

- **Read by hand, the differences come from the input.** The markdown's wrong pages come from its page-per-heading markers (ticket `page-markers-within-sections`; a section running over pages 14–19 cites its figures on p. 14). Its false "not disclosed" claims are values printed inside vector figures, which it lacks (`figure-text-lost`). Both forms' notes sometimes call the appendices "missing", which is true of the reading view they were given, which cuts them.
- **The text layer's own error is the minus sign it drops inside a figure** (the judge paper's Fig. 4, "r = 0.957" for −0.957), which the note flagged as possibly lost in two of three notes.
- **What each note adds** is about even, and varies more between runs of one form than between forms.
- The notes with fewest errors (text layer, one of three per paper) replaced the library's notes of the four papers on 26 Oct.

### Cost and size

- **Tokens, whole paper**: the markdown is 40–73% of the PDF. It costs 1.3× the text layer where it carries much LaTeX and many HTML tables, and 0.94–1.14× elsewhere. The PDF costs 2,600–4,000 tokens a page, about 1,550 of them the page image.
- **With the cache**, a further question on a paper already in the request costs $0.02–0.06 in any form; agent sessions cost $0.04–0.19 on one paper and $0.20–0.50 across papers.
- **The library's text layer almost never fails outright**: a scan of all 2,275 PDFs found none without a text layer, one with over 1% unmapped glyphs, and two badly broken by the issue records (the two in tier G). In 58% of the PDFs at least one figure is a raster image, whose numbers no text form carries.

## Decision

- **Make the PDF's text layer, with a line `[page N]` at each page and the PDF beside it, the agent's copy of a paper.** No question type was answered better from the markdown (51 single-paper, 13 cross-paper, 10 equation-structure, 14 weak-text-layer questions), and the text layer is ahead on figure text, page citations and converter errors. An agent with the PDF beside it opens the page for what the text lacks, unprompted.
- **What it saves**: the conversion step (the arXiv-HTML and PDF converters, page mapping, caption numbering, missing pages, symptoms, KaTeX checks, reconversions, hand-edit corrections), its tickets, about 8,600 of the engine's 14,000 lines of scripts with their fixture tests, and the 2.5 GB of figure images the library holds for the markdown.
- **What it keeps**: everything the library is for besides the conversion: the frontmatter (it needs a new home, since today it heads the markdown), indexes, catalog, notes, reviews, the skills, adding papers, page links. Web articles (19, no PDF) stay as markdown.
- **Not measured, and to check during the change**: notes and reviews over a whole area from the text layer (tier H covers four notes); the cost of a review's reading over hundreds of papers; papers whose text layer has a plausible wrong digit, which only a reader who opens the page catches, in either form.
- **The single-request path loses nothing**: a value drawn in a figure was lost by the markdown too, and is answered only by the PDF attachment or an agent that opens the page.
