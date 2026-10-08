#!/usr/bin/env python3
"""Find papers whose markdown shows a known conversion problem.

    ./scripts/conversion-symptoms.py [<folder> ...]          # one line per affected paper
    ./scripts/conversion-symptoms.py --counts [<folder> ...]  # papers per symptom
    ./scripts/conversion-symptoms.py --katex [<folder> ...]
    ./scripts/conversion-symptoms.py --compare <git-ref> [<folder> ...]

Looks at papers converted from arXiv HTML (all of them, or those under the
folders given). The symptoms are the ones html-to-markdown.py now fixes, so
after a reconversion they should be gone, except where arXiv's HTML itself
lacks the content:

  flat-table    a line of 25+ numbers: a table flattened into text
  forest        an empty "{forest}" where a tree should be
  pt-residue    a TeX length ("9.24994ptP") left inside an equation
  macro         \\operatorname{mathsection}, esvect internals, an unresolved \\Cref
  figure-link   a figure still linking to arXiv instead of images/
  empty-header  a pipe table whose header row is empty
  box, badge    a linked SVG that the converter would now turn into text
  digit-groups  siunitx numbers with digit groups ("0.769 142 111 540 03")
  raw-citations citations left as BibTeX keys, or references as "LABEL:tab:x"
  true-digits   a number whose digit groups are joined by "true" ("2true294")
  tex-box       \\mathchoice or \\vbox internals in an equation
  captionof     a caption left as "\\captionof" with no number
  empty-ref     a reference with nothing in it ("(Table )", "in Figure .")
  split-title   the title as two lines over a row of "="
  year-citation citations showing only a year ("[2018]")
  input-path    a line that is only a file's path, where \\input was not expanded
  double-mark   a footnote spliced into its sentence, its mark printed twice
  macro-name    the name of a macro LaTeXML did not know, left in the text ("\\sans")

--katex instead lists papers of every source with equations KaTeX (VS Code's
preview) cannot draw, with the number of them and the first error. It needs
Node; KaTeX is installed into scripts/katex/ on first use.

--compare <git-ref> instead lists papers whose text shrank by more than 5%
since <git-ref> (body against body, words outside markup, so frontmatter,
dropped alt text and tags do not count), the check that a reconversion lost
nothing.
"""

import collections
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

from paperlib import LIBRARY_DIR, paper_files, read_paper, split_frontmatter

SCRIPTS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("html_to_markdown", SCRIPTS / "html-to-markdown.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)

# A control sequence in running text; \\captionof has a symptom of its own.
MACRO_NAME = re.compile(r"(?<![\\$\w])\\(?!captionof\b)[a-zA-Z]{3,}(?![a-zA-Z{])")
MATH_OR_CODE = re.compile(r"^```.*?^```|\$\$.*?\$\$|\$[^$\n]+\$|`[^`\n]+`", re.S | re.M)
NUMBER = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")
CHECKS = {
    "flat-table": lambda t: any(
        not line.startswith(("|", "<", "$$", "!")) and len(NUMBER.findall(line)) >= 25
        for line in t.split("\n")),
    "forest": lambda t: "{forest}" in t,
    # A length glued to the next symbol; \kern and \hspace lengths are fine.
    "pt-residue": lambda t: re.search(r"(?<!\\kern )(?<!\\kern)(?:^|[ ,;={(])\d+\.?\d*pt[A-Za-z]", t, re.M),
    "macro": lambda t: re.search(r"operatorname\{math(?:section|paragraph)\}|montrait|\\Cref[a-z]", t),
    "figure-link": lambda t: re.search(
        r"\]\((?:https://arxiv\.org/html/)?\d{4}\.\d{4,5}v\d+/|src=\"\d{4}\.\d{4,5}v\d+/", t),
    "empty-header": lambda t: re.search(r"^\|(?:\s*\|)+\s*\n\|[-:| ]+\|\s*$", t, re.M),
    "digit-groups": lambda t: re.search(r"\d\.\d{3}(?:[ \u2006\u2009\u202f]|\\,)\d{3}(?:[ \u2006\u2009\u202f]|\\,)\d", t),
    "raw-citations": lambda t: "LABEL:" in t or len(re.findall(
        r"\((?:[A-Za-z][\w-]*\d{4}[a-z][\w-]*)(?:; [A-Za-z][\w-]*\d{4}[a-z][\w-]*)*\)", t)) >= 5,
    "true-digits": lambda t: re.search(r"\dtrue\d{3}(?!\d)", t),
    "tex-box": lambda t: re.search(r"\\mathchoice|operatorname\{vbox\}", t),
    "captionof": lambda t: "\\captionof" in t,
    "empty-ref": lambda t: len(re.findall(
        r"\((?:Table|Figure|Fig\.|Section|Appendix) \)|\b(?:in|see|See) (?:Table|Figure|Section|Appendix) [.,)]", t)) >= 2,
    "split-title": lambda t: re.search(r"\A\s*\S[^\n]*\\\n[^\n]+\n=+\s*$", t, re.M),
    "year-citation": lambda t: len(re.findall(r"\[\d{4}[a-z]?\]\(#bib", t)) >= 5,
    "input-path": lambda t: re.search(r"^(?:sections?|tex|content|chapters?|src)/[\w./-]+$", t, re.M),
    "double-mark": lambda t: re.search(r"<sup>([^<]{1,3})</sup><sup>\1</sup>", t),
    "macro-name": lambda t: len(MACRO_NAME.findall(MATH_OR_CODE.sub(" ", t))) >= 3,
}


def svg_kinds(md, body):
    """"box" and "badge" for linked SVGs the converter would now write as text.

    A diagram keeps its image and gets its text as a quote under it, so it
    counts only while that quote is missing.
    """
    kinds = set()
    for m in re.finditer(r'images/([^)"\s]+\.svg)[^\n]*\n\s*(>?)', body):
        f = md.parent / "images" / unquote(m.group(1))
        if not f.exists():
            continue
        svg = f.read_text(encoding="utf-8", errors="replace")
        if "foreignobject" not in svg.lower():
            continue
        kind = converter.picture_kind(svg[svg.find("<svg"):])
        if kind == "box" or kind == "diagram" and not m.group(2):
            kinds.add("box")
        elif kind == "badge":
            kinds.add("badge")
    return kinds


MATH = re.compile(r"\$\$.+?\$\$|(?<![\\$])\$(?!\$)(?:\\.|[^$\\\n])+?\$(?!\$)", re.S)


def prose_words(body):
    """Words outside markup: images, tags, table rules and pipes removed.

    Mathematics is counted apart from the rest, so that a "<" in an equation
    is not read as the start of a tag.
    """
    math = MATH.findall(body)
    body = MATH.sub(" ", body)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)
    body = re.sub(r"</?[A-Za-z][^<>]*>|<!--.*?-->", " ", body, flags=re.S)
    body = re.sub(r"[|]|^[-:| ]+$", " ", body, flags=re.M)
    return len(body.split()) + sum(len(m.split()) for m in math)


def html_papers(folders):
    roots = [Path(f).resolve() for f in folders] or [LIBRARY_DIR]
    for root in roots:
        for md in paper_files(root):
            meta, body = read_paper(md)
            if meta.get("source") == "html" and meta.get("arxiv"):
                yield md, body


def compare(ref, folders):
    shrunk = 0
    for md, body in html_papers(folders):
        # The library's own git history: a path starting with ./ is relative to cwd.
        old = subprocess.run(["git", "show", f"{ref}:./{md.name}"], cwd=md.parent,
                             capture_output=True, text=True)
        if old.returncode:
            continue  # not in that commit (added or moved since)
        # Body against body: the old copy comes with its frontmatter.
        before, after = prose_words(split_frontmatter(old.stdout)[1]), prose_words(body)
        if before and after < 0.95 * before:
            shrunk += 1
            print(f"{after / before - 1:+.1%}\t{before} -> {after} words\t{md.relative_to(LIBRARY_DIR)}")
    print(f"{shrunk} papers shrank by more than 5% since {ref}", file=sys.stderr)


def katex(folders):
    """Papers with maths KaTeX cannot parse: count, first error, path."""
    check = SCRIPTS / "katex"
    if not shutil.which("node"):
        sys.exit("symptoms --katex needs Node.js (node and npm)")
    if not (check / "node_modules" / "katex").exists():
        subprocess.run(["npm", "ci", "--silent"], cwd=check, check=True)
    papers = failures = 0
    for root in [Path(f).resolve() for f in folders] or [LIBRARY_DIR]:
        out = subprocess.run(["node", check / "check.js", root], env={**os.environ, "ALL": "1"},
                             capture_output=True, text=True, check=True).stdout
        first, count = {}, collections.Counter()
        for line in out.split("\n"):
            if line.startswith("FAIL\t"):
                _, path, kind, _ = line.split("\t", 3)
                count[path] += 1
                first.setdefault(path, kind)
        for path, n in sorted(count.items()):
            print(f"{n}\t{first[path]}\t{Path(path).relative_to(LIBRARY_DIR)}")
        papers += len(count)
        failures += sum(count.values())
    print(f"{failures} equations in {papers} papers do not parse in KaTeX", file=sys.stderr)


def main(argv):
    if "--katex" in argv:
        return katex([a for a in argv if not a.startswith("--")])
    if "--compare" in argv:
        i = argv.index("--compare")
        return compare(argv[i + 1], argv[:i] + argv[i + 2:])
    counts_only = "--counts" in argv
    folders = [a for a in argv if not a.startswith("--")]
    counts, affected = collections.Counter(), 0
    for md, body in html_papers(folders):
        found = [name for name, check in CHECKS.items() if check(body)] + sorted(svg_kinds(md, body))
        if found:
            affected += 1
            counts.update(found)
            if not counts_only:
                print(f"{','.join(found)}\t{md.relative_to(LIBRARY_DIR)}")
    if counts_only:
        print(f"{affected} papers with a symptom")
        for name, n in counts.most_common():
            print(f"  {name}: {n}")


if __name__ == "__main__":
    main(sys.argv[1:])
