---
id: html-arxiv-text-garbled
title: Text arXiv's HTML itself garbles or leaves out
converter: html
takes: [by-hand]
reason: arXiv's HTML has the fault itself; only the PDF or the LaTeX source has the text right, and the
  gaps are small
closed: '2026-10-16'
cost: by hand, from the PDF
---

# Text arXiv's HTML itself garbles or leaves out

`by-hand` · html · wont-fix

**Broken.** arXiv's HTML already has the fault, so the markdown copies it: terms set by a macro LaTeXML does not know are missing ("In , we first learn the MDP"), an acronym prints twice ("MM-EvalMM-Eval") or fused with another, a caption breaks off mid-sentence, sub-tables carry only their letters, a footnote mark has no footnote, two lists lose the labels that tell them apart.

**Fix.** None in the HTML route. The LaTeX source would restore macro terms; the PDF has the rest.

**What it gives.** Sentences without gaps, where a term is missing.

**Cost.** By hand, from the PDF.

**Examples.** "Reinforcement Learning: An Overview" pp. 24, 48, 62, 173, 193; "LLMs-as-Judges" pp. 23, 27; QLoRA Table 7 caption (p. 10); Molmo Tables 2–3 sub-captions.
