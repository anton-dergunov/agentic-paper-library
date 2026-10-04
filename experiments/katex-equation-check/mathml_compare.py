#!/usr/bin/env python3
"""Compare the two routes of mathml.py span by span.

    python3 mathml_compare.py <out-dir> [<examples>]

Counts, over the papers whose two files have the same number of maths spans
(so that span i of one is span i of the other): spans that are identical,
spans that differ, and how often each route keeps things only the author's TeX
has: \\tag numbers, aligned/array environments, \\text, named operators and
font commands. Prints <examples> differing pairs, picked at random with a
fixed seed, for reading side by side.
"""

import collections
import random
import re
import sys
from pathlib import Path

MATH = re.compile(r"\$\$.+?\$\$|(?<![\\$])\$(?!\$)(?:\\.|[^$\\\n])+?\$(?!\$)", re.S)
FEATURES = {
    "\\tag": r"\\tag\{",
    "aligned, split, cases, array, matrix": r"\\begin\{",
    "\\text and \\textrm": r"\\text(?:rm|bf|it|tt|sf)?\{",
    "\\operatorname and named macros": r"\\operatorname",
    "\\mathbf, \\bm, \\boldsymbol": r"\\(?:mathbf|bm|boldsymbol)\b",
    "\\mathcal, \\mathbb": r"\\math(?:cal|bb)\b",
    "\\left ... \\right": r"\\left\b",
    "\\frac": r"\\[dt]?frac\b",
    "\\displaystyle": r"\\displaystyle\b",
    "thin spaces and quads": r"\\[,;:!]|\\q?quad\b",
}


def main(out_dir, examples=0):
    out_dir = Path(out_dir)
    counts = collections.Counter()
    features = {route: collections.Counter() for route in ("tex", "mathml")}
    length = collections.Counter()
    pairs = []
    for tex_file in sorted((out_dir / "tex").glob("*.md")):
        tex = MATH.findall(tex_file.read_text(encoding="utf-8"))
        mathml = MATH.findall((out_dir / "mathml" / tex_file.name).read_text(encoding="utf-8"))
        counts["papers"] += 1
        for route, spans in (("tex", tex), ("mathml", mathml)):
            for name, pattern in FEATURES.items():
                features[route][name] += sum(len(re.findall(pattern, s)) for s in spans)
            length[route] += sum(map(len, spans))
            counts[f"spans, {route}"] += len(spans)
        if len(tex) != len(mathml):
            counts["papers with a different number of spans"] += 1
            continue
        for a, b in zip(tex, mathml):
            same = re.sub(r"\s+", "", a) == re.sub(r"\s+", "", b)
            counts["aligned spans identical" if same else "aligned spans different"] += 1
            if not same:
                pairs.append((tex_file.stem, a, b))
    for name, n in counts.items():
        print(f"{n:>8}  {name}")
    print(f"{length['tex']:>8}  characters of maths, tex\n{length['mathml']:>8}  characters of maths, mathml")
    print("\nfeature                                    tex   mathml")
    for name in FEATURES:
        print(f"{name:<38}{features['tex'][name]:>8}{features['mathml'][name]:>9}")
    random.seed(20261004)
    for paper, a, b in random.sample(pairs, min(int(examples), len(pairs))):
        print(f"\n[{paper}]\n  tex:    {a[:300]}\n  mathml: {b[:300]}")


if __name__ == "__main__":
    main(*sys.argv[1:])
