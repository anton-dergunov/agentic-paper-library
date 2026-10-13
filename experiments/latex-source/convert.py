#!/usr/bin/env python3
"""Convert papers from their arXiv LaTeX source, three ways.

    PAPER_LIBRARY=<library> uv run python convert.py <papers.tsv> [--jobs N] >> results/convert.jsonl

<papers.tsv> has an `arxiv` column. For each paper the source is fetched at
the version of the library's PDF (arxiv.org/e-print, through the engine's
cache) and unpacked, and three candidates are written under
$PAPERS_CACHE/experiments/latex-source/<id>/ (paper text, kept out of the
repository):

  latexml.md  LaTeXML run here (latexmlc, as far as Homebrew's 0.8.8 can be
              made to run as arXiv does), then the engine's html-to-markdown.py
  latexml2.md the same with LaTeXML's limit of 100 errors lifted
              (noerrorlimit.sty.ltxml), for a paper the first run gave up on
  pandoc.md   pandoc -f latex on the root file
  tex.tex     the source as it is: \\input files spliced in, comments and the
              preamble removed except its macro definitions, the .bbl in
              place of \\bibliography

One JSON line a paper says what converted and how long it took. A paper
already converted is skipped; delete its folder to convert it again.
"""

import gzip
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from paperlib import CACHE_DIR, fetch, paper_files, pdf_path_for, read_paper  # noqa: E402
from reconvert import pdf_version  # noqa: E402

spec = importlib.util.spec_from_file_location("html_to_markdown", SCRIPTS / "html-to-markdown.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)

HERE = Path(__file__).resolve().parent
OUT = CACHE_DIR / "experiments" / "latex-source"
# What arXiv preloads, less its own ar5iv bindings, which Homebrew's LaTeXML does not have.
LATEXML = ["latexmlc", "--preload=[nobibtex,ids,localrawstyles,nobreakuntex]latexml.sty",
           "--format=html5", "--pmml", "--mathtex", "--noinvisibletimes", "--timeout=300"]
# One conversion at a time and at low priority: LaTeXML takes a core for minutes.
NICE = ["nice", "-n", "15"]
# Files of a source that a converter would run as code: LaTeXML loads Perl bindings from the paper's folder.
CODE = (".ltxml", ".latexml", ".pl", ".pm")
DEFINITION = re.compile(r"\\(?:re|provide)?newcommand\*?|\\def\b|\\DeclareMathOperator\*?|\\newtheorem\*?|\\let\b")


def unpack(version, folder):
    """Unpack a paper's source into `folder`; return False when arXiv has none (a PDF submission)."""
    data = fetch(f"https://arxiv.org/e-print/{version}")
    if not data or data[:4] == b"%PDF":
        return False
    folder.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tar:
            members = [m for m in tar.getmembers() if not m.name.endswith(CODE)]
            tar.extractall(folder, members=members, filter="data")
    except tarfile.TarError:
        text = gzip.decompress(data)  # a single file
        if text[:4] == b"%!PS":
            return False  # PostScript, of a paper typeset before arXiv took sources
        (folder / "main.tex").write_bytes(text)
    return True


def root_file(version):
    """The name of the paper's root .tex: of the files with a \\documentclass, the one that splices longest."""
    files = {n: t for n, t in converter.source_files(version).items() if n.endswith(".tex")}

    def length(name, depth=0):
        text = files.get(name) or files.get(name + ".tex") or ""
        return len(text) + (0 if depth > 10 else sum(
            length(m.group(1).strip(), depth + 1)
            for m in re.finditer(r"\\(?:input|include|subfile)\s*\{([^}]+)\}", text)))

    roots = [n for n, t in files.items() if r"\documentclass" in t]
    return max(roots, key=length, default=None)


def odd_root(src):
    """A root file that is not named .tex (one paper's is main.flt), or None."""
    for path in sorted(src.rglob("*")):
        if path.is_file() and path.suffix not in (".sty", ".cls", ".tex", ".pdf", ".png", ".jpg", ".eps") \
                and re.search(rb"^\s*\\documentclass", path.read_bytes()[:20000], re.M):
            return path.name
    return None


def group_end(text, start):
    """The index after the brace group or line that the definition starting at `start` ends with."""
    depth, i = 0, start
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == "\n" and depth <= 0:
            return i
        i += 1
    return len(text)


def stripped_tex(version, root_text=None):
    tex = converter.latex_source(version) or (root_text and re.sub(r"(?<!\\)%.*", "", root_text))
    if not tex:
        return None
    preamble, _, body = tex.partition(r"\begin{document}")
    macros, pos = [], 0
    for m in DEFINITION.finditer(preamble):
        if m.start() >= pos:
            pos = group_end(preamble, m.start())
            macros.append(preamble[m.start():pos].strip())
    bbl = max((t for n, t in converter.source_files(version).items() if n.endswith(".bbl")), key=len, default="")
    if bbl:
        body = re.sub(r"\\bibliography\s*\{[^}]*\}|\\printbibliography\b(?:\[[^\]]*\])?", lambda _: bbl, body, count=1)
    body = re.sub(r"\n{3,}", "\n\n", body.replace(r"\end{document}", ""))
    return "\n".join(macros) + "\n\n" + body.strip() + "\n"


def timed(command, **kwargs):
    start = time.time()
    try:
        run = subprocess.run(command, capture_output=True, text=True, **kwargs)
        return run, round(time.time() - start, 1)
    except subprocess.TimeoutExpired:
        return None, round(time.time() - start, 1)


def retry(folder, src, root):
    """Convert again a paper LaTeXML gave up on at its 100th error, with the limit lifted: latexml2.md."""
    html, log_file = folder / "latexml2" / "index.html", folder / "latexml2.log"
    run, seconds = timed(
        [*NICE, *LATEXML, "--preload=noerrorlimit.sty", f"--path={HERE}", f"--path={src}", f"--sourcedirectory={src}",
         f"--dest={html}", f"--log={log_file}", str(src / root)], timeout=360)
    log = log_file.read_text(errors="replace") if log_file.exists() else ""
    counts = re.search(r"Conversion complete: (.*?)(?: \(See|$)", log, re.M)
    record = {"latexml2_s": seconds,
              "latexml2": "timeout" if run is None else counts.group(1).strip() if counts else f"exit {run.returncode}"}
    if html.exists():
        run, _ = timed([*NICE, sys.executable, SCRIPTS / "html-to-markdown.py", html, folder / "latexml2.md",
                        folder / "images2", "paper"], timeout=600)
        if run is None or run.returncode:
            record["latexml2_md"] = "failed: " + ((run.stderr.strip().splitlines() or ["?"])[-1][:200] if run else "timeout")
    return record


def convert(arxiv_id, md):
    version = arxiv_id + pdf_version(pdf_path_for(md), arxiv_id)
    folder = OUT / arxiv_id
    record = {"arxiv": arxiv_id, "version": version, "title": md.stem}
    if (folder / "done").exists():
        return None
    src = folder / "src"
    if not unpack(version, src):
        return {**record, "error": "no source"}
    root = root_file(version) or odd_root(src)
    if not root:
        return {**record, "error": "no root .tex"}
    record["root"] = root
    tex = stripped_tex(version, (src / root).read_text(encoding="utf-8", errors="replace"))
    if len(tex or "") < 3000:
        # A wrapper: \includepdf of the paper, typeset somewhere else.
        return {**record, "error": f"the source is not the paper ({len(tex or '')} characters of TeX)"}
    (folder / "tex.tex").write_text(tex, encoding="utf-8")

    html = folder / "latexml" / "index.html"
    run, record["latexml_s"] = timed(
        [*NICE, *LATEXML, f"--path={src}", f"--sourcedirectory={src}", f"--dest={html}", f"--log={folder / 'latexml.log'}",
         str(src / root)], timeout=360)
    log = (folder / "latexml.log").read_text(errors="replace") if (folder / "latexml.log").exists() else ""
    status = re.search(r"Status:conversion:(\d)", log)
    counts = re.search(r"Conversion complete: (.*)", log)
    record["latexml"] = ("timeout" if run is None else counts.group(1).split(" (See")[0].strip() if counts
                         else f"exit {run.returncode}")
    record["latexml_status"] = int(status.group(1)) if status else None
    if html.exists():
        run, _ = timed([*NICE, sys.executable, SCRIPTS / "html-to-markdown.py", html, folder / "latexml.md",
                        folder / "images", "paper"], timeout=600)
        if run is None or run.returncode:
            record["latexml_md"] = "failed: " + ((run.stderr.strip().splitlines() or ["?"])[-1][:200] if run else "timeout")
    if "too_many_errors" in log:
        record.update(retry(folder, src, root))

    run, record["pandoc_s"] = timed(
        [*NICE, "pandoc", "-f", "latex", "-t", "gfm-tex_math_gfm+tex_math_dollars", "--wrap=none",
         f"--resource-path={src}", "-o", str(folder / "pandoc.md"), str(src / root)],
        timeout=300, env={**os.environ, "TEXINPUTS": f"{src}:"}, cwd=folder)
    if run is None or run.returncode:
        record["pandoc"] = "failed: " + ((run.stderr.strip().splitlines() or ["?"])[-1][:200] if run else "timeout")
    else:
        record["pandoc_warnings"] = len(run.stderr.strip().splitlines())

    (folder / "done").touch()
    return record


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 1
    wanted = [line.split("\t")[0] for line in Path(args[0]).read_text().splitlines()[1:] if line.strip()]
    by_id = {}
    for md in paper_files():
        arxiv_id = str(read_paper(md)[0].get("arxiv") or "")
        if arxiv_id in wanted:
            by_id[arxiv_id] = md
    with ThreadPoolExecutor(jobs) as pool:
        for record in pool.map(lambda i: convert(i, by_id[i]), [i for i in wanted if i in by_id]):
            if record:
                print(json.dumps(record), flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--retry"]:
        # Papers converted before the retry existed: --retry <convert.jsonl> prints their retry records.
        for line in Path(sys.argv[2]).read_text().splitlines():
            r = json.loads(line)
            folder = OUT / r["arxiv"]
            if "too_many_errors" in ((folder / "latexml.log").read_text(errors="replace") if (folder / "latexml.log").exists() else "") \
                    and not (folder / "latexml2.log").exists():
                print(json.dumps({"arxiv": r["arxiv"], **retry(folder, folder / "src", r["root"])}), flush=True)
    else:
        main()
