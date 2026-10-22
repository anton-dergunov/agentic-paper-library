# Experiment · pages arXiv's HTML lacks, taken from the PDF

**Question.** arXiv's HTML of some papers stops partway, leaves out appendices, or drops a page of tables LaTeXML could not set (tickets `html-incomplete` and `html-dropped-floats`). Should such a paper be converted from its PDF as a whole, or should only the pages the HTML lacks be converted from the PDF and put into the HTML conversion? And what are the 78 records filed under the two tickets?

**Status.** Run 22 Oct 2026 on the records of both tickets and six papers. **Shipped: only the missing pages, spliced into the HTML conversion.** On five papers that lacked 2 to 98 pages the markdown now lacks none, except six pages of Influence Functions whose text docling reads as pictures; 95,000 words were added and KaTeX parses all 370 formulas in them. A page whose text is all inside a picture is left out (QASC's four, of screenshots). Of the 78 records, 27 were pages the HTML lacks (26 papers, and Qwen3-VL's tables); most of the rest were not lost at all: tables in appendices the reading view leaves out (12), the paper's own text or a mistaken record (12), results given only in plots (6).

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#pages-arxivs-html-lacks).

## Method

- **The records.** Each of the 46 `html-incomplete` and 32 `html-dropped-floats` records was checked against the markdown, arXiv's cached HTML, and the PDF's text at the place it names. `page-map.py`'s `missing_pages` (a page of 120 words or more with under a quarter of its three-word sequences in the markdown) was run on every paper of both tickets.
- **The splice** (`scripts/missing-pages.py`, `convert_pages` in `scripts/pdf-to-markdown.py`). The missing pages, and a page with little text between two of them, go through docling over their span; equations and paragraphs with mathematics are read by the model as for a PDF-only paper. A page is kept with 100 words outside its pictures and captions, or between two kept pages. Each run of kept pages goes before the first heading on a later page, the reference list counting as on the page its entries are printed on (from its `(p. N)`, else the PDF page holding a quarter of the list's three-word sequences: a contents page also says "References").
- **The threshold** was set on seven pages the measure flags in papers whose HTML is whole, and on two pages of Qwen3-VL's missing tables ([probe](#the-threshold)).
- **The test papers**, reconverted with `paperlib reconvert`: Qwen3-VL (results tables), Beyond Memorization and Influence Functions (key content), Absolute Zero and Training Agents Inside of Scalable World Models (ticket examples), QASC (four flagged pages of screenshots). [`measure.py`](measure.py) gives pages lacking before (the library's HEAD) and after, the runs, the words they add and KaTeX failures inside them: [`results/measure.tsv`](results/measure.tsv).

```bash
PAPER_LIBRARY=<library> paperlib reconvert <paper.md> ...
PAPER_LIBRARY=<library> uv run python measure.py <paper.md> ... > results/measure.tsv
```

## Results

### The records

| Records | What they were | Done |
|---|---|---|
| 26, `html-incomplete`; 1, `html-dropped-floats` | pages of the PDF the HTML lacks (4 to 121; Qwen3-VL's two pages of results tables) | the splice |
| 10, `html-dropped-floats`; 2, `html-incomplete` | a table or figure the main text cites, in an appendix where the source declares it; the reader is shown the main text alone (SWAG Table 2, H2O Table 6, Pythia Table 4, BIRD Table 4, …) | the reading view names them |
| 2, `html-dropped-floats` | restored by earlier fixes (Laplace Redux Eq. 5, a formula box; the Survey of LLMs' Fig. 10) | closed |
| 12, `html-incomplete` | the paper's own text, as the PDF prints it (Attention's "three types of regularization" over two, Lottery Ticket's "up to 38", the Deadly Triad's "Thi"), or a mistaken record (SAM 3's annotation card is whole) | deleted |
| 6, `html-dropped-floats` | results given only in plots | re-filed under `figure-values-in-plots` |
| 5 | small or not the HTML's loss: a run-in heading, a contents list, colour lost in the hand conversion of Confident Learning, a listing that is an image in the PDF | wont-fix |
| 2, `html-incomplete` | Knowledge Graphs' inline TikZ drawings, empty in the HTML | re-filed as new (`html-inline-tikz-empty`) |
| 12, `html-dropped-floats` | a single float lost on a page the HTML has: tables the authors set as pictures (Megatron-LM Tables 1–2, Chameleon Table 2, DARLA Fig. 5), a `longtblr`, a `nicematrix` table, TikZ printed as source | left open |

### The threshold

docling's words outside pictures and captions on pages the measure flags:

| Page | What it is | Words | Kept |
|---|---|---|---|
| H2O p. 31 | plots of activation frequency | 29 | no |
| Chameleon p. 26 | an example drawn as a figure | 26 | no |
| SAM 3 p. 57 | example questions in a figure | 59 | no |
| Wan p. 23 | prompts under video stills | 27 | no |
| QASC pp. 13–16 | screenshots of the crowdsourcing instructions | 5–11 | no |
| ILQL pp. 26–27 | example dialogues, images in the HTML | 338, 339 | yes |
| BIRD p. 23 | a table of example questions, an image in the HTML | 480 | yes |
| Qwen3-VL pp. 15–16 | Tables 2 and 3, missing from the HTML | 709, 660 | yes |

### The test papers

| Paper | Pages | Lacking before | After | Taken | Words added | KaTeX failures |
|---|---|---|---|---|---|---|
| Qwen3-VL | 42 | 2 | 0 | pp. 15–16 | 2,795 | 0 |
| Beyond Memorization | 47 | 32 | 0 | pp. 9–10, 12–46 | 36,328 | 0 of 46 |
| Influence Functions | 119 | 98 | 6 | pp. 10–55, 58–64, 66–69, 72–109, 111, 119 | 43,823 | 0 of 299 |
| Absolute Zero | 52 | 16 | 0 | pp. 29–33, 35–36, 42–50 | 7,900 | 0 of 1 |
| Training Agents | 32 | 9 | 0 | pp. 13–17, 24–29 | 4,587 | 0 of 24 |
| QASC | 16 | 4 | 4 | none (screenshots) | 0 | – |

- **The runs land in place.** Influence Functions' 92 pages of main text and appendices go before its reference list, so the reading view now holds the paper where it held §1–2.1; Absolute Zero's example prompts go into its appendix before §D, Qwen3-VL's tables before §5.5.
- **What the splice still lacks.** Influence Functions' six pages are boxes of influential sequences that docling reads in part or as pictures (p. 71 left out as figures only). A seam falls at a page boundary, mid-word where the HTML stopped ("erably higher than expected"). Where the HTML has no reference list at all (Beyond Memorization), the PDF's list arrives only from pages that also hold text (pp. 10, 12), since a page of references is never counted as missing.
- **Table quality is docling's.** A dense table comes out with some rows run together ("80.6 69.3" in one cell of Qwen3-VL's Table 2), as in any PDF-only paper; the marker over each run says to check the PDF before quoting a table.
- **Two flaws fixed on the way.** docling gives a caption once as the text layer has it and once with the marks read from the page and its mathematics read by the model ("**Table 2:** …", "bold ." against "**bold**.", "𝑁 z = 64" against "$N_z = 64$"), and the PDF converter kept both; captions are now compared by their first eight words without marks or quotes. This affects PDF-only papers too, as does the second: a running header docling took for a heading ("### Anthropic" over 41 pages of Influence Functions) is dropped when it sits within 60 points of the page's edge on three or more pages; box titles that repeat lower on the page (Absolute Zero's "Model Output:") stay.
- **Time.** The six papers took 19 minutes with two at a time, 15 of them for Influence Functions, whose 300 formulas and paragraphs with mathematics are read by the model.

## Decision

- **Splice the missing pages; do not convert the whole paper from the PDF.** For the pages it has, arXiv's HTML holds every display equation as the author's TeX, where the PDF route reads 71% of them close ([`pdf-converter-bakeoff`](../pdf-converter-bakeoff/README.md)), and keeps its table structure and figure numbering. The splice costs what converting the missing pages costs, so it is cheaper than the whole PDF in every paper but those missing nearly all their pages, where the two are the same. Not run: a whole-PDF conversion of the five papers, since its result on the pages the HTML has is the bake-off's.
- **The splice runs on every arXiv-HTML conversion** (`paperlib add`, `paperlib reconvert`), after the page and caption passes. A paper with no missing page pays only the measure (one read of the PDF's text); one with a flagged page of figures loads docling to leave it out, about half a minute.
- **The reading view names the floats the main text cites from the part it leaves out**, so a reader stops reporting appendix tables as lost.

## Not followed up

- **Single floats** lost on a page the HTML has (12 records left under `html-dropped-floats`): the same route at the float's region, found by its caption's page, would recover the tables authors set as pictures where the PDF has their text.
- **A reference list the HTML lacks entirely**: the pages of references could be taken as well when the markdown has no list; one test paper had none.
