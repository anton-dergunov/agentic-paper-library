#!/usr/bin/env python3
"""Smoke test: the example library builds and checks clean.

    paperlib test   (or: python3 tests/test_example_library.py)

Copies examples/library to a temporary folder, runs build-index and check
there, and compares the indexes it writes with the committed ones, so a change
to the engine that alters them shows up here. No network is used, and the
example's PDFs are not needed.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
EXAMPLE = ENGINE / "examples" / "library"


def run(script, root):
    env = dict(os.environ, PAPER_LIBRARY=str(root), PDF_ROOT=str(root / "no-pdfs"))
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env["PATH"]
    return subprocess.run([sys.executable, str(ENGINE / "scripts" / script)], env=env,
                          capture_output=True, text=True)


def main():
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "library"
        shutil.copytree(EXAMPLE, root, symlinks=True,
                        ignore=shutil.ignore_patterns("pdfs", ".claude"))
        for script in ("build-index.py", "check-library.py"):
            result = run(script, root)
            ok = result.returncode == 0
            failures += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {script}: {result.stdout.strip().splitlines()[-1]}")
            if not ok:
                print(result.stdout + result.stderr)
        for index in sorted(root.joinpath("library").rglob("README.md")):
            rel = index.relative_to(root)
            committed = EXAMPLE / rel
            same = committed.exists() and committed.read_text() == index.read_text()
            failures += not same
            print(f"{'ok  ' if same else 'FAIL'} {rel} matches the committed index")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
