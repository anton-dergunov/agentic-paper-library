---
id: pdf-equation-number-only
title: PDF equations that are only their number
converter: pdf
takes: [engine, reconvert, reread]
status: fixed
cost: 'engine: medium, measured on the papers; reconvert them overnight (about 3 hours); re-read those
  whose claims rest on the equations'
---

# PDF equations that are only their number

`engine` `reconvert` `reread` · pdf · fixed

**Broken.** A display equation reads `$$(7)$$`: the crop held the number and not the formula. When filed, 97 equations in 42 PDF papers.

**Fix.** Done 19 Oct 2026, two causes. Mostly (101 of 112 equations) docling's box was right and surya's reading of it flips on a point of margin: GPT-1's Eq. 5 reads as `(5)` from the box and in full from it grown by 2 pt. In PDFs whose formula has no text layer (Word's, old Distiller's), docling fits the box to the number alone (DSSM Eqs. 3–4, 12 pt wide). A number-only reading is now read again from the box grown by 2 pt, then, for a narrow box, from the band between the blocks above and below across their column; a reading is kept when it has the same number, or, from the grown box, reads as mathematics without one; else the raw text is written if it holds more than the number. Checked on GPT-1, DSSM, Cumulated Gain and SSIM. Left: equations whose band holds other text or that the model cannot read (DSSM Eqs. 13, 15). → [`experiments/pdf-equation-retry-and-table-marks`](../experiments/pdf-equation-retry-and-table-marks/README.md)

**What it gives.** The paper's method and derivations readable without the PDF; the commonest reason a PDF paper's key equation is missing.

**Cost.** Engine: medium, measured on the papers; reconvert them overnight (about 3 hours); re-read those whose claims rest on the equations.

**Examples.** "Elucidating the Design Space of Diffusion-Based Generative Models" (12 equations); CLSM Eq. (2) (p. 4); DSSM Eqs. (3)–(4) (p. 2).
