---
id: html-approx-sign-lost
title: The "~" or "≈" before a number is lost
converter: html
takes: [engine, reconvert]
closed: '2026-10-22'
cost: 'engine: small, once the TeX form is found; reconvert the papers'
---

# The "~" or "≈" before a number is lost

`engine` `reconvert` · html · done

**Broken.** An approximation sign before a number vanishes and leaves a double space: "reduced by  50%", "with  1 TB/s memory bandwidth" (printed "~1 TB/s" elsewhere in the paper), "ASR of  60%". The reader takes an estimate for an exact figure. Split from `html-symbols-lost` on 21 Oct 2026, eight papers.

**Fix.** Find the form in arXiv's HTML (most likely `$\sim$`, `\approx` or a `\textasciitilde` set as an empty `ltx_Math` or a span the Lua filter drops) and write it as "~" or "≈".

Fixed 21 Oct 2026 ([experiment](../experiments/references-shades-and-text-macros/README.md)): the sign is in neither the HTML nor the PDF. The author typed a text-mode `~` after a space ("reduced by ~50%"), which LaTeX sets as a non-breaking space, so the PDF prints "reduced by 50%" (LiRank p. 7, the DLRM training paper p. 6, Voxtral p. 9) and the HTML a space and a no-break space. `fix_text_encoding` writes that pair between a word and a digit as " ~" in the prose, as the author meant; in the bibliography ("pp. ~12"), a number's tag ("SuppFigure ~1") and after a formula ("$\pm$~0.81") it stays a space. 111 of 1,979 cached renderings hold the pair before a digit. Fixed on LiRank, the DLRM training paper, Voxtral, Memory Poisoning and "Do Vision Transformers See Like CNNs" (14 signs); two papers are left for the overnight run.

**What it gives.** Approximate figures read as approximate.

**Cost.** Engine: small, once the TeX form is found; reconvert the papers.

**Examples.** LiRank §4.2–4.3 (p. 7); "Understanding Training Efficiency of Deep Learning Recommendation Models" §IV-B1 (p. 6); "Do Vision Transformers See Like Convolutional Neural Networks?" pp. 3–7; Voxtral p. 8.
