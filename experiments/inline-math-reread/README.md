# Experiment · can paragraphs with lost or flattened mathematics be re-read from the page image?

**Question.** A PDF's text layer gives inline mathematics as bare letters ("$q \in \mathbb{R}^n$"
comes out as "q ∈ R n"), and a PDF made with Word can lose the symbols altogether ("a task _ ~ ( )").
The PDF converter already has surya, marker's model, read each display equation from its crop of
the page. Does reading whole paragraphs the same way give their inline mathematics as LaTeX, can a
guard keep the model from changing the words and numbers, and what does it cost?

**Status.** Measured 2 Oct 2026 on three papers that have arXiv HTML: **inline formulas reproduced
closely went from 0%, 0% and 31% to 76%, 84% and 98%** (Memory Layers, Larimar, DPO). **All 112
readings passed the guard, and no number in prose, tables or display equations changed.** It costs
**about 8 seconds a paragraph**, about 26 hours for the library's 279 PDF-only papers. Shipped in
commits `1b0774e` (garbled text) and `93cbfb8` (inline mathematics).

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#equations).

## Method

- **What gets read.** `scripts/pdf-to-markdown.py` sends a text block that docling found to
  `scripts/pdf-equations.py`, which crops it at 300 dpi and has surya read it, when:
  - its text is **garbled**: a stand-alone underscore, a replacement character, or Word-style
    Unicode sub- and superscripts. Always on since `1b0774e`;
  - or it has **mathematics worth writing as LaTeX**: any span in a mathematics font (`cmmi`,
    `cmsy`, `msbm`, …) or more than 2% mathematical characters, the rule marker uses. This is
    the `--inline-math` measured here.
- **The guard** (`trusted_reading`). A reading replaces the text layer's text only if it keeps at
  least 80% of the block's words and every number in it, since a misread digit would be silent.
  Otherwise the PDF's own text stays.
- **Corpus.** Memory Layers, Larimar and DPO, from the
  [bake-off](../pdf-converter-bakeoff/README.md) set, each converted from its PDF twice: without
  (`final`) and with (`inline`) the reading of mathematics paragraphs. SimPO was started and
  stopped before it finished. The reference is each paper's arXiv-HTML markdown, as in the
  bake-off. No converted text is committed.
- **Scorer.** [`score_inline.py`](score_inline.py), on top of the bake-off's
  [`score.py`](../pdf-converter-bakeoff/score.py): arXiv's inline formulas in running text (three
  or more tokens, outside display equations, tables, headings and quotes) count as reproduced
  closely when some inline formula in the output has a token F1 of at least 0.85 with them. It
  also reports prose recovered (five-word sequences) and the share of the reference's decimal
  numbers in running text that the output keeps.

  ```bash
  LIBRARY=<library root at 18cfcb53> OUTPUTS=<folder with final/ and inline/> \
    python3 score_inline.py memlayers larimar dpo                    # -> scores-inline.txt
  LIBRARY=... OUTPUTS=... python3 ../pdf-converter-bakeoff/score.py final inline   # -> scores-structure.txt
  ```

  Both result files were regenerated on 3 Oct 2026 from the saved outputs and reproduce the
  session's numbers.
- **Other apparatus.** [`eq-text.py`](eq-text.py) is the probe that first asked surya for a text
  block instead of an equation, on Meta-Learning's four garbled blocks
  ([`metalearn-text-boxes.json`](metalearn-text-boxes.json)); a `sed` variant of
  `pdf-equations.py`, kept as run with a docstring added. [`count_math_blocks.py`](count_math_blocks.py)
  counts the blocks the rule would send in every PDF-only paper ([`math-blocks.txt`](math-blocks.txt));
  its library path was made relative, otherwise it is the inline snippet as run.
- **Machine and load.** An M1 laptop, with the library-wide reconversion running alongside, so the
  times are upper bounds.

## Results

### Garbled text (Meta-Learning for Cold-Start Personalization)

The paper was made with Word and its text layer has no characters for its mathematics. Asked for
the four garbled blocks, surya returned the sentences with inline LaTeX in 40 seconds, e.g.
"Let $U = \{u_1, u_2, \dots, u_n\}$ be a set of users". One of the four, `_ ∑_ _ _ ( _ ')`, was a
display equation docling had labelled text; a block that is nearly all symbols is now read as an
equation. The model reads the PDF's own sloppy typesetting faithfully: the PDF prints literal
underscores, and the reading has `L_i T_i` where the paper means $\mathcal{L}_{T_i}$.

### Inline mathematics

From [`scores-inline.txt`](scores-inline.txt):

| | Memory Layers | Larimar | DPO |
|---|---|---|---|
| Inline formulas in arXiv's HTML | 17 | 87 | 86 |
| Reproduced closely, text layer only | 0% | 0% | 31% |
| Reproduced closely, with the model | **76%** | **84%** | **98%** |
| Mean token F1 of the best match, before → after | 0.00 → 0.85 | 0.00 → 0.94 | 0.59 → 0.99 |
| Paragraphs read, accepted by the guard | 6 of 6 | 50 of 50 | 56 of 56 |
| Prose recovered, before → after | 96% → 96% | 92% → 93% | 95% → 97% |
| Numbers in running text kept, before → after | 14% → 14% | 58% → 58% | 47% → 47% |

- **Nothing else moved** ([`scores-structure.txt`](scores-structure.txt)): table numbers stay at
  100%, headings and display equations are unchanged. DPO's display-equation score rises from
  0.63 to 0.65 only because the scorer also accepts an inline formula as a match.
- **The guard rejected nothing** in 112 readings. It was not tested here on a reading that should
  have been rejected; [`tests/test_conversion.py`](../../tests/test_conversion.py) checks it on constructed cases.
- **Detection by font is uneven.** Memory Layers sets its text in CM-Super and only 78 characters
  in a maths font ([`fonts.txt`](fonts.txt)), and only 6 of its paragraphs were read; its 76% is
  the lowest of the three.
- The low "numbers in running text" shares are the scorer's: arXiv's HTML often sets a number in
  prose as mathematics. The point is that they are identical before and after.

### Cost

From [`times.txt`](times.txt): Memory Layers 41 → 97 s, Larimar 66 → 467 s, DPO 148 → 639 s, which
is 8.0–9.3 s for each paragraph read. Across the library's 279 PDF-only papers the rule would read
11,738 paragraphs ([`math-blocks.txt`](math-blocks.txt)): median 16 a paper (about two minutes), 79
papers with none, 20 with over 100, and 1,216 in *The Algorithmic Foundations of Differential
Privacy*. That is about 26 hours of model time.

So adding a paper always reads its mathematics paragraphs, which costs minutes for one or two
papers a day, and bulk reconversion leaves it out unless asked (`reconvert.py --pdf-text
--inline-math`).

## Limits

- Three LaTeX-made papers, one run each. The Word-made paper that prompted the step has no
  reference, so its gain was checked by eye only.
- "Reproduced closely" is a bag-of-tokens F1 of at least 0.85: a swapped index or a dropped
  subscript can still count.
- The guard checks words and numbers, not symbols: a reading that keeps every word and digit but
  misreads a Greek letter or an operator is accepted.
