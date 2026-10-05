"""Ask each question in fresh headless sessions, in each copy of the library.

    python3 run.py <out-dir> [--model ID] [--repeats N] [--questions q1,q3] <condition>=<library-copy> ...

A session may read files and run shell commands; it cannot edit, search the web or start
subagents (and the copies are read-only, see copies.py). Writes
<out-dir>/<condition>-<question>-r<n>.jsonl (the event stream: every tool call, and the
final result with its usage). With --model the sessions use that model instead of the
default, and the condition is named <condition>+<model>, so the other scripts see it as a
condition of its own.

The sessions of one question, all conditions and repeats, start together; the next
question starts when they have finished. A run that already has a successful result is
skipped, so the command can be repeated until everything is done. When a session fails
(a usage limit, usually), no further question is started.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def result_of(path):
    """The final result event of an event stream, or None."""
    result = None
    if os.path.exists(path):
        for line in open(path):
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if isinstance(event, dict) and event.get("type") == "result":
                result = event
    return result


def succeeded(path):
    result = result_of(path)
    return bool(result) and not result.get("is_error") and result.get("subtype") == "success"


def option(args, name, default=None):
    if name not in args:
        return default
    value = args.pop(args.index(name) + 1)
    args.remove(name)
    return value


def main():
    out, pairs = sys.argv[1], sys.argv[2:]
    model = option(pairs, "--model")
    repeats = int(option(pairs, "--repeats", 1))
    only = option(pairs, "--questions")
    os.makedirs(out, exist_ok=True)
    questions = [line.rstrip("\n").split("\t") for line in open(os.path.join(HERE, "questions.txt"))]
    for key, question in questions:
        if only and key not in only.split(","):
            continue
        jobs = []
        for pair in pairs:
            condition, library = pair.split("=")
            if model:
                condition += "+" + model
            for repeat in range(1, repeats + 1):
                target = os.path.join(out, "%s-%s-r%d.jsonl" % (condition, key, repeat))
                if succeeded(target):
                    continue
                jobs.append((target, subprocess.Popen(
                    ["claude", "-p", question, *(["--model", model] if model else []),
                     "--output-format", "stream-json", "--verbose",
                     "--allowedTools", "Read", "Bash",
                     "--disallowedTools", "Write", "Edit", "Agent", "WebSearch", "WebFetch",
                     "NotebookEdit", "Skill", "--strict-mcp-config", "--no-session-persistence"],
                    cwd=library, stdout=open(target, "w"), stderr=subprocess.DEVNULL)))
        failed = 0
        for target, job in jobs:
            job.wait()
            ok = succeeded(target)
            failed += not ok
            result = result_of(target) or {}
            print(os.path.basename(target), "ok" if ok else "FAILED: " + str(result.get("result"))[:200], flush=True)
        if failed:
            sys.exit("%d session(s) of %s failed; run the same command again to resume" % (failed, key))


if __name__ == "__main__":
    main()
