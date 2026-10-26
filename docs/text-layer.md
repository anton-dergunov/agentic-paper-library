# A paper's text

How a paper is kept for the agent, and why. The decision and its numbers are in [`experiments/reading-formats`](../experiments/reading-formats/README.md) and the [design log](design.md#decisions-log).

| `source` | The paper file | Made by |
|---|---|---|
| `pdf` | `library/<topic>/<Title>.txt`: the frontmatter, then the PDF's text layer | `paperlib add-arxiv`, `add-pdf`, `add`; rebuilt by `paperlib text` |
| `web` | `library/<topic>/<Title>.md`: the frontmatter, then the article as markdown | `paperlib add-web` |

The PDF is always at the mirrored path under `pdf_root`. It is what the reader reads, and what an agent opens a page of when the text lacks something.

## The text layer

`pdftotext -layout` (poppler), with a line `[page N]` before each page. `N` is the PDF's page, counted from 1: what the PDF viewer and a `pdf.invalid` link open, not the number printed in the margin.

```
[page 7]
   Table 2: Results on LongMemEval ...            the model improves accuracy by ...
```

- **Two-column pages keep their columns side by side** on each line. A model reads them that way as well as it reads the markdown, and grep finds a phrase in either column.
- **Pages are split at the form feeds pdftotext puts between them.** The number of pages is checked against `pdfinfo`; a PDF that maps a glyph to a form feed, so that the split would shift every later page, is read a page at a time instead.
- **The reading view** (`paperlib read-view`, what `paperlib read` sends for a note) is the text layer cut at the reference list, with a last line saying what was left out; `--appendix` sends the whole text. The cut is at a "References" or "Bibliography" heading (also in small capitals, which the text layer spaces out as "R EFERENCES") past the first tenth of the text and followed by years, as every reference list is; the word alone is also a figure's label. At the left margin the cut is at the heading, since everything after it on the page is references. In the right column it is after the page, so that the left column below the heading is kept. In the author's library the view cuts 2,146 of 2,256 papers and keeps a median 69% of the text; the 110 it does not cut are sent whole ([`experiments/text-layer-switch`](../experiments/text-layer-switch/README.md)).
- **What it lacks:** values drawn in a plot or a raster figure (the numbers printed inside vector figures are there), and some symbols (∈, √, a fraction's bar). The guide tells the agent to read the PDF's page for those. Claude Code does that unprompted: tier F of the experiment found it opened the page for 9 of 9 drawn values and 0 of 6 questions the text answers.

## Broken text layers

A PDF can have no text layer (a scan) or one in a font without a character map. `paperlib add` and `paperlib text` check each text layer. Pages with almost no letters, or more than 5% of `\ufffd` replacement characters (the character pdftotext writes for a glyph it cannot map), get `text-layer: broken` in the frontmatter, and the command prints a warning; a mark is never taken off by a program. A figure's labels in a font without a character map leave the prose readable: the most in the author's library was 1.3%, in clumps beside clean text. The guide tells the agent to read such a paper's pages. In the author's library of 2,275 PDFs, two are broken: a PostScript conversion and an OCR layer, both marked by hand. About 60 have imperfect text layers (dropped ligatures, minus signs), which the model reads through and says so (tier G).

One failure no reader repairs from the text is a plausible wrong digit in an OCR layer ("117.8 GB" for 147.8 GB). Only an agent that opens the page catches it, in any form of the paper.

## Rebuilding

The text depends on poppler's version. A new poppler can change the text layer of papers already in a library, so an upgrade is checked:

```bash
paperlib text --dry-run llm/memory      # which papers' text would change
paperlib text llm/memory                # rewrite them; then git diff in the library
```

`paperlib text` keeps each paper's frontmatter, and writes a paper only when its text changed. Run it after replacing a PDF (a new arXiv version) too.

## Web articles

`paperlib add-web` renders the page in headless Chrome (a desktop user agent, a 20 s budget for its scripts) and converts the rendered DOM with [Defuddle](https://github.com/kepano/defuddle) 0.19.5 on jsdom 24 (`scripts/web/`, installed with `npm ci` on first use). Before Defuddle runs, pictures, SVG plots and interactive figures are removed, links inside headings become their text, and the Distill template's empty `<d-cite>` citations get their keys written into the text. Two of these were found on the library's articles after the experiment: Defuddle stopped at transformer-circuits.pub's interactive attribution graphs and kept a fifth of *Circuit Tracing*, and it dropped section titles that are links. The converter now warns when its markdown has fewer than three quarters of the words in the article's prose. The markdown keeps the maths as TeX and the footnotes as footnotes, and has no images. Its `url` is in the frontmatter, so an agent can open the page for a figure or an interactive part. Chrome also prints the page to the PDF, for the reader, unless a PDF is already there. Defuddle was chosen over Readability + Turndown and Trafilatura on three articles ([`experiments/web-articles`](../experiments/web-articles/README.md)).

`paperlib add-web <url> <topic> --force` converts an article again and keeps its frontmatter and its PDF.

## Metadata

As of 2026-09-30, for resolving a title to a paper:

- **arXiv title search** (a `ti:` word query, 3 s between requests) resolves most titles. **Crossref**'s `query.bibliographic` covers papers that aren't on arXiv.
- **Semantic Scholar**'s title search is rate-limited to near zero without an API key. Its batch endpoint works: `POST /paper/batch` with `ARXIV:`, `DOI:` or `ACL:` ids, up to 400 per call, returns year, venue and citation count.
- **OpenAlex** (anonymous search paused) and **DBLP** (behind a bot check) were unavailable.
- **Publishers that block scripts:** ACM, Wiley, Springer, SSRN and OpenReview. Their PDFs are downloaded by hand in a browser and added with `paperlib add-pdf`.

→ [`experiments/metadata-sources`](../experiments/metadata-sources/README.md)

## The canary

Reading the text first and opening a page only when needed is Claude Code's behaviour, not the engine's, and a release can change it. `experiments/reading-formats/run.py canary` asks six of tier F's questions again (three values drawn in figures, two answered by the text, one printed inside a vector figure) in a copy of the PDFs beside their text layers, for about $2–3. It records whether pages are still opened when needed and not otherwise, and what that costs. Run it on each new `claude --version`. The first run, on 2.1.301, matched tier F exactly.

## Setup

`paperlib` runs in the engine's own environment; uv creates it from `pyproject.toml` on first use. It also needs:

- **poppler** (`pdftotext`, `pdfinfo`): `brew install poppler`, or `apt install poppler-utils`.
- **Node.js and Google Chrome or Chromium**, for web articles only. Set `chrome:` in `paper-library.yaml` if Chrome isn't found.
- **Claude Code allowed to read the PDFs.** When `pdf_root` is outside the library (a synced folder, reached through `pdf/`), Claude Code treats a PDF as outside the session's folders: a headless session cannot open its page, and an interactive one asks each time ([`experiments/text-layer-switch`](../experiments/text-layer-switch/README.md#sessions-in-the-library)). `paperlib init` adds the folder to the library's `.claude/settings.local.json`, which stays on the machine and out of git:

  ```json
  { "permissions": { "additionalDirectories": ["/Users/you/Dropbox/Papers"] } }
  ```
