"""Embed the opening of each paper's main text in chunks, for the `body` variant.

    PAPER_LIBRARY=<library> uv run --with sentence-transformers python body.py <encoder>

The main text is paperlib.text_view's (no references), without page lines; its first
CHUNKS chunks of WORDS words each (abstract, introduction, the start of the method) are
embedded with the encoder's document prefix. Writes <cache>/<encoder>/body.npy and
body-owner.npy (the paper each chunk belongs to, as a row of papers()), and its seconds to
results/cost.jsonl. It saves its work in slices of SLICE chunks (<cache>/<encoder>/body-parts/),
so a run that stops starts again where it stopped. A paper's `body` score for a query is the best of its chunks and its
title, summary and abstract (rank.py).
"""
import json
import sys
import time

import numpy as np

from common import CACHE, ENCODERS, RESULTS, paperlib, papers
from embed import encode, load

WORDS, CHUNKS = 250, 8
SLICE = 1000  # chunks a saved slice: a run that stops resumes after the last whole slice


def chunks(path, meta):
    body = paperlib.split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))[1]
    words = paperlib.PAGE_MARK.sub(" ", paperlib.text_view(meta, body)).split()
    return [" ".join(words[i:i + WORDS]) for i in range(0, min(len(words), WORDS * CHUNKS), WORDS)]


def main(argv):
    if not argv or argv[0] not in ENCODERS:
        sys.exit(__doc__)
    name, spec = argv[0], ENCODERS[argv[0]]
    texts, owner = [], []
    for row, (path, _, meta) in enumerate(papers()):
        for chunk in chunks(path, meta):
            texts.append(chunk)
            owner.append(row)
    parts = CACHE / name / "body-parts"
    parts.mkdir(parents=True, exist_ok=True)
    slices = range(0, len(texts), SLICE)
    todo = [start for start in slices if not (parts / f"{start:06d}.npy").exists()]
    print(f"{name}: {len(texts)} chunks in {len(slices)} slices, {len(todo)} to embed", flush=True)
    model = load(spec, "mps") if todo else None
    began = time.perf_counter()
    for done, start in enumerate(todo, 1):
        matrix = encode(model, texts[start:start + SLICE], spec.get("doc", ""))
        partial = parts / f"{start:06d}.part.npy"
        np.save(partial, matrix)
        partial.rename(parts / f"{start:06d}.npy")
        spent = time.perf_counter() - began
        print(f"{name} body: slice {done} of {len(todo)}, {spent / 60:.0f} min, "
              f"about {spent / done * (len(todo) - done) / 60:.0f} min left", flush=True)
    seconds = round(time.perf_counter() - began, 1)
    matrix = np.vstack([np.load(parts / f"{start:06d}.npy") for start in slices])
    np.save(CACHE / name / "body.npy", matrix)
    np.save(CACHE / name / "body-owner.npy", np.asarray(owner, dtype=np.int32))
    if todo:
        with open(RESULTS / "cost.jsonl", "a", encoding="utf-8") as log:
            log.write(json.dumps({"encoder": name, "variant": "body", "chunks": len(texts),
                                  "seconds_body": seconds, "slices_embedded": len(todo),
                                  "slices": len(slices)}) + "\n")
    print(f"{name} body: {len(texts)} chunks, {len(todo)} slices embedded in {seconds} s")


if __name__ == "__main__":
    main(sys.argv[1:])
