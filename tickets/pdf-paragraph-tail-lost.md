---
id: pdf-paragraph-tail-lost
title: "The end of a PDF paragraph is lost after a page, column or footnote break"
converter: pdf
takes: [engine, reconvert]
status: open
cost: "engine: small to medium once the dropped region is found; reconvert the papers"
---

# The end of a PDF paragraph is lost after a page, column or footnote break

`engine` `reconvert` · pdf · open

**Broken.** A paragraph of a layout-analysis conversion stops mid-sentence, often mid-word, and the rest of it is nowhere in the markdown, although the PDF's text layer has it. The breaks seen so far sit where the paragraph continues across a page (LDA: "conditioned on features su", then the Acknowledgements), after a footnote at the foot of a column (Obsolete Answers: "and it took", the footnote URL, then "128 days on average to add new answers"), and in a boxed summary. The lost words carry numbers and claims.

**Fix.** Not known yet. Look at docling's regions on those pages: candidates are a continuation box dropped as page furniture (header, footer, footnote) or merged into the footnote it follows, and a hyphenated word split across the break. A check that compares each paragraph's last words with the text layer would find the others.

**What it gives.** Paragraphs that end where the paper's do; today an agent misses the number or the claim in the lost tail.

**Cost.** Engine: small to medium once the dropped region is found; reconvert the papers.

**Examples.** Latent Dirichlet Allocation p. 22–23, end of Section 8; An Empirical Study of Obsolete Answers on Stack Overflow p. 5, Section 4.1.2 and its summary box; GANs Trained by a Two Time-Scale Update Rule p. 7 ("mini-batches fo").
