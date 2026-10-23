---
id: html-unresolved-citations
title: Citations LaTeXML could not resolve
converter: html
takes: [engine, reconvert, reread]
status: fixed
cost: 'engine: small, a fixture; reconvert 19 papers; re-read NER only'
---

# Citations LaTeXML could not resolve

`engine` `reconvert` `reread` · html · fixed

**Broken.** `**?**)` and `(?)` appear where a citation was: 593 times in 19 papers when filed. The existing lookup in the LaTeX source does not catch this form.

**Fix.** Done 23 Oct 2026 in `html-to-markdown.py` (`unknown_citations`, `citations_from_bbl`). The lookup now takes every form LaTeXML leaves for a citation it could not resolve: "( ?)", "(?)", "(?, ?)", "[ ?]", an empty "( )", and in the running text "? (?)", a bold "?" and a bare "?)". As before, each one's keys come from the `\cite` that follows the same words in the LaTeX source. A citation before it, resolved or not, now stands for a `\cite` there, so "used [Bazzi (2000)]. **?**) investigate" finds `\newcite{mikolov2012}`, not Bazzi's. Five words that lead to two places are widened to up to ten ("CLBL refers to the work of … CANLM refers to the work of"). A link's address and a colour's name (`\rowcolor{Gray}`) may stand between the words. Labels come from the compiled bibliography (`.bbl`) as the paper prints them (natbib, ACL's `\citename`, apacite's `\BCAY`, `\citeauthoryear`, harvard, numbered), and from the `.bib` by citeproc for the rest. That also fills in the BibTeX-key form for papers that ship only a `.bbl`. No PDF fallback was needed: every test paper has a `.bbl`. Checked on NER, fastText, BPE, the zero-shot RL survey (345 → 10), Novelty and Primacy (6 plus 44 keys), Enriching Word Vectors and the Transformer catalog (94 → 8). Left: apacite's possessive "?’s (?, ?)", and catalog entries whose words before a citation include the section number. Not this cause, and closed or re-filed: raw keys and the empty "( )" the PDFs print too (the papers' own slips), and citations missing only their year or author (re-filed `new`).

**What it gives.** Baselines and related work named again; in NER the baseline rows are only "?)" today.

**Cost.** Engine: small, a fixture; reconvert 19 papers; re-read NER only.

**Examples.** fastText; "Neural Architectures for Named Entity Recognition"; BPE; "A Survey of Zero-shot Generalisation in Deep RL".
