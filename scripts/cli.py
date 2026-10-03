#!/usr/bin/env python3
"""paperlib: one command for every script in the engine.

    paperlib <command> [arguments]

Run it anywhere inside a library (a folder with paper-library.yaml at its
root), or set PAPER_LIBRARY. The converters, `init`, `test` and
`setup-equations` work outside one too. `paperlib <command> --help` shows a
command's own usage where the script has one.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ENGINE = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

# command: (script, needs a library, what it does)
COMMANDS = {
    "add-arxiv": ("add-arxiv-paper.sh", True, "add a paper from arXiv: <arxiv-url-or-id> <topic>"),
    "add-pdf": ("add-pdf-paper.sh", True, "add a local PDF: <file.pdf> <topic> [--title ...] [--source ...]"),
    "add-web": ("add-web-article.py", True, "add a paper published as a web page: <url> <topic>"),
    "add-batch": ("add-batch.py", True, "add a reviewed reading list (TSV), resumably"),
    "lookup": ("arxiv-lookup.py", True, "arXiv metadata, and whether a paper is in the library or skipped"),
    "pending-summaries": ("pending-summaries.py", True, "papers with an empty summary, with abstracts"),
    "apply-summaries": ("apply-summaries.py", True, "write numbered summaries back into papers"),
    "skips": ("reading-list-skips.py", True, "record papers struck from a reading list as skipped"),
    "build-index": ("build-index.py", True, "regenerate every README index and the agent guide"),
    "check": ("check-library.py", True, "check the library is consistent; non-zero on any problem"),
    "move": ("move-paper.sh", True, "move a paper's markdown, figures and PDF: <paper.md> <topic>"),
    "rename": ("rename-papers.py", True, "rename papers whose filename no longer matches the title"),
    "reconvert": ("reconvert.py", True, "regenerate paper bodies with the current converter"),
    "symptoms": ("conversion-symptoms.py", True, "list papers showing known conversion problems"),
    "localize-figures": ("localize-figures.py", True, "download figures that still link to arXiv"),
    "review-status": ("review-status.py", True, "literature-review coverage and links"),
    "set-summary": ("paperlib.py", True, "set a paper's summary: <paper.md> <summary>"),
    "set-type": ("paperlib.py", True, "set a paper's type: <paper.md> <type>"),
    "filename": ("paperlib.py", False, "the filename stem for a title: <title>"),
    "html-to-markdown": ("html-to-markdown.py", False, "convert an arXiv HTML rendering"),
    "pdf-to-markdown": ("pdf-to-markdown.py", False, "convert a PDF (docling, plus marker's equation model)"),
    "page-map": ("page-map.py", False, "add (p. N) to headings from the PDF: <paper.pdf> <paper.md>"),
}
# paperlib.py's own subcommands keep their name.
PAPERLIB_SUBCOMMANDS = {"set-summary", "set-type", "filename"}


def usage():
    width = max(map(len, COMMANDS)) + 2
    lines = [__doc__.strip(), "", "Commands:"]
    lines += [f"  {name:<{width}}{about}" for name, (_, _, about) in COMMANDS.items()]
    lines += [f"  {'init':<{width}}set up a library here: config, folders, skills, PDF link",
              f"  {'test':<{width}}run the engine's tests",
              f"  {'setup-equations':<{width}}install marker (its equation model) in its own environment"]
    return "\n".join(lines)


def run(cmd, env=None):
    return subprocess.run(cmd, env=env).returncode


def script_env(root=None):
    """The scripts call python3 by name: make that this environment's Python."""
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    if root:
        env["PAPER_LIBRARY"] = str(root)
    return env


def main(argv):
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print(usage())
        return 0
    name, args = argv[0], argv[1:]
    if name == "init":
        import init
        return init.main(args)
    if name == "test":
        env = script_env()
        code = run([sys.executable, str(ENGINE / "tests" / "test_conversion.py")], env)
        return code or run([sys.executable, str(ENGINE / "tests" / "test_example_library.py")], env)
    if name == "setup-equations":
        return setup_equations()
    if name not in COMMANDS:
        print(f"paperlib: unknown command `{name}`\n\n{usage()}", file=sys.stderr)
        return 2
    script, needs_library, _ = COMMANDS[name]
    from paperlib import CONFIG_NAME, find_library_root
    root = find_library_root()
    if needs_library and not root:
        print(f"paperlib {name}: not inside a paper library (no {CONFIG_NAME} here or above, "
              "and PAPER_LIBRARY is not set). Run `paperlib init` to make one.", file=sys.stderr)
        return 2
    path = SCRIPTS / script
    cmd = [str(path)] if script.endswith(".sh") else [sys.executable, str(path)]
    if name in PAPERLIB_SUBCOMMANDS:
        cmd.append(name)
    return run(cmd + args, script_env(root))


def setup_equations():
    """marker pins different versions of docling's libraries, so it gets its own venv."""
    from paperlib import CACHE_DIR
    venv = CACHE_DIR / "venvs" / "marker"
    if not shutil.which("uv"):
        print("setup-equations needs uv: https://docs.astral.sh/uv/", file=sys.stderr)
        return 1
    code = run(["uv", "venv", "--python", "3.12", str(venv)]) if not venv.exists() else 0
    code = code or run(["uv", "pip", "install", "--python", str(venv / "bin" / "python"), "marker-pdf"])
    if not code and not shutil.which("llama-server"):
        print("Also install llama.cpp, which serves marker's model (brew install llama.cpp).")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
