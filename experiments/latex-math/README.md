# Experiment · formulas in LaTeX, used where they help

**Question.** Answers, notes and overviews write formulas as text: `q = W_q·x` in a chat, `π_r ∝ π_ref·exp(r/β)` in a digest. And the overview format allowed "at most one small formula", so the 35 overviews in the author's vault had none. Every place these are read can draw LaTeX. If the prompts ask for LaTeX, rewritten from the text layer, and for formulas wherever they carry the idea, do the outputs get the formulas that matter, readable, without gaining decorative ones?

**Status.** Measured 31 Oct 2026, on Haiku 5.5. **The rules shipped**:
- in the overview format (§ Math, rewritten) and the review format;
- in the guide, as one bullet;
- in the reading prompt, as one sentence.

Results:
- **Overviews:** before, none of the 5 had a formula. After, the three papers whose idea is a formula (DPO, LoRA, BM25) had theirs in both runs, with every symbol defined. The two without one (Zep, JudgeBench) gained one inline formula in one of the two runs.
- **Digests:** the old reading prompt gave math as Unicode text (22 symbols in DPO's digest); the new one gave LaTeX in all four.
- **Chat:** the KV-cache answer gave the attention formula in one of two runs.
- **Rendering:** all 191 formulas render in KaTeX.

The experiment cost $0.66.

**Serves.** [`docs/design.md`](../../docs/design.md#decisions-log), [`skills/overview/format.md`](../../skills/overview/format.md), [`skills/literature-review/format.md`](../../skills/literature-review/format.md), [`guide/library-guide.md`](../../guide/library-guide.md), [`guide/reading-prompt.md`](../../guide/reading-prompt.md).

## What draws LaTeX

| Where it is read | Draws | Evidence |
|---|---|---|
| Claude Code's panel in VS Code (2.1.314) | `$…$`, `$$…$$`, `\(…\)`, `\[…\]` | Its webview bundles KaTeX through a micromark maths extension. It looks for `$$`, `\(…\)`, `\[…\]` or an inline `$` pattern in an answer, then loads KaTeX for it. Read from `webview/index.js` |
| carrel (chat, digests, reviews, overviews) | the same four | `src/carrel/static/markdown.js`, KaTeX 0.19.0, Pandoc's `$` rule |
| VS Code's markdown preview (notes, reviews) | `$…$`, `$$…$$` | built in (`markdown.math.enabled`); not tested here |
| Obsidian (overviews) | `$…$`, `$$…$$` | its documentation; not tested here |

So the prompts ask for `$…$` and `$$…$$`, the forms all four draw. Prices stay text: the panel and carrel need no space after an opening `$` and none before a closing one, so "$1.24 to $0.36", already in a review, is not read as maths. No mod or extension was needed.

## Method

- **Papers** ([`papers.txt`](papers.txt)), from the author's library:
  - formula at the core: DPO, LoRA;
  - mathematical: The Probabilistic Relevance Framework (BM25);
  - little maths: Zep, JudgeBench;
  - for the chat question: PagedAttention.
- **The library.**
  - [`setup.sh`](setup.sh) copies those papers, their notes, the catalog, the reviews and the reader's `AGENTS.md` into a scratch library, with `overview_dir` inside it, so nothing is written to the vault.
  - [`reset.sh`](reset.sh) puts it back before each run. It installs an engine's overview skill set to Haiku (the skill pins Opus), and that engine's guide.
- **Runs.** [`run.sh`](run.sh) runs the overview skill on the five papers, plus a chat question in a fresh session: the one from the chat that prompted this ("How does KV cache work? … add links to … equations"). Everything runs on Haiku through `claude -p`.
  - `base`: the prompts at commit `abcc581`;
  - `first-draft`: the first version of the rules;
  - `final-1`, `final-2`: the rules as shipped.
- **Digests.** `paperlib read --redo --model haiku` on DPO, BM25, PagedAttention and Zep.
  - The old reading prompt ran from `git archive HEAD` unpacked in the scratchpad.
  - The new prompt ran from the working tree.
- **Checks.**
  - [`count.py`](count.py) counts display and inline formulas, maths in code spans, maths in Unicode symbols, and words.
  - [`katex-check.mjs`](katex-check.mjs) renders every formula with carrel's KaTeX and fails on an error.
  - The formulas were read by hand.
- **Results** ([`results/`](results/)): every overview and chat answer, the digests, and [`counts.txt`](results/counts.txt).
  - The chat answers' links are cut to the library-relative path: the scratch library's PDFs are symlinks, so `paperlib locate` printed absolute paths for one answer.
  - The papers' text is not committed.

## Results

Formulas per overview (display + inline), over two runs of the final rules:

| | base | first draft | final-1 | final-2 |
|---|--:|--:|--:|--:|
| DPO | 0 | 9 | 12 | 8 |
| LoRA | 0 | 18 | 22 | 26 |
| BM25 | 0 | **0** | 12 | 16 |
| Zep | 0 | 0 | 1 | 0 |
| JudgeBench | 0 | 0 | 0 | 0 |
| KV-cache chat answer | 0 | 0 | 0 | 8 |

Code-span or Unicode maths: none in any overview or answer, before or after. The text formulas the reader saw came from Opus sessions; Haiku without the rule mostly wrote no formula at all. Word counts stayed in the same range (616–1,084).

- **What the formulas look like** (final runs):
  - DPO: the loss in display maths, followed by a sentence defining $\pi_\theta$, $\pi_{\text{ref}}$, $y_w$, $y_l$, $\sigma$ and $\beta$ and saying what it means. In Concepts, Bradley–Terry as $P(y_w \succ y_l) = \sigma(r(y_w) - r(y_l))$.
  - LoRA: the method's four steps around $W_0 + BA$, and the rank argument with $B \in \mathbb{R}^{d \times r}$.
  - BM25: the scoring function, split with `\underbrace` into "rarity of $t$" and "length correction" in one run, and with $B_d$ defined apart in the other, with each symbol defined.
  - Zep: the one formula, $t^{\text{old}}_{\text{invalid}} \leftarrow t^{\text{new}}_{\text{valid}}$, repeats in symbols what its sentence says: decoration, the kind the rules ask against, once in two runs.
- **The first draft** said "a formula where it says the idea better than words". BM25's overview still had no formula, and the chat answer gave attention in words. The shipped rules first say *give the formula that is the idea* (a loss, an update rule, a scoring function), and the guide's bullet names the chat case: "when a mechanism is a formula (attention, a loss, a score), give it".
- **Digests** (formulas / Unicode maths symbols):

  | | old prompt | new prompt |
  |---|---|---|
  | DPO | 0 / 22 | 16 / 0 |
  | BM25 | 0 / 4 | 27 / 0 |
  | PagedAttention | 0 / 0 | 6 / 0 |
  | Zep | 0 / 0 | 10 / 0 |

  The old digest wrote `π_r ∝ π_ref·exp(r/β)`. The new one wrote $\hat r_\theta(x,y)=\beta\log\frac{\pi_\theta(y|x)}{\pi_{ref}(y|x)}$ and the full loss with its symbols named. Zep's digest uses the paper's own retrieval notation, $f(\alpha)=\chi(\rho(\phi(\alpha)))$, which is useful in an agent's note.
- **Rendering.** All 191 formulas in the results render in KaTeX 0.19.0 with errors on.
- **Cost.** $0.57 for 24 sessions and $0.09 for 8 reads. The guide's bullet adds about 70 tokens to every turn in a library.

## Conclusions

1. Ask for LaTeX, in `$…$` and `$$…$$`, rewritten from the text layer. The panel, carrel, VS Code's preview and Obsidian all draw it, so no mod or extension is needed.
2. Stop rationing formulas, and say how to use them: give the one that is the idea; elsewhere use one only where it beats words; define each symbol; split a long formula into parts; explain a heavy one; worked examples are welcome. On these papers that added the formulas that matter and almost no others.
3. **Limits.**
   - Haiku, not the Opus the reader's sessions run on. This shows whether the rules are followed, not exactly how an Opus overview reads.
   - Two runs of the final rules and one of the others.
   - Five overviews and one chat question.
   - No review was written. The review format's rule is the overview's restated, not measured.
   - Obsidian and VS Code's preview were not opened; KaTeX stood in for both.
