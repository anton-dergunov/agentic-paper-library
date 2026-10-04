#!/usr/bin/env python3
"""Convert PDF-only papers with each OCR setting of docling and record what happens.

    PAPER_LIBRARY=<library> uv run python experiments/ocr-engines/run.py <out-dir> <repeats> <paper.md> ...

For each paper and each setting (PAPERLIB_OCR = rapidocr, ocrmac, off) the real
pdf-to-markdown.py runs <repeats> times, as `paperlib reconvert --pdf-text`
runs it (the quick conversion, --fast). Appends one JSON line per run to
<out-dir>/runs.jsonl: paper, setting, attempt, seconds, exit code (negative: killed
by that signal, -11 is a segfault), words, whether it fell back to the text
layer. The markdown of each run is kept in <out-dir>/<setting>/ for diffing.
OCR_SETTINGS=rapidocr limits the run to some settings.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from paperlib import pdf_path_for  # noqa: E402

SETTINGS = tuple(os.environ.get("OCR_SETTINGS", "rapidocr,ocrmac,off").split(","))


def main(out_dir, repeats, papers):
    out_dir = Path(out_dir)
    for md in map(Path, papers):
        for attempt in range(1, int(repeats) + 1):
            for setting in SETTINGS:
                out = out_dir / setting / f"{md.stem[:60]}.{attempt}.md"
                out.parent.mkdir(parents=True, exist_ok=True)
                start = time.time()
                run = subprocess.run(
                    [sys.executable, SCRIPTS / "pdf-to-markdown.py", "--fast", pdf_path_for(md), out,
                     out_dir / "images" / setting, f"p{attempt}"],
                    capture_output=True, text=True, env={**os.environ, "PAPERLIB_OCR": setting},
                )
                text = out.read_text(encoding="utf-8") if out.exists() and run.returncode == 0 else ""
                row = {"paper": md.stem, "setting": setting, "attempt": attempt,
                       "seconds": round(time.time() - start, 1), "exit": run.returncode,
                       "words": len(text.split()), "text_layer_fallback": "using the text layer" in run.stderr,
                       "stderr_tail": run.stderr.strip().splitlines()[-1:] if run.returncode else []}
                with open(out_dir / "runs.jsonl", "a") as f:
                    f.write(json.dumps(row) + "\n")
                print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
