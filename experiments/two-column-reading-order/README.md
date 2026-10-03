# Experiment · can a PDF-only paper be read in column order, with its pseudocode kept as code?

**Question.** Papers with no arXiv HTML were converted from the PDF's text layer with a position
sort, which prints a two-column page's columns side by side and then joins them into one paragraph:
the agent reads half a sentence from each column in turn. Can PyMuPDF's text, ordered by
pymupdf4llm's column detection, fix the reading order without losing text, and can pseudocode be
recognised and kept as an indented code block?

**Status.** Run 30 Sep 2026 over the 178 `source: pdf-text` papers, all reconverted twice:
**lines printing two columns side by side fell from 6,574 in 149 papers to 193 in 6**; the column
regions were rejected for most pages in only 4 papers, all from before 2000; word counts moved by
under 2%. Pseudocode detection finally wrote **513 code blocks
in 65 papers**, after guards cut false positives found in a first census of 545 blocks in 68.
**Superseded 1 Oct 2026**: PDF-only papers are now converted by layout analysis (docling, with
marker's model for equations), which also recovers headings and tables; this text-layer path is
gone.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#pdf-only-papers).

## Method

- **Corpus.** The 178 papers in the private library on 30 Sep 2026 whose markdown came from the PDF
  text layer: older papers (Finding Structure in Time, Long Short-Term Memory, The Google File
  System), papers never on arXiv (ACM, conference proceedings), and a few arXiv papers without an
  HTML rendering. 3,261 pages. Neither the papers nor their conversions are committed; the quoted
  lines below are short illustrations.
- **The trigger.** *Learning Optimal Personalised Reservation Prices in Impression Ad Auctions*
  (Spotify, CIKM 2025), read on request, came out with its abstract interleaved with the ACM
  reference block in the right column:

  > Abstract                                    ACM Reference Format: Reservation prices have proven
  > effective in boosting revenue in       Dmitrii Moor, Emma Zetterdahl, … Learning Optimal
  > Personalised Reservation Prices in ImpresGeneralised Second Price (GSP) auctions, particularly
  > in cost-per- sion Ad Auctions …

- **Column order** ([`pdf-to-markdown-22e0d4f3.py`](pdf-to-markdown-22e0d4f3.py), private-repo
  commit `22e0d4f3`). `pymupdf4llm.helpers.multi_column.column_boxes` splits each page into text
  regions in reading order (40 pt header and footer margins). Only the regions are used: the text
  is still PyMuPDF's raw extraction, because pymupdf4llm's own markdown drops display equations
  ([`pdf-vs-arxiv-html/`](../pdf-vs-arxiv-html/README.md)). Within a region, paragraphs are rebuilt
  from line geometry. A page falls back to the plain sort when its regions hold less than 90% of
  its characters, minus 200.
- **Pseudocode and fragments** ([`pdf-to-markdown-4a62e43c.py`](pdf-to-markdown-4a62e43c.py),
  committed in `4a62e43c` with the reconverted papers). Triggered by *Prefix Sums and Their
  Applications* (Blelloch), whose `down-sweep` procedure came out one line per paragraph with its
  indentation lost. A line is code-like when it is in a monospace font (here `CMTT10`), contains
  `←` or `:=`, or is a short line that opens with a pseudocode keyword (`procedure`, `for`,
  `in parallel`, `return` …). Two or more such lines, allowing one short plain line between them,
  become a fenced `text` block with indentation taken from the lines' x positions; a comment on
  the same baseline stays on its row. Runs of very short lines (figure and table cells) are joined
  onto one line, and lines repeated at the top or bottom of many pages (running headers, page
  numbers) are dropped.
- **Apparatus.**
  - [`fallback_pages.py`](fallback_pages.py) counts the pages where the regions were rejected.
  - [`codeblock_census.py`](codeblock_census.py) converts every pdf-text PDF in memory and lists
    the papers with the most code blocks, to read for false positives.
  - Both take the directory holding the candidate `pdf-to-markdown.py` and `paperlib.py`
    (`python3 fallback_pages.py <scripts dir>`); they need the PDFs. They are the inline scripts
    from the session with the hard-coded private paths replaced by that argument.
  - [`structure_stats.py`](structure_stats.py) was written on 3 Oct 2026 for this write-up. It
    measures the committed markdown of the 178 papers at three commits, from git, without the
    PDFs:

    ```bash
    python3 structure_stats.py before=<lib at 22e0d4f3^> columns=<lib at 22e0d4f3> code=<lib at 4a62e43c>
    ```

## Results

### Reading order

[`structure-stats.md`](structure-stats.md), over the same 178 papers in each snapshot:

| Conversion | Words | Side-by-side lines | Papers with 10+ | Paragraphs | One- or two-word paragraphs | Code blocks |
|---|---|---|---|---|---|---|
| Position sort (before) | 1,737,341 | **6,574** | **149** | 25,334 | 3,333 | 0 |
| Column regions (`22e0d4f3`) | 1,766,481 | 228 | 7 | 182,166 | 123,695 | 0 |
| + code blocks, fragments, headers (`4a62e43c`) | 1,754,562 | **193** | **6** | 80,482 | 23,027 | 513 |

- **A side-by-side line** is a line outside code with four or more spaces between two words, which
  is how the position sort prints two columns next to each other. It does not catch every
  interleaving, only the visible kind, so it undercounts the "before" state.
- **The columns stopped interleaving.** 149 of the 178 papers had ten or more such lines, so most
  of the corpus was two-column. Afterwards 6 papers do; the remaining lines are mostly tables and
  figure labels.
- **No text was lost.** Words rose 1.7% with column regions (text the old sort had glued together,
  "ImpresGeneralised", now separates) and fell 0.7% with the third step, which drops running
  headers and page numbers.
- **The column step alone fragmented figures.** Every axis tick and table cell became its own
  paragraph: 124,000 paragraphs of one or two words. Joining runs of short lines brought that to
  23,000.
- **The fallback was rarely used.** Over 3,261 pages, 4 papers fell back on more than half of
  their pages: *Adaptive Mixtures of Local Experts* (9 of 9), *A Density-Based Algorithm for
  Discovering Clusters* (6 of 6), *The Use of Multiple Measurements in Taxonomic Problems* (10 of
  11) and *The Use of MMR, Diversity-Based Reranking* (15 of 15), all from 1936–1998. The session
  judged them scans or single-column papers that the plain sort reads correctly; that was not
  checked page by page. The per-page count for the rest was not kept.
- **Paragraph rebuilding needed one correction.** Glyph boxes are about 4 pt tall with 7 pt gaps,
  so "a gap larger than a line height" split every line. Comparing baseline-to-baseline pitch with
  the region's median pitch fixed it: the Spotify paper went from 2,469 lines to 1,371, its
  abstract one paragraph. A hyphen at a line end is removed for a split word ("personal-isation")
  and kept in a compound ("cost-per-click").

### Pseudocode

The first census, before any guard ([`codeblocks-before-guards.tsv`](codeblocks-before-guards.tsv)),
found 545 blocks in 68 papers. Reading the top of the list showed three kinds of false positive:

| Paper | What became a "code block" | Guard added |
|---|---|---|
| *The relationship between Precision-Recall and ROC curves* (27) | axis ticks "0.8 ⏎ 0.6 ⏎ 0.4" | a block must be at least 30% letters |
| *Scaling to Very Very Large Corpora* (11) | plot tick labels | same |
| *LexRank* (13) | numbered footnotes, prose lines opening with "for" or "if" | a keyword counts only on a line under 70% of the column width; a run may bridge only a short plain line |

After the guards, *Prefix Sums*' procedure reads as it is printed:

```text
procedure down-sweep(A)
  a[n −1] ←0                            % Set the identity
  for d from (lg n) −1 downto 0
    in parallel for i from 0 to n −1 by 2d+1
      t ←a[i + 2d −1]                   % Save in temporary
```

LexRank's algorithm, HyperLogLog's and the Text-to-SQL paper's SQL came out the same way. Two
false positives were known and left: *BLEU*'s first-page proceedings header became a block, and the
precision-recall paper's plot axes stayed as 15 blocks of ticks. The committed reconversion has 513
blocks in 65 papers; 261 of them are in *Defeating Prompt Injections by Design* (CaMeL), whose
appendices print Python code, prompts and model transcripts in a monospace font, so those are code
blocks in the PDF too. No one checked the 513 blocks one by one.

### Why it was superseded

Column order fixed the worst defect but left a text-layer conversion: no headings, no tables,
equations as scattered glyphs. The next day's comparison against arXiv HTML on papers that have both
(recorded in `docs/conversion.md`) measured this text layer at 0% of table numbers in a table and 0%
of headings found, and replaced it with docling's layout analysis, which orders columns itself. The
lesson that carried over: take the words and numbers from the PDF's own text layer, and use a model
only for structure and for what the text layer lacks.

## Files

| File | Holds |
|---|---|
| [`pdf-to-markdown-22e0d4f3.py`](pdf-to-markdown-22e0d4f3.py) | the converter with column regions and paragraph rebuilding |
| [`pdf-to-markdown-4a62e43c.py`](pdf-to-markdown-4a62e43c.py) | the same with code blocks, fragment joining and header removal |
| [`fallback_pages.py`](fallback_pages.py) | pages where the column regions were rejected |
| [`codeblock_census.py`](codeblock_census.py) | code blocks per paper, for reading false positives |
| [`codeblocks-before-guards.tsv`](codeblocks-before-guards.tsv) | its output before the guards: blocks per paper |
| [`structure_stats.py`](structure_stats.py), [`structure-stats.md`](structure-stats.md) | the reading-order table above |
| [`reconvert-pdftext.log`](reconvert-pdftext.log) | the second reconversion: every paper "ok", with its word count |

The first reconversion's log was not kept; the session reports all 178 "ok" and the library check
passing.

## Limits

- No reference reading order. Side-by-side lines measure the visible symptom; columns joined in the
  wrong order without wide gaps would not show. The improvement was confirmed by reading a handful of
  papers (the Spotify paper, *DBSCAN Revisited, Revisited*, a RecSys offline-evaluation paper), not
  by scoring all 178.
- The fallback threshold (90% of characters, minus 200) was set once and not tuned.
- Pseudocode detection was judged from the census's top entries and a spot check of six papers.
