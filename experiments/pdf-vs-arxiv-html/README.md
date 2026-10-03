# Experiment · does arXiv's HTML rendering beat PDF text extraction for equations and tables?

**Question.** An agent reads a paper as text. arXiv renders most recent papers to HTML from their LaTeX source (LaTeXML), and that HTML can be converted to markdown with pandoc. The alternative, open to every paper, is extracting text from the PDF. Which keeps equations and tables intact, and is the difference large enough to make the HTML the default source?

**Status.** Measured 29 Sep 2026 on three papers, Zep, DPO and SimPO: **in the two maths papers the HTML kept all 35 display equations as exact LaTeX; pymupdf4llm kept the equation number of 1, and DPO's objective is an empty gap in its output; raw PyMuPDF text kept 26 equation numbers, with the equations flattened over several lines.** On Zep's simple tables all three conversions were fine. The difference is concentrated in maths and multi-level tables.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#why-arxiv-html).

## Method

- **Corpus.** Three papers:
  - **Zep** ([2501.13956](https://arxiv.org/abs/2501.13956)): single column, simple results tables, no display maths.
  - **DPO** ([2305.18290](https://arxiv.org/abs/2305.18290)) and **SimPO** ([2405.14734](https://arxiv.org/abs/2405.14734)): maths-heavy, with results tables that have two header rows and a table of objectives with a formula in each cell.
- **Conversions compared.**
  - **Raw PDF text**: PyMuPDF's `get_text("text", sort=True)`, page by page. This is what most tools that read a PDF's text layer hand to a model (Zotero's PDF worker is one), and it was the library's own fallback for papers without HTML at the time (`scripts/pdf-to-markdown.py`).
  - **pymupdf4llm** 1.28.0: a layout-aware PDF-to-markdown converter with no ML models for text. It ran Tesseract OCR on a few pages it judged to be images (pages 2, 17 and 27 of DPO; 7, 9 and 19 of SimPO; none of Zep).
  - **arXiv HTML through pandoc**: fetch `arxiv.org/html/<id>`, cut out LaTeXML's `ltx_page_content` element, convert with `pandoc -f html -t gfm-raw_html --wrap=none`. This was the library's `add-arxiv-paper.sh` pipeline that day, before any of the later fixes to the converter.
- **Apparatus.** [`convert.py`](convert.py) produces the three conversions; [`count.py`](count.py) counts what each kept. Both are reassembled from the commands run in the session: the code is as run, with the paper and the directory turned into arguments.

  ```bash
  python3 convert.py html 2501.13956v1 zep        # -> zep_html.md
  python3 convert.py pdf zep.pdf zep              # -> zep_pdftext.md, zep_p4llm.md
  python3 count.py .                              # -> results/counts.txt
  ```

  In the run only Zep's HTML was converted fresh. DPO's and SimPO's `_html.md` were copies of markdown made earlier with the same pipeline, by the library this one replaced; the arXiv versions they were made from were not recorded. The DPO PDF is v3 (July 2024).
- **Judging.** The counts in [`results/counts.txt`](results/counts.txt) are automatic. The qualitative findings come from reading the same passages side by side: Zep's Tables 2 and 3, DPO's objective (Eq. 7), SimPO's main results table (Table 4) and its table of objectives (Table 3).
- **Outputs.** [`outputs/`](outputs/) holds the three conversions of DPO, which arXiv distributes under CC BY 4.0 (Rafailov et al., *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*, 2023). Zep (CC BY-NC-SA 4.0) and SimPO (arXiv's non-exclusive licence) are not redistributed; the snippets quoted below are a line or two each.

`count.py` was re-run on 3 Oct 2026 on the saved conversions and printed the same numbers as on 29 Sep.

## Results

| | Zep | DPO | SimPO |
|---|---|---|---|
| Display equations in arXiv HTML (exact LaTeX) | 0 | 25 | 10 |
| Equation numbers still present, raw PDF text | – | 21, flattened | 5, flattened |
| Equation numbers still present, pymupdf4llm | – | **0** | **1** |
| Inline math spans in arXiv HTML | 73 | 236 | 148 |

**Simple tables survive any conversion.** All three kept Zep's Table 2 and Table 3 intact, one row per line, and pymupdf4llm even produced proper markdown tables. For a paper of prose and simple tables, the PDF is fine.

**pymupdf4llm drops display maths silently.** DPO's central objective, Eq. 7, is an empty gap in its output: the sentence "our policy objective becomes:" is followed by blank lines and then the next paragraph, with no placeholder and no warning. Of the 35 display equations in the two maths papers, the number of one survived.

**Raw PDF text keeps equations but flattens them.** Fractions spread over three lines, and the reader has to reassemble numerator and denominator from their horizontal positions. DPO's Eq. 7:

```
                                             πθ(yw | x)         πθ(yl | x)
      LDPO(πθ; πref) = −E(x,yw,yl)∼D  log σ  β log       −β log                      .     (7)
                                                      πref(yw | x)          πref(yl | x)
```

The HTML gives the author's LaTeX:

```
\mathcal{L}_{\text{DPO}}(\pi_{\theta};\pi_{\text{ref}})=-\mathbb{E}_{(x,y_{w},y_{l})\sim\mathcal{D}}\left[\log\sigma\left(\beta\log\frac{\pi_{\theta}(y_{w}\mid x)}{\pi_{\text{ref}}(y_{w}\mid x)}-\beta\log\frac{\pi_{\theta}(y_{l}\mid x)}{\pi_{\text{ref}}(y_{l}\mid x)}\right)\right].
```

**The worst case is a formula inside a table cell.** SimPO's objective, in its Table 3, from the raw PDF text:

```
SimPO       −log σ  |yw| log πθ(yw|x) − |yl| log πθ(yl|x) −γ
```

The β numerators of the β/|y| length normalisation fell onto another line. That normalisation is the whole idea of SimPO, and here the line reads as a different formula. The HTML gives:

```
-\log\sigma\left(\frac{\beta}{|y_{w}|}\log\pi_{\theta}(y_{w}|x)-\frac{\beta}{|y_{l}|}\log\pi_{\theta}(y_{l}|x)-\gamma\right)
```

**Two-level table headers lose their structure in both PDF conversions.** In SimPO's Table 4 (four model settings side by side in pairs, three benchmarks, one to two metrics each), the raw text keeps every row but not which header each column belongs to. pymupdf4llm splits header words across cells (`|**Alpac**|**aEval 2 **|`, `|**L**|**lama-3-Base**|**(8B)**|`). The HTML keeps the structure.

What followed:

- **arXiv's HTML became the source whenever it exists**, and the PDF text only the fallback.
- **pymupdf4llm was not adopted as the fallback for maths papers.** A silent loss is worse than the raw text's visible mess, because the agent cannot tell that something is missing.
- **PDF-only papers with maths needed an ML-based converter**, which was compared next, on 1 Oct 2026 (docling, marker, and a model reading equations from page images).

## Limits

- Three papers, chosen by hand to span the two cases; no sample of the library.
- "Equation numbers still present" is a proxy: the distinct `(k)` with 0 < k < 40 at the end of a line. A surviving number shows the equation is at least partly there, and the line it ends can still be garbled; a stray `(k)` ending a prose line would also count. The 25 and 10 are the HTML's display-math blocks; the HTML conversions show 22 and 7 distinct equation numbers, so raw PDF text kept the number of nearly every numbered equation in DPO and fewer than half in SimPO.
- The display count misses equations LaTeXML lays out as tables (aligned multi-line equations), which pandoc wrote as markdown tables with inline math. For the same reason the table counts `count.py` prints (104 and 74 delimiter rows in the HTML) count equation layouts as well as tables, and were not used.
- The PyMuPDF and pandoc versions of the run were not recorded.
