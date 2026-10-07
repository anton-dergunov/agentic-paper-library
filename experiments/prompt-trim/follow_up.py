"""Run the follow-up measurements, resumably: one command, run again until it says done.

    python3 follow_up.py [<work>] [--library <library>]

<work> (default ~/.cache/papers/prompt-trim) holds what outlives a session: the old engine
(engine-before/), the library's old AGENTS.md (papers-before/), the library copies, and each
condition's mini library and caches. <library> defaults to ~/papers.

Steps, each skipped when its results exist:
  1. build the before and after library copies (sessions.py build);
  2. read every paper of papers.txt in three conditions: before, before again, after (reads.py);
  3. judge the notes (judge.py);
  4. run every session task (sessions.py run);
  5. grade the sessions (check.py) and print what the experiment has spent.

When the account's usage limit is reached, a step stops with exit code 3 and keeps what it
finished. Switch account (`/login` in Claude Code, or wait for the reset) and run the same
command again: it continues where it stopped.
"""
import glob
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent.parent
PYTHON = str(ENGINE / ".venv" / "bin" / "python")


def step(title, argv):
    print(f"\n== {title}", flush=True)
    code = subprocess.run(argv, cwd=HERE).returncode
    if code:
        print(f"\nfollow_up: stopped at \"{title}\" (exit code {code}). "
              + ("The usage limit was reached: switch account or wait for the reset, then "
                 if code == 3 else "")
              + "run the same command again; finished work is kept.", flush=True)
        sys.exit(code)


def spent():
    usd = {}
    for name in ("before", "after"):
        cache = HERE / "results" / f"tokens-{name}.tsv.cache.json"
        if cache.exists():
            usd["accounting"] = usd.get("accounting", 0) + sum(v["usd"] or 0 for v in json.loads(cache.read_text()).values())
    for log in (HERE / "results").glob("reads-*.jsonl"):
        usd["reads"] = usd.get("reads", 0) + sum(json.loads(line)["usd"] or 0 for line in log.read_text().splitlines() if line.strip())
    usd["judge"] = sum(json.loads(Path(p).read_text()).get("usd") or 0 for p in glob.glob(str(HERE / "results" / "judge" / "*.json")))
    total = 0.0
    for stream in (HERE / "results" / "sessions").glob("*.jsonl"):
        for line in reversed(stream.read_text().splitlines()):
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "result":
                total += event.get("total_cost_usd") or 0
                break
    usd["sessions"] = total
    for art in (HERE / "results" / "artifacts").glob("*/reads.jsonl"):
        usd["reads inside sessions"] = usd.get("reads inside sessions", 0) + sum(
            json.loads(line)["usd"] or 0 for line in art.read_text().splitlines() if line.strip())
    print("\nSpent, as `claude -p` reports it (not counting the probes run by hand while planning):")
    for key, value in usd.items():
        print(f"  {key:<24} ${value:6.2f}")
    print(f"  {'total':<24} ${sum(usd.values()):6.2f}")


def main(argv):
    library = Path("~/papers").expanduser()
    if "--library" in argv:
        i = argv.index("--library")
        library = Path(argv[i + 1]).expanduser()
        argv = argv[:i] + argv[i + 2:]
    work = Path(argv[0] if argv else "~/.cache/papers/prompt-trim").expanduser()
    for needed in ("engine-before", "papers-before"):
        if not (work / needed).exists():
            sys.exit(f"follow_up: {work / needed} is missing: see the README's follow-up section")
    if not all((work / "copies" / f"pristine-{c}").exists() for c in ("before", "after")):
        step("build the library copies", [sys.executable, "sessions.py", "build", str(library), str(work),
                                          f"before={work / 'engine-before'}:{work / 'papers-before'}",
                                          f"after={ENGINE}:{library}"])
    for condition, engine in (("before", work / "engine-before"), ("before-repeat", work / "engine-before"),
                              ("after", ENGINE)):
        step(f"read the papers: {condition}", [sys.executable, "reads.py", str(library), str(engine), str(work),
                                              condition, "--python", PYTHON])
    step("judge the notes", ["env", f"PAPER_LIBRARY={library}", PYTHON, "judge.py"])
    step("run the sessions", [sys.executable, "sessions.py", "run", str(work)])
    step("grade the sessions", [sys.executable, "check.py", str(work)])
    spent()
    print("\nfollow_up: done.")


if __name__ == "__main__":
    main(sys.argv[1:])
