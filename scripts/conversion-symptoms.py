#!/usr/bin/env python3
"""Find papers whose markdown shows a known conversion problem.

    ./scripts/conversion-symptoms.py [<folder> ...]          # one line per affected paper
    ./scripts/conversion-symptoms.py --counts [<folder> ...]  # papers per symptom
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

--compare <git-ref> instead lists papers whose text shrank by more than 5%
since <git-ref> (words outside markup, so dropped alt text and tags do not
count), the check that a reconversion lost nothing.
"""

import collections
import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

from paperlib import LIBRARY_DIR, REPO_ROOT, paper_files, read_paper

SCRIPTS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("html_to_markdown", SCRIPTS / "html-to-markdown.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)

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
}


def svg_kinds(md, body):
    """"box" and "badge" for linked SVGs the converter would now write as text."""
    kinds = set()
    for link in re.findall(r'images/([^)"\s]+\.svg)', body):
        f = md.parent / "images" / unquote(link)
        if not f.exists():
            continue
        svg = f.read_text(encoding="utf-8", errors="replace")
        if "foreignobject" not in svg.lower():
            continue
        kind = converter.picture_kind(svg[svg.find("<svg"):])
        if kind in ("box", "diagram"):
            kinds.add("box")
        elif kind == "badge":
            kinds.add("badge")
    return kinds


def prose_words(body):
    """Words outside markup: images, tags, table rules and pipes removed."""
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"[|]|^[-:| ]+$", " ", body, flags=re.M)
    return len(body.split())


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
        rel = md.resolve().relative_to(REPO_ROOT)
        old = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=REPO_ROOT, capture_output=True, text=True)
        if old.returncode:
            continue  # not in that commit (added or moved since)
        before, after = prose_words(old.stdout), prose_words(body)
        if before and after < 0.95 * before:
            shrunk += 1
            print(f"{after / before - 1:+.1%}\t{before} -> {after} words\t{md.relative_to(LIBRARY_DIR)}")
    print(f"{shrunk} papers shrank by more than 5% since {ref}", file=sys.stderr)


def main(argv):
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
