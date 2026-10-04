# Experiment · which OCR should the PDF converter use, and why does it crash?

**Question.** docling runs OCR on the bitmap parts of a PDF page. With RapidOCR, the conversion of some PDFs segfaults on some attempts ("Canaries in the Coal Mine" crashed three times in five during the library reconversion). Would another OCR engine, or none, convert the papers as well without crashing?

**Status.** Measured 4 Oct 2026 on 12 PDF-only papers. **RapidOCR stays, on OpenCV 4.12.** Apple's OCR does not crash but reads logos and chart labels into the text and garbles tables that are images; no OCR loses those tables. The crash is in OpenCV's Arm resize (KleidiCV), which opencv-python has from 4.13: 5 of 15 conversions of Canaries crashed on 4.14 and 5.0, none of 10 on 4.12, with identical output.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#pdf-only-papers).

## Method

- **Settings.** `scripts/pdf-to-markdown.py` reads `PAPERLIB_OCR`: `rapidocr` (docling's `RapidOcrOptions`, what the library was converted with), `ocrmac` (`OcrMacOptions`, Apple's Vision framework, no OpenCV; ocrmac 1.0.1 installed for the test and removed after), `off` (`do_ocr=False`). docling 2.117.0, RapidOCR 3.9.2, on an Apple-silicon Mac.
- **Papers.** "Canaries in the Coal Mine" (the paper that crashed), five conversions per setting. One conversion per setting of 11 others: "Long Short-Term Memory" and "The power of two random choices" (old PDFs with a broken text layer), "Accurate predictions on small data with a tabular foundation model" (its Extended Data tables are images), and eight drawn at random (seed 20261004) from the library's 277 PDF-only papers.
- **Apparatus.** [`run.py`](run.py) runs the real converter as `paperlib reconvert --pdf-text` does (the quick conversion) and records each run's time, exit code and word count; an exit code of −11 is a segfault. [`compare.py`](compare.py) counts, against the conversion without OCR, the lines each engine adds and removes, and how many of them are table rows.

  ```bash
  PAPER_LIBRARY=<library> uv run python experiments/ocr-engines/run.py <out-dir> 5 <Canaries.md>
  PAPER_LIBRARY=<library> uv run python experiments/ocr-engines/run.py <out-dir> 1 <paper.md> ...
  python3 experiments/ocr-engines/compare.py <out-dir>
  ```

  For the OpenCV versions the package was installed into the environment with `uv pip install opencv-python==<version>` and `run.py` was started with the environment's own Python, with `OCR_SETTINGS=rapidocr`; `uv run` would put the locked version back.
- **Results.** [`runs-engines.jsonl`](runs-engines.jsonl) (48 runs, OpenCV 5.0.0.93) and [`engines.txt`](engines.txt), the output of `compare.py` on them; [`runs-opencv-4.14.jsonl`](runs-opencv-4.14.jsonl) (5 runs) and [`runs-opencv-4.12.jsonl`](runs-opencv-4.12.jsonl) (10 runs). The converted papers are not committed.

## Results

### The engines

| | RapidOCR | Apple (ocrmac) | no OCR |
|---|---|---|---|
| Conversions that crashed, of 16 | 1 (Canaries, attempt 3) | 0 | 0 |
| Canaries, median seconds | 115 | 47 | 37 |
| All 12 papers once, seconds | 1,179 | 931 | 917 |
| Papers whose markdown differs from no OCR | 6 | 8 | |

What each engine adds to the conversion without OCR:

| Paper | RapidOCR | Apple |
|---|---|---|
| Accurate predictions on small data (tables that are images) | 137 table rows, read as tables: `0.971 ±0.01` | 104 table rows with rows merged and `±` read as `£`, `1` or `+` (`0.952 £0.01`, `0.950 10.01`); 373 other lines, among them chart labels and "Check for updates" |
| Joint Word and Entity Embeddings (one table that is an image) | the table, 22 rows | its cells as 20 loose lines; "Check for updates" |
| A simple introduction to MCMC (code listings that are images) | the listings as code blocks | the listings as loose lines; the publisher's logo ("Springer", "CrossMark") inside paragraphs |
| Online controlled experiments at large scale | a 4-row table | 13 loose lines |
| Canaries in the Coal Mine | nothing: byte-identical to no OCR | 749 lines of chart axis labels ("Headcount", "1.2", "1.1", …) |
| The power of two random choices | 2 lines | 342 lines |
| Leveraging tropical reef, bird and unrelated sounds | nothing | 120 lines |
| Language Model Tokenizers Introduce Unfairness | 1 line | 22 lines |
| Long Short-Term Memory, GraphSAINT, The LSM-Tree, TFX | nothing | nothing |

RapidOCR adds text only where a table or a listing is an image, and adds it as a table or a code block. Apple's OCR reads everything in every bitmap, and docling places it as paragraphs. Without OCR the image tables and listings are missing. Neither engine helps the old PDFs with a broken text layer: LSTM is the same by all three.

Tables read by RapidOCR are not stable between runs: of the 137 rows in "Accurate predictions", 46 differ somewhere from the library's copy, converted with the same engine two days earlier.

### The crash

The crash report of the failed run (macOS writes one per crash) puts it in `cv::resize` → `kleidicv::hal::resize` → `kleidicv_resize_generic_stripe_u8`, reading past the end of a mapping (`KERN_INVALID_ADDRESS` at a page boundary). KleidiCV is Arm's accelerated backend; `cv2.getBuildInformation()` lists it in opencv-python 4.13, 4.14 and 5.0 and not in 4.12 or 4.11. A read past a buffer crashes only when the buffer ends at the end of a mapping, which fits a crash on some attempts and not others.

| opencv-python | KleidiCV | Canaries conversions | crashed |
|---|---|---|---|
| 5.0.0.93 | yes | 5 on 4 Oct (and 5 on 2 Oct) | 1 (and 3) |
| 4.14.0.94 | yes (26.03) | 5 | 1 |
| 4.12.0.88 | no | 10 | 0 |

The first conversion on 4.12 is byte-identical to the first on 5.0, and all ten have its word count. If the crash rate on 4.12 were the one in three seen with KleidiCV, ten clean runs would have a chance of under 2%.

Running OpenCV on one thread was considered and not measured: `cv2.setNumThreads(1)` does nothing on macOS, where OpenCV's threads are Grand Central Dispatch (`getNumThreads()` still says 8), `setNumThreads(0)` does turn threading off, but a read past a buffer does not need a second thread.

**Decision.** `pyproject.toml` pins `opencv-python==4.12.0.88`. That release asks for numpy below 2.3, which would also move pandas back a major version, so numpy is held at 2.5.3 by a uv override; the ten runs used exactly that pair. `pdf-to-markdown.py` names RapidOCR instead of leaving docling to choose, because docling's default picks Apple's OCR whenever ocrmac happens to be installed.

## Limits

- One paper carries the crash measurement. Other PDFs may crash more or less often; none of the 11 others did in one conversion each.
- Ten clean runs make a crash on 4.12 unlikely, not impossible. The cause is argued from the crash report and the build information, not shown by a fixed OpenCV.
- The OpenCV pin has to be lifted when a release fixes KleidiCV's resize: convert Canaries ten times on it first.
- Only Apple's OCR was tried as an alternative; Tesseract and EasyOCR, which docling also supports, were not.
- The differences were read by a person for the papers in the table, not scored against a reference.
