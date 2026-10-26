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

## Not measured

- A literature review written from notes read off the text layer. The kept reviews were written from markdown notes.
- What reading a whole area costs. The cost line is fitted on four papers until 20 readings are logged with their length.
- How often a plausible wrong digit in a text layer misleads an answer when nobody opens the page.
