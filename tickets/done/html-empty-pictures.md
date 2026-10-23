---
id: html-empty-pictures
title: TikZ pictures LaTeXML drew empty
converter: html
takes: [engine, reconvert, reread]
closed: '2026-10-23'
cost: 'engine: medium (splice the regions from the PDF); reconvert 8 papers'
---

# TikZ pictures LaTeXML drew empty

`engine` `reconvert` `reread` · html · done

**Broken.** LaTeXML turns a TikZ picture into an inline `<svg class="ltx_picture">`; for some it draws nothing (an empty `<g>`), so the picture is lost before the converter sees it. In "Knowledge Graphs" 724 of them are empty: the in-depth/brief coverage marks of Table 1 (p. 3), the axiom, condition and example cells of Tables 2–6 (pp. 13–31), the query patterns of Figure 22 and the node-and-edge drawings in the prose, which carry most worked examples. 8 papers in the 1,979 cached renderings have empty pictures, 1,157 in all. Split from `html-symbols-lost` on 23 Oct 2026.

**Fix.** Not from the PDF, as first planned: its text layer has the drawings' labels but not their order or the edges' direction ("Santa Lucía / Santiago / city"), and layout analysis would read Table 1's circles as nothing. The source has them exactly: every empty picture in "Knowledge Graphs" is a call to one of its own TikZ macros (`\gnode{Santiago}`, `\gedge{Santa Lucía}{city}{Santiago}`, `\id` for a circled ✓) or a `tikzpicture`.

Fixed 23 Oct 2026 (`empty_pictures` in `html-to-markdown.py`, run before `clean_math`): the source's pictures are listed in document order, the paper's macros (from its `.tex` and `.sty` files) and TikZ styles expanded, and each empty picture becomes its text: the edges with an arrow each, its direction from the arrow options and styles ("Santa Lucía –city→ Santiago"), then the nodes on no edge; an empty circle "○", a filled one "●", one with something set in it that ("✓"); a `tikz-qtree` `\Tree` as "Event (Festival (…), …)". A picture in a formula gets its text there (`$\#\{{a}\mid{x} \text{–} {p} \text{→} {a}\}\star n$`). The source's pictures must match the HTML's in number, and one-node pictures must be about as wide as their text, or the empty ones are marked "[picture lost]", as is a picture whose source has no text (Figure 13, a tikz-uml diagram). A mark of 1 pt a side or less (`\tikzmark`) is left alone: the other 7 papers of the first count have only such marks (Phi-4, the GCG attack paper, HackAPrompt, Self-Instruct, EuroBERT, the SSL cookbook and the continual-learning survey), which draw nothing in the PDF either, so they lose nothing and are unchanged.

Checked on Knowledge Graphs: 828 source pictures against 828 in the HTML, every one-node picture's width in line with its text; 827 filled in, 1 marked lost; Table 1's marks agree with the PDF (p. 4, rows Pan et al. and Paulheim), Tables 2–6 read "$x$ –type→ $c$ implies $x$ –type→ $d$", Figure 22 reads "$\Join$ ( ?festival –location→ Santiago $\cup$ … )", Figure 1 as its 30 edges. The markdown is 0.1% smaller (53 links to blank images gone), KaTeX parses every formula, `symptoms --compare HEAD` reports nothing. Four new checks. → [`docs/conversion.md`](../docs/conversion.md)

**What it gives.** Knowledge Graphs' comparison table and its OWL/RDFS feature tables, now unreadable.

**Cost.** Engine: medium (splice the regions from the PDF); reconvert 8 papers; re-read Knowledge Graphs.

**Examples.** "Knowledge Graphs" Table 1 (p. 3), Tables 2–6 (pp. 13–31), Figure 22 (p. 31).
