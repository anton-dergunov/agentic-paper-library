# Experiment · how many figures did the converter drop as SVG objects, and what should they be stored as?

**Question.** In *Spurious Rewards* only the legend squares of Figure 3 survived conversion: the
eight plot panels were gone. arXiv's HTML embeds them as `<object type="image/svg+xml"
data="….svg">`, not `<img>`, and pandoc drops the element. How many papers in the library lost
figures this way, and once they are restored, should an SVG be kept as a vector or rasterized like
other figures?

**Status.** Measured 1 Oct 2026 over the 1,185 papers converted from arXiv HTML: **831 of them
(70%) had image `<object>` figures, 10,016 in all, every one dropped.** A sample of 94 of those SVGs
had a median of 97 KB, but a mean of 234 KB and a maximum of 4.3 MB. **Rasterizing only SVGs over
300 KB to WebP converts 17 of the 94 and cuts the projected cost of the 10,016 figures from 2.24 GB
to 0.91 GB on disk, and from 435 MB to 326 MB in git.** The threshold shipped and the 830 affected
papers were reconverted the same day.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html).

## Method

- **The fix measured.** Before pandoc runs, each `<object>` with an image type becomes an `<img>` of
  the same file, so the existing figure downloader saves it. On *Spurious Rewards* that brought the
  images from 107 to 239, with no links left to arXiv.
- **Census.** [`scan_objects.py`](scan_objects.py) fetches the arXiv HTML of every `source: html`
  paper at the version of its PDF and counts `<object type="image/…">` elements. Its output,
  reduced to arXiv id and count, is [`objects.tsv`](objects.tsv); the aggregates are in
  [`objects-summary.txt`](objects-summary.txt).

  ```bash
  python3 experiments/svg-figures/scan_objects.py <scripts dir> objects.tsv
  ```

- **Size sample.** [`sample_sizes.sh`](sample_sizes.sh) draws 40 papers at random from those with
  objects ([`sample_ids.txt`](sample_ids.txt)) and records the size of up to three SVGs from each:
  94 files, in [`svg-sizes.txt`](svg-sizes.txt).
- **Threshold sweep.** [`threshold_sweep.py`](threshold_sweep.py) rasterizes each sampled SVG with
  `rsvg-convert` at 1,600 px wide and encodes it with the library's own `to_webp` (quality 85, as for
  every raster figure). For each threshold it keeps SVGs at or under it as vectors and the rest as
  WebP, and projects to 10,016 figures. Git's cost is approximated by zlib level 9 for an SVG,
  since git compresses text, and by the WebP's own size. It was re-run on 3 Oct 2026 on the saved
  SVGs and reproduced the session's numbers exactly ([`threshold-sweep.txt`](threshold-sweep.txt)).

  ```bash
  python3 experiments/svg-figures/threshold_sweep.py <scripts dir> <svgs dir>
  ```

- **What was changed when copying.** The scan and the sweep were inline scripts with the private
  repository's paths hard-coded; they now take the scripts directory and the input and output paths
  as arguments, and the sweep's two passes (averages, then thresholds) are one script.
  `sample_sizes.sh` joins two shell commands from the session. The downloaded SVGs are arXiv's
  renderings of the papers' figures and are not committed.

## Results

### How much was lost

| | |
|---|---|
| Papers converted from arXiv HTML | 1,185 |
| with image `<object>` figures | **831 (70%)** |
| figures dropped | **10,016** |
| per affected paper | median 6, 90th percentile 23, max 591 (RewardBench) |
| papers with 1–5 / 6–20 / 21–50 / 51+ | 381 / 350 / 75 / 25 |

The loss did not show in the markdown: a figure's caption stayed, only the image above it was
missing. RewardBench had 19 figure captions and 1 image.

### Vector or raster

| Rasterize SVGs over | Rasterized in sample | Per figure on disk | Per figure in git | 10,016 figures on disk | in git |
|---|---|---|---|---|---|
| never | 0 of 94 | 235 KB | 44 KB | 2.24 GB | 435 MB |
| 500 KB | 9 | 119 KB | 34 KB | 1.14 GB | 328 MB |
| **300 KB** | **17** | **95 KB** | **33 KB** | **0.91 GB** | **326 MB** |
| 200 KB | 20 | 90 KB | 34 KB | 0.86 GB | 329 MB |
| 100 KB | 47 | 67 KB | 42 KB | 0.64 GB | 409 MB |

- **Most SVGs should stay vectors.** At the median of 97 KB a plot compresses to a fraction of its
  size in git, and a WebP of it would cost more there (rasterizing everything over 100 KB makes git
  larger, 409 MB).
- **A few dense plots carry the cost.** The largest sample, a 4.3 MB scatter plot, became a 75 KB
  WebP that still reads. A threshold of 300 KB rasterizes 18% of the files, takes most of the disk
  saving, and is at the git minimum; going lower buys little on disk and starts to cost in git.
- **The rule shipped as** `SVG_MAX_BYTES = 300_000`: an SVG figure over 300 KB is rasterized with
  `rsvg-convert` and stored as WebP like any other raster figure, and anything smaller stays SVG.

### The repair

All 830 remaining affected papers (*Spurious Rewards* had been fixed first) were reconverted, every
one "ok". 137 figures in 6 papers failed to download at first and kept an arXiv link; a list of 16
papers was then re-localized, and its outcome was not recorded here. The whole change set, with the
papers added in the same session, came to 2.2 GB on disk and an estimated 1.1 GB compressed: 16,647
SVGs (1,183 MB, compressing to 18%) and 15,177 WebPs (855 MB, which do not compress), close to
GitHub's 2 GB limit for one push.

## Files

| File | Holds |
|---|---|
| [`scan_objects.py`](scan_objects.py) | the census |
| [`objects.tsv`](objects.tsv), [`objects-summary.txt`](objects-summary.txt) | its result per paper (arXiv id, objects) and in aggregate |
| [`sample_sizes.sh`](sample_sizes.sh) | the sample and its SVG sizes |
| [`sample_ids.txt`](sample_ids.txt), [`svg-sizes.txt`](svg-sizes.txt) | the 40 papers and 94 SVG sizes |
| [`threshold_sweep.py`](threshold_sweep.py), [`threshold-sweep.txt`](threshold-sweep.txt) | the sweep and its output |

## Limits

- 94 SVGs from 40 papers; the projection to 10,016 figures assumes they are typical. The mean is
  driven by a few multi-megabyte files, so a different sample could move the totals noticeably.
- The git cost is a zlib estimate, not a measured pack size.
- The rasterized plots were checked by eye on one figure, the 4.3 MB scatter plot.
