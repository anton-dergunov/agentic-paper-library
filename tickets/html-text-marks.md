---
id: html-text-marks
title: "Underline, strikethrough and un-bold in arXiv's HTML are not read"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small; reconvert the papers that use them"
---

# Underline, strikethrough and un-bold in arXiv's HTML are not read

`engine` `reconvert` · html · open

**Broken.** Marks arXiv's HTML carries in forms the converter does not map: the ulem package's underline (`ltx_ulem_uline`) and strikethrough (`text-decoration:line-through`) are dropped, and an `ltx_font_medium` span inside bold, which ends the bold, is ignored, so the bold runs on.

**Fix.** In `arxiv-html.lua`, map `ltx_ulem_uline` to Underline and a line-through style to Strikeout, and close Strong at an `ltx_font_medium` span.

**What it gives.** The second-best and excluded results tables mark, and captions whose bold stops where the paper's does.

**Cost.** Engine: small; reconvert the papers that use them.

**Examples.** "Word Rotator's Distance" Tables 1, 4, 5 (60 ulem spans in arXiv's HTML); TRUE Table 3 (p. 6, 12 struck cells); "Batch Normalization Explained" Figure 7 caption (p. 8).
