"""Run the same agent tasks in a library copy with the old instructions and one with the new.

    python3 sessions.py build <library> <work> before=<engine>:<library-files> after=<engine>:<library-files>
    python3 sessions.py run <work> [<task> ...]

build  Makes <work>/copies/lib-<condition> with ../review-usefulness/copies.py (paper
       markdown without figures, catalog, notes, reviews; about 260 MB), writable, with the
       library's docs/. Then gives it that condition's instructions: AGENTS.md from
       <library-files> (a folder holding the library's AGENTS.md as it was), the guide
       rendered by <engine>'s build-index, and .claude/skills linked to <engine>'s skills.
       Its paper-library.yaml points pdf_root and overview_dir into <work>, so no session
       can write to the reader's PDF folder or notes vault. Keeps <work>/copies/pristine-<condition>
       to reset the copy from, and <work>/bin-<condition>/paperlib, which runs <engine>'s
       command line, so a session's `paperlib` is its condition's engine.
run    Runs each task (all by default) the number of times TASKS gives, once per condition
       each time, in a fresh `claude -p` session started in the copy, with the model the
       task's skill names. Before each run the copy is reset to its pristine state; after it,
       what the run left (files changed in the copy, the overview note, the paper added, the
       notes read) is saved in results/artifacts/<condition>-<task>-r<n>/. The event stream
       goes to results/sessions/<condition>-<task>-r<n>.jsonl (not committed: it holds paper
       text). A run that already succeeded is skipped, so after a usage limit (exit code 3)
       or any failure (exit code 1) the same command continues where it stopped.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = str(HERE.parent.parent / ".venv" / "bin" / "python")
GPT1 = "Improving Language Understanding by Generative Pre-Training"
TASKS = {
    # task: (model, runs per condition, prompt)
    "qa": ("opus", 2, "How does Zep invalidate outdated facts, and what did it score on LongMemEval "
                      "against which baseline?"),
    "overview": ("opus", 2, f"/overview {GPT1}"),
    "add": ("sonnet", 2, "/add-paper 2505.22101"),
    "synthesis": ("opus", 1, "What does current research say about managing obsolete facts in LLM memory?"),
    "reorganize": ("opus", 1, "/reorganize llm/text-analytics"),
    "reviewstatus": ("opus", 1, "/literature-review status"),
    "reviewread": ("opus", 1, "/literature-review read experimentation-and-metrics/variance-reduction 1"),
}
# What `claude -p` says when the account's usage window is used up.
LIMIT = re.compile(r"(session|usage|weekly|daily|monthly) limit|resets? (at )?\d|quota|credit balance", re.I)


def build(library, work, specs):
    copies = work / "copies"
    copies.mkdir(parents=True, exist_ok=True)
    names = [spec.split("=")[0] for spec in specs]
    subprocess.run([sys.executable, str(HERE.parent / "review-usefulness" / "copies.py"), str(library),
                    str(copies), *[f"{n}=asis" for n in names]], check=True)
    for spec in specs:
        name, paths = spec.split("=")
        engine, files = (Path(p) for p in paths.split(":"))
        copy = copies / f"lib-{name}"
        subprocess.run(["chmod", "-R", "u+w", str(copy)], check=True)
        shutil.copytree(library / "docs", copy / "docs")
        if not (files / "places.md").exists():
            (copy / "docs" / "places.md").unlink(missing_ok=True)
        shutil.copy(files / "AGENTS.md", copy / "AGENTS.md")
        for folder in ("pdfs", "overview", "cache"):
            (work / f"{folder}-{name}").mkdir(exist_ok=True)
        (copy / "paper-library.yaml").write_text(
            f"reader: Anton\npdf_root: {work / f'pdfs-{name}'}\n"
            f"overview_dir: {work / f'overview-{name}'}\n")
        subprocess.run([PYTHON, str(engine / "scripts" / "build-index.py")], check=True,
                       env={**os.environ, "PAPER_LIBRARY": str(copy)})
        skills = copy / ".claude" / "skills"
        skills.mkdir(exist_ok=True)
        for skill in (engine / "skills").iterdir():
            if skill.is_dir():
                (skills / skill.name).symlink_to(skill)
        shim = work / f"bin-{name}" / "paperlib"
        shim.parent.mkdir(exist_ok=True)
        shim.write_text(f'#!/bin/sh\nexec "{PYTHON}" "{engine / "scripts" / "cli.py"}" "$@"\n')
        shim.chmod(0o755)
        pristine = copies / f"pristine-{name}"
        subprocess.run(["rsync", "-a", "--delete", f"{copy}/", f"{pristine}/"], check=True)
        print(f"{name}: {copy} (engine {engine}, AGENTS.md from {files})")


def reset(work, condition):
    """The copy, the PDF and overview folders and the cache as they were after build."""
    copy, pristine = work / "copies" / f"lib-{condition}", work / "copies" / f"pristine-{condition}"
    subprocess.run(["rsync", "-a", "--delete", f"{pristine}/", f"{copy}/"], check=True)
    for folder in ("pdfs", "overview", "cache"):
        shutil.rmtree(work / f"{folder}-{condition}", ignore_errors=True)
        (work / f"{folder}-{condition}").mkdir()


def save_artifacts(work, condition, out):
    """What a run left: changed files, overview note, added papers, new notes, inner reads."""
    copy, pristine = work / "copies" / f"lib-{condition}", work / "copies" / f"pristine-{condition}"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    # Files whose content differs from the pristine copy, or that are new or gone: a file a
    # command rewrote unchanged (an index) is not a change.
    listing = subprocess.run(["rsync", "-ainc", "--delete", f"{copy}/", f"{pristine}/"],
                             capture_output=True, text=True).stdout
    changed = []
    for line in listing.splitlines():
        flags, _, rel = line.partition(" ")
        if flags == "*deleting":
            changed.append("deleted: " + rel.strip())
        elif flags[:1] in (">", "c") and flags[1:2] == "f":
            changed.append(rel)
    (out / "changes.txt").write_text("\n".join(changed) + "\n")
    for note in (work / f"overview-{condition}").glob("*.md"):
        shutil.copy(note, out / "overview.md")
    added = []
    for rel in changed:
        path = copy / rel
        if rel.startswith("library/") and rel.endswith(".md") and not rel.endswith("README.md") \
                and path.exists() and not (pristine / rel).exists():
            added.append({"path": rel[len("library/"):], "frontmatter": path.read_text().split("---")[1]})
        elif rel.startswith("notes/") and path.exists():
            shutil.copy(path, out / ("memory.md" if GPT1 in rel else "note-" + Path(rel).name))
        elif rel.startswith("reviews/.work/") and path.exists():
            shutil.copy(path, out / Path(rel).name)
    (out / "added.json").write_text(json.dumps(added, indent=1, ensure_ascii=False))
    log = work / f"cache-{condition}" / "read-papers.jsonl"
    if log.exists():
        shutil.copy(log, out / "reads.jsonl")


def result_of(path):
    for line in reversed(path.read_text().splitlines() if path.exists() else []):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("type") == "result":
            return event
    return None


def succeeded(result):
    return bool(result) and result.get("subtype") == "success" and not result.get("is_error")


def run(work, tasks):
    out = HERE / "results" / "sessions"
    out.mkdir(parents=True, exist_ok=True)
    conditions = sorted(p.name[4:] for p in (work / "copies").glob("lib-*"))
    for task in tasks or TASKS:
        model, runs, prompt = TASKS[task]
        for n in range(1, runs + 1):
            for condition in conditions:
                name = f"{condition}-{task}-r{n}"
                target = out / f"{name}.jsonl"
                if succeeded(result_of(target)):
                    continue
                reset(work, condition)
                env = {**os.environ, "PATH": f"{work / f'bin-{condition}'}{os.pathsep}{os.environ['PATH']}",
                       "PAPERS_CACHE": str(work / f"cache-{condition}")}
                with target.open("w") as stream:
                    done = subprocess.run(
                        ["claude", "-p", prompt, "--model", model, "--output-format", "stream-json",
                         "--verbose", "--no-session-persistence", "--strict-mcp-config",
                         "--add-dir", str(work / f"overview-{condition}"),
                         "--allowedTools", "Read", "Bash", "Write", "Edit", "Glob", "Grep", "Skill",
                         "--disallowedTools", "Agent", "WebSearch", "WebFetch", "NotebookEdit"],
                        cwd=work / "copies" / f"lib-{condition}", stdout=stream, stderr=subprocess.PIPE,
                        text=True, env=env)
                result = result_of(target) or {}
                if succeeded(result):
                    save_artifacts(work, condition, HERE / "results" / "artifacts" / name)
                    print(f"{name}: ok ${result.get('total_cost_usd', 0):.2f}", flush=True)
                    continue
                message = str(result.get("result") or done.stderr or "no result")[:300]
                if LIMIT.search(message) or LIMIT.search(target.read_text()[-3000:]):
                    print(f"{name}: usage limit: {message}\nSwitch account (or wait for the reset) "
                          "and run the same command again; finished runs are kept.", flush=True)
                    sys.exit(3)
                print(f"{name}: FAILED: {message}\nRun the same command again to retry.", flush=True)
                sys.exit(1)


def main(argv):
    if len(argv) >= 4 and argv[0] == "build":
        build(Path(argv[1]).expanduser(), Path(argv[2]).expanduser(), argv[3:])
    elif len(argv) >= 2 and argv[0] == "run":
        run(Path(argv[1]).expanduser(), argv[2:])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
