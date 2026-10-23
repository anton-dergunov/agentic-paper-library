---
id: html-ot1-angle-glyphs
title: "\"¿\" and \"¡\" stand for \">\" and \"<\""
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small, one mapping; reconvert about 35 papers"
---

# "¿" and "¡" stand for ">" and "<"

`engine` `reconvert` · html · open

**Broken.** A ">" or "<" typed in running text comes out as "¿" or "¡": "mostly (¿85%) code data" (Llama 3, p. 16), "If g(o1)¿t" (RouterBench, p. 7), "¡html¿¡body¿" in Qwen2.5-VL's prompt format (p. 6). In LaTeX's old OT1 text encoding those two slots hold the Spanish marks, and LaTeXML follows it, so arXiv's HTML already has "¿". A comparison reads as a stray glyph: "¿85%" loses that 85% is a lower bound. Split from `html-symbols-lost` on 23 Oct 2026; 35 papers hold a "¿".

**Fix.** In the text (not in math, and not after a Spanish word or at the start of a Spanish sentence), write "¿" as ">" and "¡" as "<"; in a code block or a quoted prompt always. Check the 35 papers' hits for a real Spanish quotation first.

**What it gives.** Comparisons and markup examples that read as written.

**Cost.** Engine: small, one mapping; reconvert about 35 papers.

**Examples.** Llama 3 p. 16; RouterBench §5.2 (p. 7); Qwen2.5-VL p. 6.
