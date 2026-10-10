#!/usr/bin/env python3
"""Smoke test: the example library builds and checks clean.

    paperlib test   (or: python3 tests/test_example_library.py)

Copies examples/library to a temporary folder, runs build-index and check
there, and compares the indexes it writes with the committed ones, so a change
to the engine that alters them shows up here. No network is used, and the
example's PDFs are not needed.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
EXAMPLE = ENGINE / "examples" / "library"


def run(script, root, *args):
    env = dict(os.environ, PAPER_LIBRARY=str(root), PDF_ROOT=str(root / "no-pdfs"),
               PAPERS_CACHE=str(root.parent / "cache"))
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env["PATH"]
    return subprocess.run([sys.executable, str(ENGINE / "scripts" / script), *args], env=env,
                          capture_output=True, text=True)


def read_view_problems(root):
    """read-view keeps the main text and its pages, and drops references and link targets."""
    problems = []
    for paper in sorted(p for p in root.joinpath("library").rglob("*.md") if p.name != "README.md"):
        view = run("read-view.py", root, str(paper)).stdout
        full = paper.read_text()
        if not view.startswith("# ") or "\n---\n" in view[:400]:
            problems.append(f"{paper.name}: no title line, or the frontmatter is still there")
        if "](#" in view or "](http" in view:
            problems.append(f"{paper.name}: link targets left in")
        if "(p. " in full and "(p. " not in view:
            problems.append(f"{paper.name}: page markers lost")
        if "\n## References" in full and ("\n## References" in view or "Left out of this view" not in view):
            problems.append(f"{paper.name}: references not cut, or the cut not announced")
        if not len(full) * 0.2 < len(view) <= len(full):
            problems.append(f"{paper.name}: view is {len(view)} characters of {len(full)}")
    return problems


def filing_problems(root):
    """A filing model's reply is used only when it names a declared folder."""
    code = ("import json, paperlib as p; t = p.load_topics(); f = next(iter(t)); "
            "r = lambda folder: p.filing_choice('Here: ' + json.dumps({'folder': folder, 'reason': 'r', "
            "'summary': 'a  b'}), t); "
            "assert r(f) == (f, 'r', 'a b'), r(f); assert r('none')[0] is None; "
            "assert r('not/declared')[0] is None; assert r(f + '/')[0] == f")
    env = dict(os.environ, PAPER_LIBRARY=str(root), PYTHONPATH=str(ENGINE / "scripts"))
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    return result.stderr.strip().splitlines()[-1:] if result.returncode else []


def info_problems(root):
    """`info` answers for a library paper from the library alone, by arXiv id and by title words.

    Run after the indexes are built: it renames a paper in the copy."""
    problems = []
    paper = next(p for p in sorted(root.joinpath("library").rglob("*.md")) if p.name != "README.md"
                 and "\narxiv:" in p.read_text()[:1500])
    arxiv_id = re.search(r"^arxiv: '?([\d.]+)", paper.read_text(), re.M).group(1)
    title = re.search(r"^title: (.+)$", paper.read_text(), re.M).group(1).strip("'\"")
    for query in (arxiv_id, " ".join(re.findall(r"[A-Za-z]{4,}", title)[:3])):
        result = run("paper-info.py", root, query, "--json")
        try:
            info = json.loads(result.stdout.splitlines()[0])
        except (ValueError, IndexError):
            problems.append(f"`{query}`: no JSON ({result.stderr.strip()[:100]})")
            continue
        if info.get("status") != "in library" or not root.joinpath(info.get("paper", "?")).is_file():
            problems.append(f"`{query}`: not found in the library")
    # The saved index of frontmatter follows a paper that changes.
    paper.write_text(re.sub(r"^title: .+$", "title: Renamed Zebra Paper", paper.read_text(), 1, re.M))
    result = run("paper-info.py", root, "zebra renamed")
    if "in library" not in result.stdout:
        problems.append("a changed title is not found: the saved index is stale")
    if "\033" in result.stdout:
        problems.append("piped output carries terminal escape codes")
    # -C names the library from anywhere.
    env = {k: v for k, v in os.environ.items() if k != "PAPER_LIBRARY"}
    env.update(PDF_ROOT=str(root / "no-pdfs"), PAPERS_CACHE=str(root.parent / "cache"))
    result = subprocess.run([sys.executable, str(ENGINE / "scripts" / "cli.py"), "-C", str(root), "info", arxiv_id],
                            env=env, cwd=tempfile.gettempdir(), capture_output=True, text=True)
    if "in library" not in result.stdout:
        problems.append(f"-C: {(result.stderr or result.stdout).strip()[:100]}")
    return problems


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
        problems = read_view_problems(root)
        failures += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} read-view.py: " + ("; ".join(problems) or "main text kept, references cut"))
        problems = filing_problems(root)
        failures += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} filing: " + ("; ".join(problems) or "only a declared folder is accepted"))
        problems = info_problems(root)
        failures += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} paper-info.py: " + ("; ".join(problems) or "library papers found by id, by title and with -C"))
        for index in sorted(root.joinpath("library").rglob("README.md")):
            rel = index.relative_to(root)
            committed = EXAMPLE / rel
            same = committed.exists() and committed.read_text() == index.read_text()
            failures += not same
            print(f"{'ok  ' if same else 'FAIL'} {rel} matches the committed index")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
