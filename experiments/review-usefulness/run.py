"""Ask each question in a fresh headless session, once per copy of the library.

    python3 run.py <out-dir> <condition>=<library-copy> ...

A session may read files and run shell commands; it cannot edit, search the web or start
subagents. Writes <out-dir>/<condition>-<question>.jsonl (the event stream: every tool
call, and the final result with its usage). A run that already has a result is skipped.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    questions = [line.rstrip("\n").split("\t") for line in open(os.path.join(HERE, "questions.txt"))]
    jobs = []
    for pair in sys.argv[2:]:
        condition, library = pair.split("=")
        for key, question in questions:
            target = os.path.join(out, "%s-%s.jsonl" % (condition, key))
            if os.path.exists(target) and '"type":"result"' in open(target).read():
                continue
            jobs.append((target, subprocess.Popen(
                ["claude", "-p", question, "--output-format", "stream-json", "--verbose",
                 "--allowedTools", "Read", "Bash",
                 "--disallowedTools", "Write", "Edit", "Agent", "WebSearch", "WebFetch",
                 "NotebookEdit", "Skill", "--strict-mcp-config", "--no-session-persistence"],
                cwd=library, stdout=open(target, "w"), stderr=subprocess.DEVNULL)))
    for target, job in jobs:
        job.wait()
        print(os.path.basename(target), job.returncode, flush=True)


if __name__ == "__main__":
    main()
