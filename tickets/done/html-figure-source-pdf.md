---
id: html-figure-source-pdf
title: A figure arXiv serves broken, which the LaTeX source has only as a PDF
converter: html
takes: [engine, reconvert]
closed: '2026-10-22'
cost: 'engine: small; reconvert the papers whose figures still link to arXiv (minutes)'
---

# A figure arXiv serves broken, which the LaTeX source has only as a PDF

`engine` `reconvert` · html · done

**Broken.** arXiv's HTML links a figure as a PNG it made from the author's PDF figure. Sometimes that PNG is missing on arXiv's server or cut off. `localize_figures` then looks in the paper's LaTeX source under the same path, but takes only raster and SVG files. Two other things defeat that lookup:

- LaTeXML often drops the directories, so `figs/6_diff.pdf` is linked as `6_diff.png`.
- An author may keep a figure in several variants and choose one with a TeX switch: ACDC has every ROC plot in `figs/plots_rgb/` and `figs/plots_yellow/`, chosen by `\ifthenelse{\boolean{ispreprint}}`.

So the figure keeps an absolute arXiv link that shows nothing: Failing Loudly's `6_diff.png` (p. 6, served cut off at a third) and ACDC's seven ROC and metric plots (pp. 6, 21, 23, not on the server). `paperlib reconvert` reports both papers as partial on every run.

**Fix.** When neither arXiv's copy nor the source's file at the same path decodes, look for the figure in the source by its name without extension: first at the same path, then by its file name in any directory. A PDF found that way is rendered (its first page, by pymupdf) and saved like any raster. Where several different files fit, take the one in the directory the TeX selects. That needs the source's simple switches resolved: `\ifthenelse{\boolean{x}}{…}{…}` with `\setboolean`, and `\ifx … \else … \fi` with `\newif`. When the TeX does not settle it, keep the link rather than guess.

Fixed 22 Oct 2026 (`source_figure`, `tex_resolved`, `render_pdf_figure` in `paperlib.py`). The source's PDFs and TeX files are read with its images. A PDF is rendered at `FIGURE_MAX_SIDE` and goes through `to_webp`. A directory counts as named in the TeX when it, or its last parts (under a `\graphicspath`), appears as a whole path once the switches are resolved. These were the only two library papers whose figures still linked to arXiv. Both reconverted `ok` with no link left, and only their image links changed: Failing Loudly's averages of the 6s, and ACDC's seven plots in the `plots_rgb` colours its preprint switch selects. Four new checks: a PDF in another directory, variants chosen by `\ifthenelse`, two variants the TeX does not tell apart, and a `\newif` switch.

**What it gives.** The figure itself instead of a dead link, in these two papers and in any later paper whose figure arXiv fails to serve.

**Cost.** Engine: small; reconvert the papers whose figures still link to arXiv (minutes).

**Examples.** "Failing Loudly. An Empirical Study of Methods for Detecting Dataset Shift" p. 6; "Towards Automated Circuit Discovery for Mechanistic Interpretability" pp. 6, 21, 23.
