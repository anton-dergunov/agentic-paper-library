"""Run the same agent tasks in a library copy with the old instructions and one with the new.

    python3 sessions.py build <library> <scratch> before=<engine>:<library-files> after=<engine>:<library-files>
    python3 sessions.py run <scratch> [<task> ...]

build  Makes <scratch>/copies/lib-<condition> with ../review-usefulness/copies.py (paper
       markdown without figures, catalog, notes, reviews; about 260 MB), writable, with the
       library's docs/. Then gives it that condition's instructions: AGENTS.md from
       <library-files> (a folder holding the library's AGENTS.md as it was), the guide
       rendered by <engine>'s build-index, and .claude/skills linked to <engine>'s skills.
       Its paper-library.yaml points pdf_root and overview_dir into <scratch>, so no session
       can write to the reader's PDF folder or notes vault.
run    Runs each task (all by default) once per condition, in a fresh `claude -p` session
       started in the copy, with the model the task's skill names. Writes
       results/sessions/<condition>-<task>.jsonl (the event stream; not committed, it holds
       paper text). A task that already succeeded is skipped.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = str(HERE.parent.parent / ".venv" / "bin" / "python")
GPT1 = "Improving Language Understanding by Generative Pre-Training"
TASKS = {
    # task: (model, prompt)
    "qa": ("opus", "How does Zep invalidate outdated facts, and what did it score on LongMemEval "
                   "against which baseline?"),
    "overview": ("opus", f"/overview {GPT1}"),
    "add": ("sonnet", "/add-paper 2505.22101"),
}


def build(library, scratch, specs):
    copies = scratch / "copies"
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
        for folder in ("pdfs", "overview"):
            (scratch / f"{folder}-{name}").mkdir(exist_ok=True)
        (copy / "paper-library.yaml").write_text(
            f"reader: Anton\npdf_root: {scratch / f'pdfs-{name}'}\n"
            f"overview_dir: {scratch / f'overview-{name}'}\n")
        subprocess.run([PYTHON, str(engine / "scripts" / "build-index.py")], check=True,
                       env={**os.environ, "PAPER_LIBRARY": str(copy)})
        skills = copy / ".claude" / "skills"
        skills.mkdir(exist_ok=True)
        for skill in (engine / "skills").iterdir():
            if skill.is_dir():
                (skills / skill.name).symlink_to(skill)
        print(f"{name}: {copy} (engine {engine}, AGENTS.md from {files})")


def result_of(path):
    for line in reversed(path.read_text().splitlines() if path.exists() else []):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("type") == "result":
            return event
    return None


def run(scratch, tasks):
    out = HERE / "results" / "sessions"
    out.mkdir(parents=True, exist_ok=True)
    conditions = sorted(p.name[4:] for p in (scratch / "copies").glob("lib-*"))
    for task in tasks or TASKS:
        model, prompt = TASKS[task]
        for condition in conditions:
            target = out / f"{condition}-{task}.jsonl"
            done = result_of(target)
            if done and done.get("subtype") == "success" and not done.get("is_error"):
                continue
            copy = scratch / "copies" / f"lib-{condition}"
            with target.open("w") as stream:
                subprocess.run(
                    ["claude", "-p", prompt, "--model", model, "--output-format", "stream-json",
                     "--verbose", "--no-session-persistence", "--strict-mcp-config",
                     "--add-dir", str(scratch / f"overview-{condition}"),
                     "--allowedTools", "Read", "Bash", "Write", "Edit", "Glob", "Grep", "Skill",
                     "--disallowedTools", "Agent", "WebSearch", "WebFetch", "NotebookEdit"],
                    cwd=copy, stdout=stream, stderr=subprocess.DEVNULL)
            result = result_of(target) or {}
            print(f"{condition}-{task}: {'ok' if result.get('subtype') == 'success' else 'FAILED'} "
                  f"${result.get('total_cost_usd', 0):.2f}", flush=True)


def main(argv):
    if len(argv) >= 4 and argv[0] == "build":
        build(Path(argv[1]).expanduser(), Path(argv[2]), argv[3:])
    elif len(argv) >= 2 and argv[0] == "run":
        run(Path(argv[1]), argv[2:])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
