# Experiment · can a citation mark the exact place in the PDF?

**Question.** A citation link opens the PDF at a page, or at a LaTeX named destination (`dest=table.2`), and the reader then looks for the value, the sentence or the figure on that page. The PDF knows where every word is printed. Can a command find the region an agent means (a quote, a value in a table, a table, a figure, an equation) well enough that the link can carry its rectangle (`rect=`) and the viewer can mark it? And will an agent use the command, at what cost?

**Status.** Measured 30 Oct 2026 on 59 citations that agents wrote in the author's library (16 chats, 98 distinct links), turned into `paperlib locate` targets.
- **The final version marks the right region for 58 of 59 targets**, and for 3 more added later from an Opus chat that had caught it out. The one left is a quote that occurs 5 times on its page, which the command reports as such: the agent lengthens it. By kind, judged by eye on crops of each page:
  - quotes: 16 of 17 (and the repeated one)
  - values in a table: 6 of 6
  - tables: 21 of 21
  - figures: 12 of 12
  - equations: 3 of 3
- **The page the agent gave was wrong for 7 of the 21 tables** and one quote. It was the page whose text mentions the table, not the one that prints it; a named destination had hidden this until now. The command tries the page it is given first, then the whole paper, and says "(on p. 8)".
- **Haiku 4.5 followed the new rule** in 5 fresh questions through carrel: every one of its 14 page links carried a rectangle, and all 14 marked what the answer meant. It made one `locate` call per answer, about 60–200 tokens in and 250–450 tokens back, and $0.01 for each whole answer. The rule adds 95 tokens to the guide.

**`paperlib locate` shipped, with PyMuPDF 2.0; the guide tells agents to use it for every specific citation; both viewers draw the mark.** The experiment cost about $0.06 (the Haiku chats and the token counts).

**Serves.** [`docs/design.md`](../../docs/design.md#decisions-log), `paperlib locate`, the guide's "Linking to a place in a paper", vscode-pdf-viewer and carrel.

## Method

- **Cases.** [`cases.yaml`](cases.yaml) holds the citations, each with the link as the agent wrote it, the claim it backed, the target for `locate` and what the mark should cover. They come from the 16 chats in the author's library that hold `pdf.invalid` links: 17 quotes (the 11 phrases agents had passed as `search=`, and 6 values and sentences in prose), 21 tables, 6 values in a table, 12 figures and 3 equations, over 11 papers. The set covers two-column pages, a table without rules, a figure made of tables, a figure of text, and a paper without named destinations.
- **Apparatus.** [`run.py`](run.py) runs `scripts/locate.py` on each case and writes [`results.tsv`](results.tsv): the page, the rectangles or why there are none, the seconds, and the length the rectangles add to a link. It also draws each result on its page, as the viewers draw it, into crops and contact sheets in the cache folder. The crops are not committed: most of these papers are not CC BY. Each crop was judged by eye.
- **Alternatives measured in the same run.**
  - Quotes: poppler's word boxes (`pdftotext -bbox`), the tool that makes the text layer.
  - Tables: pdfplumber's `find_tables` (MIT licence) beside PyMuPDF's (AGPL).
  - The previous PyMuPDF release, 1.28, against 2.0, whose table finder uses a layout model: [`results-pymupdf-1.28.tsv`](results-pymupdf-1.28.tsv).
- **The agent.** A copy of the library with the new guide, served by carrel. Five questions, one per paper, asked through `scripts/shots.py --ask` on Haiku 4.5. Each question asks for numbers or an equation and where they are. The transcripts were read for the `locate` calls, their size and the links, and each link was drawn as above.
- **Tokens of the rule.** The guide's link section before and after, counted with [`../prompt-trim/count.py`](../prompt-trim/count.py) on Haiku 4.5.

```bash
PAPER_LIBRARY=<library> uv run --with pdfplumber --with pillow python experiments/pdf-locations/run.py
PAPER_LIBRARY=<library> uv run --isolated --with "pymupdf<2" --with pyyaml --with lxml --with pillow --with pdfplumber \
    python experiments/pdf-locations/run.py --results results-pymupdf-1.28.tsv
```

## How the command finds a place

- **A quote** is matched against the page's words with both sides folded to letters and digits. Ligatures, spacing, punctuation and hyphenation at a line's end therefore never decide a match. A match must start and end at word boundaries, so `49.60` does not match inside `149.60`. Only when nothing matches that way does it match inside words: one PDF printed justified lines without spaces. The matched words become one rectangle per printed line.
- **A table** is its caption plus the table PyMuPDF finds within 30 pt of it, plus text within 8 pt beyond the table (a row above its rules, the notes under it). Failing that, the region is grown from the caption, as for a figure.
- **A figure** is grown from its caption, upward first, through the text, drawings and images in the caption's column, while the whitespace between them stays under 18 pt. Growing stops at running text, at another float's caption, or at a table that has a caption of its own. A figure can be made of tables, so uncaptioned ones don't stop it. The region never reaches into the running text it stopped at; a drawing's box can.
- **An equation** is its number "(N)" at the column's right, plus the printed rows next to it that are not running text. A row is running text when it has six words, or three when it starts at the column's left edge. A "word" is a run of four ASCII letters, so `θℓhℓ` is not one.
- **Running text** is a block in the body's type size that spans most of the column, with at least half a column's width of letters per printed row and fewer digits than a third of its letters. Letters are counted rather than words because of the PDFs printed without spaces. Rows are counted rather than PyMuPDF's lines, because a bold run-in heading is a line of its own.

## Results

### Iterations

Each fix came from a crop that was wrong. The first version found a region for 52 of the 59.

| Version | Wrong or missing | Fixed by |
|---|---|---|
| 1 | 6 tables not found: the agent's page was wrong | searching the whole paper when the page misses |
| 2 | captions of two lines cut (a figure, a table); a table's top row and its note left out; figures under a table grew into it (3); a figure grew into the paragraph above it, whose `GPT-4o` and `Claude-3.5` counted as numbers | captions continued across blocks; text near a found table added; stopping at captions and captioned tables; counting numbers by letters |
| 3 | a figure made of tables cut short; a bold run-in heading hid running text; an equation took the paragraph under it, whose superscripts touch its subscripts | stopping only at captioned tables; printed rows; equations never take running text |
| 4 | none on the 59 | |
| 5 (30 Oct, from the reader's Opus chat on KV caches: 3 more cases) | a figure on a first page took the title and abstract: arXiv's stamp, set sideways in the margin, moved the text's left edge, so the two columns were not seen; an equation took the end of the sentence leading into it ("wise computation:"); a table cited from a note on p. 8 is on p. 9 | sideways text left out of the page's layout; a row at the column's left edge with two words is running text; the guide asks for `locate` also on citations from notes and reviews, whose pages were often wrong ([corrected since](../text-layer-switch/README.md#afterwards-the-pages-notes-and-reviews-cite-30-oct-2026)). The 59 unchanged; the 3 right |

### Alternatives

| | Found right |
|---|--:|
| Quotes on PyMuPDF's words | **17 of 18** (the 18th repeats) |
| Quotes on poppler's words | 16 of 18: it splits a table row's values differently |
| A table next to its caption, PyMuPDF 2.0 | **21 of 21** (20 by its table finder, one grown from its caption) |
| A table next to its caption, pdfplumber | 5 of 21; on figures of plots it finds grids of "tables" |
| All targets, PyMuPDF 1.28 | 49 of 59: 5 tables wrong (one the width of the page), one cell not found and one wrong, two figures cut |

PyMuPDF 2.0 brings onnxruntime and a layout model with it (about 100 MB). Its table finder is why 1.28 is worse, so the weight is kept; `locate` switches off onnxruntime's telemetry and its warnings, which otherwise reach the agent's output.

### Cost

- **Time.** A quote takes 0.01–0.03 s on its page. A table takes 0.2–0.5 s (the table finder), and a figure or equation about 0.02 s. One `paperlib locate` call with five targets takes about 1.5 s, starting Python included.
- **A link.** The rectangle adds 21 characters for a block, or two rectangles for a phrase over a line break (`&rect=130,306,479,397`); it replaces `dest=…`, which `locate`'s links leave out.
- **The rule.** The guide's link section went from 376 to 458 tokens (+82), and to 471 (+95) once it also asks for `locate` on citations from notes and reviews; it is loaded in every session.

### The agent (Haiku 4.5, through carrel)

| Question about | `locate` calls | Call / result (characters) | Links | With `rect` | Right |
|---|--:|--:|--:|--:|--:|
| Zep against MemGPT on DMR | 2 (the first failed in the sandbox) | 580 / 1,440 | 4 | 4 | 4 |
| CompleteP's compute saving | 2 (the first named the paper by title) | 677 / 848 | 2 | 2 | 2 |
| LongMemEval, oracle against full history | 1 | 187 / 752 | 1 | 1 | 1 |
| LMCor's corrector, its equation | 1 | 218 / 756 | 3 | 3 | 3 |
| Spec learning, how many pairs | 1 | 272 / 1,312 | 4 | 4 | 4 |

- **One call an answer**, batched as the rule says, with 3–7 targets. In the fifth answer `7:table.6` came back "(on p. 8)", and the link text says p. 8.
- **Two first calls failed**, and both causes are fixed:
  - carrel's sandbox kept `uv run` from writing its cache. carrel now gives its sessions a uv cache in the engine's cache folder.
  - The agent named a paper by its title. `locate` now accepts that.
- **A table row** was cited by quoting its name and model (`6:MemGPT† gpt-4-turbo`), which marks those two cells but not the score. The guide's example now puts `7:table.2>49.60`, a value in a table, before the free phrase.
- Each answer cost $0.01 on Haiku. On Opus the call costs about the same number of tokens.

## What is not measured

- **How often the reader follows a link**, and so whether rectangles are worth their tokens in notes and reviews, which are read again and again: they keep `page` and `dest` for now ([design, Next](../../docs/design.md#next)).
- **Opus.** The questions ran on Haiku, which followed the rule; the reader's sessions run on Opus, and its compliance shows in use.
- **Rotated and cropped pages** in real papers: none of the 11 papers has one. The coordinates are tested on a generated PDF with both (`tests/test_locate.py`).
