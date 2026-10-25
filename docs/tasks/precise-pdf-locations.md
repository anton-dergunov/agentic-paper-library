# Task: cite a place in a PDF by its rectangle, and show it

An agent's citation now opens the PDF at a page, or at a named destination (`dest=table.2`) where LaTeX wrote one. A value in a table, a sentence in a long section, a label in a figure are left for the reader to find on the page. The PDF's text layer knows where every word is printed, so a citation can carry the rectangle, and the viewer can show it.

`search=<phrase>` is not the way: it opens the search bar, which is for the reader's own searches, and a phrase can occur twice on a page, or not at all where the agent's quote differs from what the PDF prints (an equation, a converted table cell, a ligature).

Two repositories: the viewer ([vscode-pdf-viewer](../../../vscode-pdf-viewer/), `src/shared/linkFormat.ts` reads `dest`, `page`, `search`) and the engine (a command that finds the rectangle, and the rules that tell an agent to use it).

## 1. The viewer: `rect=` and a gentle highlight

- A link parameter `rect=x0,y0,x1,y1` in PDF points (1/72 inch) from the page's top-left corner, as PyMuPDF reports them, on the page `page=` names; several rectangles separated by `;` for a phrase over two lines, or a table and its caption. `dest`, when present, still decides the scroll; without it, the viewer scrolls the rectangle into the middle of the view.
- Show the rectangles as a temporary overlay, never as an annotation: nothing is written to the PDF and the tab does not become dirty. A soft fill and outline in the theme's accent colour, a few points of padding, fading in so the eye goes to it; it stays until the reader clicks or scrolls away, or for a few seconds, whichever is later, and fades out. A second link to the same tab replaces it.
- Invalid or off-page rectangles are ignored, and the link still opens at its page.
- Tests: parsing (`rect` beside `dest`, `page`, a title with `&`), the conversion from top-left points to the PDF.js viewport (PDF space is bottom-left), and that a highlight never reaches the saved file.

## 2. The engine: find the rectangle

- `paperlib locate <paper> --quote "<text>" | --table N | --figure N | --equation N [--page N]` prints the page, the rectangle(s) and the link, from the PDF with PyMuPDF.
- A quote is matched with whitespace, hyphenation at line ends and ligatures normalised. It answers only when the match is unique on the page (or in the paper, without `--page`); otherwise it says how many matches there are, or none, and gives the page alone. A table or figure is its caption ("Table 2:", "Figure 3.") plus the region it labels: the table PyMuPDF's `find_tables` finds next to the caption, or the drawings and images above a figure caption, within the caption's column; failing that, the caption's own rectangle.
- A quote copied from the text layer is in the PDF by construction; one copied from the markdown may not be (LaTeX, cells the converter changed), so this works best if the agent's copy of the paper is the text layer (see the reading-formats experiment, tiers F–H).
- Fixtures: a quote that is unique, one that repeats, one that spans a line break, a table and a figure from papers in `examples/library`.

## 3. Teach the agent, in few tokens

- One rule where citations are written (the guide's citation rule, the note- and review-writing skills): a citation of a specific value, table, figure or sentence carries `page` and the `rect` from `paperlib locate`; `dest` as now for sections. Never open the PDF for the reader.
- No rectangle in notes and reviews by default: they are read for the claim, and a rectangle per number costs tokens on every later read. Measure first on 10 notes: tokens added against how often the reader follows a link.
- `editors/vscode` (the library's own extension) reads the same links, if it opens PDFs.

## Done when

20 citations taken from real answers open on the right region in the viewer (count how many `locate` finds uniquely, and why the others fail), nothing is ever saved into a PDF by the highlight, and the rule costs under about 100 tokens of the guide.
