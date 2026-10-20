#!/usr/bin/env python3
"""How often does LaTeXML drop a \\multirow's span, and does the HTML show where it did?

    python3 -I multirow_spans.py

For every paper whose LaTeX source and arXiv rendering are both in the cache, finds each
\\multirow{n} of two rows or more in the source and the table cells of the rendering that
hold the same words: the span is kept when one of them has a rowspan. Prints the counts by
the sign of n, and then the most common shapes of the cells' markup (text taken out), for
the cells whose span was dropped and for all others: a shape only the first have would let
the converter fetch the source only where it is needed. Words are matched loosely ("Yes",
"No" match anywhere), so the shape counts are rough; the span counts read only labels found.
"""

import collections
import gzip
import html
import io
import re
import tarfile
from pathlib import Path

CACHE = Path("~/.cache/papers/arxiv").expanduser()


def tex(version):
    data = gzip.decompress((CACHE / "e-print" / f"{version}.gz").read_bytes())
    try:
        tar = tarfile.open(fileobj=io.BytesIO(data), mode="r:*")
        return "\n".join(tar.extractfile(m).read().decode("utf-8", "replace")
                         for m in tar.getmembers() if m.isfile() and m.name.endswith(".tex"))
    except tarfile.TarError:
        try:
            return gzip.decompress(data).decode("utf-8", "replace")
        except OSError:
            return data.decode("utf-8", "replace")


def argument(s, i):
    """The braced argument opening at s[i], and where it ends."""
    depth = 0
    for j in range(i, len(s)):
        depth += {"{": 1, "}": -1}.get(s[j], 0)
        if depth == 0:
            return s[i + 1:j], j + 1
    return None, len(s)


def words(text):
    return tuple(re.findall(r"[A-Za-z0-9]+", re.sub(r"\\[a-zA-Z]+", " ", text)))


def labels(source):
    """(n, the label's words) of each \\multirow{n}[...]{width}[...]{label}."""
    for m in re.finditer(r"\\multirow\s*\{\s*(-?[\d.]+)\s*\}", source):
        i, text = m.end(), None
        for _ in range(2):  # the width, then the label
            i = re.match(r"\s*(?:\[[^\]]*\])?", source[i:]).end() + i
            if i >= len(source) or source[i] != "{":
                text = None
                break
            text, i = argument(source, i)
        if text is not None:
            yield float(m.group(1)), words(text)


spans, shapes, others = collections.Counter(), collections.Counter(), collections.Counter()
papers = collections.defaultdict(set)
for path in sorted((CACHE / "e-print").glob("*.gz")):
    version = path.name[:-3]
    rendering = CACHE / "html" / version / "index.html.gz"
    if not rendering.exists():
        continue
    source = re.sub(r"(?<!\\)%.*", "", tex(version))
    page = gzip.decompress(rendering.read_bytes()).decode("utf-8", "replace")
    cells = [(m.group(2), m.group(3), words(html.unescape(re.sub(r"<math.*?</math>|<[^>]+>", " ", m.group(3)))))
             for m in re.finditer(r"<(t[dh])\b([^>]*)>(.*?)</\1>", page, re.S)]
    found = {}
    for n, label in labels(source):
        if not label or abs(n) < 1.5:
            continue
        hits = [attrs for attrs, _, w in cells if w == label]
        if not hits:
            spans["label not found"] += 1
            continue
        kept = any(re.search(r'rowspan="[2-9]', attrs) for attrs in hits)
        spans[("n < 0" if n < 0 else "n > 0", "kept" if kept else "dropped")] += 1
        papers[version].add(kept)
        found[label] = found.get(label, True) and kept
    for attrs, inner, w in cells:
        if not w:
            continue
        inner = re.sub(r'\s(?:id|style)="[^"]*"', "", inner).strip()
        shape = re.sub(r">[^<]+<", "><", re.sub(r"<math.*?</math>", "<math/>", inner, flags=re.S))[:100]
        (shapes if found.get(w) is False and not re.search(r'rowspan="[2-9]', attrs) else others)[shape] += 1

print(dict(spans))
print(f"papers with a dropped span: {sum(False in k for k in papers.values())} of {len(papers)}")
for name, counter in (("dropped", shapes), ("all other cells", others)):
    print(f"\nshapes, {name}:")
    for shape, n in counter.most_common(8):
        print(f"{n:7} {shape}")
