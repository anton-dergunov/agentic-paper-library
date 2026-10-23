---
id: html-empty-pictures
title: "TikZ pictures LaTeXML drew empty"
converter: html
takes: [engine, reconvert, reread]
status: open
cost: "engine: medium (splice the regions from the PDF); reconvert 8 papers"
---

# TikZ pictures LaTeXML drew empty

`engine` `reconvert` `reread` · html · open

**Broken.** LaTeXML turns a TikZ picture into an inline `<svg class="ltx_picture">`; for some it draws nothing (an empty `<g>`), so the picture is lost before the converter sees it. In "Knowledge Graphs" 724 of them are empty: the in-depth/brief coverage marks of Table 1 (p. 3), the axiom, condition and example cells of Tables 2–6 (pp. 13–31), the query patterns of Figure 22 and the node-and-edge drawings in the prose, which carry most worked examples. 8 papers in the 1,979 cached renderings have empty pictures, 1,157 in all. Split from `html-symbols-lost` on 23 Oct 2026.

**Fix.** Not from the HTML. Splice the table or page that holds empty pictures from the PDF, as `html-incomplete` does for missing pages (layout analysis), when the empty pictures are many or in a table; mark a lone one in prose "[picture lost]". Check on Knowledge Graphs Tables 1–2 first.

**What it gives.** Knowledge Graphs' comparison table and its OWL/RDFS feature tables, now unreadable.

**Cost.** Engine: medium (splice the regions from the PDF); reconvert 8 papers; re-read Knowledge Graphs.

**Examples.** "Knowledge Graphs" Table 1 (p. 3), Tables 2–6 (pp. 13–31), Figure 22 (p. 31).
