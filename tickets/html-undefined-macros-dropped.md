---
id: html-undefined-macros-dropped
title: "A macro LaTeXML did not know is dropped with its meaning"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small to medium, a mapping plus the source's definitions; reconvert the papers"
---

# A macro LaTeXML did not know is dropped with its meaning

`engine` `reconvert` · html · open

**Broken.** LaTeXML leaves a macro it cannot expand as `<span class="ltx_ERROR undefined">\vs</span>`, and the converter drops the span. Most are layout or front matter and rightly go (`\State`, `\xspace`, `\cellcolor`, `\NoHyper`), but some carry the text: Cosmos's "17% higher throughput than H100 (0.0674 0.0574)" lost its `\vs`, and also `\eg`, `\ie`, `\etc` 37 times; AlphaZero's principal variations lost the pieces `\symknight`, `\symbishop`, `\symrook` ("g3 d5 cxd5 f6 g2 xd5"); the piano-transcription paper's accidentals (`\musDoubleSharp`, `\musDoubleFlat`) are blank; The Power of Noise's `\dice` marks the random documents (25 uses). In the 1,979 cached renderings: 1,925 such spans, 186 distinct macros. Split from `html-symbols-lost` on 23 Oct 2026.

**Fix.** Write a known text macro as its text (`\vs` "vs.", `\eg` "e.g.", `\ie` "i.e.", `\etc` "etc.", chess pieces as K Q R B N, `\musSharp` ♯, `\musFlat` ♭, `\musDoubleSharp` 𝄪, `\musDoubleFlat` 𝄫); otherwise take its definition from the LaTeX source (shared with `html-own-macros-as-names`) when it expands to text or a symbol; keep dropping the layout and front-matter ones (a list). An unknown one inside a sentence that still has no meaning can stay out.

**What it gives.** Comparisons, chess lines and notes that read as printed.

**Cost.** Engine: small to medium, a mapping plus the source's definitions; reconvert the papers.

**Examples.** Cosmos p. 8; "Mastering Chess and Shogi by Self-Play" Table 2; "End-to-end Piano Performance-MIDI to Score Conversion" Table 1 (p. 2); The Power of Noise Tables 1–5.
