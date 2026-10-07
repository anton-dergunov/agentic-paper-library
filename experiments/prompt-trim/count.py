"""Count the tokens of instruction files, and of the context a session starts with, on a real model.

    python3 count.py files <out.tsv> [--model ID] <name>=<path> ...
    python3 count.py session <out.tsv> [--model ID] <name>=<dir> ...
    python3 count.py flags <out.tsv> [--model ID]

files    Each file's text goes to the model in one `claude -p` request with no tools; its
         tokens are that request's input tokens minus an empty request's. A <path> that is
         a skills folder counts what every session lists of it: each skill's name and
         description.
session  `claude -p "Reply OK."` with Claude Code's own system prompt and tools, started in
         each <dir>: everything a session there starts with (harness, CLAUDE.md chain,
         skill list), the same for every condition except the library's files.
flags    The fixed input of an empty no-tools request, as `paperlib read` and `add` send it,
         under each candidate set of flags and environment variables.

Rows are appended to <out.tsv>: kind, name, characters, input tokens, model. Each request's
result is cached by content in <out.tsv>.cache.json, so a rerun costs nothing.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PROBE = "Reply OK."
# The flags of ask_model in scripts/paperlib.py, with the overhead switched off, so a file's
# count is not mixed with what claude -p adds.
QUIET_ENV = {"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}
FLAG_SETS = {
    "as before (no tools, own system prompt)": ({}, []),
    "+ CLAUDE_CODE_DISABLE_CLAUDE_MDS": ({"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"}, []),
    "+ both env vars (shipped)": (QUIET_ENV, []),
    "+ both env vars + --setting-sources ''": (QUIET_ENV, ["--setting-sources", ""]),
}


def input_tokens(reply):
    usage = reply.get("usage", {})
    return sum(usage.get(k, 0) or 0 for k in
               ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))


class Counter:
    def __init__(self, out, model):
        self.out, self.model = Path(out), model
        self.cache_file = Path(str(out) + ".cache.json")
        self.cache = json.loads(self.cache_file.read_text()) if self.cache_file.exists() else {}

    def run(self, key, argv, prompt, cwd=None, env=None):
        key = hashlib.sha256(json.dumps([key, argv, prompt, self.model]).encode()).hexdigest()
        if key not in self.cache:
            with tempfile.TemporaryDirectory() as empty:
                done = subprocess.run(argv, input=prompt, capture_output=True, text=True,
                                      cwd=cwd or empty, env={**os.environ, **(env or {})})
            reply = json.loads(done.stdout)
            if reply.get("is_error"):
                sys.exit(f"count: request failed: {str(reply.get('result'))[:200]}")
            self.cache[key] = {"tokens": input_tokens(reply), "usd": reply.get("total_cost_usd")}
            self.cache_file.write_text(json.dumps(self.cache, indent=1))
        return self.cache[key]["tokens"]

    def no_tools(self, text, env=QUIET_ENV, extra=()):
        argv = ["claude", "-p", "--model", self.model, "--tools", "", "--system-prompt", PROBE,
                "--output-format", "json", "--no-session-persistence", *extra]
        return self.run(["no-tools", sorted(env.items())], argv, text + "\n\n" + PROBE, env=env)

    def session(self, folder):
        argv = ["claude", "-p", "--model", self.model, "--output-format", "json",
                "--no-session-persistence"]
        # The key holds every instruction file, so an edited copy is counted again.
        files = sorted(p for p in Path(folder).rglob("*") if p.is_file() and p.suffix in (".md", ".json", ".yaml"))
        digest = hashlib.sha256(b"".join(p.read_bytes() for p in files)).hexdigest()
        return self.run(["session", digest], argv, PROBE, cwd=folder)

    def write(self, kind, name, chars, tokens):
        new = not self.out.exists()
        with self.out.open("a", encoding="utf-8") as f:
            if new:
                f.write("kind\tname\tchars\ttokens\tmodel\n")
            f.write(f"{kind}\t{name}\t{chars}\t{tokens}\t{self.model}\n")
        print(f"{kind}\t{name}\t{chars}\t{tokens}")


def skill_list(folder):
    """What a session lists of a skills folder: name and description of each skill."""
    lines = []
    for skill in sorted(Path(folder).glob("*/SKILL.md")):
        head = skill.read_text(encoding="utf-8").split("---")[1]
        name = re.search(r"^name:\s*(.*)$", head, re.M).group(1)
        description = re.search(r"^description:\s*(.*)$", head, re.M).group(1)
        lines.append(f"- {name}: {description}")
    return "\n".join(lines)


def main(argv):
    if len(argv) < 2 or argv[0] not in ("files", "session", "flags"):
        sys.exit(__doc__)
    kind, out, rest = argv[0], argv[1], argv[2:]
    model = "opus"
    if rest[:1] == ["--model"]:
        model, rest = rest[1], rest[2:]
    counter = Counter(out, model)
    if kind == "flags":
        for name, (env, extra) in FLAG_SETS.items():
            counter.write("flags", name, 0, counter.no_tools("", env=env, extra=extra))
        return
    for item in rest:
        name, path = item.split("=", 1)
        path = Path(path).expanduser()
        if kind == "session":
            counter.write("session", name, 0, counter.session(path))
            continue
        text = skill_list(path) if path.is_dir() else path.read_text(encoding="utf-8")
        tokens = counter.no_tools(text) - counter.no_tools("")
        counter.write("file", name, len(text), tokens)


if __name__ == "__main__":
    main(sys.argv[1:])
