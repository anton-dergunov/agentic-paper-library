# Reading formats: progress and handoff

The plan is [docs/plans/reading-formats.md](../../docs/plans/reading-formats.md). This file says what has been run, what was decided, and what comes next, so that a new session (or the author's terminal) can carry on. The block between the `report.py` markers is regenerated; the rest is written by hand at each checkpoint.

## How to continue

All commands run from this directory with `PAPER_LIBRARY=~/papers uv run python …`. Each can be stopped (Ctrl-C, a usage limit) and run again: a request whose result file exists is not asked again.

```bash
cd experiments/reading-formats
PAPER_LIBRARY=~/papers uv run python run.py status          # what is done
PAPER_LIBRARY=~/papers uv run python run.py D --budget 20    # the next tier (see "Tier D: run plan"); stops by itself at 80% of the five-hour window
PAPER_LIBRARY=~/papers uv run python judge.py               # grade anything not yet graded (run.py does this per group)
PAPER_LIBRARY=~/papers uv run python report.py              # results/summary.md and the block below
```

`--stop-at 0.9` moves the utilisation at which a run stops; the default 0.8 leaves room for the session that started it. A new session: "Continue the reading-formats experiment from `experiments/reading-formats/PROGRESS.md`."

## Tiers, in priority order

| Tier | What | Status |
|---|---|---|
| A pilot | E0 extras on DPO; E1 on DPO in all five conditions (c0, pdf, txt, html, md) | done 24 Oct |
| B core | E1 on SimPO, GPT-1, Lost in the Middle, InstructGPT in c0, pdf, txt, md; E4 | done 25 Oct |
| B2 unseen papers | E1 in c0, pdf, txt, md on four papers published after the model's training cutoff (June 2026), all with arXiv HTML: PAIR (LinkedIn, arXiv 2610.30941, 22 Oct), SFT Conflicts, RL Coexists (4 Aug, theory and equations), Cross-Model KV Cache Transfer in LLM Families (4 Aug, a closed-form mapping, tables), GenRec at Netflix (10 Aug, industrial tables and plots). Six questions each (two tables, an equation, an appendix or setup detail, a figure-only value, an unanswerable trap), drafted by `draft.py` (one request per paper from the PDF, `results/drafts/`) and checked by hand against the PDF pages and with `inputs.py check`. Plus a txt condition in E4: does the naive text layer have the converter's errors? Chosen 24 Oct: DPO is answered from memory, and memory can hide what a form loses | done 25 Oct |
| Checkpoint 1 | read the disagreements by hand; decide whether C–E still pay | decided 24 Oct (below); the hand check is still to do |
| C | E5 (small print); E1 html beyond DPO dropped 24 Oct, and taken out of `run.py C` | done 25 Oct |
| C2 small print and equations on unseen papers | E5 on PAIR, SFT Conflicts, KV transfer, GenRec pages chosen by the author for small print (R5–R9), in page, img1255, img2576, md and txt; E6, nine equation-structure questions (Q1–Q9) in pdf, txt, md | done 25 Oct |
| D | E3 across papers (X1–X11) in four conditions: Claude Code in the library copy (x-lib), in a copy of the PDFs (x-pdf), in a copy of the PDFs' text layers with page markers (x-txt, added 25 Oct at the author's suggestion), and the named papers' PDFs attached to one request (x-att, every question that names its papers) | code, copies and golds ready 25 Oct; X3 piloted in all four conditions and X4 in x-pdf and x-txt (6 of 42 first answers, all correct); the rest to run: see "Tier D: run plan" |
| E | E2 single paper as an agent (CC-LIB, CC-PDF) | not started |

How a tier runs: group by group (a paper); the conditions of a group in parallel, each asking its questions in turn so that the document is read from the cache; then the group is judged, and every question whose answers differ between conditions (closed book aside) is asked twice more in each condition while the cache is warm (one hour on the subscription) and judged again. Only differences that hold in two of three runs count.

## Rules for changing course

- PDF ≈ MD ≈ TXT on everything but figures: conversion buys cost, not accuracy. Drop tier C's HTML; run E5 only for the resolution fact.
- MD > TXT on tables or equations, holding across reruns: the conversion pays at answer time. Keep the rest as planned.
- E4: old markdown answers confidently wrong where the new markdown and the PDF are right: that is the blog's lead, and no more E4 is needed.
- InstructGPT's PDF is about 200K tokens. If it does not fit, the record says `too_long`, which is itself a finding.

## Departures from the written plan

- The judge grades one question at a time, with all its answers shuffled and numbered, not one request per answer: the same standard for every condition, at a fraction of the cost.
- Reruns of disagreements happen immediately after a group is judged, while its documents are in the cache, instead of in a later pass.
- Requests run without the user's CLAUDE.md files and background traffic (as `paperlib`'s `ask_model` does), so the empty request is about 800 tokens, not the 2,052 measured on 23 Oct.

## Findings so far

### Tier A, the pilot (24 Oct 2026, $16.54 of requests, about 40% of a five-hour window with this session's own work)

- **DPO is answered from memory.** Closed book got D1–D4 and D6 right, quoting Table 1's 0.31 / 0.23 and Table 2's agreement rates. On DPO only the figure question separates the forms. For the rest of E1, a question C0 gets right says nothing about the format, unless a document condition gets it wrong (a document that misleads).
- **Figure values: only the PDF.** D5 (TL;DR win rates at temperature 1.0, in a plot only): PDF correct in 3 of 3 runs. TXT, HTML and MD declined in 3 of 3 each ("the figure is not in the text"), and none guessed. P3 holds on DPO.
- **Every other DPO question: all five forms correct**, the text layer included (D2, D3 are tables, D1 an equation).
- **Tokens of DPO, whole paper, one request** (input including about 800 fixed): PDF 80,063; HTML `<article>` 197,077; MD 45,606; MD with in-document links reduced to their text 44,226 (the anchors cost only 1,380 tokens, 3%); TXT 40,210. MD is 57% of the PDF, as measured on 23 Oct; raw HTML is 2.5× the PDF.
- **Page resolution (E0):** page 9 as a 1,255 px image costs 1,613 tokens, as a 2,576 px image about 4,100, and as a one-page PDF 3,250. A PDF page is sent as its text plus an image at the standard cap (about 1,550): P9's first half holds. DPO page 1 alone cost 3,448, not 6,285: the 23 Oct figure did not repeat.
- **The cache needs a breakpoint after the document.** Claude Code puts its cache breakpoint at the end of the message, so without one of our own each new question wrote the whole document again (a PDF question $0.65, an HTML one $1.58). With `cache_control` on the document block the next question costs $0.02–0.06. The first half of the pilot ran without it; the answers are valid, they only cost more.
- **The judge**: six answers checked by hand (PDF D5 r1 and r3, MD D5, TXT D4, C0 D6, HTML D3) agree with its grades. The D5 declines were graded "declined", not "wrong". The plan's full hand check (every disagreement plus 10 agreements) is still to do.
- **HTML answers cannot cite pages**: arXiv's HTML has no page markers ("I can't give page numbers because the document has no page markers"), so `page_ok` is structurally false for HTML.

### Tier B so far (24 Oct 2026)

- **E4, conversion fixes: the old markdown's errors reach the answer.** F1 (MuSiQue, padding digit): the old markdown gave 53.4 / 50.0 for 3.4 / 0.0 in 3 of 3 runs, without a hedge; the fixed markdown and the PDF were right 3 of 3. F3 (GPT-1 Eq. 5 shown as "(5)"), F4, F5 (Qwen3-VL Table 2 absent): the old markdown declined 3 of 3, the new markdown and the PDF were right 3 of 3. P8 holds: a wrong value that looks plausible gives a confident wrong answer; a missing one gives a decline.
- **An impossible value is caught.** F2 (Toolformer, 99.3 printed 199.3): the old markdown was graded correct, because the model saw that a share cannot exceed 100%, found the same stray "1" in the other cells of the column, and answered "about 99.3%" with the repair stated. A padding digit is silent only when the result is plausible (F1).
- **The current Qwen3-VL splice still misleads the model, which recovers by inference.** F6: the new markdown leaves MMBench-EN's instruct cell empty and shows 89.3 a row down. The model answered "most likely 89.3", working out the shift from the prose (p. 13, "89.3/88.9") and the neighbouring rows. The judge counted it correct; it is a correct answer from a broken table (ticket `pdf-table-structure`).
- **SimPO: PDF, TXT and MD all 6 of 6.** Closed book got S2 wrong (it named SimPO as best, where the answer is CPO) and S5, S6 partly. Unlike DPO, SimPO is not answered from memory, and the text forms are level with the PDF on its tables, equation, appendix, citation and trap.

### Checkpoint 1 (24 Oct 2026, after tier B up to InstructGPT)

- **On 22 single-paper questions (DPO, SimPO, GPT-1, Lost in the Middle): PDF 22, TXT 18, MD 18, closed book 15.5.** TXT and MD lose exactly the same four questions, the four whose values exist only in a plot (D5, G5, L2, L3). They decline all of them, in 3 of 3 runs, and never guess. The PDF reads them off the page image: 11 of 12 runs correct, one partial.
- **Everything else is level.** Tables (6), equations (3), appendix details (3), a citation, setup, prose and two unanswerable traps: PDF, TXT and MD all correct. P1 and P4 hold. P2 does not, so far: the raw text layer is not below the markdown on tables or equations in these papers. The table questions here are simple lookups that `pdftotext -layout` keeps legible; the harder cases are E4's.
- **Where conversion matters is E4**: a converter error gives a confident wrong answer (F1) or a decline (F3–F5), and the fix turns both into correct answers. So the case for the conversion work is the silent error, not average accuracy over clean papers.
- **Cost**: the markdown is 55–57% of the PDF's tokens and about the same as the text layer; HTML is 2.5× the PDF. With the cache, a further question on a paper already read costs $0.02–0.05 in any form.
- **Memory**: closed book is right on 15.5 of 22, DPO almost wholly. Hence tier B2 (papers after the training cutoff).

Decisions for the next session, in order (1–3 done 25 Oct, below; 4 ready to run, see "Tier D: run plan"):
1. Finish tier B (InstructGPT): `run.py B`.
2. Tier B2, the papers the model cannot know: this tests the figure and table results without memory to fall back on.
3. Tier C: run E5 (the resolution question is cheap, and it says whether small print comes from the text layer or the image). E1 html beyond DPO is dropped (agreed with the author 24 Oct): HTML costs 2.5× the PDF and cannot cite pages.
4. Tier D (E3, across papers) is now the main open question: single-paper accuracy is settled as "PDF ≥ MD = TXT, the gap being figures".
5. Tier E (E2) only if E3 leaves the single-paper agent case open; one cheaper variant is to ask only the four figure questions in CC-LIB, to see whether an agent in the library opens the figure.
6. The hand check of disagreements (the plan's grading step) before any of this is written up.

### Tier B finished, and tier B2 (25 Oct 2026; InstructGPT $2.93, drafting $2.21, B2 $8.63; the five-hour window at 41% at the end, this session's own work included)

- **InstructGPT: all four conditions 5 of 5**, closed book included: it is answered from memory, like DPO. Its PDF fits (174K tokens of input, $1.41 for the first question, $0.04–0.05 for each further one from the cache); markdown 83K, text layer 73K.
- **On the four unseen papers the result holds without memory: PDF 24 of 24, TXT 20, MD 20, closed book 2** (the two traps it declined; it knows none of the four papers, and on PAIR it answered the equation question for an older paper of the same name, from memory and wrong). TXT and MD lose exactly the four figure questions, decline them in 3 of 3 runs and never guess; the PDF answers all four in 3 of 3. Tables (8), equations (4), appendix and setup details (4) and traps (4) are level across PDF, TXT and MD. With DPO, SimPO, GPT-1, LitM and InstructGPT that makes 51 single-paper questions with one pattern: the forms differ only where a value is drawn, not written.
- **The figure questions include a diagram label, not only plot values.** PAIR has no plot, so P5 asks for the pooling labels of its architecture diagram; "Temporal-Gated Pooling" exists only in the picture. The PDF answer read it and also noticed that the diagram disagrees with the caption and Section 4.3 (positional attention, not GeM pooling, for the history). The text forms quoted the caption and declined.
- **Axis ticks in the text layer do not tempt a guess.** pdftotext keeps a vector plot's tick labels (SFT Conflicts' 83.0–88.0, GenRec's 1.00–1.16); the TXT answers named the axis range and declined.
- **E4 in txt: the naive text layer has none of the converter's errors.** `pdftotext -layout` got F1–F6 right, in 3 of 3 runs where rerun, including Qwen3-VL Table 2 (F4–F6), which both markdown versions broke. The converter's errors are its own, not the PDF's: the text layer is the baseline a conversion must not fall below.
- **Tokens, all nine E1 papers: MD is 40–73% of the PDF, not "55–57%"** (that was DPO's figure, generalised too early at checkpoint 1). The spread is set by equations and complex tables, not by the paper's date. Where the markdown carries much LaTeX and many HTML tables (merged cells), it costs 1.3× the text layer and runs at 2.0 characters a token (SimPO 1.35×, KV transfer 1.36×, SFT Conflicts 1.30×: 34K characters of LaTeX, 785 `<td>`); elsewhere it costs 0.94–1.14× the text layer at 2.5–2.6 characters a token (GPT-1, LitM, PAIR, GenRec, DPO, InstructGPT). The PDF costs 2,600–4,000 tokens a page, about 1,550 of them the page image. On these questions the extra structure bought nothing: TXT answered every equation (7) and table (15) question MD did. Whether LaTeX pays on harder equation questions (derivations, a term's role across equations) is not tested here.
- **How B2's questions were made**: `draft.py` wrote six per paper from the PDF ($0.32–1.03 each, `results/drafts/`); each value was checked against the PDF page by eye and with `inputs.py check`, the comparison claims (K2, M2) against their tables, and the traps for absence. Changed from the drafts: M5 asked the peak of a curve, which sits on the 86.0 grid line printed in the text layer, so it asks two points off the grid lines instead; P5 is a diagram label (above); GenRec's only table repeats its cells in the prose, so N1 and N2 test reading, not table structure; P4 and N4 are setup details, the papers having no appendix.

### Tier C, E5: small print and resolution (25 Oct 2026, $1.51; window 48% at the end)

- **Small print is read from the image at the standard resolution.** Qwen3-VL's Table 2 (R1–R3: OCRBench 750, ZeroBench 2, HallusionBench 60.4) was right in all four forms: page 15 as a one-page PDF, as a 1,255 px image (2,250 tokens), as a 2,576 px image, and the current markdown. The 1,255 px image alone (about 115 dpi), with no text layer, was enough: P9's middle claim (small print in a dense table is read from the text layer, not the image) does not hold for this table. Its last claim holds: the plot value read from the images is within the tolerance. The test was easier than planned: the table's print is small but clean.
- **A plot value, again only from a picture.** R4 (LitM Figure 7, LongChat-13B at the 70th of 140 pairs, about 35%): the page and both images 3 of 3, the markdown declined 3 of 3.
- **The smallest form that answers is a 1,255 px image of the page**: 2,250 tokens against 3,900–5,100 for the one-page PDF. For a question about one known page, an agent that renders that page to an image pays the least.
- **Image token counts are not stable.** The same 2,576 px image was counted as about 4,530 tokens in four requests and about 10,110 in two (R3 r1, R4 r2), the request otherwise identical; and its Qwen3-VL requests were never read from the cache, though the 1,255 px image's LitM requests were. Cost per image above the standard cap is therefore uncertain by about 2×; the 1,255 px image (about 2,250) and the one-page PDF did not vary.

### Tier C2: small print and equation structure on the unseen papers (25 Oct 2026, $2.02; window 59% at the end)

Asked because tier C's papers may be in the model's memory and its table's print is clean, and because LaTeX's value on harder equation questions was untested. The author chose the pages.

- **Small print: every form read it** (R5–R7: PAIR Table 2's operations column, SFT Conflicts Table 4's superscripts on the 7B rows, KV transfer Table 4's Ministral 3B→8B shifts): page, 1,255 px image, 2,576 px image, txt and md all correct. With tier C, 6 small-print questions on 4 papers, none lost in any form.
- **Text inside vector figures is in the text layer and not in the markdown.** R8 (GenRec Figure 3's bar labels: +0.115%, P = 3.1 × 10⁻¹⁰) and R9 (SFT Conflicts Figure 2's heatmap cells: −3.92e-04, 8.7e-02): page, both images and txt 3 of 3; md declined 3 of 3. The first questions in this experiment where the text layer beats the markdown: the converter keeps a figure as a picture file, so the numbers drawn as text inside it are lost to a reader of the markdown.
- **Equation structure: PDF, TXT and MD all 9 of 9** (Q1–Q9: PAIR's positional attention, normalised fusion and Matryoshka sum; GenRec's verbaliser; SFT Conflicts' KL argmin over P* ∩ Π, the 1/G in the advantage's standard deviation, Lemma 4.3's double sum over Â·Â·⟨δS, δS⟩, the 2 exp(−c t² d) tail bound, g_SFT against g_RL). Read by hand: the TXT answers rebuild each formula as clean LaTeX from a text layer that scatters it over lines and interleaves the other column. The formulas here are all standard forms (softmax attention, a population standard deviation, a KL argmin), so the model may be completing them from what such formulas usually are, not reading them; a formula that breaks convention would tell the two apart. Q10 is one: SFT Conflicts' appendix bounds |cos(g_SFT)| ≥ (1 − 2η − η²)/(1 + η)² and |cos(g_RL)| ≤ γ_{i,j}G/(1 − γ_in G) (Eqs. 9–10, pp. 19, 21), forms no prior gives, with each fraction spread over three lines of the text layer and its bar lost. PDF, TXT and MD were all correct, the TXT answer with every coefficient and the definitions of η, γ_{i,j} and γ_in ($0.18, from the cache). The text layer is read, not completed.
- **So far the markdown's LaTeX has bought no accuracy** over the raw text layer, on 17 equation questions over 7 papers.
- **Filed**: ticket `figure-text-lost` (engine `tickets/`): take the text-layer words inside a vector figure's region into the markdown under the figure; issue records on GenRec (Figure 3) and SFT Conflicts (Figure 2) in the library's `issues/`. The Qwen3-VL record (`pdf-table-structure`, p. 15) now names F6's MMBench cell.

### How often would the text layer fail? A scan of the library's PDFs (25 Oct 2026, no model requests)

PyMuPDF over all 2,275 PDFs: characters per page, unmapped glyphs (U+FFFD and private-use characters), and raster images by area. The script and its output are not committed (a scratch measurement; rerun in about 30 minutes on one core if needed).

- **No PDF lacks a text layer** (none has a median page under 200 characters). The 50 with a few near-empty pages covered by an image are full-page figures (Taming Transformers' sample grids, ExpeL's screenshots), not scans.
- **Unmapped glyphs**: one PDF over 1% (a piano-transcription paper, 3.9%), 31 between 0.1% and 1%.
- **What the scan cannot see**, from the library's issue records: dropped ligatures and OCR text layers count as text. `pdf-broken-text-layer` has 2 papers (LSTM, a PostScript conversion with "signi cant", "e cient" and garbled equations; Google's Anatomy of a Search Engine, an OCR layer with garbled headings), `pdf-text-layer-errors` 30 papers (41 records).
- So the text layer is badly broken in about 2 papers of 2,275 and imperfect in about 60 (under 3%); in this library, which is mostly arXiv, it almost never fails outright. Its own weakness is elsewhere: in 58% of the PDFs at least one figure is a raster image (over 3% of a page), whose numbers no text form carries; in the other 42% the figures, if any, are vector, and their printed numbers are in the text layer and not in the markdown (ticket `figure-text-lost`).

## Tier D: run plan (written 25 Oct 2026, to run in a fresh session and window)

**What it tests.** Whether the library's structure (indexes, notes, reviews, markdown with page markers) helps an agent answer across papers, against an agent with only the PDFs, and against an agent with the PDFs' text layers, the cheap pipeline that needs no conversion. Single-paper accuracy is settled ("PDF ≥ MD = TXT, the gap being drawn values"); this is the library's main claim.

**Conditions.**

| Id | Where | What it has |
|---|---|---|
| x-lib | `copies/lib-asis` | the library as an agent finds it: `CLAUDE.md` → `AGENTS.md` → the guide, `catalog/`, `notes/`, `reviews/`, the markdown (no figures, no PDFs) |
| x-pdf | `copies/pdf` | the 2,275 PDFs under the same topic tree (APFS clones) and a one-line `CLAUDE.md` |
| x-txt | `copies/txt` | each PDF's `pdftotext -layout` text, with a line `[page N]` at each page, same tree, one-line `CLAUDE.md` |
| x-att | one request | the PDFs of the papers the gold rests on, attached; not for X4, X5 (what the library holds) |

Sessions: `claude -p` with `--tools Read,Grep,Glob,Bash`, `--setting-sources project,local` (no user settings, hooks or plugins), `--strict-mcp-config`, `--max-budget-usd 5`, stdin closed, no session persistence. The copies are read-only. Each record keeps every tool call (`calls`), turns, cost, `opened_pdf` (a `Read` of a PDF or a PDF tool in the shell) and `outside` (calls naming a path outside the copy). The prompt is the question plus "Answer from the papers in this folder. Give the page number for every fact you use." The copies live in `~/.cache/papers/experiments/reading-formats/copies/` (`copies.py` rebuilds them in about 2 minutes).

**What the smoke tests and the X3 pilot showed (25 Oct).**
- `--restricted` stops the copy's `CLAUDE.md` from loading (the library agent found its guide only by reading the files), so it is not used; the copies' read-only bits and the `outside` record take its place.
- The user's `~/.claude/CLAUDE.md` (git workflow, changelog rules) loads in every condition alike: about 1K tokens, read from the cache after the first turn, and unrelated to answering. Left in (decided with the author 25 Oct): removing it means pointing `CLAUDE_CONFIG_DIR` at an empty folder, which risks the subscription login.
- `subprocess.run` must close stdin, or the session reads the caller's stdin as part of the prompt (fixed).
- X3 pilot: x-lib $0.33 (6 turns: notes, then grep in the markdown; it also found that NoLiMa quotes RULER as 32K, against RULER's own 64K); x-txt $0.21 (6 turns, grep on the `[page N]` files); x-pdf $0.36 (12 turns: it ran `pdftotext` itself into `/tmp/rn` and tracked pages with awk, which is the author's point: an agent with PDFs builds the text layer it needs). All three gave 64K against 2K and the reasons. Not yet judged.
- An x-pdf session writes its converted text to `/tmp` (`/tmp/rn`, `/tmp/pt`), where a later session could find it. Now each session gets its own `TMPDIR`, removed afterwards, and anything new in `/tmp` whose name the session's calls use is deleted when it ends (the run prints "removed …"). Sessions of one condition run in turn, so no running session loses its files. `outside` still lists every call that leaves the copy.
- Second pilot (25 Oct, $1.68, sessions capped at $2): X3 in x-att correct ($1.16: RULER and NoLiMa, 139K tokens); X4 in x-pdf correct ($0.22, 5 turns: it listed the tree, picked candidates by file name, and checked KTO and ORPO with `pdftotext` on a few pages) and in x-txt correct ($0.20, 8 turns: grep for "reference-free" over the whole tree). Both named SimPO and ORPO and set KTO's reference-free variant aside. The judge graded X3 correct in all four conditions and X4 correct in both. The enumeration question, where the reviews were expected to help, is answered as well and as cheaply by grep over text.

**Review-mined questions (X7–X11), added 25 Oct at the author's suggestion.** The other questions were written by a model reading the PDF and checked by looking at page images, which favours what is visible on a page. The library's reviews were written by agents reading the markdown and notes, so questions taken from their surprising findings come by the other route, and they are cross-paper by nature: how much training data is correct (Self-Instruct, s1, OpenThoughts), whether a sliding window costs quality (Mistral 7B, Gemma 3, Phi-4, GLM-5; Gemma 3's evidence is in figures only), Mem0 against Zep's memory size and delay, Memory-R1's 152 training questions and small LongMemEval gain, OLMo 2's learning-rate result. Their golds were checked against the PDFs. **The reviews cite three of these ten papers one page early** (Self-Instruct's Table 2 is on p. 5, cited p. 4; Memory-R1's Tables 1 and 5 on pp. 6 and 18, cited 5 and 17; OLMo 2's Table 8 on p. 19, cited 18): a citation problem in the library itself, to check (is it the markdown's page markers or the review's writer?) before the write-up.

**Golds** checked 25 Oct: RULER's Table 3 is on p. 7, not p. 6 (fixed); X4 checked against the preference-learning folder (SimPO and ORPO only; KTO and DPO keep a reference model); X5 gained LongLLMLingua's document reordering (§4.2, p. 4) beside the review's three "Repairing the reader" papers; X1, X2, X6 pages match.

**Cost.** Agent sessions cost $0.20–0.36 in the pilots, the enumeration question included; x-att $1.16 for two papers, and with InstructGPT and DPO, or X8's four technical reports, 250K tokens or more (it may record `too_long`). The 36 first answers left: about $10–15; with reruns of disagreements (two more runs in every condition): $15–25, half to two-thirds of a window. Every session is capped at $5. With the hand check and the write-up, the experiment needs about one more window.

**How to run it** (from this directory):

```bash
PAPER_LIBRARY=~/papers uv run python run.py status                   # tier D: 6 of 42 first answers
PAPER_LIBRARY=~/papers uv run python copies.py                       # only if ~/.cache/.../copies is gone
PAPER_LIBRARY=~/papers uv run python run.py D --budget 20 --stop-at 0.9
PAPER_LIBRARY=~/papers uv run python report.py                       # "E3: across papers" in results/summary.md
```

It runs the four conditions in parallel (about 40–90 minutes), each condition's questions in turn, judges, then reruns the questions whose grades differ between conditions (r2, r3). It can be stopped and repeated; it skips what is done. If it stops at the budget or the window, run the same command again later.

**What to look at afterwards.** Scores per condition, with the hand check of every disagreement (the judge cannot verify X4 and X5's names beyond the gold); cost and turns per condition (`Sessions` table); whether x-lib used reviews and notes (`calls`), whether x-pdf converted PDFs itself and how; the `outside` column. Then decide E2 (single paper as an agent): if x-lib ≈ x-txt across papers, the library's structure is not what answers questions, and the case for it becomes cost, citations and the notes; if x-lib wins, measure where (X4, X5 enumeration from reviews, or equations).

## Generated

<!-- report.py -->
Requests: 429, $47.77; judge (latest grading of each question) $2.81; last five-hour utilisation seen: 85%.

```
tier A: 38 of 38 first answers
tier B: 102 of 102 first answers
tier B2: 102 of 102 first answers
tier C: 16 of 16 first answers
tier C2: 55 of 55 first answers
tier D: 6 of 42 first answers
reruns: 111; requests so far $47.77
```
<!-- /report.py -->
