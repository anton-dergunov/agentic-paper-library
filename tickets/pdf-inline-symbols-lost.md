---
id: pdf-inline-symbols-lost
title: "PDF paragraphs that lost their symbols without a mark"
converter: pdf
takes: [engine, reconvert]
status: open
cost: "engine: medium; reconvert the papers overnight"
---

# PDF paragraphs that lost their symbols without a mark

`engine` `reconvert` · pdf · open

**Broken.** Some paragraphs lost their symbols and left no mark in the text layer ("where the constant is included to avoid instability when is very close to zero", SSIM), so the inline-mathematics pass never reads them. Symbols set as images (CLSM's J values) go the same way.

**Fix.** Find paragraphs with ink on the page image where the text layer has no character, and read them like inline mathematics.

**What it gives.** Definitions and settings in the prose readable again; today the agent must infer them from tables or the PDF.

**Cost.** Engine: medium; reconvert the papers overnight.

**Examples.** SSIM; CLSM §5.2–5.3 (J values, p. 6–7); DSSM §3.1 (p. 2–4).
