#!/usr/bin/env python3
"""Smoke test: the example library builds and checks clean.

    paperlib test   (or: python3 tests/test_example_library.py)

Copies examples/library to a temporary folder, runs build-index and check
there, and compares the indexes it writes with the committed ones, so a change
to the engine that alters them shows up here. No network is used, and the
example's PDFs are not needed: the papers' text layers are committed.
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


def run(script, root, *args, **extra_env):
    env = dict(os.environ, PAPER_LIBRARY=str(root), PDF_ROOT=str(root / "no-pdfs"),
               PAPERS_CACHE=str(root.parent / "cache"))
    env.update(extra_env)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env["PATH"]
    return subprocess.run([sys.executable, str(ENGINE / "scripts" / script), *args], env=env,
                          capture_output=True, text=True)


def papers(root):
    """The example's paper files: text layers, and the web article's markdown."""
    return sorted(p for suffix in ("*.txt", "*.md") for p in root.joinpath("library").rglob(suffix)
                  if p.name != "README.md")


def read_view_problems(root):
    """read-view keeps the main text and its pages, and drops the frontmatter and the references."""
    problems = []
    for paper in papers(root):
        view = run("read-view.py", root, str(paper)).stdout
        full = paper.read_text()
        if not view.startswith("# ") or "\n---\n" in view[:400]:
            problems.append(f"{paper.name}: no title line, or the frontmatter is still there")
        if paper.suffix == ".txt" and (view.count("[page ") < 2 or "[page 1]\n" not in view):
            problems.append(f"{paper.name}: page markers lost")
        if "Left out" not in view:
            problems.append(f"{paper.name}: references not cut, or the cut not announced")
        if not len(full) * 0.2 < len(view) <= len(full):
            problems.append(f"{paper.name}: view is {len(view)} characters of {len(full)}")
        whole = run("read-view.py", root, str(paper), "--appendix").stdout
        if len(whole) <= len(view):
            problems.append(f"{paper.name}: --appendix does not give the whole paper")
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
    paper = next(p for p in papers(root) if "\narxiv:" in p.read_text()[:1500])
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
    paper.write_text(re.sub(r"^title: .+$", "title: Renamed Zebra Paper", paper.read_text(), count=1, flags=re.M))
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


def remove_problems(root):
    """`remove` deletes a paper's files only when told to, and can record the skip.

    Run last: it takes a paper out of the copy."""
    problems = []
    paper = next(p for p in papers(root) if "\narxiv:" in p.read_text()[:1500])
    text = paper.read_text()
    arxiv_id = re.search(r"^arxiv: '?([\d.]+)", text, re.M).group(1)
    topic = paper.parent.relative_to(root / "library")
    pdf = root / "no-pdfs" / topic / f"{paper.stem}.pdf"
    note = root / "notes" / f"{paper.stem}.md"
    for f in (pdf, note):
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x")
    skipped = root / "catalog" / "skipped.yaml"

    result = run("remove-paper.py", root, arxiv_id, "--reason", "not for this library")
    if not all(f.exists() for f in (paper, pdf, note)) or "nothing removed" not in result.stdout:
        problems.append("deleted without --yes")
    if "skipped.yaml" not in result.stdout or yaml_list(skipped):
        problems.append("the skip is not announced, or recorded before the paper is removed")
    result = run("remove-paper.py", root, arxiv_id, "--reason", "not for this library", "--yes")
    left = [f.name for f in (paper, pdf, note) if f.exists()]
    if left:
        problems.append(f"left behind: {left}")
    entry = (yaml_list(skipped) or [{}])[-1]
    if (entry.get("arxiv"), entry.get("reason"), entry.get("topic")) != (arxiv_id, "not for this library", str(topic)):
        problems.append(f"skipped.yaml: {entry}")
    if not skipped.read_text().startswith("#"):
        problems.append("skipped.yaml: the header comment is gone")
    if result.returncode:
        problems.append(f"the check fails afterwards: {result.stdout.strip().splitlines()[-3:]}")
    if run("remove-paper.py", root, arxiv_id, "--yes").returncode == 0:
        problems.append("a paper that is not in the library: no error")
    # By path, without recording a skip.
    paper.write_text(text)
    run("remove-paper.py", root, str(paper), "--yes")
    if paper.exists():
        problems.append("by path: the paper is still there")
    return problems


def check_problems(root):
    """check fails on a text-layer paper without its text, and on one in both forms."""
    problems = []
    paper = next(p for p in papers(root) if p.suffix == ".txt")
    text = paper.read_text()
    head = text[:text.index("\n---\n", 4) + 5]
    paper.write_text(head)
    if "no text layer" not in run("check-library.py", root).stdout:
        problems.append("a .txt paper without its text layer passes")
    paper.write_text(text)
    twin = paper.with_suffix(".md")
    twin.write_text(head.replace("source: pdf", "source: web"))
    if "also in the library" not in run("check-library.py", root).stdout:
        problems.append("a paper in both forms passes")
    twin.unlink()
    return problems


def reading_problems(root):
    """reading counts the scopes' papers, and reread marks a note and clears it."""
    problems = []
    paper = papers(root)[0]
    note = root / "notes" / f"{paper.stem}.md"
    note.parent.mkdir(exist_ok=True)
    note.write_text("# T\n\ntype: method\n\n## Digest\n\n- a claim\n\n## Q&A\n")
    listing = run("reading.py", root)
    top = paper.relative_to(root / "library").parts[0]
    row = next((x for x in listing.stdout.splitlines() if x.split()[:1] == [top]), "")
    if listing.returncode or not row or "all scopes" not in listing.stdout:
        problems.append(f"reading does not list the scopes: {listing.stdout[-300:]} {listing.stderr[-300:]}")
    run("reading.py", root, "reread", str(paper), "--reason", "Table 1 was misread")
    if "reread: Table 1 was misread (" not in note.read_text() or "## Digest" not in note.read_text():
        problems.append("reread did not mark the note above its digest")
    row = next((x for x in run("reading.py", root).stdout.splitlines() if x.split()[:1] == [top]), "")
    if len(row.split()) < 5 or row.split()[4] != "1":
        problems.append(f"reading does not count the note to re-read: {row}")
    run("reading.py", root, "reread", str(paper), "--clear")
    if "reread:" in note.read_text():
        problems.append("reread --clear left the mark")
    note.unlink()
    return problems


def note_fields_problems(root):
    """note_fields reads the type, family and evidence above a note's digest, and only there."""
    paper = papers(root)[0]
    note = root / "notes" / f"{paper.stem}.md"
    note.parent.mkdir(exist_ok=True)
    code = ("import paperlib as p, sys; paper = sys.argv[1]; note = p.note_path(paper); "
            "assert p.note_fields(paper) == {}, 'no note'; "
            "note.write_text('# T\\n\\ntype: Method\\nfamily: sparse attention\\n"
            "evidence: two benchmarks; strength: one run\\nreread: x (2026-10-01)\\n\\n"
            "## Digest\\n\\ntype: survey\\nfamily: not this\\n'); "
            "f = p.note_fields(paper); assert f == {'type': 'method', 'family': 'sparse attention', "
            "'evidence': 'two benchmarks; strength: one run'}, f; "
            "assert p.reread_reason(paper) == 'x (2026-10-01)'; "
            "n = p.read_note(paper); assert n['digest'].startswith('type: survey') and n['reread'] == 'x (2026-10-01)', n; "
            "note.write_text('# T\\n\\ntype: method\\n\\n## Digest\\n\\n- a claim\\n\\n## Q&A\\n\\nQ?\\n'); "
            "assert p.read_note(paper)['digest'] == '- a claim', p.read_note(paper); "
            "note.write_text('# T\\n\\ntype: essay\\nfamily: \\n\\n## Digest\\n'); "
            "assert p.note_fields(paper) == {}, p.note_fields(paper); "
            "note.write_text('# T\\n\\ntype: study\\n'); "
            "assert p.note_fields(paper) == {'type': 'study'} and not p.has_digest(paper); "
            "assert p.read_note(paper)['digest'] is None; note.unlink(); assert p.read_note(paper) is None; "
            "assert [s for _, g in p.review_scopes() for s in g] == sorted({t.split('/')[0] for t in p.load_topics()})")
    env = dict(os.environ, PAPER_LIBRARY=str(root), PYTHONPATH=str(ENGINE / "scripts"))
    result = subprocess.run([sys.executable, "-c", code, str(paper)], env=env, capture_output=True, text=True)
    note.unlink(missing_ok=True)
    return result.stderr.strip().splitlines()[-1:] if result.returncode else []


def yaml_list(path):
    import yaml
    return yaml.safe_load(path.read_text()) or []


def report(name, problems, fine):
    print(f"{'FAIL' if problems else 'ok  '} {name}: " + ("; ".join(problems) or fine))
    return bool(problems)


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
        failures += report("read-view.py", read_view_problems(root), "main text and pages kept, references cut")
        failures += report("filing", filing_problems(root), "only a declared folder is accepted")
        failures += report("paper-info.py", info_problems(root), "library papers found by id, by title and with -C")
        for index in sorted(root.joinpath("library").rglob("README.md")):
            rel = index.relative_to(root)
            committed = EXAMPLE / rel
            same = committed.exists() and committed.read_text() == index.read_text()
            failures += not same
            print(f"{'ok  ' if same else 'FAIL'} {rel} matches the committed index")
        failures += report("check-library.py", check_problems(root), "a missing text layer and a paper in two forms fail")
        failures += report("reading.py", reading_problems(root), "scopes counted, notes marked to re-read and cleared")
        failures += report("note_fields", note_fields_problems(root), "type, family and evidence read from the note's head")
        failures += report("remove-paper.py", remove_problems(root), "asks first, deletes the paper's files, records the skip")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
