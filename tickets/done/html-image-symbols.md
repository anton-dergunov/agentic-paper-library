---
id: html-image-symbols
title: Symbols set as small images in arXiv-HTML papers are lost
converter: html
takes: [engine, reconvert]
closed: '2026-10-16'
cost: 'engine: small to medium (one vision-model call per distinct icon, cached); reconvert the papers
  with such icons'
---

# Symbols set as small images in arXiv-HTML papers are lost

`engine` `reconvert` · html · done

**Broken.** A check mark, a cross, an icon or a logo set with `\includegraphics` in a table cell or a sentence arrives as "[figure]", an image placeholder or an empty cell. arXiv's HTML gives such images only `alt="[Uncaptioned image]"`, so the alt text does not help. When split from `html-symbols-lost`, 8 papers.

**Fix.** Done 16 Oct 2026 (`small_pictures`, `picture_text`, `paperlib.read_icon`): a picture of at most 40 px or pt a side with no text is its file's name when that says what it is (now also an `<object>`, Spider 2.0's `yes.svg`: 960 uses in 52 papers), else what Haiku reads in it through `claude -p` (a symbol bare, a word as "[Jupyter logo]", a plain shape with its colour, "[green ●]"), cached by its hash with ids stripped under the cache's `icons/`; an empty picture goes. `icon_model` sets the model, `off` keeps the pictures. 1,558 uses in 60 papers, about 330 distinct pictures. Checked on Spider 2.0, R1-Zero, the USPTO dataset, Robustness Gym, To Tune, OpenThoughts. EuroBERT's two cells are not fixable here: the badge holding the digit is empty in arXiv's HTML. → [`experiments/colours-marks-and-icons`](../experiments/colours-marks-and-icons/README.md) **After the full reconversion of 16 Oct 2026**, CheckList's "bert_bw" picture is Bert of Sesame Street, standing for BERT-base: too large a picture to be read as an icon, and the sentence that introduces it names BERT, so its record was closed as fine. EuroBERT's record is wont-fix.

**What it gives.** Feature tables that say which benchmark or method has what, and rows whose label was an icon.

**Cost.** Engine: small to medium (one vision-model call per distinct icon, cached); reconvert the papers with such icons.

**Examples.** Spider 2.0 Table 2 (check-mark columns); OpenThoughts Table 1 (logos and check marks); "Understanding R1-Zero-Like Training" Table 2 ("Unbiased?" column); "To Tune or Not to Tune" Tables 3–6 (snowflake and fire icons); CheckList Tables 1–3 (model logos); Robustness Gym Table 3 (idiom icons); EuroBERT Tables 1–2 (a digit set as an image).
