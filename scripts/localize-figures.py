#!/usr/bin/env python3
"""Download figures that papers still link on arXiv into their images/ folder.

    ./scripts/localize-figures.py <paper.md> [<paper.md> ...]
    ./scripts/localize-figures.py --all
    ./scripts/localize-figures.py --all --pause 2   # slower, when arXiv throttles

Papers converted before the converter stored raster figures locally link them
on arxiv.org. This downloads each one, stores it as WebP like the converter
does (paperlib.to_webp), numbers it after the paper's existing figures and
rewrites the link. Only the links change, so hand-edited papers are safe to
run on. A figure that fails to download keeps its arXiv link; re-run later.
arXiv answers bursts of requests with HTTP 406 for a while, so a re-run for
the failures goes better with a longer --pause between downloads (seconds).
"""

import sys
from pathlib import Path
from urllib.parse import quote

from paperlib import ARXIV_FIGURE, localize_figures, paper_files, read_paper, write_paper


def next_figure_number(images, stem):
    numbers = [0]
    for f in images.glob("*"):
        if f.name.startswith(f"{stem}-fig"):
            digits = f.name[len(stem) + 4:].split(".")[0]
            if digits.isdigit():
                numbers.append(int(digits))
    return max(numbers) + 1


def localize(md, pause):
    meta, body = read_paper(md)
    if not ARXIV_FIGURE.search(body):
        return None
    images = md.parent / "images"
    number = next_figure_number(images, md.stem)

    def save(data):
        nonlocal number
        name = f"{md.stem}-fig{number:02d}.webp"
        number += 1
        images.mkdir(exist_ok=True)
        (images / name).write_bytes(data)
        return f"images/{quote(name)}"

    new_body, failed = localize_figures(body, save, pause=pause)
    write_paper(md, meta, new_body)
    total = len({m.group(2) for m in ARXIV_FIGURE.finditer(body)})
    return f"{total - failed} of {total} figures saved" + (f", {failed} failed" if failed else "")


def main(argv):
    pause = 0.2
    if "--pause" in argv:
        i = argv.index("--pause")
        pause = float(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    papers = paper_files() if argv == ["--all"] else [Path(a).resolve() for a in argv]
    if not papers:
        sys.exit(__doc__)
    for i, md in enumerate(papers):
        result = localize(md, pause)
        if result:
            print(f"[{i + 1}/{len(papers)}] {md.stem[:70]}: {result}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
