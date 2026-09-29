# PDF vs arXiv HTML as the agent's copy of a paper

Run on 2026-09-29. This compares three ways to turn a paper into text for an agent:

- **Raw PDF text**: PyMuPDF `get_text(sort=True)`. This is roughly what most tools feed the model:
  Zotero's PDF worker, llm-for-zotero without MinerU, PaperNook, and this repo's own fallback
  (`scripts/pdf-to-markdown.py`).
- **pymupdf4llm** 1.28: a layout-aware PDF-to-markdown converter, with no ML models.
- **arXiv HTML** converted with pandoc: the `scripts/add-arxiv-paper.sh` pipeline.

Papers used:

- **Zep** (2501.13956): single column, simple tables, no display maths.
- **DPO** and **SimPO**: maths-heavy, with multi-level tables.

## Results

| | Zep | DPO | SimPO |
|---|---|---|---|
| Display equations in arXiv HTML (exact LaTeX) | 0 | 25 | 10 |
| Numbered equations still present, raw PDF text | – | 21 of 25, flattened | 5 of 10 |
| Numbered equations still present, pymupdf4llm | – | **0** | **1** |

**Simple tables.** All three conversions kept Zep's Table 2 and Table 3 intact, one row per line.
pymupdf4llm even produced proper markdown tables. For papers like this, the PDF is fine.

**Display maths: pymupdf4llm drops it silently.** DPO's central objective (Eq. 7) is an empty gap
in its output, with no warning. Only 1 numbered equation of the 35 in the two maths papers survived.

**Raw PDF text keeps equations but flattens them.** Fractions spread over three lines, and the
reader has to reassemble the numerator and denominator from their positions.

**The worst case: a formula inside a table cell.** This is SimPO's objective in Table 3, from the raw
PDF text:

```
SimPO       −log σ  |yw| log πθ(yw|x) − |yl| log πθ(yl|x) −γ
```

The β numerators of the β/|y| length normalisation fell onto another line. That normalisation is
the whole idea of SimPO, and here it reads as a different formula. The arXiv HTML gives:

```
-\log\sigma\left(\frac{\beta}{|y_{w}|}\log\pi_{\theta}(y_{w}|x)-\frac{\beta}{|y_{l}|}\log\pi_{\theta}(y_{l}|x)-\gamma\right)
```

**Two-level table headers.** Raw PDF text keeps the rows but loses which header each column belongs
to. pymupdf4llm splits header words across cells ("Alpac" | "aEval 2"). The HTML keeps the
structure.

## Conclusion

- **Prefer arXiv HTML whenever it exists.** The advantage is real, but it is concentrated in maths
  and complex tables. For prose-and-simple-table papers, any of the three is fine.
- **Don't use pymupdf4llm as a fallback for maths papers.** Silently dropping equations is worse than
  the raw text's visible mess.
- **For PDF-only papers with maths,** an ML-based converter is the thing to test next. llm-for-zotero
  uses MinerU for this; marker and docling are alternatives.

## Reproduce

Convert with `scripts/add-arxiv-paper.sh`'s pipeline: `curl arxiv.org/html/<id>`, extract `ltx_page_content`, then
`pandoc -f html -t gfm-raw_html --wrap=none`. For the PDFs:
`pymupdf.open(pdf)[i].get_text("text", sort=True)` and `pymupdf4llm.to_markdown(pdf)`.

Sources:

- Zep: `llm/memory/agent/`,
- DPO and SimPO: `llm/alignment/preference-learning/`,

as markdown under `library/` and as PDFs under `~/Yandex.Disk.localized/Papers/`.
