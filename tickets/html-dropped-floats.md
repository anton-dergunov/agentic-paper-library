---
id: html-dropped-floats
title: "Tables and figures LaTeXML dropped"
converter: html
takes: [engine, reconvert, reread]
status: open
cost: "engine: medium, by the route of html-incomplete; reconvert; re-read the papers whose results are in the missing tables"
---

# Tables and figures LaTeXML dropped

`engine` `reconvert` `reread` · html · open

**Broken.** A table or figure the text cites is missing, or is only a picture where the PDF has its text.

**Fix.** Read such a float's region from the PDF: on the page whose text prints its caption, the table docling finds there (`convert_pages` in `pdf-to-markdown.py`, which `missing-pages.py` uses for whole pages), placed under the caption the HTML kept, or with its caption where the HTML has none. A table set as a picture in the PDF too stays as it is.

Looked at 22 Oct 2026 (`/fix-conversions`), over the 32 records then open. Most were not this cause:

- **12 were in the markdown.** Ten tables and figures the main text cites sit in an appendix, where arXiv's HTML places a float its source declares there (SWAG Table 2, H2O Table 6, Pythia Table 4, ILQL Tables 5–6, Prompt-to-Leaderboard Table 1, Auditing Table 2, Three Mechanisms Table 3, Diffusion vs AR Table 6, jina-v3, Bad Characters Table III); the reader, shown the main text alone, took them for lost. The reading view now names them ("The main text cites Table 6 from there: not shown, not lost"; `cited_after` in `paperlib.py`). Laplace Redux's Eq. 5 and the Survey of LLMs' Fig. 10 had been restored by earlier fixes. All 12 closed.
- **6 were results given only in plots** (Scaling Laws Beyond Fixed Durations, Emergent Abilities, the Deadly Triad, Statistical Precipice, F5-TTS, Wan): re-filed under `figure-values-in-plots`.
- **Qwen3-VL's results tables are whole pages** (pp. 15–16) arXiv's HTML lacks: taken from the PDF by `missing-pages.py` (ticket `html-incomplete`), record closed.
- **KAG's rule listing** is an image in the PDF too: wont-fix.

What is left, 12 records in 11 papers:

- **Tables the authors set as pictures**, which arXiv serves as an image and the PDF holds as text: Megatron-LM Tables 1–2 (`\includegraphics` of a PDF table; key content), Chameleon Table 2, DARLA's results table inside Fig. 5 (key content). Not yet checked for text in the PDF: BIRD Table 1's icon columns, Quantization's axis labels (Tables 4.7–4.8), the shell commands of "Deep Reinforcement Learning, a textbook", the Tinker listings of "Reinforcement Learning. An Overview".
- **Tables LaTeXML could not set**, on pages the HTML otherwise has: the 17-benchmark appendix table of "Establishing Best Practices" (`longtblr`, 14 undefined), SAM 3 Table 19 (`nicematrix` `\Block`).
- **TikZ drawings** printed as their source ("Real numbers, data science and chaos") or lost (the block-decomposition example of "Transformers are SSMs", p. 17).

**What it gives.** Results tables back where the findings rest on them.

**Cost.** Engine: medium, by the route of html-incomplete; reconvert; re-read the papers whose results are in the missing tables.

**Examples.** "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM" Tables 1–2 (pp. 7–8, pictures); "DARLA" Fig. 5 (p. 8, a results table set as a figure); "Establishing Best Practices for Building Rigorous Agentic Benchmarks" (a `longtblr` of 17 benchmarks); "SAM 3" Table 19 (p. 26, `\Block`).
