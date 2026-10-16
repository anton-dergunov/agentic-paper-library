---
id: html-figure-download
title: Figures of arXiv-HTML papers that cannot be downloaded stay links to arXiv
converter: html
takes: [engine, reconvert]
closed: '2026-10-16'
cost: 'engine: small (download checks, a fallback to the paper''s LaTeX source); reconvert the papers'
---

# Figures of arXiv-HTML papers that cannot be downloaded stay links to arXiv

`engine` `reconvert` · html · done

**Broken.** A figure the converter cannot download or decode keeps its absolute arXiv link, and `paperlib reconvert` reports the paper `partial` ("N figures could not be downloaded and still link to arXiv"). The same 16 papers (206 figures) were partial in every full reconversion from 1 to 16 Oct 2026, so retrying does not help. Three causes:

- **arXiv's HTML links a file its server does not have** (404): 199 figures in 9 papers. 192 of them are in the paper's LaTeX source (the e-print) under exactly the linked path and decode; the other 7 (Automated Circuit Discovery) are PDFs in the source, under another folder.
- **arXiv serves a truncated file**: 4 figures (Failing Loudly, Genie, Baidu ranking, UI-TARS); the source holds an intact copy of 3. A draw.io PNG (class-imbalance study) is refused by Pillow, in the source too: draw.io rewrote the diagram it keeps in a text chunk but not the chunk's checksum.
- **A download cut off by curl's time limit was cached as complete**: 2 figures (diffusion augmentation, the NeurIPS 2019 reproducibility report). `download` read only the HTTP status, so a timed-out transfer (exit 28, status 200) was stored, and every later run reused it.

**Fix.** Done 16 Oct 2026 for 199 of the 206 figures (`paperlib.download`, `localize_figures`, `source_images`, `png_without_bad_chunks`): a download counts only when curl exits cleanly (a stalled one is dropped after 60 s below 1 KB/s, a slow one may take 10 minutes); a figure that will not decode is downloaded again when its copy came from the cache, then taken from the paper's LaTeX source under the same path, then, for a PNG, decoded with its ancillary chunks of bad checksum dropped. A cut-off file is not decoded as far as it goes: Failing Loudly's `6_diff.png` came out two-thirds black, which would read as part of the figure; it keeps its link (wont-fix: no intact copy on arXiv). 14 of the 16 papers now reconvert `ok`, with no text changed. Automated Circuit Discovery's 7 plots are wont-fix: its source has them only as PDFs, under `figs/` rather than the linked path, and 4 exist in two colour variants (`plots_rgb/`, `plots_yellow/`) that a LaTeX `\ifthenelse` chooses between. If the pattern recurs, the safe rule is: when the linked file is nowhere, take the one file in the source with the same name stem in any folder, rasterizing a PDF, and skip a stem with several matches (Failing Loudly's source has a dozen different `top_diff.jpg`); here that would give 3 of the 7, not the main-text ROC plot.

**What it gives.** The figures themselves, where the markdown has only a link to arXiv; GANsformer (127), Taming Transformers (40) and GPT-3's scale plots (12) the most.

**Cost.** Engine: small (download checks, a fallback to the paper's LaTeX source); reconvert the papers.

**Examples.** Generative Adversarial Transformers (127 figures, attention maps and samples); Taming Transformers (40 samples); Language Models are Few-Shot Learners (12 scale plots, `superglue_--_boolq.png`); Effective Data Augmentation With Diffusion Models (`site_tiled.png`, half cached).
