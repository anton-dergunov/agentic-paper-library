"""Draw the papers of the experiment: N a type, from the papers whose note gives a type.

    PAPER_LIBRARY=<library> python3 sample.py [N] > papers.txt

Each line is `<the note's type>\t<the paper's path in the library, without its suffix>`.
Drawn with a fixed seed, so it repeats on the same library.
"""
import random
import sys

from common import paperlib, relative


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    by_type = {}
    for paper in sorted(paperlib.paper_index()):
        kind = paperlib.note_fields(paper).get("type")
        if kind and paperlib.has_digest(paper):
            by_type.setdefault(kind, []).append(paper)
    draw = random.Random(20261030)
    for kind in sorted(by_type):
        papers = by_type[kind][:]
        draw.shuffle(papers)
        for paper in sorted(papers[:count]):
            print(f"{kind}\t{relative(paper)}")
    print({k: len(v) for k, v in sorted(by_type.items())}, file=sys.stderr)


if __name__ == "__main__":
    main()
