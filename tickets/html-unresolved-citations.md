---
id: html-unresolved-citations
title: "Citations LaTeXML could not resolve"
converter: html
takes: [engine, reconvert, reread]
status: open
cost: "engine: small, a fixture; reconvert 19 papers; re-read NER only"
---

# Citations LaTeXML could not resolve

`engine` `reconvert` `reread` · html · open

**Broken.** `**?**)` and `(?)` appear where a citation was: 593 times in 19 papers when filed. The existing lookup in the LaTeX source does not catch this form.

**Fix.** Extend the lookup to it. Where the source has no `.bib`, take the author from the PDF's reference list.

**What it gives.** Baselines and related work named again; in NER the baseline rows are only "?)" today.

**Cost.** Engine: small, a fixture; reconvert 19 papers; re-read NER only.

**Examples.** fastText; "Neural Architectures for Named Entity Recognition"; BPE; "A Survey of Zero-shot Generalisation in Deep RL".
