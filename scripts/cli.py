#!/usr/bin/env python3
"""paperlib: one command for every script in the engine.

    paperlib [-C <library>] <command> [arguments]

Run it anywhere inside a library (a folder with paper-library.yaml at its
root), or name the library with -C or PAPER_LIBRARY. The converters, `init`, `test` and
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
    "add": ("add-paper.py", True, "add arXiv papers, a model choosing the folder and summary: <arxiv-url-or-id> ... [--dry-run]"),
    "info": ("paper-info.py", True, "what is known about a paper, in the library or not: <arxiv-url-or-id or title words> ... [--json] [--facts] [--abstract]"),
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
    "conversion-issues": ("conversion-issues.py", True, "copy the conversion problems notes report into the catalog: [<scope or paper.md> ...]"),
    "localize-figures": ("localize-figures.py", True, "download figures that still link to arXiv"),
    "read": ("read-papers.py", True, "read papers into notes, one request each: <scope or paper.md> ... [--limit N]"),
    "read-view": ("read-view.py", True, "a paper's main text for reading, without references or link targets: <paper.md>"),
    "review-status": ("review-status.py", True, "literature-review coverage and links"),
    "review-refs": ("review-refs.py", True, "turn a review's paper links into reference-style links: [<scope>]"),
    "set-summary": ("paperlib.py", True, "set a paper's summary: <paper.md> <summary>"),
    "set-type": ("paperlib.py", True, "set a paper's type: <paper.md> <type>"),
    "filename": ("paperlib.py", False, "the filename stem for a title: <title>"),
    "html-to-markdown": ("html-to-markdown.py", False, "convert an arXiv HTML rendering"),
    "pdf-to-markdown": ("pdf-to-markdown.py", False, "convert a PDF (docling, plus marker's equation model)"),
    "page-map": ("page-map.py", False, "add (p. N) to headings from the PDF: <paper.pdf> <paper.md>"),
    "caption-numbers": ("caption-numbers.py", False, "number tables and figures as the PDF does: <paper.pdf> <paper.md>"),
}
# paperlib.py's own subcommands keep their name.
PAPERLIB_SUBCOMMANDS = {"set-summary", "set-type", "filename"}


def usage():
    width = max(map(len, COMMANDS)) + 2
    lines = [__doc__.strip(), "", "Commands:"]
    others = {"init": "set up a library here: config, folders, skills, PDF link",
              "test": "run the engine's tests",
              "setup-equations": "install marker (its equation model) in its own environment",
              "install-vscode": "build and install the Paper Library extension for VS Code"}
    from paperlib import styled
    lines += [f"  {styled(name, 1)}{' ' * (width - len(name))}{about}"
              for name, about in [(name, about) for name, (_, _, about) in COMMANDS.items()] + list(others.items())]
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
    if argv[:1] == ["-C"]:
        if len(argv) < 2 or not (Path(argv[1]).expanduser() / "paper-library.yaml").is_file():
            print(f"paperlib -C: no paper library at `{' '.join(argv[1:2])}` (no paper-library.yaml there)",
                  file=sys.stderr)
            return 2
        # Before paperlib is imported: it finds the library when it loads.
        os.environ["PAPER_LIBRARY"] = str(Path(argv[1]).expanduser().resolve())
        argv = argv[2:]
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
    if name == "install-vscode":
        return install_vscode()
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


def install_vscode():
    """Build the extension in editors/vscode into a .vsix and install it into VS Code."""
    missing = [tool for tool in ("npm", "code") if not shutil.which(tool)]
    if missing:
        print(f"install-vscode needs {' and '.join(missing)} on the PATH (Node.js: https://nodejs.org; "
              "code: VS Code's 'Shell Command: Install code command in PATH').", file=sys.stderr)
        return 1
    folder = ENGINE / "editors" / "vscode"
    npm = ["npm", "--prefix", str(folder)]
    code = run(npm + ["ci" if (folder / "package-lock.json").exists() else "install"])
    code = code or run(npm + ["run", "package"])
    return code or run(["code", "--install-extension", str(folder / "paper-library.vsix"), "--force"])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
