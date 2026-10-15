# Task: conversion follow-ups

What is open in the converters and in the conversion of the author's library (`~/papers`); the examples and counts are from that library. Each item says what is broken, how to fix it, and what it takes:

- **Engine**: a change to the converters, with a fixture in `tests/test_conversion.py` and, where the rules in `AGENTS.md` ask for it, a measurement in `experiments/`. New papers get it at once; papers already in a library only through a reconversion.
- **Reconvert**: `paperlib reconvert` on the papers named. An arXiv-HTML paper takes seconds (the whole library's HTML papers took under two hours on 2026-10-10). A PDF paper takes about 3 minutes, and a 100,000-word report more than an hour (2026-10-14: 279 papers in 20.5 hours at one job). Run a long one overnight, at one job and low priority, so that the laptop stays usable: `caffeinate -i nice -n 19 paperlib reconvert … --jobs 1`. `taskpolicy -b` instead of `nice` keeps it on the efficiency cores, which is slower still.
- **Re-read**: `paperlib read --redo <papers>`, about $0.30 a paper with Opus. Needed only where a change can alter what a note says (a table, an equation a claim rests on, missing text), not for a reference's number or an icon's name.
- **By hand**: an edit in the paper, marked `<!-- hand-edited -->`.

A new paper needs nothing from the reader: `paperlib add-arxiv` and `add-pdf` run every converter step there is. The engine items below improve what new papers get once they are done.

## A. Finish the PDF reconversion of 2026-10-14

Both runs are done (`reconvert-pdf-2026-10-08.jsonl`, `reconvert-pdf-inline.jsonl`); no paper shrank. What is left, in order, in `~/papers`:

1. **Five papers lost their equations.** The equation model had one 30-minute limit per paper, which the inline mathematics of a long paper outran, so their equations are raw text: "Anytime-Valid Linear Models…", "Reinforcement Learning for LLM Post-Training. A Survey", "A Tutorial on Markov Chain Monte-Carlo…", "International AI Safety Report 2026", "The Algorithmic Foundations of Differential Privacy". The limit now grows with the paper. Two more crashed in the OCR: "Unbiased Learning to Rank. On Recent Advances…" and "Improving Cloud Storage Search with User Activity". Put the five back, commit the rest of the run, and convert the seven again overnight (takes: reconvert, several hours):
   ```sh
   cd ~/papers
   cat > /tmp/rerun.txt <<'EOF'
   library/experimentation-and-metrics/ab-testing/Anytime-Valid Linear Models and Regression Adjusted Causal Inference in Randomized Experiments.md
   library/llm/post-training/rl-for-reasoning/Reinforcement Learning for LLM Post-Training. A Survey.md
   library/ml-foundations/probabilistic-and-statistics/A Tutorial on Markov Chain Monte-Carlo and Bayesian Modeling.md
   library/trustworthy-ml/ai-safety/International AI Safety Report 2026.md
   library/trustworthy-ml/privacy-and-federated/The Algorithmic Foundations of Differential Privacy.md
   library/search-and-ranking/click-models-and-unbiased-ltr/Unbiased Learning to Rank. On Recent Advances and Practical Applications.md
   library/search-and-ranking/search-systems/Improving Cloud Storage Search with User Activity.md
   EOF
   head -5 /tmp/rerun.txt | tr '\n' '\0' | xargs -0 git restore --staged --worktree --
   git commit -m "…"    # the rest of the reconversion
   tr '\n' '\0' < /tmp/rerun.txt | xargs -0 caffeinate -i nice -n 19 \
     paperlib reconvert --pdf-text --inline-math --jobs 1 --state ~/.cache/papers/reconvert-pdf-rerun.jsonl
   ```
   A state line that still says "equation model failed" or "fell back to the text layer": `git restore` that paper and report it here.
2. **"A Latent Semantic Model with Convolutional-Pooling Structure for Information Retrieval"** was skipped as hand-edited, and its equations are blank (takes: reconvert, by hand): `paperlib reconvert --pdf-text --inline-math --force <paper.md>`, then restore the row labels and captions on p. 7 from the page and mark the edit. The five other hand-edited PDF papers stay as they are.
3. **Re-read the thoroughly converted papers** (takes: re-read, 32 papers, about $12). Their notes describe the old conversion's tables and equations. "Command A" was read again already; "A Latent Semantic Model…" follows step 2.
   ```sh
   grep -v -e 'Command A' -e 'A Latent Semantic Model' docs/tasks/pdf-reconversion-papers.txt \
     | tr '\n' '\0' | xargs -0 paperlib read --redo --jobs 2
   ```
   The 39 other PDF papers whose notes predate the run gained only inline mathematics, which seldom changes a digest. They are listed in `docs/tasks/reread-after-inline-math.txt`: re-read an area's share of them before its next review (about $8 for all), then delete the list.
4. `paperlib conversion-issues`, then `/fix-conversions search-and-ranking` and the two `llm` papers of the list: replace each catalog entry with what the new note reports, or remove it. Check the PDF before marking key content broken.
5. `paperlib check`, delete `pdf-reconversion-papers.txt`, commit.

## B. Engine fixes, most useful first

The counts come from the notes of 986 papers read by 2026-10-15 and from searching the library's markdown.

1. **References to floats that share an anchor print the wrong number.**
   - *Broken:* arXiv's HTML puts two figures in one float with one anchor, and every reference to either names the second. ViT's Figures 3 and 4 share `S4.F4`, so its references to Figure 3 read "Figure [4]". At least 17 read papers report numbers off by one (BERTScore, HuBERT, RMSNorm, mixup, "Delving Deep into Rectifiers", "Stop Regressing", MiniCPM).
   - *Fix:* in `caption-numbers.py`, for a link to a float that holds several captions, take the number the PDF prints after the same words.
   - *Takes:* engine change, measured on those 17 papers; then reconvert the papers with such floats. No re-read.
2. **PDF equations that are only their number.**
   - *Broken:* 97 display equations in 42 PDF papers are `$$(7)$$`: the crop held the number and not the formula ("Elucidating the Design Space of Diffusion-Based Generative Models" has 12). Some paragraphs also lost their symbols without leaving any mark ("where the constant is included to avoid instability when is very close to zero", SSIM), so the inline pass never reads them.
   - *Fix:* widen a number-only equation's crop to the band between its neighbouring blocks and read it again. Find paragraphs with ink on the page image where the text layer has no character, and read them like inline mathematics.
   - *Takes:* engine change, measured on the 42 papers; reconvert them (about 3 hours, overnight); re-read those with notes whose claims rest on the equations.
3. **Colour marking with more than one colour is dropped.**
   - *Broken:* shading or coloured text is kept only when the caption names it and the table has one colour. 28 notes report a lost colour, three as key content: SAM 3 Table 1 (grey: trained on the closed set), "End-to-end Piano Performance-MIDI to Score Conversion" Table 6 (grey: invalid values), and "A Survey of Agent Memory in the Second Half" Table 4 (two kinds of ✓). Red/blue for best and second best becomes bold for both (MM-LLMs Table 2).
   - *Fix:* keep each colour the caption names, marked with its name.
   - *Takes:* engine change, measured as in [`experiments/table-emphasis`](../../experiments/table-emphasis/README.md); reconvert the papers affected; re-read the three.
4. **Citations LaTeXML could not resolve.**
   - *Broken:* `**?**)` and `(?)` appear 593 times in 19 papers: fastText, "Neural Architectures for Named Entity Recognition" (its baseline rows are only "?)"), BPE, "A Survey of Zero-shot Generalisation in Deep RL". The existing lookup in the LaTeX source does not catch this form.
   - *Fix:* extend the lookup to it. Where the source has no `.bib`, take the author from the PDF's reference list.
   - *Takes:* engine change, a fixture; reconvert the 19. A re-read only for NER.
5. **LaTeXML's macros left in formulas.**
   - *Broken:* `\operatorname{mathbfcal}`, `displaystyleh`, `textsubscript`, the physics package's `quantity` and `expectationvalue`, and `[1.0]{-}` for a minus sign, 396 in 20 papers. `0pt` appears in 88 papers and may be a length or a lost symbol ("depth $0pt$" where L was meant).
   - *Fix:* map them in `arxiv-html.lua`; inspect the `0pt` cases first.
   - *Takes:* engine change, fixtures; reconvert the papers. No re-read.
6. **Page markers in long documents.**
   - *Broken:* books and tutorials have sparse or out-of-order markers, so notes cite wrong pages: "A Tutorial on Thompson Sampling" and "An Introduction to Conditional Random Fields" (none from Chapter 3 on), "Deep Reinforcement Learning, a textbook", "Introduction to Multi-Armed Bandits", "Understanding Diffusion Models", "Mastering Chess and Shogi by Self-Play" (all on p. 1), MMMU, "The Implicit Bias of Gradient Descent on Separable Data".
   - *Fix:* in `page-map.py`, search the page text for every heading without a marker, and drop a marker that goes backwards.
   - *Takes:* engine change, measured on these 8; reconvert them. No re-read.
7. **The reader reports the paper's own errors as conversion problems.**
   - *Broken:* 55 of 246 HTML notes with a problem describe numbers the paper itself prints inconsistently, which are not a conversion fault and add work to `/fix-conversions`.
   - *Fix:* in `guide/reading-prompt.md`, a disagreement between two printed numbers goes in the digest, unless digits look garbled.
   - *Takes:* prompt change, measured on a few papers as in [`experiments/prompt-trim`](../../experiments/prompt-trim/README.md). No re-read.
8. **A model's reading of an equation that does not parse** (PDF papers).
   - *Broken:* the reading can have unbalanced braces or delimiters. `paperlib symptoms --katex` finds 66 equations in 28 papers; 28 of them are the TeX of item 12, and 13 of the 28 papers are PDF ones.
   - *Fix:* check each reading with KaTeX when it is made, and read again one that fails.
   - *Takes:* engine change; it reaches the library's PDF papers with their next reconversion.
9. **Tables that are images.**
   - *Broken:* their numbers come from OCR and differ a little from run to run, while the note at the top of the paper says the numbers are the PDF's own (TabPFN's Extended Data tables, pp. 18–23).
   - *Fix:* say so in the note when a table had no text layer under it.
   - *Takes:* engine change; reconvert the papers with such tables.
10. **arXiv HTML that is incomplete.**
    - *Broken:* 27 papers in `catalog/conversion-issues.yaml` miss eight pages or a quarter of the paper (the GPT-4 Technical Report has no System Card; "Studying Large Language Model Generalization with Influence Functions" ends at §2.1; "Sparks of Artificial General Intelligence" ends at §3.1.2; "Training Agents Inside of Scalable World Models" ends in §4.2). `paperlib symptoms --pages` lists 73 papers missing three pages or more.
    - *Fix:* `paperlib reconvert` cannot convert a `source: html` paper from its PDF. Add `--from-pdf`, and compare it on five papers with adding only the missing pages to the HTML conversion.
    - *Takes:* engine change and a measurement; reconvert the papers (PDF speed); re-read them, about $0.30 each.
11. **Floats and figures LaTeXML dropped.**
    - *Broken:* tables cited but missing: "Establishing Best Practices for Building Rigorous Agentic Benchmarks" (a `longtblr` of 17 benchmarks), Qwen3-VL's results tables ("results_flagship"), "A Simple Baseline for Bayesian Uncertainty in Deep Learning" Table 2, "Offline RL for Natural Language Generation with Implicit Language Q Learning" Tables 5–6, "Bad Characters" Table III. Figures arXiv does not serve still link to arXiv (16 papers, `figure-link` in `paperlib symptoms`).
    - *Fix:* take such a table or figure from the PDF, by the route of item 10.
    - *Takes:* engine change; reconvert; re-read the papers whose results are in the missing tables.
12. **TeX that KaTeX does not draw.**
    - *Broken:* a `tabular` or an `\includegraphics` inside a formula stays as its TeX (23 formulas in 4 papers, 20 of them in CheckList). A `NiceArray` arrives empty (5 formulas in "Multiple Randomization Designs").
    - *Fix:* write such a formula as a table or an image.
    - *Takes:* engine change; reconvert the 5 papers.
13. **References to an equation, a theorem or an appendix that LaTeXML lost.**
    - *Broken:* they show the label's name ("eq.(exactSol)", "Appendix minibatch"), in nine papers; "Real numbers, data science and chaos" has thirteen. Collapsed numbers ("Assumptions [2.1]-[2.1]", "([2]) follows from ([2])") are the same fault.
    - *Fix:* take an equation's number from its place among the numbered equations of the LaTeX source.
    - *Takes:* engine change; reconvert the papers.
14. **A taxonomy tree's leaves that hold only citations arrive empty, and a table of paragraph columns is run-on text.**
    - *Broken:* "A Survey on Hallucination in Large Language Models", Figure 1 on p. 2 and Tables 1 and 5 on pp. 5 and 26.
    - *Takes:* engine change for one paper; or by hand.

## C. Waiting

- **OpenCV is held at 4.12** ([`experiments/ocr-engines`](../../experiments/ocr-engines/README.md)); it crashed one paper of the 2026-10-14 run all the same. Lift the pin, and the numpy override that goes with it, when a release converts "Canaries in the Coal Mine" ten times without a crash.

## D. By hand

- **Old PDFs with a broken text layer** ("Long Short-Term Memory", "The power of two random choices", "The Anatomy of a Large-Scale Hypertextual Web Search Engine") lose ligatures and, for LSTM, headings and equations; the Google paper is a scan whose OCR garbled headings and numbers (its two tables were rewritten by hand). Replace each PDF with a cleaner copy, then reconvert.
- **"Memory in the Age of AI Agents"** is edited by hand, so it keeps "§ what-memory" for Section 3. A reconversion with `--force` resolves such references from the LaTeX source; its cropped Figure 1 has to be put back after.
