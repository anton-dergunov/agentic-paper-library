# Experiment · which converter should make a web article's markdown?

**Question.** Papers are now read from their PDF's text layer ([`reading-formats`](../reading-formats/README.md)). Web articles stay markdown: a web page is made for the browser, and its printed PDF often loses pages and figures. The engine's web converter reused the arXiv-HTML converter, its pandoc Lua filter and the KaTeX command list, all of which go with the switch. Which current web-to-markdown converter should replace it?

**Status.** Run 26 Oct 2026 on three of the library's 19 web articles, one from each kind of site, chosen at random. No model was called, so the cost was $0.
- **Defuddle** (0.19.5, on jsdom 24) kept the article as fully as the old converter: 97–99% of its sentences. It also kept every equation as TeX, the footnotes and the code blocks, plus the appendix the old converter dropped.
- **Readability + Turndown** printed every formula twice, as flattened text and then as escaped TeX, and lost the code blocks.
- **Trafilatura** dropped every heading and a third of the long article.
- **Shipped:** Defuddle, run on the page as headless Chrome renders it, with images removed and the Distill template's citation keys written into the text.

**Serves.** `paperlib add-web`; [`docs/design.md`](../../docs/design.md#decisions-log).

## Method

- **Articles.** One article from each kind of site in the library, drawn with a fixed seed (`run.py pick`):
  - *Why Momentum Really Works* (distill.pub, 1 of 6): mathematics, interactive figures.
  - *Emotion Concepts and their Function in a Large Language Model* (transformer-circuits.pub, 1 of 8): the largest web article in the library, at 52K words.
  - *Introducing Contextual Retrieval* (anthropic.com, 1 of 5 blog posts): prose, code and prompts.
- **Input.** The page as headless Chrome renders it after its scripts run (`--dump-dom`, a 20 s virtual-time budget, the desktop user agent of `add-web-article.py`), so that the KaTeX and the lazily loaded parts are in the DOM.
- **Candidates**, each with images dropped:
  - **Defuddle** 0.19.5, the extractor of Obsidian's Web Clipper, through `defuddle/node` with `markdown: true`.
  - **Readability** 0.6.0 + **Turndown** 7.2.4 with GFM tables.
  - **Trafilatura** 2.3.1, markdown with formatting and tables, `favor_recall`.
  - These were the candidates that 2026 comparisons ranked highest: [Zyte](https://www.zyte.com/blog/how-to-convert-a-website-to-markdown-for-ai-7-methods-compared/), [webforai](https://webforai.dev/benchmarks/), [Botmonster](https://botmonster.com/coding/best-10-html-to-markdown-converters-in-2026/).
  - The JavaScript ones share one DOM (`convert.mjs`). Pictures, canvases and inline SVG plots are removed first, and each empty `<d-cite key="…">` is replaced by `[key]`.
  - **Baseline:** the library's current markdown, with its image links removed.
- **Scores** (`run.py score`, [`results/summary.md`](results/summary.md), [`results/scores.json`](results/scores.json)):
  - *Coverage:* the share of sentences of 8 or more words that have 80% of their word 5-grams in the output. It is measured against two references: the rendered article element's text, and the baseline. Maths is taken out of both sides.
  - *Outside:* the share of an output's words in 5-grams found in neither reference. This is page chrome, an appendix or a footnote list the baseline left out, or text put in a new order.
  - Counts of `$…$` and `$$…$$`, headings, table rows, footnotes, captions and links.
  - Then every output was read by hand against the page and the baseline.
- **Converted text** stays in the cache. Of the three sites, only distill.pub is CC BY.

```bash
cd experiments/web-articles && npm ci
PAPER_LIBRARY=<library> uv run run.py          # pick, render, convert, score
```

## Results

| | Defuddle | Readability + Turndown | Trafilatura | Baseline |
|---|---|---|---|---|
| Covers the baseline: Momentum / Emotions / Retrieval | 0.97 / 0.99 / 0.94 | 0.78 / 0.99 / 0.91 | 0.77 / 0.66 / 0.90 | 1 |
| Covers the rendered article | 0.57 / 0.98 / 0.86 | 0.64 / 0.97 / 0.80 | 0.47 / 0.66 / 0.77 | 0.58 / 0.97 / 0.88 |
| Momentum: display / inline formulas as TeX | 95 / 239 | 0 / 0 | 0 / 168 | 67 / 197 |
| Headings (Emotions) | 96 | 94 | 0 | 94 |
| Footnotes kept as footnotes (Emotions) | 53 | 0 | 0 | 0 |
| Words (Momentum / Emotions / Retrieval) | 9,191 / 53,726 / 2,472 | 8,912 / 51,821 / 2,367 | 6,563 / 41,488 / 2,203 | 6,042 / 52,046 / 2,576 |

- **Defuddle loses nothing the baseline has.**
  - In the blog post it misses three baseline sentences: two are the old converter's own note, and one is the acknowledgements.
  - It turns KaTeX back into the author's TeX, so Momentum's equations read as they were written.
  - It keeps Momentum's appendix, which the old converter dropped. That accounts for most of its 30% "outside" and its 50% more words.
  - Its flaws: a line of interactive-figure labels at the top of Momentum (`$\star$ $+$ $-$ …`), and Distill's numbered citations set on a line of their own.
- **Readability + Turndown flattens maths.** Each formula comes out as the rendered characters followed by the escaped TeX (`wk+1\=wk−α∇f(wk).w^{k+1} = w^k-\\alpha…`): twice the tokens, and neither copy reads well. It also drops the blog post's code blocks, and with them the article's prompt template.
- **Trafilatura keeps the least.** It drops every heading, two thirds of Emotions' text and Momentum's display equations. It is the shortest output, but only because it lost the content.
- **Citations.** The Distill template's `<d-cite>` elements are empty in the DOM and carry their keys in an attribute. Without the pre-step that writes `[key]`, every candidate lost transformer-circuits' citations ("the logit lens” )"). With it, the citations read as the old converter had them.
- **What first went wrong** (fixed before scoring):
  - On jsdom 30, Defuddle's long selectors fail ("Selector exceeds maximum allowed length of 2048"). It then returns the page unprocessed, 2 MB for Momentum. Defuddle is developed against jsdom 24, which works.
  - Defuddle's `removeImages` keeps inline SVG plots, and Turndown's image rule outranks its `remove`, which let base64 PNGs through (41 MB for Emotions). Removing images from the DOM first fixes both.

## Decision

`paperlib add-web` renders the page in headless Chrome, prints the PDF for the reader, and converts the rendered DOM with Defuddle 0.19.5 on jsdom 24.1.3. Before Defuddle runs, it removes pictures and SVG plots and writes the Distill template's citation keys into the text. Neither PDF nor images are the agent's copy. The article keeps its `url`, so an agent can open the page for a figure or an interactive part. Not measured: answers to questions from each form. The differences were large enough to decide without them.

## Afterwards: the library's 19 articles

Converting all 19 web articles of the author's library ([`text-layer-switch`](../text-layer-switch/README.md)) found two more failures the three-article sample had missed, both on transformer-circuits.pub:

- **A truncated paper.** On *Circuit Tracing*, Defuddle stopped at the first interactive attribution graph (`.cg-div`, a widget of positioned boxes) and kept 18% of the old markdown's sentences. With those widgets removed first, as interactive figures, it keeps the whole paper. The converter now warns when its markdown has fewer than three quarters of the words in the article's prose (paragraphs, list items, headings, captions), so a truncation of this kind shows: the truncated conversion had 0.52 of them, the whole ones on that site 1.6–1.9.
- **Bare section headings.** Where a heading's title is a link (`§ 2 <a href="#building">Building …</a>`), Defuddle dropped the link as a permalink and left "§ 2". Links inside headings now become their text first.

With both, 18 of the 19 articles keep 82–99% of the old markdown's sentences; what they miss is mostly the old converter's own note, share buttons and bylines. *Circuit Tracing* keeps 67%: its page has been revised since it was first converted, and the missing sentences are not on it any more.
