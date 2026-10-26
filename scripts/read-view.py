#!/usr/bin/env python3
"""Print a paper as a reader needs it: the main text, without what a reader skips.

    ./scripts/read-view.py <paper.txt> [--appendix]

Keeps the title and the text layer, with its "[page N]" lines, up to the reference list;
the last line says what was left out. With --appendix, nothing is cut: for a paper whose
main results live in its appendices. A web article's markdown is cut at its references
heading.

Reading this in one call costs a request for the paper instead of four or five for
slices of it (experiments/review-token-cost). `paperlib read` gives a model this text.
"""

import sys
from pathlib import Path

from paperlib import read_paper, text_view


def main(argv):
    appendix = "--appendix" in argv
    argv = [a for a in argv if a != "--appendix"]
    if len(argv) != 1 or argv[0].startswith("-"):
        sys.exit(__doc__)
    path = Path(argv[0])
    if not path.is_file():
        sys.exit(f"read-view: no such paper: {path}")
    sys.stdout.write(text_view(*read_paper(path), appendix=appendix))


if __name__ == "__main__":
    main(sys.argv[1:])
