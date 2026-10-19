#!/usr/bin/env python3
"""Move a library's hand edits into corrections/, onto the papers' fresh conversions.

    PAPER_LIBRARY=~/papers uv run python migrate.py <fresh library dir> [--write]

For each hand-edited paper converted afresh in <fresh library dir> (see reapply.py), the
corrections are its marked edits captured against the fresh conversion
(diff_corrections(<fresh>, <paper now>, marked_only)), less those listed in DROP after
review (the converter's own change beside a marked block). Without --write they are
printed. With --write each paper becomes what `paperlib reconvert` would make of it: the
fresh conversion and its figures (keeping the figures the corrections link) with the
corrections applied again, and corrections/<stem>.yaml written. The fresh conversions are
the current converter's output, so this is the reconversion without running it twice.
"""

import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from paperlib import (  # noqa: E402
    HAND_EDITED, LIBRARY_DIR, content_lines, diff_corrections, paper_files, read_paper, save_corrections,
    write_paper,
)
import reconvert  # noqa: E402

# Corrections that review found to be the converter's change, not the edit: (stem prefix,
# a regex on `was`). Kept short, and each one says why.
DROP = [
    # A-TMA: the captions under the two cropped figures differ only by the bold the
    # converter now gives their titles.
    ("A-TMA.", r"^Figure [23]: \*\*"),
    # Yahoo: the converter now reads Eq. (3) itself (the number-only fix), as the edit
    # wrote it but for spacing; and it writes the paragraph after Table 1 with its
    # inline mathematics, which the edited paper had flattened.
    ("Ranking Relevance in Yahoo", r"\\quad \(3\)\$\$"),
    ("Ranking Relevance in Yahoo", r"^Logistic loss targets"),
    ("Ranking Relevance in Yahoo", r"^where \$\\text\{scale\}"),
    # Toward Activity Discovery: the converter now writes Table 4's caption with its
    # mathematics; the edited paper kept the older text.
    ("Toward Activity Discovery", r"^Table 4: Performance"),
    # Memory in the Age of AI Agents: the converter now downloads arXiv's Figure 1, whole
    # and sharper than the crop from the PDF that stood in for it.
    ("Memory in the Age of AI Agents", r"-fig02\.webp"),
]
# Fields review set by hand: (stem prefix, `where` or "" for any) → fields.
FIX = [
    ("Text-to-SQL", "", {"where": "title and authors"}),
    ("PersonaMem-v3", "", {"why": "Figure 3 transcribed, since the figure is an image"}),
]


def dropped(stem, correction):
    return any(stem.startswith(prefix) and re.search(pattern, correction.get("was") or "", re.M)
               for prefix, pattern in DROP)


def fixed(stem, correction):
    for prefix, where, fields in FIX:
        if stem.startswith(prefix) and where in ("", correction.get("where")):
            correction = {**correction, **fields}
    # A note left beside an edit that says reconvert skips the paper is no longer true.
    now = "\n".join(line for line in correction["now"].split("\n")
                    if not re.match(r"<!--.*reconvert\.py skips.*-->$", line.strip()))
    return {**correction, "now": now.strip("\n")}


def main(argv):
    fresh_root = Path(argv[0]).resolve()
    write = "--write" in argv
    total = 0
    for p in paper_files():
        meta, body = read_paper(p)
        if not HAND_EDITED.search(body):
            continue
        fresh_path = fresh_root / "library" / p.relative_to(LIBRARY_DIR)
        if not fresh_path.exists() or read_paper(fresh_path)[1] == body:
            print(f"{p.stem[:70]}: no fresh conversion, left as it is")
            continue
        fresh_meta, fresh = read_paper(fresh_path)
        corrections = [fixed(p.stem, c) for c in diff_corrections(fresh, body, marked_only=True)
                       if not dropped(p.stem, c)]
        total += len(corrections)
        print(f"{p.stem[:70]}: {len(corrections)} corrections")
        for c in corrections:
            print(f"    {c['where'] or '?':24s} {len(content_lines(c['was'])):3d} → {len(content_lines(c['now'])):3d} lines"
                  f" · {' '.join((c['why'] or '').split())[:90]}")
        if not write:
            continue
        save_corrections(p, corrections)
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp) / "images"
            images.mkdir()
            for f in (fresh_path.parent / "images").glob(f"{reconvert.glob_escape(p.stem)}-fig*"):
                shutil.copy2(f, images / f.name)
            reconvert.replace_images(p, images)
        write_paper(p, fresh_meta, fresh)
        print("    " + reconvert.reapply(p, corrections))
    print(f"{total} corrections" + ("" if write else " (dry run; --write applies them)"))


if __name__ == "__main__":
    main(sys.argv[1:])
