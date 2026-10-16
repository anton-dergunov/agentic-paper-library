# Experiment · four tickets in one pass: several colours in a table, ulem's marks and the end of bold, symbols set as small pictures, and links to the paper's own page

**Question.** Four tickets (`html-table-colours`, `html-text-marks`, `html-image-symbols`, `html-self-links`) named marking that arXiv's HTML carries and the converter dropped: a table's colours when it has more than one, underlining and striking out from the ulem package, the place where bold ends, check marks and logos set as small pictures, and links to the paper's own arXiv page. What does each take, and what does it change across the library?

**Status.** Run 16 Oct 2026 on the 1,974 cached arXiv renderings, 19 papers of the author's library chosen for the tickets and 30 at random. **Tables whose colours are marked went from 160 in 90 papers to 327 in 173, 4,225 of the 5,516 marks naming their colour; 1,558 small pictures in 60 papers are read by Haiku, about 330 distinct ones; 960 `<object>` icons in 52 papers take their file's name; the 30 random papers grew 0.03%, 4 of them changed, no word of any paper was lost.** The icon readings cost about $0.0002 each.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html).

## Method

- **Where each comes from.** The examples the tickets give were read in arXiv's HTML beside the library's markdown.
  - Colours: the rule of [`table-emphasis`](../table-emphasis/README.md) marked one colour only, and looked at a table's text colour only when it had no shading. SAM 3's Table 1 shades its Human row and sets the closed-set numbers in gray text, and the caption is about the numbers ("Gray numbers indicate …"): the Human row was marked. A caption may also name no colour and show it instead ("A Survey of Agent Memory …", Table 4: a green ✓ "explicitly covered", a gray ✓ "partially covered").
  - Marks: ulem's `\uline`, `\uuline` and `\sout` arrive as `ltx_ulem_*` spans, `\st` as a `line-through` style; `\mdseries` inside bold as an `ltx_font_medium` span, which pandoc's reading of the spans ignored, so the bold ran on to the end of the caption. ulem's `\uline` takes one token, so `\uline 80.84` underlines the "8" ("Entity Matching using Large Language Models", Table 2).
  - Pictures: an `<img>` with a file name was already named by it; an `<object>` (Spider 2.0's `yes.svg`, `not.svg`) got no alt text at all. A TikZ drawing (the crosses of "Understanding R1-Zero-Like Training", Table 2) or a picture named `x1.svg` says nothing in its markup. Many of the drawings are empty 1×1 pictures (`tikzmark` anchors), which became an image file and "[figure]".
  - Links: four renderings in the cache write their table of contents and cross-references as `https://arxiv.org/html/<id>v<n>#S1.SS1`.
- **Apparatus.**
  - [`survey.py`](survey.py) classified every table float with two or more colours by whether its caption names them or shows them in coloured text of its own.
  - [`shading_compare.py`](shading_compare.py) ran the old `mark_shading` (`git show HEAD:scripts/html-to-markdown.py > h2m_old.py`) and the new one over every cached rendering → [`shading-compare.tsv`](shading-compare.tsv); tables were then read in a random sample and in every paper that lost marks.
  - [`collect.py`](collect.py) drew 66 distinct small pictures from 30 papers; [`readall.py`](readall.py) read them with Haiku 4.5 and Sonnet 5.5 → [`read-haiku.json`](read-haiku.json), [`read-sonnet.json`](read-sonnet.json), graded by eye against the rendered pictures. [`distinct.py`](distinct.py) counted what a reconversion would read.
  - The 19 papers of [`test-papers.tsv`](test-papers.tsv) were reconverted in the library and the 30 of [`sample.tsv`](sample.tsv) (seed 20261016, arXiv-HTML papers not edited by hand) in a git worktree of it; [`words.py`](words.py) compared each paper's words with the last commit, link targets aside, and `paperlib symptoms --compare HEAD` the symptoms.

  ```bash
  uv run python survey.py
  git show HEAD:scripts/html-to-markdown.py > h2m_old.py && uv run python shading_compare.py
  uv run python collect.py && uv run python readall.py haiku && uv run python readall.py sonnet
  uv run python distinct.py
  paperlib reconvert --jobs 4 $(cat sample.tsv)      # in a worktree of the library, PAPER_LIBRARY set to it
  python3 words.py <paper.md>
  ```

## Results

### Colours

Of the table floats with two or more colours, 848 have a caption that refers to none of them, 46 name them, 96 show them in a legend and 80 do both. The rule kept: a colour is marked where the caption names it, by its own word ("the red denotes the highest", with the neighbouring hues allowed, as a light red is "red" to the caption and pink to the hue), or sets text in it; where one name fits a shading and a text colour both, "gray numbers" and "grayed out" mean the text. A table with one colour keeps `<mark>`; with several, each mark says which: `<mark class="red">`.

| In 1,974 renderings | Before | After |
|---|---|---|
| Tables with marks | 160 | 327 |
| Papers with marks | 90 | 173 |
| Marks | 1,076 | 5,516 |
| of them naming a colour | 0 | 4,225 |

- **The colours named**: green 1,136, red 1,019, blue 682, orange 572, gray 453, gold 126, pink 80, cyan 78, yellow 38, purple 34.
- **One paper lost marks, rightly.** Tülu 3's Table 7 had 42 marks on rows shaded for grouping; its caption is about the new datasets, set in pink text, and those 10 are what is marked now.
- **White text is not a colour.** A first run named 154 marks "white": white text on a dark cell. White and black are left out in both layers.
- **Noise seen in a sample of eight tables**: a brand colour a caption sets a model's name in (Olmo 3, Table 33, 3 cells), and a caption's legend of coloured task boxes whose pink also marks two unrelated cells ("LLMs Get Lost In Multi-Turn Conversation", Table 1).
- **In the test papers** MM-LLMs Table 2 separates best (red) from second best (blue); SAM 3 Table 1 marks the gray numbers and not the Human row; the Piano-MIDI Table 6 marks its invalid values; the agent-memory survey's Table 4 and its legend mark 81 green, 41 gray and 31 red signs; Checklists Tables 2–4 carry better, worse and neutral (blue, orange, gray), 5% more characters for that paper.

### Marks

| | Papers in the cache |
|---|---|
| `ltx_ulem_uline` | 19 |
| `ltx_ulem_sout` | 6 |
| `ltx_ulem_uuline` | 1 |
| `line-through` style | 3 |
| `ltx_font_medium` near bold, in text | 557 |
| `ltx_font_medium` near bold, inside a picture | 136 |

- **Kept**: "Word Rotator's Distance" 45 underlines (none before), TRUE's struck-out cells (`~~93.2~~`), "Batch Normalization Explained" Figure 7's caption in bold only on its colour names.
- **`\mdseries` inside a picture says nothing.** A TikZ node or a box sets its text in the medium series: EuroBERT's rank badges read "<b>95.1</b>1", and a box of model output lost all its bold. The class is ignored inside pictures; there the bold runs on as before.
- **In text the end of bold is where the paper ends it**: of 12 sampled places, caption titles ("**Overview of the proposed evaluation**. A controlled random …"), run-in headings ("**WKV head construction.** For any …"), a footnote mark after a bold value. Two of the 30 random papers changed this way (Harmony's proof steps, "**(⟹)** Let X …").

### Small pictures

| In 1,974 renderings | Uses | Papers | Distinct |
|---|---|---|---|
| `<object>` named by its file (`yes.svg`) | 960 | 52 | 178 |
| A generic name, or a TikZ drawing with no text | 1,558 | 60 | 330 |

Of the 66 sampled pictures, 30 are empty: one colour throughout, read without a request.

| 36 drawn pictures | Haiku 4.5 | Sonnet 5.5 |
|---|---|---|
| Reply unusable (over 3 words or 30 characters, or an error) | 1 | 8 |
| ✓ ✗ ○ ● ★ arrows, logos read | all the others | all the others |

- **Haiku**: cheaper and keeps to the reply's form. Sonnet wrote "❶" for a circled one where Haiku wrote "1", and failed on lamps, logos and a gradient.
- **Colour is the point of a dot.** With the first prompt both models read six coloured dots as "●"; told to name a plain shape's colour, Haiku writes "green ●", "red ○", "blue ■", now and then a shade ("dusty rose", "steel blue").
- **Ids are not the picture.** The same drawing used twice differs only in its ids; they are dropped before the picture is hashed, which leaves 330 distinct pictures to read for 1,558 uses.
- **In the test papers**: Spider 2.0's feature columns read `yes`/`not`, R1-Zero's "Unbiased?" column ✗, the USPTO dataset's field columns ✓, Robustness Gym's idiom icons and their legend "[light blue ■] → subpopulations, [pink ■] → evaluation sets, [orange ■] → transformations". EuroBERT's two badges with a digit missing are empty in arXiv's HTML; nothing recovers the digit.

### Links

The four renderings with links to their own page lost them all: 195, 195, 134 and 95 links became in-page links, and with them the hover titles the filter drops for in-page links. Those papers are 8–13% shorter in characters, with no word of the text lost (words.py).

### The papers, reconverted

| | Test papers (19) | Random papers (30) |
|---|---|---|
| Changed | 19 | 4 |
| Characters | −1.35% (+0.12% without the four with self-links) | +0.03% |
| Words lost, image paths aside | 0 | 0 |
| Symptoms (`paperlib symptoms`) | none before or after | none new |

## What the numbers do not say

The colour rule's success was judged by reading tables (the ticket's four examples, eight sampled, one that lost marks), not by asking a model questions as [`table-emphasis`](../table-emphasis/README.md) did. The caption-word match is a word list and fires on any colour word, also one about a figure, when the table holds that colour. Colours of text inside a cell (a span in a case study's prose) are not marked, nor are heat maps. The icon grades are one reading of 36 pictures by the author of the change; the readings are a model's, and a word for an icon ("gold chevron" for an arrow) can be worse than the file name it replaces, which is used whenever it says something.

## Findings

- A table's colours are marked where the caption names them or shows them; several colours carry their names. Shipped.
- ulem's underline and strike-out are kept, and bold ends at `\mdseries` in text, not in pictures. Shipped.
- A small picture is its file's name when that says what it is, else what Haiku reads in it, cached by its hash; an empty one goes. Shipped, `icon_model` in `paper-library.yaml` (`off` keeps the pictures).
- Links to the paper's own page are in-page links. Shipped.
