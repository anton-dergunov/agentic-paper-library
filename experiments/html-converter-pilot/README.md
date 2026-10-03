# Experiment · what does the rebuilt arXiv-HTML converter recover, and what does it break?

**Question.** A literature review had flagged 25 papers whose markdown, converted from arXiv's HTML,
was visibly broken: boxed findings and definitions present only as images, tables in `\resizebox`
flattened into one line of numbers, `forest` taxonomy trees left as empty `{forest}` placeholders,
`9.24994pt` spacing residue inside equations, headings without the PDF page they start on. Do the
converter fixes repair those papers, and do they change anything they should not on papers that
were fine?

**Status.** Run 1 Oct 2026 on the 25 flagged papers, 45 random papers and 82 papers for page
markers: **22 of the 25 catalog entries closed** (20 repaired, 2 found to be in the authors' own
source), **numbered headings without a page 25 → 0** with no existing page changed, and **no prose
lost** on the 45 random papers. The changes shipped in commit `d791f1a`; the library was then
reconverted with them.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html).

## Method

- **Corpus.** [`papers.tsv`](papers.tsv): the 25 papers listed in `catalog/conversion-issues.yaml`
  on 1 Oct 2026 (24 arXiv-HTML conversions and MemGPT, then still converted from PDF text), mostly
  `llm/memory`. [`regression-sample.tsv`](regression-sample.tsv): 45 arXiv-HTML papers drawn at
  random (seed 11) from the rest of the library. The arXiv pages, the converted markdown and the
  PDFs are not committed; titles are.
- **Apparatus.**
  - [`fetch_html.py`](fetch_html.py) caches each paper's arXiv HTML at the PDF's version.
  - [`run.py`](run.py) runs `html-to-markdown.py` on the cached pages, with figure downloads cached
    on disk, so old and new converters see identical input. `SCRIPTS` selects the converter.
  - [`compare.py`](compare.py) counts, per paper and old → new, the symptoms the catalog named:
    words, local image links, `{forest}` placeholders, `pt` residue, "flat" lines (25 or more
    decimals outside a table), empty markdown header rows, HTML tables with a `<thead>`, quote lines
    (recovered boxes), and figure links still pointing at arXiv.
  - [`pm_compare.py`](pm_compare.py) runs the old and new `page-map.py` on copies of Larimar,
    Memanto and 80 random papers (seed 3), and reports headings placed, numbered headings left
    unplaced, and every heading line that differs.
  - [`classify.py`](classify.py) sorts the library's SVG figures that contain text into box,
    badge, diagram with text, and image; [`detect.py`](detect.py) lists the library papers that
    show any symptom, to size the reconversion.

  ```bash
  # from the library's root; the old converter is this repository at d791f1a^
  python3 $X/fetch_html.py $X/papers.tsv $X/html
  mkdir old && for f in html-to-markdown.py arxiv-html.lua paperlib.py katex-commands.txt; do
    git -C <engine> show d791f1a^:scripts/$f > old/$f; done
  SCRIPTS=old HTML=$X/html python3 $X/run.py base
  HTML=$X/html python3 $X/run.py new
  python3 $X/compare.py base new           # -> symptoms-pilot.txt
  git -C <engine> show d791f1a^:scripts/page-map.py > page-map-old.py
  python3 $X/pm_compare.py page-map-old.py  # -> page-map-compare.txt
  ```
  (`X` is this folder.) `html/`, the outputs and `run.py`'s `fetch-cache/` hold paper content and
  are not committed. The same two `run.py` calls over `regression-sample.tsv` give
  `symptoms-regression.txt`.
- **Changes to the scripts as run.** Absolute paths to the private library and the session's
  scratch folder were replaced by this repository's `scripts/`, environment variables or
  arguments; `pm_compare.py` takes the old `page-map.py` as an argument and copies papers into a
  temporary folder. The logic is as run. `classify.py` is its last revision; the counts in
  [`svg-classes.txt`](svg-classes.txt) were taken with the two earlier revisions of the box rule
  recorded there.
- **Which converter.** The `new` outputs were produced during development, before the last small
  fixes in `d791f1a` (placeholder alt text, duplicate headings). The library reconversion at the
  end ([`pilot.log`](pilot.log)) used the converter as committed.

## Results

### The 25 flagged papers

Symptom totals over the 25 papers, old converter → new, from
[`symptoms-pilot.txt`](symptoms-pilot.txt):

| Symptom | Old | New | Papers changed |
|---|---|---|---|
| `{forest}` placeholders | 4 | 0 | 4 |
| `pt` spacing residue in equations | 11 | 0 | 2 |
| Flattened table lines | 16 | 0 | 4 |
| Empty markdown header rows | 60 | 8 | 19 |
| HTML tables with a header | 0 | 81 | 20 |
| Quote lines (boxes recovered as text) | 2 | 1,251 | 14 |
| Figure links still pointing at arXiv | 87 | 1 | 5 |
| Words | 502,526 | 522,306 (+3.9%) | 25 |

The one remaining arXiv link is *Memory in the Age of AI Agents*' Figure 1, which arXiv serves
truncated; it and A-TMA's Figures 2–3 (served empty) were cropped from the PDFs by hand. In the
library itself ([`library-before-after.tsv`](library-before-after.tsv)), headings carrying a page
went from 1,121 to 1,213 and none was lost: MemGPT 0 → 25 (now converted from HTML), Memanto 0 → 36,
Larimar 9 → 40.

Of the 25 catalog entries:

- **20 repaired** and removed.
- **2 are in the authors' source**, not the conversion: Mem-α's sentence that stops at
  "approximately 50" (an unescaped `%` comments out the rest of the line, in the PDF too) and M+'s
  "160 tokens" for 160k. Recorded in the papers' notes and removed.
- **3 still open**: Cartridges' two-part KV-layout equation set on one line and its Figure 8 after
  the References; Sparse Memory Finetuning's Table 1, whose result is carried by colour shading;
  *Memory in the Age of AI Agents*' unresolved `\Cref` targets showing a label ("§ what-memory")
  instead of a number.

[`symptoms-after-pilot.txt`](symptoms-after-pilot.txt) is the check of the reconverted library
copies. The headings still without a page there are unnumbered paragraph and definition headings
("Definition 1 (Environment).", "Vector Index."), which `page-map.py` leaves alone by design.

### Page markers on 82 papers

From [`page-map-compare.txt`](page-map-compare.txt):

| | Headings placed | Numbered headings unplaced |
|---|---|---|
| Old `page-map.py` | 2,786 | 25 |
| New `page-map.py` | **2,978** | **0** |

Five papers changed, all gains: IEEE numbering (`II-A`) is now recognised (Memanto, *Transformers in
Vision*, *Large Language Models: A Survey*, *Revisiting Reliability…*), and a numbered heading is no
longer placed by its bare title. That rule had put Larimar's "5 Results" on p. 15, where the title
recurs; it starts on p. 4, checked against the PDF. No page already on a heading changed.

### Regression on 45 random papers

From [`symptoms-regression.txt`](symptoms-regression.txt): words 688,958 → 692,171, empty header
rows 148 → 50, tables with a header 0 → 137, figure links pointing at arXiv 125 → 0 (now
downloaded), quote lines 45 → 635 (prompt templates in *Textbooks Are All You Need* and *Rubrics as
Rewards*). The two large word-count drops were read by hand:

- **DINO, −1,454 words.** No content: 448 `alt="Refer to caption"` placeholders removed and table
  cells turned from `<td>` to `<th>`.
- **Concept Induction, −248 words.** ACM's `\Description` figure texts, which the first version
  dropped along with the placeholders. The converter was then changed to drop only generic
  placeholders and keep authors' descriptions; the saved output predates that change.

The `pt` count left in *Faith and Fate* is `\kern 3.44444pt`, valid TeX inside a formula.

### Sizing the reconversion

[`detect.py`](detect.py) flagged **1,618 of the 1,904** arXiv-HTML papers
([`detector-counts.txt`](detector-counts.txt)): an empty header row in 1,256, a table without a
header in 1,071, text boxes drawn as SVG in 317, broken figure links in 207, flattened tables in
131. [`classify.py`](classify.py) found about 3,140 text boxes among the library's SVG figures,
mostly prompt templates. Old and new converters took the same time on two large papers (84 s); the
cost is re-encoding figures to WebP, not the new passes. So the whole library was reconverted
rather than only the flagged papers.

## Limits

- The symptom counts are pattern counts. A quote line or a `<thead>` shows that structure came
  back, not that it is right; the 25 entries were checked by hand against the catalog's
  descriptions, the 45 random papers only by word-count drops.
- Some results here were recovered from the session transcript rather than regenerated
  (`page-map-compare.txt`, `library-before-after.tsv`, `symptoms-after-pilot.txt`,
  `detector-counts.txt`, `svg-classes.txt`): they read the library as it stood on 1 Oct 2026.
