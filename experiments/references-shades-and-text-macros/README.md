# References, shades and text macros

**Question.** Four conversion tickets from one triage: references that print the wrong float number (`html-shared-float-anchor`, 74 records in 66 papers), two shades of one colour marked alike (`html-colour-shades`, 16 in 13), text-mode TeX left raw in formulas (`html-math-text-macros`, 11 in 10) and an approximation sign lost before a number (`html-approx-sign-lost`, 7 in 7). What causes each, and what does fixing it change beyond the papers filed?

**Run** 21 Oct 2026 in one fix-conversions session, on the author's library (2,274 papers) and its cache of 1,979 arXiv renderings. The scripts here are the apparatus; `references.tsv` and `marks.txt` the results.

## Approximation sign

The sign is in neither the HTML nor the PDF. The author typed a text-mode `~` after a space ("reduced by ~50%"), which LaTeX sets as a non-breaking space: the PDFs print "reduced by 50%" (LiRank p. 7, the DLRM training-efficiency paper p. 6, Voxtral p. 9, read from the text layer), and the HTML a space and a no-break space. 111 of 1,979 cached renderings hold that pair before a digit. In a sample of 60 places most are prose approximations ("~86%", "~2/3", "about ~25"), but the same bytes are a tie in reference lists ("pp. ~12", "volume~3, pp. ~5"), in a number's tag ("SuppFigure ~1") and after a formula ("$\pm$~0.81").

Shipped: between a word and a digit, in the prose, the pair is written " ~". Five papers reconverted, 14 signs back, nothing else in them changed by it.

## Text macros in formulas

The Lua filter writes a command KaTeX lacks as its name (`\operatorname{textquoteright}`). Counted over the library before the fix, the names that are TeX's or LaTeX's own rather than an author's macro: `\textrm{boldmath}` 67, `\operatorname{hss}` 56, `\textrm{unboldmath}` 24, `\textrm{textdagger}` 13, `\textrm{sl}` 10, `\textbackslash` 11, `\textdoublevertline` 7, `\adjustlimits` 5, `\vtop`, `\halign`, `\raise` and a dozen text symbols once or twice. Box constructions, surveyed with `scan.py` over every cached formula: two `\perp` overlaid in a zero-width `\hbox` (independence) in 8 papers, mostly inside a `\mathchoice`; a `\not` laid over `\implies` in a zero-width box, or stacked above it in a `\vtop\halign`, in 2. amsmath's nested accent left as its internals (`\macc@depth\char 1\relax\macc@set@skewchar\macc@nested@a 111{Y}`) occurs in 2 papers, always with code 111; the MathML does not resolve it, and GRF's PDF (p. 20, rendered) prints an overbar.

Shipped: text symbols by mode, `\textsl` as italic, `\text{\boldmath$y$}` as `\boldsymbol{y}`, layout dropped, the three box constructions as `\perp\!\!\!\perp` and `\not\implies`, code 111 as `\bar`. The ten papers reconverted: every construct gone, every formula parses in KaTeX. 33 other papers hold 229 such leftovers and no record.

## Reference numbers

When two figures share one float, LaTeXML gives them one anchor, and every reference to either prints the second's number (ViT's Figures 3 and 4 are both "Figure 4"). The records show the same symptom from other causes: a `\label` the HTML attached to a section ("Table [5.2.2]"), a footnote ("Figure [18]" for Figure 3) or an algorithm line. The markdown no longer shows which floats share an anchor, so the fix reads every in-paper reference's number from the PDF's text: the words before the reference are matched in the PDF's words, and the number after them is taken.

The rule was built against the ticket's 66 papers and checked on 60 papers taken at random (`refdiff.py` lists each change; every one was compared with its record or the PDF text). Each false match on the way became a rule:

| Seen | Rule |
| --- | --- |
| e-values' equations and Switchback's theorems renumbered to the PDF's numbers, while the markdown's own tags and theorem headings keep the HTML's | the number must label a place of the kind the reference names in the markdown; a section, theorem or equation the link reaches by its own anchor keeps the HTML's number |
| A CRF tutorial's "Section [1]" became "2.1": the PDF numbers sections by chapter, and the markdown has an unrelated "2.1" | the same anchor rule |
| Model Collapse's "the estimation procedure $\mathcal{M}(\cdot)$ satisfies Assumption [3]" matched "the estimation procedure satisfies Assumption 4" elsewhere | a formula is a gap no PDF word matches; the words after it count as a short context |
| "Propositions B.3 and A.6" printed in the other order than the PDF's "A.6 and B.3" | the words after a reference are used only where fewer than five words precede it, and then the words before must match too |
| "the inductive assumption ([8.13])" read as an assumption | an equation's link is never renumbered |

Kept as matches: a reference opening its paragraph (BERTScore's "Table [6] shows correlation results", found by the words after it), and words the PDF prints twice with two numbers, told apart by the three words after the reference (RAPTOR).

Result (`references.tsv`, 124 of the 125 changes; Open Bandit's one is already in its library copy): 125 references changed in 48 of the 126 papers, 98 in 38 of the ticket's 66 and 27 in 10 of the 60 random ones. Not reached in 20 ticket papers, re-filed as `new:html-reference-number-unmatched`: the HTML printing the wrong kind ("Figure [1]" for Table 1, "Tab. [2]" for Fig. 2, "[Footnote 18]"), lost subfigure letters, row numbers, Switchback's assumptions. Two records describe the PDF's own text (LiRank's "Table 5", KAG's "Algorithm 17").

## Shades of one colour

A colour was named by its hue only, so AlignScore's dark green (best) and light green (second best) were one `<mark class="green">`; its Tables 3–4 say "The color format is the same as in Table 2" and were not marked at all; Open Bandit's legend is a "Note" paragraph under the table, outside the caption. Reconverting the ticket's 13 papers with the converter of 17 Oct had already fixed 8 of them.

`markcmp.py` runs the shading step of the committed converter and of the new one on every cached rendering with coloured tables (1,336), and `markdetail.py` shows a paper's changed tables. Three first versions were changed after this measurement:

- Naming the shades of every colour by lightness, whatever the caption says, also numbered heatmaps (46 shades of cyan in one table, whose values say it anyway). Shipped: shades are named only where the caption tells shades apart ("dark green", "darker red", "shade", "intensity") or shows each in a legend of its own, and only up to five. A split that looked wrong, two greens in one paper's prompt tables, is right: the caption calls one of them "blue", a mint green standing for a second category.
- Counting columns from the right, so a colour in every other row under spanning labels would not count as a whole column (ClashEval's header was marked instead of its prior-bias cells), broke a table whose gray columns were marked once at the top (LongBench v2: 8 marks became 104). Shipped instead: a column read from the full-width rows only counts when they are at least half the table.
- Marking a row in one colour cell by cell where the colour picks out cells did the same to row-shaded tables. Dropped; a row in one colour is still marked on its label.

Result (`marks.txt`): 14 of 1,336 papers' marks changed, each read: AlignScore's two greens in Tables 2–4 (14 marks → 70), the RAG survey's two oranges, DocRED's head and tail, four graded tables ("darker red indicates a larger share"), Open Bandit's red and blue (22 marks from none), ClashEval's prior-bias cells. FollowBench's group tints (#FFF2F2, #F2F2FF, #F2FFF2) read as white and are left: re-filed as `new:html-faint-tints`.

## Checks

`paperlib test` passes with 23 new checks. The 34 library papers reconverted keep every conversion symptom count as before, and none shrank by more than 5%.
