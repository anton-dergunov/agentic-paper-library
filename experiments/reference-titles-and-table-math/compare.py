#!/usr/bin/env python3
"""What a reconversion changed in each arXiv-HTML paper, against the library's last commit.

    python3 compare.py <library> > compare.tsv

One row per paper that has both versions: size, the characters spent on link
titles, formulas pandoc had rendered into tags inside HTML tables, characters
of formulas holding a picture's drawing commands, captions, headings with a
page, and the words of three letters or more that the new body lacks. The
titles are left out of the old body before its words are counted, since
removing them is the change. The lost words go to stderr, most frequent
first, for reading.
"""

import collections
import re
import subprocess
import sys
from pathlib import Path

TITLE = re.compile(r'(\]\(#[^ )\n]+) "(?:[^"\\\n]|\\.)*"(?=\))|(<a href="#[^"]*") title="[^"]*"')
MATH = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.S)
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
RENDERED_MATH = re.compile(r'<span class="math (?:inline|display)">')


def words(body):
    text = MATH.sub(" ", FENCE.sub(" ", body))
    text = re.sub(r"<[^>]+>|\]\([^)]*\)", " ", text).replace("*", "")
    return collections.Counter(re.findall(r"[A-Za-z]{3,}", text))


def counts(body):
    return {
        "chars": len(body),
        "title chars": sum(len(m.group(0)) - len(m.group(1) or m.group(2)) for m in TITLE.finditer(body)),
        "rendered formulas": len(RENDERED_MATH.findall(body)),
        "picture chars": sum(len(line) for line in body.split("\n") if "pgfpicture" in line),
        "captions": len(re.findall(r"^(?:Table|Figure) [\w.]+:", body, re.M)),
        "paged headings": len(re.findall(r"^#{2,6} .*\(p\. \d+\)$", body, re.M)),
    }


def main():
    library = Path(sys.argv[1])
    changed = subprocess.run(["git", "-C", library, "diff", "--name-only", "-z", "HEAD", "--", "library"],
                             capture_output=True, text=True).stdout.split("\0")
    keys = list(counts(""))
    print("paper\t" + "\t".join(f"{k} before\t{k} after" for k in keys) + "\twords lost")
    totals, lost_words = collections.Counter(), collections.Counter()
    for path in sorted(p for p in changed if p.endswith(".md") and "/images/" not in p):
        old = subprocess.run(["git", "-C", library, "show", f"HEAD:{path}"], capture_output=True, text=True)
        new = library / path
        if old.returncode or not new.exists() or "\nsource: html\n" not in old.stdout[:3000]:
            continue
        new = new.read_text(encoding="utf-8")
        before, after = counts(old.stdout), counts(new)
        lost = words(TITLE.sub(lambda m: m.group(1) or m.group(2), old.stdout)) - words(new)
        lost_words.update(lost)
        print(path.removeprefix("library/") + "\t" + "\t".join(f"{before[k]}\t{after[k]}" for k in keys)
              + f"\t{sum(lost.values())}")
        for k in keys:
            totals[f"{k} before"] += before[k]
            totals[f"{k} after"] += after[k]
        totals["papers"] += 1
        totals["words lost"] += sum(lost.values())
    print("# totals: " + ", ".join(f"{k} {v}" for k, v in totals.items()), file=sys.stderr)
    print("# lost words: " + ", ".join(f"{w} {n}" for w, n in lost_words.most_common(150)), file=sys.stderr)


if __name__ == "__main__":
    main()
