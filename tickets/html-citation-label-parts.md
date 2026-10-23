---
id: html-citation-label-parts
title: "A citation's label has lost its author or year"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: small to medium, once the forms are seen; reconvert 4 papers"
---

# A citation's label has lost its author or year

`engine` `reconvert` · html · open

**Broken.** A resolved citation prints with part of its label missing or garbled: "[et al., 2016a]", "[Shan et al.,]" (Deep Interest Network), "Wang, 533Z", "Zeng et al., 0 11" (the data-synthesis survey), a bare "[1]" for a dataset the paper names elsewhere (Inference economics), or the raw key "Yang:naacl2016:HAN" (BERT4Rec). Re-filed from `html-unresolved-citations`, whose fix covers citations LaTeXML could not resolve at all, on 23 Oct 2026.

**Fix.** Not known yet: check each against the PDF first, since raw keys are often the paper's own slip. Where the PDF is right, take the label from the compiled bibliography (`.bbl`) as `citations_from_bbl` does for unresolved ones.

**What it gives.** Baselines and sources named in full.

**Cost.** Engine: small to medium, once the forms are seen; reconvert 4 papers.

**Examples.** Deep Interest Network pp. 1–6; "A Survey on Data Synthesis and Augmentation for Large Language Models"; BERT4Rec §2.3 (p. 2); "Inference economics of language models" pp. 1–21.
