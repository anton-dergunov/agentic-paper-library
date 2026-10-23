---
id: html-coloured-markers
title: "A marker told apart only by its colour loses the colour"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small; reconvert the papers"
---

# A marker told apart only by its colour loses the colour

`engine` `reconvert` · html · open

**Broken.** A symbol whose colour is its meaning, a legend square or dot in a caption or the prose, keeps the symbol and loses the colour, so "comparing ■ and ■" or "Negative examples are marked with ⚫ and Positive with ⚫" no longer says which is which. arXiv's HTML has the colour on the span (`style="--ltx-fg-color:#E3494B"`). Split from `html-symbols-lost` on 23 Oct 2026.

**Fix.** A span holding only a symbol (a geometric shape, a dash, a dot) with a foreground colour becomes the symbol with its colour's name, in the form `html-image-symbols` gives icons ("[red ●]"); the colour names as `html-colour-shades` names them. Leave coloured words and numbers to the existing colour handling.

**What it gives.** Captions and legends that say which series is which.

**Cost.** Engine: small; reconvert the papers.

**Examples.** "Calibrate Before Use" Figure 5 caption (p. 4); "Rethinking the Role of Demonstrations" Figures 8–10 and §5.3 (pp. 5–6).
