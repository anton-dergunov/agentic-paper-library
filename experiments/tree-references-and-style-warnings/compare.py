#!/usr/bin/env python3
"""What the reconversion changed in each paper, against the library's last commit.

    python3 compare.py <library> <papers.tsv> > compare.tsv

papers.tsv has two columns: kind ("forest" or "warning") and the paper's path
in the library. For each paper: lines removed and added, the lines of each
kind among them, and the lines that are neither (which should be none).
"""

import difflib
import re
import subprocess
import sys
from pathlib import Path

WARNING = re.compile(r"has been altered\.|violates the \w+ style|Please do not change the page layout"
                     r"|not able to reliably undo arbitrary changes")
ITEM = re.compile(r"^\s*- ")
SECTION_REF = re.compile(r"\[§[\w.-]+\]\(#")
EMPTY_REF = re.compile(r"\(\s*\)|[(\[]\s*§?\s*[)\]]")


def main():
    library, papers = Path(sys.argv[1]), Path(sys.argv[2])
    print("kind\tpaper\tremoved\tadded\twarning lines removed\ttree lines changed\tsection refs added"
          "\tempty brackets before\tempty brackets after\tpadded tree lines before\tother lines changed")
    for row in papers.read_text(encoding="utf-8").splitlines():
        kind, path = row.split("\t")
        old = subprocess.run(["git", "-C", library, "show", f"HEAD:{path}"], capture_output=True, text=True).stdout
        new = (library / path).read_text(encoding="utf-8")
        removed, added = [], []
        for line in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0):
            if line.startswith("-") and not line.startswith("---"):
                removed.append(line[1:])
            elif line.startswith("+") and not line.startswith("+++"):
                added.append(line[1:])
        warnings = [l for l in removed if WARNING.search(l)]
        tree_removed = [l for l in removed if ITEM.match(l)]
        tree_added = [l for l in added if ITEM.match(l)]
        other = [l for l in removed if l.strip() and l not in warnings and l not in tree_removed] + \
                [l for l in added if l.strip() and l not in tree_added]
        print("\t".join(map(str, [
            kind, Path(path).stem, len(removed), len(added), len(warnings), len(tree_added),
            sum(len(SECTION_REF.findall(l)) for l in tree_added),
            sum(len(EMPTY_REF.findall(l)) for l in tree_removed),
            sum(len(EMPTY_REF.findall(l)) for l in tree_added),
            sum(1 for l in tree_removed if re.search("\xa0{2}|^\\s*- \xa0", l)),
            len(other),
        ])))
        for l in other[:6]:
            print(f"#\t{l[:160]}", file=sys.stderr)


if __name__ == "__main__":
    main()
