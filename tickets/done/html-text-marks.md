---
id: html-text-marks
title: Underline, strikethrough and un-bold in arXiv's HTML are not read
converter: html
takes: [engine, reconvert]
closed: '2026-10-16'
cost: 'engine: small; reconvert the papers that use them'
---

# Underline, strikethrough and un-bold in arXiv's HTML are not read

`engine` `reconvert` · html · done

**Broken.** Marks arXiv's HTML carries in forms the converter does not map: the ulem package's underline (`ltx_ulem_uline`) and strikethrough (`text-decoration:line-through`) are dropped, and an `ltx_font_medium` span inside bold, which ends the bold, is ignored, so the bold runs on.

**Fix.** Done 16 Oct 2026: `ltx_ulem_uline`/`uuline` are Underline, `ltx_ulem_sout` and a `line-through` style Strikeout (`~~`), a number underlined from its first digit (`\uline 80.84`) is underlined whole, and bold is split at an `ltx_font_medium` span, except in a picture's text, where TikZ and boxes set the medium series anyway. `\mdseries` near bold is in 557 papers of the cache, mostly a caption's bold title. Checked on Word Rotator's Distance, TRUE and Batch Normalization Explained. → [`experiments/colours-marks-and-icons`](../experiments/colours-marks-and-icons/README.md)

**What it gives.** The second-best and excluded results tables mark, and captions whose bold stops where the paper's does.

**Cost.** Engine: small; reconvert the papers that use them.

**Examples.** "Word Rotator's Distance" Tables 1, 4, 5 (60 ulem spans in arXiv's HTML); TRUE Table 3 (p. 6, 12 struck cells); "Batch Normalization Explained" Figure 7 caption (p. 8).
