---
id: html-image-symbols
title: "Symbols set as small images in arXiv-HTML papers are lost"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small to medium (one vision-model call per distinct icon, cached); reconvert the papers with such icons"
---

# Symbols set as small images in arXiv-HTML papers are lost

`engine` `reconvert` · html · open

**Broken.** A check mark, a cross, an icon or a logo set with `\includegraphics` in a table cell or a sentence arrives as "[figure]", an image placeholder or an empty cell. arXiv's HTML gives such images only `alt="[Uncaptioned image]"`, so the alt text does not help. When split from `html-symbols-lost`, 8 papers.

**Fix.** Read each small inline image (a few tens of pixels, inside a table cell or a paragraph) once with a vision model into a symbol or a short word (✓, ✗, ❄, 🔥, "BERT"), cached by the image's hash, and put that in its place; fall back to the image's file name when it says what it is (`bert_bw`).

**What it gives.** Feature tables that say which benchmark or method has what, and rows whose label was an icon.

**Cost.** Engine: small to medium (one vision-model call per distinct icon, cached); reconvert the papers with such icons.

**Examples.** Spider 2.0 Table 2 (check-mark columns); OpenThoughts Table 1 (logos and check marks); "Understanding R1-Zero-Like Training" Table 2 ("Unbiased?" column); "To Tune or Not to Tune" Tables 3–6 (snowflake and fire icons); CheckList Tables 1–3 (model logos); Robustness Gym Table 3 (idiom icons); EuroBERT Tables 1–2 (a digit set as an image).
