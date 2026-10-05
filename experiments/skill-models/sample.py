"""Draw the papers of the experiment: one from each of N folders, so that small folders count
as much as large ones.

    python3 sample.py <library> [N] > papers.txt

Only papers with an abstract heading, an abstract of 400 characters or more and a
stored summary, are drawn. The draw is seeded, so it repeats on the same library.
"""
import random
import sys
from collections import defaultdict
from pathlib import Path

from common import paper


def main():
    library, count = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 60
    root = Path(library) / "library"
    folders = defaultdict(list)
    for path in sorted(root.rglob("*.md")):
        if path.name != "README.md":
            folders[path.parent].append(str(path.relative_to(root))[:-3])
    draw = random.Random(20261005)
    names = sorted(folders)
    draw.shuffle(names)
    chosen = []
    for folder in names:
        candidates = folders[folder][:]
        draw.shuffle(candidates)
        for relative in candidates[:5]:
            p = paper(library, relative)
            if len(p["abstract"]) >= 400 and p["summary"]:
                chosen.append(relative)
                break
        if len(chosen) == count:
            break
    print("\n".join(sorted(chosen)))


if __name__ == "__main__":
    main()
