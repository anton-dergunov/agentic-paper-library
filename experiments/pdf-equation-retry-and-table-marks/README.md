# Experiment · PDF equations read as their number, and the marks of PDF tables

**Question.** Why does a display equation of a PDF paper come out as `$$(7)$$`, and why are a PDF table's bold and underlining lost; what fixes each?

**Status.** Run 19 Oct 2026 on nine library papers. **Both causes of number-only equations found and fixed: of the 9 such equations in the four test papers, 4 read as LaTeX, 3 as the text layer's raw text and 2 stayed number-only, in a run made before the last two fixes below; re-converting one paper after them turned a raw-text equation into LaTeX. Bold and underlining come back in the four test papers' tables exactly where the PDF's fonts and rules have them.** The tickets' papers (51 with number-only equations, 100 with bold-font numbers on a table page, 127 in all) are reconverted overnight from 19 Oct; their counts are added here after it.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#pdf-only-papers).

## Number-only equations

**Size.** 112 equations in 49 of the library's 283 PDF papers read `$$(N)$$`. For each, the PDF's text layer was searched for the line "(N)": in 101 the formula's glyphs sit beside the number, in 8 the number stands alone in an empty band, 3 not found.

**Cause 1: a fragile reading of a right crop** (the 101). GPT-1's Eq. 5 (p. 3): docling's box is `[248.4, 688.9, 504.0, 698.5]` and holds the formula. surya read that exact crop as `(5)` alone, in the paper's batch and by itself, every time. Crops tried:

| Crop | Reading |
|---|---|
| docling's box (+3 pt, the reader's own margin) | `(5)` |
| +2 pt more | `L_3(\mathcal{C}) = L_2(\mathcal{C}) + \lambda * L_1(\mathcal{C}) \quad (5)` |
| +4 pt, +8 pt | the same, with a neighbour's fragment above and below (`\gamma`, `W_n`) |
| the band across the column, x 108–504 | "See the additional supplement for details of the remaining complex weights." |

Rounded to whole points, the same box read correctly: the reading flips on a fraction of a point.

**Cause 2: a box around the number only** (the 8). In a PDF made with Word (DSSM, CLSM) or with old Distiller, the formula has no text in the text layer, and docling fits a formula's box to the text cells it holds: DSSM's Eqs. 3 and 4 (p. 3) got boxes 12 pt wide (x 282–294). The band between the block above (ending y 404) and below (starting y 462), across the column (x 54–296), read the whole system: `\begin{aligned} l_1 &= W_1 x \\ l_i &= f(W_i l_{i-1} + b_i), \dots \end{aligned} \tag{3}`; Eqs. 4 and 5 likewise.

**Fix.** An equation whose reading is its number alone is read again, in one more model call per paper: from its box grown by 2 pt, then, where the box is under half its column's width, from the band. A reading is kept when it carries the same number, or, from the grown box, reads as mathematics without one (Cumulated Gain's Eq. 5 came back without its "(5)"; the number is added). Else the raw text is written when it holds more than the number.

**Results on the test papers** (reconverted with `--pdf-text --inline-math`):

| Paper | Before | After |
|---|---|---|
| GPT-1 | Eq. 5 number-only | LaTeX |
| DSSM | Eqs. 3, 4, 13, 15 | Eqs. 3, 4 LaTeX (band); 13, 15 still number-only |
| Cumulated Gain | Eqs. 5, 6 | both raw text (the pairing bug); converted again after its fix, Eq. 6 LaTeX and Eq. 5 raw text, whose correct reading without its number the number-less rule now accepts |
| SSIM | Eqs. 7, 12 | Eq. 12 LaTeX; Eq. 7 raw text (converted before the pairing bug below was fixed) |

Two bugs were found on the way and fixed before the overnight run: the retry readings were paired with the wrong equations when a paper had several (a `zip` over a shared iterator), and the rule needing the number rejected a correct reading without one.

## Bold, italics and underlining in tables

**Cause.** docling's table model keeps a cell's text and its box (`TableCell.bbox`, points from the top left), not its font. Under the box, the text layer still has each character's font: in Glorot & Bengio's Table 1 (p. 7), whose bold marks the results significant at p = 0.005, every cell is either `NimbusRomNo9L-Medi` or `-Regu`. `**…**` in a cell's text survives docling's markdown export.

**Fix.** A cell is bold (italic) when every letter and digit under its box is in a bold (text-italic) font, and underlined when a drawn rule lies within 3 pt under the text and ends within 4 pt of its ends. The first version allowed a rule up to 1.5× the text's width and underlined GPT-1's Table 1 cell over the table's bottom rule and DSSM's header cells over Word's per-cell borders (each a separate segment of the cell's width); requiring the rule to stop at the text's ends removed both. Header cells and a mark shared by every body cell are left plain.

**Results.** Glorot Table 1: bold on exactly the 14 cells set in `-Medi`. LambdaLoss Tables 3–4: the best value of each column bold. Interleaved Comparisons Tables 2 and 4: bold, and Table 4's underline on the best of each row, ties included; its grey cells are not read. GPT-1 Tables 2–5: the paper's own results bold and the previous best underlined, as the PDF has them. DSSM: a second header row that docling does not flag as a header comes out bold, as the PDF sets it.

## Apparatus

Throwaway scripts in the session, not kept: docling run on single pages to print item boxes; `scripts/pdf-equations.py` fed boxes on stdin to compare crops; a PyMuPDF scan of the 283 PDF papers for "(N)" lines and for bold-font numbers on pages with a "Table N" caption (headings like "3.1 Method" left out), which chose the papers for the overnight run. The fixtures are in `tests/test_conversion.py`.

```bash
paperlib reconvert --pdf-text --inline-math <paper.md> ...                     # the test papers
paperlib reconvert --issue pdf-equation-number-only --jobs 1 --state run.jsonl  # overnight, then
paperlib reconvert --issue pdf-table-bold --jobs 1 --state run.jsonl            # the same state file
```
