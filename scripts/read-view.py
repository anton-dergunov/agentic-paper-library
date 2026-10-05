#!/usr/bin/env python3
"""Print a paper as a reader needs it: the main text, without what a reader skips.

    ./scripts/read-view.py <paper.md> [--appendix]

Keeps the title and the body up to the references heading, with the (p. N) markers on
headings and the tables as they are. Drops the frontmatter, link targets (the link text
stays), inline span, sup and anchor tags, and image links: a figure becomes "[figure]"
beside its caption. The last line says what was left out. With --appendix, the sections
after the reference list are kept: for a paper whose main results live there.

Reading this in one call costs a request for the paper instead of four or five for
slices of it (experiments/review-token-cost). `paperlib read` gives a model this text.
"""

import sys
from pathlib import Path

from paperlib import read_paper, read_view


def main(argv):
    appendix = "--appendix" in argv
    argv = [a for a in argv if a != "--appendix"]
    if len(argv) != 1 or argv[0].startswith("-"):
        sys.exit(__doc__)
    path = Path(argv[0])
    if not path.is_file():
        sys.exit(f"read-view: no such paper: {path}")
    sys.stdout.write(read_view(*read_paper(path), appendix=appendix))


if __name__ == "__main__":
    main(sys.argv[1:])
