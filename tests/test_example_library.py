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


def run(script, root, *args, **extra_env):
    env = dict(os.environ, PAPER_LIBRARY=str(root), PDF_ROOT=str(root / "no-pdfs"),
               PAPERS_CACHE=str(root.parent / "cache"), **extra_env)
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


def remove_problems(root):
    """`remove` deletes a paper's files only when told to, and can record the skip.

    Run last: it takes a paper out of the copy."""
    problems = []
    paper = next(p for p in sorted(root.joinpath("library").rglob("*.md")) if p.name != "README.md"
                 and "\narxiv:" in p.read_text()[:1500])
    text = paper.read_text()
    arxiv_id = re.search(r"^arxiv: '?([\d.]+)", text, re.M).group(1)
    topic = paper.parent.relative_to(root / "library")
    figure = paper.parent / "images" / f"{paper.stem}-fig99.png"
    other = paper.parent / "images" / f"{paper.stem}-figures of another paper-fig01.png"
    pdf = root / "no-pdfs" / topic / f"{paper.stem}.pdf"
    note = root / "notes" / f"{paper.stem}.md"
    issues = root / "issues" / f"{paper.stem}.yaml"
    for f in (figure, pdf, note):
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x")
    issues.parent.mkdir(exist_ok=True)
    issues.write_text("- kind: new\n  where: p. 1\n  what: a table\n")
    skipped = root / "catalog" / "skipped.yaml"

    result = run("remove-paper.py", root, arxiv_id, "--reason", "not for this library")
    if not all(f.exists() for f in (paper, figure, pdf, note)) or "nothing removed" not in result.stdout:
        problems.append("deleted without --yes")
    if "skipped.yaml" not in result.stdout or yaml_list(skipped):
        problems.append("the skip is not announced, or recorded before the paper is removed")
    result = run("remove-paper.py", root, arxiv_id, "--reason", "not for this library", "--yes")
    left = [f.name for f in (paper, figure, pdf, note) if f.exists()]
    if left:
        problems.append(f"left behind: {left}")
    # A paper whose title begins with this one's keeps its figures.
    paper.write_text(text)
    other.parent.mkdir(exist_ok=True)
    other.write_text("x")
    run("remove-paper.py", root, str(paper), "--yes")
    if paper.exists() or not other.exists():
        problems.append("by path: the paper is still there, or another paper's figure went with it")
    other.unlink()
    if issues.exists():
        problems.append("issues/: the paper's problems are still there")
    entry = (yaml_list(skipped) or [{}])[-1]
    if (entry.get("arxiv"), entry.get("reason"), entry.get("topic")) != (arxiv_id, "not for this library", str(topic)):
        problems.append(f"skipped.yaml: {entry}")
    if not skipped.read_text().startswith("#"):
        problems.append("skipped.yaml: the header comment is gone")
    if result.returncode:
        problems.append(f"the check fails afterwards: {result.stdout.strip().splitlines()[-3:]}")
    if run("remove-paper.py", root, arxiv_id, "--yes").returncode == 0:
        problems.append("a paper that is not in the library: no error")
    return problems


def issues_problems(root):
    """issues add records a problem, the listing shows it, close removes it and names the
    notes to read again; the reader's Conversion section becomes records."""
    problems = []
    paper = sorted(root.joinpath("library").rglob("*.md"))
    paper = next(p for p in paper if p.name != "README.md")
    rel = str(paper.relative_to(root))
    result = run("issues.py", root, "add", rel, "pdf-table-bold", "bold lost", "--where", "p. 2, Table 1",
                 "--key-content")
    run("issues.py", root, "add", rel, "new:odd-glyph", "a stray glyph", "--where", "p. 3")
    records = yaml_list(root / "issues" / f"{paper.stem}.yaml") if (root / "issues" / f"{paper.stem}.yaml").exists() else []
    if result.returncode or [r.get("kind") for r in records] != ["pdf-table-bold", "new"] \
            or records[1].get("suggested") != "odd-glyph" or not records[0].get("key-content"):
        problems.append(f"add did not record both problems: {records} {result.stderr.strip()[-200:]}")
    again = run("issues.py", root, "add", rel, "pdf-table-bold", "bold lost again", "--where", "p.  2, table 1")
    if "already recorded" not in again.stdout or len(yaml_list(root / "issues" / f"{paper.stem}.yaml")) != 2:
        problems.append("add recorded a problem the paper already has")
    if run("issues.py", root, "add", rel, "no-such-ticket", "x", "--where", "p. 1").returncode == 0:
        problems.append("add accepted a kind that is no ticket")
    path = root / "issues" / f"{paper.stem}.yaml"
    path.write_text(path.read_text() + "- kind: new\n  where: p. 9\n  what: left alone\n  wont-fix: small\n")
    if "1 records in 1 papers" not in run("issues.py", root, "--wont-fix").stdout:
        problems.append("--wont-fix does not list only the wont-fix records")
    listing = run("issues.py", root).stdout
    if "KEY CONTENT" not in listing or "2 records in 1 papers" not in listing:
        problems.append("the listing lacks the records")
    if run("check-library.py", root).returncode:
        problems.append("check fails on valid records")
    closed = run("issues.py", root, "close", "pdf-table-bold", rel)
    left = yaml_list(root / "issues" / f"{paper.stem}.yaml")
    if [r.get("kind") for r in left] != ["new", "new"] or "read --redo" not in closed.stdout:
        problems.append("close did not remove the kind's records or name the note to read again")
    (root / "issues" / f"{paper.stem}.yaml").unlink()

    sys.path.insert(0, str(ENGINE / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("read_papers", ENGINE / "scripts" / "read-papers.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    note = ("# T\n\n## Digest\n\n- a claim\n\n## Related in library\n\n## Conversion\n\n"
            "- pdf-table-bold | p. 4, Table 2 | bold lost | key-content\n- new:odd | p. 5 | a glyph\n- none\n"
            "- pdf-equation-garbled | p. 6 | p(w|z) reads p(w z) | key-content\n"
            "- pdf-equation-garbled | p. 7 | |V| lost\n")
    body, records = module.take_conversion(note, {"pdf-table-bold": {}, "pdf-equation-garbled": {}})
    if "## Conversion" in body or "## Related in library" not in body:
        problems.append("the Conversion section was not taken out of the note")
    if [(r["kind"], r.get("suggested"), r["key-content"]) for r in records] != \
            [("pdf-table-bold", None, True), ("new", "odd", False), ("pdf-equation-garbled", None, True),
             ("pdf-equation-garbled", None, False)] \
            or [r["what"] for r in records[2:]] != ["p(w|z) reads p(w z)", "|V| lost"]:
        problems.append(f"the reader's records were parsed wrongly: {records}")
    listed = {"a": {"title": "A", "status": "open"}, "b": {"title": "B", "status": "wont-fix"},
              "c": {"title": "C", "status": "done"}}
    if module.kinds_list(listed) != "- a: A" or module.kinds_list(listed, "wont-fix") != "- b: B":
        problems.append("the reader is offered wont-fix or done causes as ones to record")
    pdf_paper = root / "pdf-paper.md"
    pdf_paper.write_text("---\ntitle: P\nsource: pdf-text\n---\n\nBody.\n")
    if module.unclean_reason(pdf_paper) != "converted from pdf-text":
        problems.append("read --clean would read a paper converted from a PDF")
    pdf_paper.unlink()
    old = [{"kind": "a", "where": "p. 1", "what": "x", "by": "reader"},
           {"kind": "b", "where": "p. 2", "what": "y", "by": "session"},
           {"kind": "c", "where": "p. 3", "what": "z", "by": "reader", "wont-fix": "small"}]
    new = [{"kind": "c", "where": "p.  3", "what": "z again"}, {"kind": "d", "where": "p. 4", "what": "w"}]
    merged = [r["kind"] for r in module.merge_reader_records(old, new)]
    if merged != ["b", "c", "d"]:
        problems.append(f"a new reading did not replace only the reader's open records: {merged}")
    return problems


def tickets_problems(root):
    """tickets move puts a ticket in the folder of its state, and back; a closed status at the
    top of tickets/ is reported."""
    problems = []
    copy = root.parent / "tickets"
    shutil.copytree(ENGINE / "tickets", copy)
    env = {"TICKETS_DIR": str(copy)}
    tid = sorted(p.stem for p in copy.glob("*.md") if p.name != "README.md")[0]
    if run("tickets.py", root, "move", tid, "wont-fix", **env).returncode == 0:
        problems.append("a ticket became wont-fix without a reason")
    run("tickets.py", root, "move", tid, "wont-fix", "--reason", "not worth it", **env)
    moved = copy / "wont-fix" / f"{tid}.md"
    text = moved.read_text() if moved.exists() else ""
    if (copy / f"{tid}.md").exists() or "reason: not worth it" not in text or "closed:" not in text \
            or "status:" in text.split("---")[1] or f"(wont-fix/{tid}.md)" not in (copy / "README.md").read_text():
        problems.append("move to wont-fix/ did not move the file, set its reason and date, or link it")
    run("tickets.py", root, "move", tid, "open", **env)
    back = copy / f"{tid}.md"
    if not back.exists() or "status: open" not in back.read_text() or "closed:" in back.read_text():
        problems.append("move back to open did not restore the ticket")
    other = sorted(p for p in copy.glob("*.md") if p.name != "README.md")[1]
    other.write_text(other.read_text().replace("status: open", "status: done", 1))
    if "belongs in done/" not in run("tickets.py", root, **env).stdout:
        problems.append("a done ticket at the top of tickets/ is not reported")
    return problems


def matching_problems():
    """apply_corrections places a correction by its text, by its landmarks when the text
    repeats or drifted, retires one the converter now makes, and points to one it cannot
    place; diff_corrections stores the changed rows of a table."""
    sys.path.insert(0, str(ENGINE / "scripts"))
    from paperlib import apply_corrections, diff_corrections
    problems = []
    rows = "\n".join(f"| m{i}  | {i}.{i}   |" for i in range(6))
    base = ("> **Converted from the PDF.**\n\n# T\n\n## 2 Method (p. 2)\n\nThe loss is defined below, "
            "with its two terms.\n\n$$L = a (1)$$\n\n## 3 Results (p. 3)\n\nTable 1: Scores.\n\n"
            f"| Model | Score |\n|-------|-------|\n{rows}\n\nWe see the gains.\n\n## 4 More (p. 4)\n\n"
            "We see the gains.\n")
    edited = base.replace("$$L = a (1)$$", "$$L = a + b (1)$$").replace("| m2  | 2.2   |", "| m2 | 2.25 |")
    found = diff_corrections(base, edited, why="from the PDF")
    if [(c["where"], c["was"].strip(), c["now"].strip()) for c in found] != [
            ("p. 2, Eq. (1)", "$$L = a (1)$$", "$$L = a + b (1)$$"),
            ("p. 3, Table 1", "| m2  | 2.2   |", "| m2 | 2.25 |")]:
        problems.append(f"diff_corrections did not take the two edits, the table's one row only: {found}")

    def outcomes(fresh, corrections=found):
        body, kept, out = apply_corrections(fresh, corrections, pointer="corrections/T.yaml", today="2026-01-01")
        return body, kept, [o for _, o, _ in out]

    repadded = base.replace("| m4  | 4.4   |", "| m4 | **4.4** |").replace("| m0  |", "|  m0 |") \
        .replace("We see the gains.\n\n## 4", "We see larger gains.\n\n## 4")
    body, kept, out = outcomes(repadded)
    if out != ["exact", "exact"] or "| m2 | 2.25 |" not in body or "$$L = a + b (1)$$" not in body \
            or "| m4 | **4.4** |" not in body:
        problems.append(f"a re-padded conversion with a change elsewhere did not take both edits: {out}")
    if "<!-- hand-edited: from the PDF -->\n| Model" not in body:
        problems.append("a row's marker is not above its table")
    twice = [{"where": "p. 4", "why": "x", "section": "4 More", "was": "We see the gains.",
              "now": "We see the gains, twice."}]
    body, _, out = outcomes(base, twice)
    if out != ["landmarks"] or not body.rstrip().endswith("We see the gains, twice."):
        problems.append(f"a repeated `was` was not placed by its section: {out}")
    insert = [{"where": "p. 2", "why": "y", "prev": "The loss is defined below, with its two terms.",
               "was": "", "now": "where b is the penalty."}]
    body, _, out = outcomes(base, insert)
    if out != ["exact"] or "terms.\n\n<!-- hand-edited: y -->\n\nwhere b is the penalty.\n\n$$L" not in body:
        problems.append(f"an insertion was not placed after `prev`: {out}")
    drifted = base.replace("$$L = a (1)$$", "$$L = a\\, (1)$$")
    body, kept, out = outcomes(drifted)
    if out[0] != "drifted" or "$$L = a + b (1)$$" not in body or "drifted" not in kept[0]:
        problems.append(f"a slightly changed `was` was not placed by its landmarks: {out}")
    body, kept, out = outcomes(edited)
    if out != ["obsolete", "obsolete"] or kept:
        problems.append(f"corrections the conversion already makes were not retired: {out}")
    algo = "|  Algorithm 1 |\n|----|\n|  1. loop |\n|  x = 1 |\n|  2. end |"
    indent = [{"where": "p. 5", "why": "loop body indented", "was": "|  x = 1 |", "now": "|      x = 1 |"}]
    body, _, out = outcomes(f"# A\n\n{algo}\n", indent)
    again = apply_corrections(body.replace("<!-- hand-edited: loop body indented -->\n", ""), indent)[2]
    if out != ["exact"] or "|      x = 1 |" not in body or [o for _, o, _ in again] == ["exact"]:
        problems.append(f"a one-column table's indentation is not told apart: {out}")
    aligned = [{"where": "p. 3", "why": "z", "was": "|   Score | Model |\n|---|---|\n|    **4.3** | a |", "now": "| x |"}]
    if outcomes("| Score   | Model |\n|---------|-------|\n| **4.3** | a |\n", aligned)[2] != ["exact"]:
        problems.append("a table writer's right alignment is taken for indentation")
    gone = base.replace("$$L = a (1)$$", "The loss is shown in Figure 2 instead.")
    body, kept, out = outcomes(gone)
    if out[0] != "stale" or kept[0].get("stale") != "2026-01-01" \
            or "> A hand correction of p. 2, Eq. (1) could not be re-applied" not in body.split("# T")[0]:
        problems.append(f"a correction that cannot be placed was not marked stale with a pointer: {out}")
    return problems


def corrections_problems(root):
    """capture records an edit against a base and marks it; the listing shows it; check
    accepts it and reports a corrections file without a paper."""
    problems = []
    paper = next(p for p in sorted(root.joinpath("library").rglob("*.md")) if p.name != "README.md")
    text = paper.read_text()
    line = next(x for x in text.split("\n") if len(x) > 200 and not x.startswith(("|", ">", "#")))
    base = root.parent / "base.md"
    base.write_text(text)
    paper.write_text(text.replace(line, line[:120] + " [corrected]", 1))
    result = run("corrections.py", root, "capture", str(paper), "--base", str(base), "--why", "a test edit")
    path = root / "corrections" / f"{paper.stem}.yaml"
    stored = yaml_list(path) if path.exists() else []
    if result.returncode or len(stored) != 1 or stored[0]["was"] != line \
            or "<!-- hand-edited: a test edit -->" not in paper.read_text():
        problems.append(f"capture did not record and mark the edit: {result.stdout} {result.stderr[-300:]}")
    if "1 in 1 papers" not in run("corrections.py", root).stdout:
        problems.append("the listing does not show the correction")
    if run("check-library.py", root).returncode:
        problems.append("check fails on a valid corrections file")
    orphan = root / "corrections" / "No Such Paper.yaml"
    orphan.write_text(path.read_text())
    if "No Such Paper" not in run("check-library.py", root).stdout:
        problems.append("check does not report a corrections file without a paper")
    orphan.unlink()
    path.unlink()
    paper.write_text(text)
    return problems


def reading_problems(root):
    """reading counts the scopes' papers, reread marks a note and clears it, and issues close
    marks the note of a paper whose key content it closed."""
    problems = []
    paper = next(p for p in sorted(root.joinpath("library").rglob("*.md")) if p.name != "README.md")
    note = root / "notes" / f"{paper.stem}.md"
    note.parent.mkdir(exist_ok=True)
    note.write_text("# T\n\ntype: method\n\n## Digest\n\n- a claim\n\n## Q&A\n")
    listing = run("reading.py", root)
    top = paper.relative_to(root / "library").parts[0]
    row = next((x for x in listing.stdout.splitlines() if x.split()[:1] == [top]), "")
    if listing.returncode or not row or "all scopes" not in listing.stdout:
        problems.append(f"reading does not list the scopes: {listing.stdout[-300:]} {listing.stderr[-300:]}")
    run("reading.py", root, "reread", str(paper), "--reason", "Table 1 was broken")
    if "reread: Table 1 was broken (" not in note.read_text() or "## Digest" not in note.read_text():
        problems.append("reread did not mark the note above its digest")
    row = next((x for x in run("reading.py", root).stdout.splitlines() if x.split()[:1] == [top]), "")
    if len(row.split()) < 5 or row.split()[4] != "1":
        problems.append(f"reading does not count the note to re-read: {row}")
    run("reading.py", root, "reread", str(paper), "--clear")
    if "reread:" in note.read_text():
        problems.append("reread --clear left the mark")
    rel = str(paper.relative_to(root))
    run("issues.py", root, "add", rel, "pdf-table-bold", "bold lost", "--where", "p. 2, Table 1", "--key-content")
    run("issues.py", root, "close", "pdf-table-bold", rel)
    if "reread: pdf-table-bold fixed" not in note.read_text():
        problems.append("issues close did not mark the note of a paper whose key content it closed")
    note.unlink()
    return problems


def yaml_list(path):
    import yaml
    return yaml.safe_load(path.read_text()) or []


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
        problems = issues_problems(root)
        failures += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} issues.py: " + ("; ".join(problems) or "add, list, close; the reader's records parsed and merged"))
        problems = tickets_problems(root)
        failures += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} tickets.py: " + ("; ".join(problems) or "move to wont-fix/ and back, closed status checked"))
        problems = matching_problems()
        failures += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} corrections matching: " + ("; ".join(problems) or "exact, landmarks, drifted, obsolete, stale; table rows"))
        problems = corrections_problems(root)
        failures += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} corrections.py: " + ("; ".join(problems) or "capture against a base, list, check"))
        problems = reading_problems(root)
        failures += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} reading.py: " + ("; ".join(problems) or "scopes counted, notes marked to re-read and cleared"))
        problems = remove_problems(root)
        failures += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} remove-paper.py: " + ("; ".join(problems) or "asks first, deletes the paper's files, records the skip"))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
