"""Every change to a paper's body in a library's git history: its size, and whether the paper
had a note (had been read) by then.

    python3 measure.py <library> changes.tsv

Walks the first-parent history of main, oldest first, so a merge counts once, as the change it
brings. A change is a commit that alters a paper's body: the frontmatter is left out, and so
are papers added, deleted, or only moved. Its size is the number of lines changed (the longer
side of each differing block) and the number of characters changed (edit distance over those
blocks), and the share of the body that is. A note's birth is the commit that added it,
followed through renames. Writes one row per change, and notes-born.tsv beside it with the
index of the commit that added each note.
Needs rapidfuzz.
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

from rapidfuzz.distance import Levenshtein

REPO = sys.argv[1]
FM = re.compile(r"\A---\n.*?\n---\n", re.S)


def git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True, check=True).stdout


def blob(spec):
    r = subprocess.run(["git", "-C", REPO, "show", spec], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def body(text):
    return FM.sub("", text, count=1)


def stem(path):
    return path.rsplit("/", 1)[-1][:-3]


# First-parent history, oldest first: merges count once, as the change they bring to main.
commits = git("log", "--first-parent", "--reverse", "--format=%H|%ad|%s", "--date=short").strip().split("\n")
note_born = {}   # stem -> index of the commit that added its note
rows = []
for i, line in enumerate(commits):
    sha, date, subject = line.split("|", 2)
    parent = f"{sha}^1"
    out = git("diff", "--name-status", "-M", parent, sha) if i else git("show", "--name-status", "--format=", sha)
    for entry in out.strip().split("\n"):
        if not entry:
            continue
        parts = entry.split("\t")
        status = parts[0]
        if status.startswith("R"):
            old, new = parts[1], parts[2]
        else:
            old = new = parts[1]
        if new.startswith("notes/") and new.endswith(".md"):
            # A note renamed with its paper keeps its birth.
            if status.startswith("R") and stem(old) in note_born:
                note_born[stem(new)] = note_born[stem(old)]
            elif status == "A":
                note_born.setdefault(stem(new), i)
            continue
        if not (new.startswith("library/") and new.endswith(".md")) or new.endswith("README.md"):
            continue
        if status == "A" or status == "D" or not i:
            continue
        a, b = blob(f"{parent}:{old}"), blob(f"{sha}:{new}")
        if a is None or b is None:
            continue
        ba, bb = body(a), body(b)
        if ba == bb:
            continue  # frontmatter or path only
        al, bl = ba.split("\n"), bb.split("\n")
        changed_lines = changed_chars = 0
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, al, bl, autojunk=False).get_opcodes():
            if op == "equal":
                continue
            old_part, new_part = "\n".join(al[i1:i2]), "\n".join(bl[j1:j2])
            changed_lines += max(i2 - i1, j2 - j1)
            changed_chars += Levenshtein.distance(old_part, new_part)
        rows.append((i, sha[:8], date, subject[:60], stem(new), len(ba), len(al), changed_lines, changed_chars))
    print(f"{i + 1}/{len(commits)} {date} {subject[:50]}", file=sys.stderr)

with open(sys.argv[2], "w") as f:
    f.write("commit_index\tsha\tdate\tsubject\tpaper\tbody_chars\tbody_lines\tchanged_lines\tchanged_chars\tnote_before\n")
    for r in rows:
        before = r[4] in note_born and note_born[r[4]] < r[0]
        f.write("\t".join(map(str, r)) + f"\t{int(before)}\n")
with open(str(Path(sys.argv[2]).with_name("notes-born.tsv")), "w") as f:
    for s, i in note_born.items():
        f.write(f"{s}\t{i}\n")
