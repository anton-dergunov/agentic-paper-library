# Experiment · which converter should read papers that have no arXiv HTML?

**Question.** About 280 papers in the library have no arXiv HTML rendering and were converted from
the PDF's text layer, which keeps the prose but loses headings, tables and equations. Which PDF
converter recovers them best — docling, docling with its formula model, marker, MinerU, or a
combination — judged against arXiv's HTML for papers that have both, and at what cost in time?

**Status.** Measured 1 Oct 2026 on six papers that have arXiv HTML: **docling for structure plus
marker's equation model (surya) on docling's equation boxes puts 100% of table numbers in their
tables and reads 71% of display equations close to arXiv's LaTeX, in 0.5–2.5 minutes a paper.**
marker alone: 83% and 68%, and it splits decimals across table cells. docling alone: 100% and no
equations. The old text-layer conversion: 0% and none. **MinerU was not evaluated**: version 4
replaced the command line the runs used, and the rerun with the new one never ran. Shipped in
commits `98ffa50` (equations) and `0380b54` (docling).

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#pdf-only-papers).

## Method

- **Corpus.** [`papers.tsv`](papers.tsv): nine PDFs. Six have arXiv HTML and are scored against
  its conversion, chosen for what breaks PDF converters: DPO and SimPO (many display equations,
  multi-level tables), Zep (simple tables), Larimar and Memory Layers (equations, two-column),
  HippoRAG (large result tables). Three are the PDF-only papers a review had flagged
  (Meta-Learning for Cold-Start Personalization, a Word-made PDF; the text-prediction paper; the
  theory-of-mind paper); they have no reference and were read by eye. Neither the PDFs nor any
  converted text is committed.
- **Ground truth.** Each paper's arXiv-HTML markdown as it was in the library during the run
  (private-repo commit `18cfcb53`, the same files as this repository's `d791f1a`).
- **Candidates.**

  | Name | What ran | Script |
  |---|---|---|
  | `textlayer` | `scripts/pdf-to-markdown.py` before docling (PyMuPDF text layer), at `d791f1a` | — |
  | `docling` | docling 2.117, OCR off, formula enrichment off | [`run_docling.py`](run_docling.py) `plain` |
  | `docling-formula` | the same with docling's formula model | [`run_docling.py`](run_docling.py) `formula`, then [`run_docling_eq.py`](run_docling_eq.py) |
  | `marker` | marker 2.0.0 (`marker_single --output_format markdown`), surya 0.22.1 served by llama.cpp 0.5.0 | [`run_all.sh`](run_all.sh), [`run_rest.sh`](run_rest.sh), [`run_rest2.sh`](run_rest2.sh) |
  | `mineru` | MinerU 4.0.10, `mineru -p <pdf> -o mineru -b pipeline` | the same scripts |
  | `final` | `scripts/pdf-to-markdown.py` after `98ffa50`: docling, then each equation box cropped at 300 dpi with a 3-point margin and read by surya (`scripts/pdf-equations.py`) | — |

  The `final` outputs for DPO, Larimar and Memory Layers come from a rerun after the step that
  also reads garbled text blocks (`1b0774e`); it left their scores unchanged except DPO's count of
  decoded equations (31 → 34). Zep and HippoRAG were not run through `final`.
- **Scorer.** [`score.py`](score.py), per paper and tool:
  - **table numbers**: the share of the decimal numbers in the reference's tables that appear
    inside a table in the output (as a multiset, after rejoining docling's `34 . 8`);
  - **display equations close**: the share of the reference's display equations (six or more
    tokens) for which some equation in the output scores a token F1 of at least 0.85, LaTeX
    styling commands removed; an equation a tool set inline counts too;
  - **headings found**: the share of the reference's headings before the References whose
    normalised text occurs as a heading in the output;
  - **prose recovered**: the share of the reference's five-word sequences outside tables,
    headings, quotes and maths that occur in the output.

  ```bash
  LIBRARY=<library root at 18cfcb53> OUTPUTS=<folder with textlayer/ docling/ ...> \
    python3 score.py textlayer docling docling-formula marker final   # -> scores.txt
  ```

  [`scores.txt`](scores.txt) was regenerated on 3 Oct 2026 from the saved outputs and the ground
  truth taken from git; it reproduces the numbers reported on 1 Oct.
- **Crop settings.** [`boxes.py`](boxes.py) writes docling's equation boxes
  ([`larimar-boxes.json`](larimar-boxes.json), [`metalearn-boxes.json`](metalearn-boxes.json));
  [`eqtest.py`](eqtest.py) runs `pdf-equations.py` at three resolution and margin settings on them
  ([`eqtest.txt`](eqtest.txt)).
- **Changes to the scripts as run.** The scratch folder path in the shell scripts became the
  script's own folder; `score.py` reads the ground truth from `LIBRARY` and the outputs from
  `OUTPUTS` instead of absolute paths; `eqtest.py` takes `pdf-equations.py` and the PDF folder as
  arguments. `boxes.py` is the inline snippet the session ran, saved as a file.
- **Machine and load.** An M1 laptop, while the library-wide HTML reconversion ran alongside; the
  load average reached 66 at one point. The times are upper bounds, and marker's suffer most.

## Results

Means over the six reference papers ([`scores.txt`](scores.txt); `final` and `docling-formula`
over the papers they ran on):

| | Table numbers in a table | Display equations close to arXiv's LaTeX | Headings found | Prose recovered | Time per paper |
|---|---|---|---|---|---|
| Text layer (old conversion) | 0% | none | 0% | 91% | seconds |
| docling | 100% | none (not decoded) | 75% | 93% | 15–70 s |
| docling with its formula model (Memory Layers only) | 100% | 2 of 2, one misread | 74% | 96% | 316 s |
| marker | 83% | 68% (token F1 0.87) | 69% | 90% | 68–336 s |
| **docling + surya on docling's boxes** (4 papers) | **100%** | **71%** (token F1 0.89) | 68% | 93% | 28–148 s |

On the four papers `final` ran on, docling alone also finds 68% of headings and 93% of prose: the
equation step changes neither.

Per tool:

- **docling** takes words and digits from the PDF's own text layer, so it cannot misread a
  number; its table model put every table number in a table (HippoRAG 99%, once the
  `34 . 8` spacing is rejoined). It does not decode equations.
- **marker** reads equations best of the single tools but re-reads whole pages with a vision
  model. In HippoRAG's tables it split every decimal across two cells (`| 34 | 8 |` for 34.8), so
  only 17% of that paper's table numbers survived, and a number it reads can be wrong. Its first
  four runs failed because marker 2.0 needs llama.cpp's `llama-server`, which was then installed
  with Homebrew; the theory-of-mind paper was stopped before it finished. Meta-Learning, 5 pages,
  took 1,222 s under the heaviest load.
- **docling's formula model** spent over 15 minutes on DPO's 46 equations without finishing and
  was stopped. On Memory Layers alone it took 316 s and set `silu` as `\sinu`; the token F1 still
  counts that equation as close, so the score overstates it.
- **MinerU** failed on every paper in one to six seconds ([`mineru-failure.txt`](mineru-failure.txt)):
  4.x turned `mineru` into a document-library tool with subcommands (`mineru parse <file>`,
  backed by a local server, first ten pages by default), and `-p` now means pages. A rerun with
  `mineru parse <pdf> -p all --tier advanced` was queued in `run_rest2.sh` behind marker's reruns
  and stopped, unrun, to free the CPU once docling plus surya had settled the question.
- **docling + surya** keeps docling's tables and prose and adds marker's equation reading: the
  helper hands surya docling's equation boxes, the same per-block call marker's own equation step
  makes. A paper without equations never loads the model. About three equations in ten still
  differ from arXiv's LaTeX in a symbol or an index.

Crop settings ([`eqtest.txt`](eqtest.txt)): 192 dpi with no margin and 300 dpi with a 3-point
margin decoded Larimar's 10 equations equally (7 close; mean token F1 0.79 and 0.80); an 8-point
margin pulled in neighbouring text (6 close, and Meta-Learning's third equation lost its `\min`).
300 dpi with 3 points was kept.

On the three flagged papers, `final` converted all three in 76 s: page-marked headings, tables with
headers, figures with captions. Meta-Learning's equations came out readable but not exact (`L_T i`
for $\mathcal{L}_{T_i}$): its PDF, made with Word, prints the subscripts as literal underscores,
and its text layer has no usable characters for the mathematics at all. That led to
[`inline-math-reread`](../inline-math-reread/README.md).

## Limits

- Six reference papers, all LaTeX-made and mostly ML; one run each, under varying load.
- Tool versions were read from the installed environments on 3 Oct 2026; they were not recorded at run time.
- Ground truth is arXiv's HTML as converted by this repository, which has its own errors.
- The equation score is a bag-of-tokens F1: it ignores order and can count a one-symbol misreading
  as close. The 71% says how many equations are nearly right, not how many are exactly right.
- `docling-formula` was scored on one paper with two equations.
