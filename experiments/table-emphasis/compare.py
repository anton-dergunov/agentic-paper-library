#!/usr/bin/env python3
"""What the reconversion changed in each sample paper, against the library's last commit.

    python3 compare.py <library worktree> papers.tsv > compare.tsv

One row per paper: size, the marks gained (bold, italics, underline),
footnotes whose mark was printed twice before and after, macro names left as
text, and the words of three letters or more that the new body lacks. Those
words go to stderr, for reading: they should be macro names and the
"thanks" / "footnotemark" labels of notes, nothing else.
"""

import collections
import re
import subprocess
import sys
from pathlib import Path

DOUBLE_MARK = re.compile(r"<sup>([^<]{1,3})</sup><sup>\1</sup>")
MACRO = re.compile(r"(?<![\\$\w])\\[a-zA-Z]{3,}(?![a-zA-Z{])")
MATH = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.S)
FENCE = re.compile(r"^```.*?^```", re.S | re.M)


def prose(body):
    return MATH.sub(" ", FENCE.sub(" ", body))


def words(body):
    text = re.sub(r"<[^>]+>|\]\([^)]*\)", " ", prose(body)).replace("*", "")  # "**P**rompt" is one word
    return collections.Counter(re.findall(r"[A-Za-z]{3,}", text))


def counts(body):
    text = prose(body)
    return {
        "chars": len(body),
        "bold": len(re.findall(r"\*\*[^*\n]+\*\*", text)) + text.count("<b>") + text.count("<strong>"),
        "italic": len(re.findall(r"(?<![*\w])\*[^*\n]+\*(?![*\w])", text)) + text.count("<em>"),
        "underline": text.count("<u>"),
        "double marks": len(DOUBLE_MARK.findall(text)),
        "macro names": len(MACRO.findall(text)),
        "captions": len(re.findall(r"^(?:Table|Figure) [\w.]+:", text, re.M)),
        "paged headings": len(re.findall(r"^#{2,6} .*\(p\. \d+\)$", text, re.M)),
    }


def main():
    library, papers = Path(sys.argv[1]), Path(sys.argv[2])
    keys = list(counts(""))
    print("kind\tpaper\t" + "\t".join(f"{k} before\t{k} after" for k in keys) + "\twords lost")
    totals = collections.Counter()
    for row in papers.read_text(encoding="utf-8").splitlines():
        kind, path = row.split("\t")
        old = subprocess.run(["git", "-C", library, "show", f"HEAD:library/{path}"], capture_output=True, text=True).stdout
        new = (library / "library" / path).read_text(encoding="utf-8")
        if old == new:
            print(f"# unchanged: {path}", file=sys.stderr)
        before, after = counts(old), counts(new)
        lost = words(old) - words(new)
        for k in keys:
            totals[f"{k} before"] += before[k]
            totals[f"{k} after"] += after[k]
        totals["words lost"] += sum(lost.values())
        print("\t".join([kind, Path(path).stem] + [f"{before[k]}\t{after[k]}" for k in keys] + [str(sum(lost.values()))]))
        if lost:
            print(f"# {Path(path).stem[:50]}: " + ", ".join(f"{w}×{n}" for w, n in lost.most_common(12)), file=sys.stderr)
    print("total\t\t" + "\t".join(f"{totals[f'{k} before']}\t{totals[f'{k} after']}" for k in keys) + f"\t{totals['words lost']}")


if __name__ == "__main__":
    main()
