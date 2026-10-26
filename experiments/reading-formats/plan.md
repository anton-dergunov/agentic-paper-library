# Plan: what does the library's markdown buy over the PDF?

The library rests on two claims that nobody has measured: an agent answers questions about papers better, or as well and more cheaply, from the library's markdown than from the PDF; and the conversion work (tickets, fixes, reconversions) changes the answers, not only how the markdown looks. This plan tests both with Claude only, on a small set of papers and questions chosen in advance, run through `claude -p` on the author's Pro subscription (there is no API key). It starts small and scales only where a result is ambiguous.

The background research behind it, written up for the blog, is the draft [Papers as markdown for agents](../../../../../Library/CloudStorage/Dropbox/notes/blog/_drafts/2199-01-01-papers-as-markdown-for-agents.md) (outside this repository). Its substance is repeated below, so this plan stands on its own.

The experiment's directory will be `experiments/reading-formats/`: `questions.yaml` (the test set below, with gold answers), `run.py`, `judge.py`, `results/` and the write-up.

## The questions

1. **Single paper, format only.** Asked about one paper, with the whole paper in the request, does Claude answer better from the PDF (text layer plus page images, what an attachment sends), the PDF's text layer, the raw arXiv HTML, or the library's markdown? What does each cost?
2. **Single paper, the agent.** Does Claude Code in the library (markdown, notes, the PDF when it decides to open it) answer as well as Claude Code given only the paper's PDF, and at what cost?
3. **Across papers.** For a question that spans several papers, how does Claude Code in the library compare with Claude Code in a folder of the same PDFs, and with the named papers attached to one request?
4. **Conversion fixes.** On the places a fix changed, does the old markdown give wrong answers that the fixed markdown and the PDF get right?
5. **Page images.** At what resolution are PDF pages sent, and does small print (dense tables, plot labels) survive it?

## What is known before measuring

### What the assistants do with a PDF

None converts a single attached paper to markdown. The whole paper goes into the context, as text layer plus page images:

| Product | One paper | Many or large files |
|---|---|---|
| Claude API, claude.ai | Each page as its extracted text and a rendered image ([docs](https://platform.claude.com/docs/en/build-with-claude/pdf-support)); the docs estimate 1,500–3,000 text tokens a page plus the image. claude.ai reads the images only up to 100 pages; 101–1,000 pages are text only ([help](https://support.claude.com/en/articles/8241126)) | Projects switch to retrieval as their files approach the context window ([help](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects)); one user reports it far earlier ([issue](https://github.com/anthropics/claude-code/issues/25759)) |
| ChatGPT | Under about 110K tokens the file goes into the context whole ([help](https://help.openai.com/en/articles/10029836)); the API sends text plus page images to vision models ([docs](https://developers.openai.com/api/docs/guides/pdf-files)) | Above it, text and images go into a private index searched once per prompt, keyword plus semantic |
| Gemini | Pages read as images, 258 tokens a page ([docs](https://ai.google.dev/gemini-api/docs/document-processing)) | NotebookLM's internals are not documented |
| Claude Code `Read` on a PDF | Text plus page image, 20 pages a call, kept by nothing between sessions; an open request asks for a text-only mode because of the cost ([issue](https://claudeissues.com/issue/80449-read-tool-pdfs-cost-way-more-tokens-than-they-need-to-because-of-the-image-rende)) | Not searchable with grep |

Relevant parts are selected only across collections, by fixed-size chunks; for one paper the model sees all of it, and the page image covers for what the text layer mangles.

### What a page costs (measured 23 Oct 2026)

Claude Opus 5.5 through `claude -p`, input tokens above the 2,052 of an empty request, on the DPO paper (27 pages, letter size). The scripts and outputs are in this session's scratchpad and will be redone as E0.

| DPO as | Input tokens | Per page |
|---|---|---|
| PDF document block, 27 pages | 79,254 | 2,935 |
| PDF document block, pages 1–10 | 30,771 | 3,077 |
| PDF document block, page 2 alone | 3,001 | 3,001 |
| PDF document block, page 1 alone | 6,285 | 6,285 (unexplained; page 1 holds Figure 1) |
| `pdftotext` of the whole PDF | 37,420 | 1,386 |
| the library's markdown | 44,791 | 1,659 |
| Claude Code `Read` of pages 1–10 (`pages: "1-20"`) | about 19,400 | about 1,940 |

- **The markdown costs 57% of the PDF**, not the 25–50% assumed before measuring, and 20% more than the raw text layer: LaTeX, table markup, image links and in-document anchors (`[31](#bib.bib31)`, `[3](#S3.E3)`) cost tokens. E0 measures how much of that is anchors.
- **An image is charged by patches, not bytes**: `⌈w/28⌉ × ⌈h/28⌉` tokens, capped at 1,568 on standard-tier models and 4,784 (2,576 px long edge) on Claude 4.7 and later ([docs](https://platform.claude.com/docs/en/build-with-claude/vision)). The PDF minus its text layer leaves about 1,550 tokens a page, the standard cap: pages seem to be rendered at about 970 × 1,250 px (about 115 dpi) even for Opus 5.5. This is inferred from counts, assuming Anthropic's text extraction matches `pdftotext`; E0 checks it.
- **Raw arXiv HTML is the largest form**: DPO's page is 411,092 characters (375,851 in `<article>`; 217,182 with MathML replaced by its LaTeX `alttext`), against 106,011 for the markdown. Tokens to be measured.
- **Prompt caching works across `claude -p` calls**: a second request with the same 10-page PDF read 31,980 tokens from the cache and cost $0.013 instead of $0.26. Asking several questions about one paper, one request each, costs little more than one.

### What the evidence says

- **[DocBench](https://arxiv.org/abs/2407.10701)** (2024): 229 documents, 1,102 questions, real upload products. Academic papers: Claude-3 Opus 73.9%, GPT-4 65.7%, humans 83.0%; GPT-4 reading text extracted with PyMuPDF (fitz) 70.0%. Failures: locating a table or figure, reading values off it, long documents, and unanswerable questions (GPT-4 as a product 37.1%, as a pipeline 70.2%).
- **[OCR Hinders RAG](https://arxiv.org/html/2412.02592v4)** (OHRBench, ICCV 2025): the best parser 31.1 end to end against 36.1 for ground-truth text (about 14% worse); MinerU 30.0, Marker 29.5. Losses sit in tables, formulas and charts (charts 32.9 → about 10 for pipeline parsers). Severe *semantic* noise halves performance; *formatting* noise costs large models about 7%, only on table and formula questions. Page images fed directly to a VLM compete on tables and charts and lose on plain text.
- **Long contexts degrade**: Lost in the Middle, NoLiMa and RULER (all in the author's library) and Chroma's [context-rot report](https://trychroma.com/research/context-rot): accuracy falls with length and position, and similar-but-wrong passages hurt most.
- **This engine's own experiments**: stripped LaTeX source answered 47.5 of 48 questions against 48 for the markdown ([`latex-source/`](../../experiments/latex-source/README.md)); dropping table shading cost 4 of 15 dependent questions, three answerable elsewhere ([`table-emphasis/`](../../experiments/table-emphasis/README.md)); reviews and notes did not make answers more accurate than reading the papers ([`review-usefulness/`](../../experiments/review-usefulness/README.md)); one padding-digit bug had changed 256 table values in five papers, and no note had quoted one ([`review-flagged-fixes/`](../../experiments/review-flagged-fixes/README.md)).

### Who else converts papers to markdown

Many: arXiv MCP servers ([blazickjp](https://glama.ai/mcp/servers/blazickjp/arxiv-mcp-server) and others), zotero-fulltext-mcp, ScholarAIO (MinerU, LaTeX and figures kept, keyword plus vector search, per-paper agent notes, a Claude Code plugin), Ai2 Asta's `local-paper-index` skill (markdown cut into 2,000-character chunks for vector search), alphaXiv's full-text markdown, Karpathy's "LLM Wiki" pattern. None found publishes a measured conversion: issue records, tickets by cause, converter tests, reconversion, or an error rate. Elicit's, SciSpace's and alphaXiv's parsing is not published.

## Priors to test

| # | Prior | Tested by |
|---|---|---|
| P1 | On prose questions every in-context form scores about the same | E1 |
| P2 | On table and equation questions the markdown is at or above the PDF, and the text layer clearly below both | E1 |
| P3 | On values that exist only in a plot the PDF is ahead; the markdown in context has no figure at all, and the agent opens figures rarely | E1, E2 |
| P4 | Unanswerable questions: no form differs much; Opus 5.5 declines in all | E1 |
| P5 | Cost: markdown about 55% of the PDF's tokens; raw HTML above the PDF; the agent in the library above the markdown in context but below the agent with the PDF | E0, E1, E2 |
| P6 | Famous papers' numbers are partly known without any document (DPO's β = 0.1, InstructGPT's 85%) | E1, closed-book control |
| P7 | Across papers the library beats a folder of PDFs on correctness and cost, and beats attaching the named papers on cost | E3 |
| P8 | An old conversion with a wrong value gives a confident wrong answer where the PDF is right; the fixed markdown is right | E4 |
| P9 | PDF pages are sent at about 115 dpi; small print in a dense table is read from the text layer, not the image, and a plot's values read from the page image are within a few points | E0, E5 |

## Set-up shared by all runs

- **Model**: Claude Opus 5.5 (`--model claude-opus-5-5`), Claude Code's default effort, one sample per question and condition in the pilot. Record `claude --version`.
- **Single requests** (E1, E3's attachment condition, E4, E5): `claude -p --input-format stream-json --output-format stream-json --verbose --tools "" --max-turns 1 --system-prompt "<the prompt below>"`, with one user message whose content is the document blocks first and the question last. A PDF goes as `{"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": ...}}`, an image as an `image` block, text as a `text` block. Verified on 23 Oct 2026. All questions on one paper and condition run back to back so the document is read from the cache.
- **System prompt for single requests**: "Answer the question using only the document provided. Give the page number for every fact you use. If the document does not contain the answer, say so." For the closed-book control: "Answer the question from what you know. If you do not know, say so."
- **Agent runs** (E2, E3): `claude -p --output-format stream-json --verbose` started in the condition's directory, with Read, Grep, Glob and Bash allowed and no web, no edits, no subagents, as in [`review-usefulness/`](../../experiments/review-usefulness/README.md). The prompt names the paper by title (single-paper) or nothing (cross-paper) and asks for page citations.
- **Recorded per run**: the answer, `usage` (input, cache write, cache read, output), `total_cost_usd`, turns, and for agent runs the files read and whether a PDF or image was opened.
- **Copies**: agent conditions run in copies made by a script, as `review-usefulness/copies.py` does: the library copy has `library/`, `notes/`, `reviews/`, `catalog/` and the guide; the PDF copy has the PDFs under the same topic tree, a one-line `CLAUDE.md` ("Papers are PDFs under the topic folders; answer with page citations") and nothing else.

## The experiments

### E0. Token cost and page resolution (about $3)

1. The table above for the five E1 papers: each form's input tokens (the first E1 request per paper and condition records it; no extra requests).
2. Two requests on DPO: the markdown with in-document anchors removed (`[31](#bib.bib31)` → `[31]`), to price the anchors; the raw HTML `<article>`, to price HTML.
3. Resolution: one request per size with DPO page 9 as an image block only, at 970 × 1,255 and 1,990 × 2,576 px. If the first costs about what the PDF's per-page image share costs (about 1,550), pages are sent at standard resolution.
4. Page 1 of DPO again, alone, to see whether the 6,285 tokens repeat; if so, try a page-1 cut with Figure 1 removed.

### E1. Single paper, format only (about $13)

Conditions, all single requests with the whole paper in context:

| Id | The paper as | Notes |
|---|---|---|
| C0 | nothing (closed book) | prices what the model knows |
| PDF | the PDF as a document block | what attaching a PDF to Claude sends |
| TXT | `pdftotext -layout` of the PDF | claude.ai's path over 100 pages; a naive parser |
| HTML | the arXiv HTML `<article>`, scripts and styles removed, otherwise raw | not for GPT-1, which has none |
| MD | the library's markdown file as it is, figures not attached | |

Papers: DPO (27 pp, arXiv HTML), SimPO (32 pp, HTML), GPT-1 (12 pp, PDF-only conversion), Lost in the Middle (18 pp, HTML, figure-heavy), InstructGPT (68 pp, HTML, long appendix). Questions D1–D6, S1–S6, G1–G5, L1–L5, I1–I5 below: 27 questions × 5 conditions, minus 5 HTML runs for GPT-1 = 130 requests.

### E2. Single paper, the agent (about $8)

Twelve E1 questions (D2, D4, D5, S2, S3, S6, G1, G5, L2, L3, I1, I2: tables, equations, figures, deep appendix, a citation) asked to Claude Code:

| Id | Started in | Prompt names |
|---|---|---|
| CC-LIB | the library copy | the paper's title |
| CC-PDF | a directory holding only that paper's PDF | the file |

24 sessions. Recorded beyond the answer: whether CC-LIB opened the PDF or a figure, and whether CC-PDF read the PDF with `Read` or converted it with a shell tool.

### E3. Across papers (about $15)

Six questions (X1–X6 below). Conditions:

| Id | Set-up |
|---|---|
| X-LIB | Claude Code in the library copy |
| X-PDF | Claude Code in the PDF copy (all 2,200 PDFs, same tree) |
| X-ATT | the papers the gold answer rests on attached as PDF document blocks to one request, with the single-request prompt; not for X4 and X5, which ask what the library holds |

16 runs.

### E4. Conversion fixes (about $4)

The markdown before and after a fix, from git, and the PDF, each as a single request:

| Paper | Old markdown | New markdown | What the fix changed |
|---|---|---|---|
| MuSiQue | `7f5bc9b3a` | `HEAD` | padding digit: Table 4's C-only cells read 53.4 / 50.0 for 3.4 / 0.0 |
| Toolformer | `7f5bc9b3a` | `HEAD` | padding digit: Table 9's 99.3 read 199.3 |
| GPT-1 | `8969b9e25^` | `HEAD` | Eq. 5 was only its number, `$$(5)$$` |
| Qwen3-VL Technical Report | `c4100a513^` | `HEAD` | pp. 15–16 (Tables 2 and 3) absent from arXiv's HTML, now spliced from the PDF; Table 2 still has merged rows (recorded 23 Oct, `pdf-table-structure`, key content) |

Questions F1–F6, 3 conditions: 18 requests. G1 in E1 already asks for Eq. 5 of the current markdown; F3 asks it of the old one.

### E5. Small print and resolution (about $2)

Four questions (R1–R4) about Qwen3-VL p. 15 (a dense 8-column table) and Lost in the Middle Figure 7, under four conditions: the PDF page as a one-page document block; the page as an image only at about 115 dpi (970 × 1,255 px); at 2,576 px; the markdown. 16 requests. It separates what the text layer carries from what the image carries.

### Grading

- **Gold answers** are below, each with its PDF page. Every value was found in the PDF's own text layer on that page with `pdftotext` on 23 Oct 2026; figure-only values were read off the figure with a tolerance. The questions were written from the markdown and checked against the PDF; that favours questions the markdown can answer, which the figure-only and fixed-defect questions offset in part.
- **Judge**: Opus 5.5 through `claude -p`, one request per answer, blind to the condition, given the question, the gold answer with its tolerance, and the answer. Scores: `correct`, `partial` (some of the asked values right), `wrong` (a stated value contradicts the gold), `declined` (says the document does not say). Separately: `page_ok` (the cited page holds the fact, ±1) and `confident_wrong` (wrong without a hedge). For unanswerable questions, `declined` or a correct "not reported, but …" is correct.
- **Check**: the author reads every answer where conditions disagree, and 10 where they agree.
- **Variance**: answers that differ between conditions are asked twice more in both, to tell a format effect from sampling noise. Only differences that hold in at least two of three runs count.

### Budget and stages

Costs are API-equivalent dollars as `claude -p` reports them; the subscription's five-hour window held about $28 of such work in [`latex-source/`](../../experiments/latex-source/README.md). Estimates assume the cache works as measured.

| Stage | Experiments | Estimate |
|---|---|---|
| 0 | E0, then E1 on DPO only (6 questions × 5 conditions) as a pilot of the scripts and the judge | $4 |
| 1 | E1 on the other four papers, E4, E5, grading | $19 |
| 2 | E2, E3, grading | $23 |
| | **Total** | **about $46, two windows over two or three days** |

Stop after a stage if it already answers its question. Scale up (a second set of papers, three samples throughout) only where a difference between conditions is within the run-to-run noise and the blog claim depends on it.

### How the results would change the claim

- **PDF ≥ MD on accuracy in E1**: the claim becomes cost, search and citation, not accuracy. The blog says so.
- **MD > PDF on tables or equations**: the conversion work pays at answer time; the claim stands with its numbers.
- **E4 shows confident wrong answers from old markdown**: the case for fixing conversions is the silent error, and the blog leads with it.
- **CC-LIB ≈ CC-PDF in E2 at similar cost**: on single papers the library adds little over a PDF in a folder; its value is E3.
- **X-LIB ≫ X-PDF in E3**: the library's main claim, measured.

## Test set

Pages are the PDF's. "Tol." is the tolerance for values read off a plot.

### DPO: Direct Preference Optimization (`llm/post-training/preference-learning`)

| Id | Kind | Question | Gold | Page |
|---|---|---|---|---|
| D1 | equation | Write the DPO loss as the paper gives it, and say what plays the role of the reward. | Eq. 7: $\mathcal{L}_{\text{DPO}} = -\mathbb{E}_{(x,y_w,y_l)\sim\mathcal{D}}[\log\sigma(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)} - \beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)})]$; the implicit reward $\hat r_\theta(x,y) = \beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\text{ref}}(y\mid x)}$ | 4 |
| D2 | table, merged header | On CNN/DailyMail, what GPT-4 win rates against the ground truth do DPO and PPO get at temperature 0.25? | DPO 0.31, PPO 0.23 (Table 1) | 9 |
| D3 | table | In the human study, how often did humans agree with each other on the PPO-1 comparison, and how often did GPT-4 (C) agree with humans on the DPO comparison? | H-H 87%; GPT-4 (C)–H 67% (Table 2) | 10 |
| D4 | appendix detail | What β, batch size, optimizer, learning rate and warm-up does DPO use by default, and what β for TL;DR? | β 0.1, batch 64, RMSprop, lr 1e-6, linear warm-up over 150 steps; TL;DR β 0.5 | 20 |
| D5 | figure only | In the TL;DR win-rate plot, what are PPO's and DPO's win rates at sampling temperature 1.0? | PPO ≈ 0.07 (tol. 0.05–0.10); DPO ≈ 0.39 (tol. 0.35–0.42) (Figure 2, right) | 7 |
| D6 | unanswerable | What AlpacaEval 2 win rate does DPO report? | Not reported; the paper evaluates on IMDb, TL;DR, Anthropic-HH and CNN/DailyMail | — |

### SimPO (`llm/post-training/preference-learning`)

| Id | Kind | Question | Gold | Page |
|---|---|---|---|---|
| S1 | table, 3-row header | In the Llama-3-Instruct (8B) setting, what Arena-Hard win rate do SimPO and DPO get? | SimPO 33.8, DPO 32.6 (Table 4) | 6 |
| S2 | table, column trap | In the Mistral-Instruct (7B) setting, which method has the highest Arena-Hard win rate, and what is it? | CPO, 22.6 (SimPO 21.0) (Table 4) | 6 |
| S3 | equation | Write SimPO's objective and name its two differences from DPO's reward. | Eq. 6: $-\mathbb{E}[\log\sigma(\frac{\beta}{\lvert y_w\rvert}\log\pi_\theta(y_w\mid x) - \frac{\beta}{\lvert y_l\rvert}\log\pi_\theta(y_l\mid x) - \gamma)]$; reward is the length-normalised average log-likelihood with no reference model, and a target margin γ | 4 |
| S4 | appendix table | Which β, γ and learning rate does SimPO use for Llama-3-Instruct (8B)? | β 2.5, γ 1.4, lr 1e-6 (Table 8) | 18 |
| S5 | trap | What AlpacaEval 2 LC win rate does SimPO reach when applied to Llama-3-70B? | Not reported: SimPO is not trained on a 70B model; 34.4 LC in Table 1 is the off-the-shelf Llama-3-70B-Instruct on the leaderboard | 2 |
| S6 | citation | Which work does SimPO cite for Arena-Hard, and under what reference number? | [54], Li et al., "From live data to high-quality benchmarks: The Arena-Hard pipeline", April 2024 | 14 |

### GPT-1: Improving Language Understanding by Generative Pre-Training (`llm/foundation-models`, PDF-only)

| Id | Kind | Question | Gold | Page |
|---|---|---|---|---|
| G1 | equation | What objective is optimised during fine-tuning, and with what weight on the auxiliary term? | Eq. 5: $L_3(\mathcal{C}) = L_2(\mathcal{C}) + \lambda L_1(\mathcal{C})$; λ = 0.5 | 3, 5 |
| G2 | table | In the ablation table, what average score does the Transformer without pre-training get, and which variant has the highest average? | 59.9; Transformer w/o aux LM, 75.0 (Table 5) | 8 |
| G3 | table | What accuracy does the model get on RACE-h, and what was the previous best? | 57.4; 50.3 by BiAttention MRU (9× ensemble) (Table 3) | 6 |
| G4 | setup | Give the model's layers, state size, attention heads, context length, optimizer and peak learning rate. | 12 layers, 768-d states, 12 heads, 3,072-d feed-forward, 512 tokens, Adam, 2.5e-4; 100 epochs, minibatches of 64 | 5 |
| G5 | figure only | What RACE dev accuracy is reached with 0 layers transferred and with all 12? | ≈ 40% and ≈ 60% (tol. ±3) (Figure 2, left) | 7 |

### Lost in the Middle (`llm/context`)

| Id | Kind | Question | Gold | Page |
|---|---|---|---|---|
| L1 | appendix table | With 20 documents, what is GPT-3.5-Turbo's accuracy when the answer document is first, and at its worst position; and how does the worst compare with closed-book? | 75.8% at index 0; worst 53.8% at index 9; closed-book 56.1%, so the worst position is below closed-book (Tables 6 and 1) | 18, 5 |
| L2 | figure only | In the key-value task with 300 pairs, what accuracy does GPT-3.5-Turbo (16K) reach when the key is at the 200th position? | ≈ 45% (tol. 40–50) (Figure 7) | 7 |
| L3 | figure only | With 50 retrieved documents, what are Contriever's recall and GPT-3.5-Turbo (16K)'s accuracy in the open-domain experiment? | recall ≈ 89% (tol. 87–91); accuracy ≈ 60% (tol. 58–62) (Figure 11) | 10 |
| L4 | prose | How is the key-value retrieval task built: how many pairs, what are the keys, how many examples? | 75, 140 and 300 pairs; keys and values are random 128-bit UUIDs; 500 examples per setting | 6 |
| L5 | unanswerable | What accuracy does GPT-4 reach with 30 documents? | Not reported: GPT-4 is evaluated only with 20 documents, on 500 random examples (Appendix D) | 15 |

### InstructGPT: Training language models to follow instructions with human feedback (`llm/post-training/preference-learning`, 68 pp)

| Id | Kind | Question | Gold | Page |
|---|---|---|---|---|
| I1 | side-by-side table | How many reward-model training prompts came from labelers and how many from customers? | 6,623 labeler, 26,584 customer (Table 6) | 33 |
| I2 | deep appendix | What KL coefficient and pretraining-gradient coefficient are used in PPO-ptx, and for how many episodes is RL trained? | β = 0.02, γ = 27.8; 256k episodes with about 31k unique prompts | 42 |
| I3 | deep appendix | What learning rate, batch size and number of epochs are used for the 175B SFT model? | lr 5.03e-6, batch 8, 16 epochs | 40 |
| I4 | prose (control) | How often are 175B InstructGPT outputs preferred to GPT-3's, and to few-shot GPT-3's? | 85 ± 3% and 71 ± 4% | 11 |
| I5 | trap | How many GPU-hours did PPO training of the 175B model take? | Not reported in GPU-hours; the paper gives 60 petaflop/s-days for 175B PPO-ptx and 4.9 for 175B SFT, against 3,640 for GPT-3 | 17 |

### Across papers (E3)

| Id | Kind | Question | Gold | Papers |
|---|---|---|---|---|
| X1 | equations across papers | How do the DPO, IPO and SimPO losses differ? Write each. | DPO Eq. 7 (p. 4); IPO's empirical loss Eq. 17, $\mathbb{E}[(h_\pi(y_w,y_l) - \frac{\tau^{-1}}{2})^2]$, a squared loss towards a fixed margin (p. 7); SimPO Eq. 6, length-normalised, reference-free, margin γ (p. 4) | DPO, IPO, SimPO |
| X2 | tables across papers | What AlpacaEval 2 score does each of DPO, ORPO and SimPO report for its own method on Mistral-7B? | DPO: none (no AlpacaEval 2); ORPO: Mistral-ORPO-β 12.20% raw win rate (Table 1, p. 6); SimPO: 21.5 LC / 20.8 WR (Base), 32.1 LC / 34.8 WR (Instruct) (Table 4, p. 6). The two are not comparable: LC vs raw, different bases | DPO, ORPO, SimPO |
| X3 | numbers and reasons | What effective context length do RULER and NoLiMa report for Llama 3.1 70B, and why do they differ? | RULER 64K of 128K claimed (Table 3, p. 6); NoLiMa 2K of 128K (Table 3, p. 5); NoLiMa's needles share no literal words with the question, so retrieval needs a latent association; the thresholds differ too (RULER: Llama-2-7B's 85.6; NoLiMa: 85% of each model's base score) | RULER, NoLiMa |
| X4 | enumeration (library) | Which papers in the library propose a preference-optimisation method without a reference model? | SimPO, ORPO; anything else found must be checked against `catalog` and `reviews/llm/post-training.md` before the run | library |
| X5 | synthesis (library) | Which papers in the library propose a remedy for the lost-in-the-middle position bias, and what does each change? | Found in the Middle (subtracts measured positional attention bias), Make Your LLM Fully Utilize the Context (IN2 training on synthetic long-context data), STRING in Why Does the Effective Context Length of LLMs Fall Short (shifts position indices); Lost in the Middle's own query-aware contextualization helps key-value retrieval only (`reviews/llm/context.md`, "Repairing the reader") | library |
| X6 | equations across papers | InstructGPT and DPO both start from a KL-regularised RL objective. Write each and say how they differ. | InstructGPT Eq. 2: $E[r_\theta(x,y) - \beta\log(\pi^{RL}_\phi/\pi^{SFT})] + \gamma E_{x\sim D_{\text{pretrain}}}[\log\pi^{RL}_\phi(x)]$ (p. 9); DPO Eq. 3: $\max_\pi \mathbb{E}[r_\phi(x,y)] - \beta D_{KL}[\pi_\theta \Vert \pi_{\text{ref}}]$ (p. 3); InstructGPT adds the pretraining term (γ = 27.8) | InstructGPT, DPO |

X3, X5 and X6 need their pages checked against the PDFs before the run, as the single-paper golds were.

### Conversion fixes (E4)

| Id | Paper | Question | Gold | Old markdown says |
|---|---|---|---|---|
| F1 | MuSiQue | What answer and support scores does the C-only artifact model get on MuSiQue-Ans? | An 3.4, Sp 0.0 (Table 4, p. 11) | 53.4 / 50.0 |
| F2 | Toolformer | With k = 3, for what share of WebQS examples does Toolformer call an API? | 99.3% (Table 9, p. 9) | 199.3 |
| F3 | GPT-1 | Write the fine-tuning objective, Eq. 5. | $L_3 = L_2 + \lambda L_1$ (p. 3) | only "(5)"; the text around it names $L_1$, $L_2$ and λ, so a model may rebuild it |
| F4 | Qwen3-VL | What MathVision scores do Qwen3-VL-235B-A22B (thinking) and Gemini 2.5 Pro (thinking) get? | 74.6 and 73.3 (Table 2, p. 15) | table absent |
| F5 | Qwen3-VL | What MMMU-Pro score does GPT-5 (high) get? | 78.4 (Table 2, p. 15) | table absent; the new markdown merges the MMMU and MMMU-Pro rows |
| F6 | Qwen3-VL | What MMBench-EN score does Qwen3-VL-235B-A22B (instruct) get? | 89.3 (Table 2, p. 15) | table absent; the new markdown leaves the cell empty and shows 89.3 in the MMBench-CN row |

F5 and F6 test the current markdown as much as the old: a wrong answer from the new markdown is a finding about the splice.

### Small print (E5)

| Id | Question | Gold |
|---|---|---|
| R1 | In Qwen3-VL's Table 2, what OCRBench score does Claude Opus 4.1 (non-thinking) get? | 750 (p. 15) |
| R2 | In the same table, what ZeroBench score does GPT-5 (minimal) get? | 2 (p. 15) |
| R3 | In the same table, what HallusionBench score does Claude Opus 4.1 (thinking) get? | 60.4 (p. 15) |
| R4 | In Lost in the Middle's Figure 7, with 140 pairs, what accuracy does LongChat-13B (16K) reach with the key at the 70th position? | ≈ 35% (tol. 32–40) (p. 7) |

## Before the run

- Write `questions.yaml` from these tables, and check the pages of X3, X5 and X6 against the PDFs.
- Write `run.py` (conditions, caching order, usage capture, resumable) and `judge.py`; pilot both on DPO (stage 0).
- Confirm the subscription's remaining window before each stage.
